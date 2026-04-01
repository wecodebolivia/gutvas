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

    # ========== INTERCEPCIÓN PIPELINE cucu_fact_core ==========
    def create_invoice_account(self):
        """
        Intercepción del pipeline de cucu_fact_core:
        Las facturas de alquileres NO deben procesarse a través del webservice
        de ventas/compras. El envío se realiza manualmente mediante el botón
        'Enviar a CUCU (Alquileres)' que usa los endpoints y credenciales
        propios de cucu_fact_rent.
        """
        if self.is_rent_invoice:
            return None
        return super().create_invoice_account()

    # ========== ONCHANGE ==========
    @api.onchange('is_rent_invoice')
    def _onchange_is_rent_invoice(self):
        """Autocompletar campos al marcar como factura de alquileres"""
        if self.is_rent_invoice and not self.rent_billed_period:
            from datetime import datetime
            month_names = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }
            now = datetime.now()
            self.rent_billed_period = f"{month_names[now.month]} {now.year}"

    # ========== PREPARAR DETALLE DE LÍNEAS ==========
    def _prepare_cucu_rent_detail_line(self, line):
        """
        Construye el dict de detalle para una línea de factura de alquiler.
        Lee activityEconomic, codeProductSin y unitMeasure directamente del
        producto (igual que cucu_fact_core), lanzando errores descriptivos
        si algún campo SIN no está configurado.
        """
        product = line.product_id
        tmpl = product.product_tmpl_id

        # ── activityEconomic ──────────────────────────────────────────────────
        activity_code = (
            tmpl.code_type_activity
            or getattr(tmpl.code_activity_sin_id, 'code_type', None)
        )
        if not activity_code:
            raise UserError(
                f'El producto "{product.display_name}" no tiene configurada la '
                f'Actividad Económica SIN (code_activity_sin_id).\n\n'
                f'Configúralo en: Producto > pestaña SIN > "Actividad Económica".'
            )

        # ── codeProductSin ────────────────────────────────────────────────────
        code_product_sin = tmpl.sin_code_product or product.sin_code_product
        if not code_product_sin:
            raise UserError(
                f'El producto "{product.display_name}" no tiene configurado el '
                f'Código de Producto SIN (code_product_sin_id).\n\n'
                f'Configúralo en: Producto > pestaña SIN > "Código Producto SIN".'
            )

        # ── unitMeasure ───────────────────────────────────────────────────────
        unit_measure = (
            tmpl.unit_measure_id.code_type
            or product.unit_measure_id.code_type
        )
        if not unit_measure:
            raise UserError(
                f'El producto "{product.display_name}" no tiene configurada la '
                f'Unidad de Medida SIN (unit_measure_id).\n\n'
                f'Configúralo en: Producto > pestaña SIN > "Unidad de Medida".'
            )

        # ── codeProduct (referencia interna) ──────────────────────────────────
        if not product.default_code:
            raise UserError(
                f'El producto "{product.display_name}" no tiene Referencia Interna '
                f'(default_code).\n\n'
                f'Configúralo en: Producto > "Referencia Interna".'
            )

        return {
            'activityEconomic': activity_code,
            'unitMeasure': unit_measure,
            'codeProductSin': int(code_product_sin),
            'codeProduct': product.default_code,
            'description': line.name or product.display_name,
            'qty': line.quantity,
            'priceUnit': line.price_unit,
        }

    # ========== PREPARAR PAYLOAD ==========
    def _prepare_cucu_rent_invoice_data(self):
        """Prepara el payload JSON según especificaciones CUCU API para alquileres"""
        self.ensure_one()
        company = self.company_id

        if not company.cucu_rent_username:
            raise UserError(
                'Configure las credenciales CUCU para sector alquileres en:\n'
                'Configuración > Compañías > Facturación Alquileres'
            )

        if not self.rent_billed_period:
            raise UserError(
                'El campo "Período Facturado" es obligatorio para facturas de alquileres.'
            )

        lines_with_product = self.invoice_line_ids.filtered(lambda l: l.product_id)
        if not lines_with_product:
            raise UserError(
                'La factura debe tener al menos una línea con producto/servicio configurado.'
            )

        # ── Ciudad desde la sucursal CUCU (igual que cucu_fact_core usa branch_id.municipality)
        branch = company.cucu_rent_branch_id
        if not branch:
            raise UserError(
                'No hay Sucursal Alquileres configurada en la compañía.\n\n'
                'Configúrala en: Configuración > Compañías > pestaña "Facturación Alquileres" '
                '> campo "Sucursal Alquileres".'
            )
        client_city = branch.municipality or branch.city
        if not client_city:
            raise UserError(
                f'La sucursal "{branch.name}" no tiene Municipality ni City configurados.\n\n'
                f'Configúrala en: CUCU > Sucursales > "{branch.name}".'
            )

        # ── Cliente ───────────────────────────────────────────────────────────
        partner = self.partner_id

        if not partner.vat:
            raise UserError(
                f'El cliente "{partner.name}" no tiene NIT/CI configurado.\n\n'
                f'Configúralo en: Contacto > "NIT".'
            )

        client_email = (
            getattr(partner, 'cucu_email', None)
            or partner.email
        )
        if not client_email:
            raise UserError(
                f'El cliente "{partner.name}" no tiene email configurado.\n\n'
                f'Configúralo en: Contacto > "Email CUCU" o "Email".'
            )

        # ── Detalle de líneas (con validación por producto) ───────────────────
        detail_invoice = []
        for line in lines_with_product:
            detail_invoice.append(self._prepare_cucu_rent_detail_line(line))

        payload = {
            'posId': 1,
            'clientReasonSocial': partner.name,
            'clientDocumentType': getattr(partner.doc_id, 'code_type', '1') or '1',
            'clientNroDocument': partner.vat,
            'clientCode': partner.ref or f'CLI-{partner.id}',
            'paramPaymentMethod': '1',
            'dateEmission': (
                self.invoice_date.strftime('%Y-%m-%dT%H:%M:%S')
                if self.invoice_date
                else fields.Datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            ),
            'userPos': 'A4INC12ABCH',
            'paramDocumentSector': '1',
            'paramCurrency': '1',
            'clientComplement': partner.complement if getattr(partner, 'complement', None) else '',
            'clientCity': client_city,
            'clientEmail': client_email,
            'typeInvoice': 1,
            'typeOperation': int(self.rent_type_operation) if self.rent_type_operation else 2,
            'billedPeriod': self.rent_billed_period,
            'detailInvoice': detail_invoice,
        }

        return payload

    # ========== ACCIÓN: ENVIAR A CUCU ==========
    def action_send_rent_invoice_cucu(self):
        """Acción de botón: Enviar factura de alquileres a CUCU API"""
        self.ensure_one()

        if not self.is_rent_invoice:
            raise UserError('Esta factura no está marcada como factura de alquileres.')

        if self.state != 'posted':
            raise UserError('Solo se pueden enviar facturas confirmadas (estado: Publicado).')

        if self.cucu_rent_cuf:
            raise UserError(
                f'Esta factura ya fue enviada a CUCU.\n'
                f'CUF: {self.cucu_rent_cuf}\n\n'
                f'Para reenviar, primero debe anularla.'
            )

        api_service = self.env['cucu.rent.api']

        try:
            _logger.info(f'=== Iniciando envío de factura {self.name} a CUCU (Alquileres) ===')

            result = api_service.send_rent_invoice(self)

            self.write({
                'cucu_rent_cuf': result.get('cuf'),
                'cucu_rent_response': json.dumps(result, indent=2, ensure_ascii=False),
                'cucu_rent_state': 'validated' if result.get('cuf') else 'rejected',
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
                'cucu_rent_state': 'rejected',
            })

            raise UserError(f'❌ Error al enviar factura a CUCU:\n\n{error_msg}')
