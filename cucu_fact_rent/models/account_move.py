# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import json
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    # ========== IDENTIFICACIÓN SECTOR ALQUILERES ==========
    is_rent_invoice = fields.Boolean(
        string='Factura Alquileres',
        help='Marcar si esta factura pertenece al sector alquileres (artículo X normativa SIN)'
    )
    
    # ========== CAMPOS ESPECÍFICOS SECTOR ALQUILERES ==========
    rent_billed_period = fields.Char(
        string='Período Facturado',
        help='Período de alquiler que se está facturando. Ejemplo: "mayo 12", "Enero 2026"'
    )
    
    rent_property_address = fields.Text(
        string='Dirección Inmueble',
        help='Dirección completa del inmueble en alquiler'
    )
    
    rent_type_operation = fields.Selection([
        ('1', 'Alquiler'),
        ('2', 'Venta'),
    ], string='Tipo Operación', default='2', help='Tipo de operación según catálogo SIN')
    
    # ========== RESPUESTA CUCU ALQUILERES ==========
    cucu_rent_cuf = fields.Char(
        string='CUF Alquileres',
        readonly=True,
        copy=False,
        help='Código Único de Factura generado por SIN para sector alquileres'
    )
    
    cucu_rent_response = fields.Text(
        string='Respuesta API Alquileres',
        readonly=True,
        copy=False,
        help='Respuesta completa de CUCU API (JSON)'
    )
    
    cucu_rent_state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviada a CUCU'),
        ('validated', 'Validada por SIN'),
        ('rejected', 'Rechazada'),
        ('cancelled', 'Anulada'),
    ], string='Estado CUCU Alquileres', default='draft', readonly=True, copy=False)
    
    # ========== ONCHANGE ==========
    @api.onchange('is_rent_invoice')
    def _onchange_is_rent_invoice(self):
        """Autocompletar campos al marcar como factura de alquileres"""
        if self.is_rent_invoice and not self.rent_billed_period:
            # Sugerir período actual
            from datetime import datetime
            month_names = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }
            now = datetime.now()
            self.rent_billed_period = f"{month_names[now.month]} {now.year}"
    
    # ========== PREPARAR PAYLOAD ==========
    def _prepare_cucu_rent_invoice_data(self):
        """Prepara el payload JSON según especificaciones CUCU API para alquileres"""
        self.ensure_one()
        
        # Validaciones previas
        if not self.company_id.cucu_rent_username:
            raise UserError(
                'Configure las credenciales CUCU para sector alquileres en:\n'
                'Configuración > Compañías > Facturación Alquileres'
            )
        
        if not self.rent_billed_period:
            raise UserError('El campo "Período Facturado" es obligatorio para facturas de alquileres')
        
        if not self.invoice_line_ids.filtered(lambda l: not l.display_type):
            raise UserError('La factura debe tener al menos una línea de producto/servicio')
        
        # Preparar detalle de factura
        detail_invoice = []
        for line in self.invoice_line_ids.filtered(lambda l: not l.display_type):
            detail_invoice.append({
                'activityEconomic': '465000',  # Código actividad económica: alquileres
                'unitMeasure': 62,  # Unidad de medida: Servicio
                'codeProductSin': 99100,  # Código producto SIN: servicios genéricos
                'codeProduct': line.product_id.default_code or f'ALQ-{line.product_id.id}',
                'description': line.name or 'Servicio de Alquiler',
                'qty': line.quantity,
                'priceUnit': line.price_unit
            })
        
        # Construir payload según documentación CUCU
        payload = {
            'posId': 1,
            'clientReasonSocial': self.partner_id.name,
            'clientDocumentType': '1',  # 1=CI, 5=NIT
            'clientNroDocument': self.partner_id.vat or '0',
            'clientCode': self.partner_id.ref or f'CLI-{self.partner_id.id}',
            'paramPaymentMethod': '1',  # 1=Efectivo, 2=Tarjeta, etc.
            'dateEmission': (
                self.invoice_date.strftime('%Y-%m-%dT%H:%M:%S') 
                if self.invoice_date 
                else fields.Datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            ),
            'userPos': 'A4INC12ABCH',  # Usuario punto de venta
            'paramDocumentSector': '1',  # Sector según catálogo SIN
            'paramCurrency': '1',  # 1=BOB, 2=USD
            'clientComplement': self.partner_id.street2 or '',
            'clientCity': self.partner_id.city or 'La Paz',
            'clientEmail': self.partner_id.email or '',
            'typeInvoice': 1,  # 1=Con derecho a crédito fiscal
            'typeOperation': int(self.rent_type_operation) if self.rent_type_operation else 2,
            'billedPeriod': self.rent_billed_period,  # 🔑 Campo obligatorio sector alquileres
            'detailInvoice': detail_invoice
        }
        
        return payload
    
    # ========== ACCIÓN: ENVIAR A CUCU ==========
    def action_send_rent_invoice_cucu(self):
        """Acción de botón: Enviar factura de alquileres a CUCU API"""
        self.ensure_one()
        
        # Validaciones
        if not self.is_rent_invoice:
            raise UserError('Esta factura no está marcada como factura de alquileres')
        
        if self.state != 'posted':
            raise UserError('Solo se pueden enviar facturas confirmadas (estado: Publicado)')
        
        if self.cucu_rent_cuf:
            raise UserError(
                f'Esta factura ya fue enviada a CUCU.\n'
                f'CUF: {self.cucu_rent_cuf}\n\n'
                f'Para reenviar, primero debe anularla.'
            )
        
        # Llamar al servicio API
        api_service = self.env['cucu.rent.api']
        
        try:
            _logger.info(f'=== Iniciando envío de factura {self.name} a CUCU (Alquileres) ===')
            
            result = api_service.send_rent_invoice(self)
            
            # Guardar respuesta en la factura
            self.write({
                'cucu_rent_cuf': result.get('cuf'),
                'cucu_rent_response': json.dumps(result, indent=2, ensure_ascii=False),
                'cucu_rent_state': 'validated' if result.get('cuf') else 'rejected'
            })
            
            _logger.info(f'Factura {self.name} enviada exitosamente. CUF: {result.get("cuf")}')
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Factura Enviada a CUCU',
                    'message': f'CUF generado: {result.get("cuf")}',
                    'type': 'success',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            _logger.error(f'Error al enviar factura {self.name}: {error_msg}')
            
            self.write({
                'cucu_rent_response': f'ERROR: {error_msg}',
                'cucu_rent_state': 'rejected'
            })
            
            raise UserError(f'❌ Error al enviar factura a CUCU:\n\n{error_msg}')