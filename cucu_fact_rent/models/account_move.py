# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)

# Campos que el template base accede con header['clave'] (sin .get())
# La API CUCU rent puede no devolverlos todos, por eso se definen defaults
_HEADER_DEFAULTS = {
    'nitEmisor': '',
    'razonSocialEmisor': '',
    'branch_name': '',
    'codigoPuntoVenta': '',
    'direccion': '',
    'telefono': '',
    'municipio': '',
    'numeroFactura': '',
    'cuf': '',
    'fechaEmision': '',
    'nombreRazonSocial': '',
    'numeroDocumento': '',
    'codigoCliente': '',
    'montoTotal': '0.00',
    'montoTotalMoneda': '0.00',
    'montoTotalSujetoIva': '0.00',
    'descuentoAdicional': '0.00',
    'montoGiftCard': '0.00',
    'montoLiteral': '',
    'leyenda': '',
    'observations': '',
    'qr': '',
    'qr_code': '',
    'invoice_url': '',
    'payment_key': 'no',
    'periodoFacturado': '',
    'dirInmueble': '',
    'doc_sector': 1,
}


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_rent_invoice = fields.Boolean(
        string='Factura Alquileres',
        help='Marcar si esta factura pertenece al sector alquileres'
    )

    rent_billed_period = fields.Char(
        string='Período Facturado',
        help='Período de alquiler. Ejemplo: "mayo 2026"'
    )
    rent_property_address = fields.Text(string='Dirección Inmueble')
    rent_type_operation = fields.Selection([
        ('1', 'Alquiler'),
        ('2', 'Venta'),
    ], string='Tipo Operación', default='2')

    cucu_rent_cuf = fields.Char(string='CUF Alquileres', readonly=True, copy=False)
    cucu_rent_invoice_code = fields.Char(string='Invoice Code Alquileres', copy=False)
    cucu_rent_invoice_number = fields.Char(string='Número Factura Alquileres', copy=False)
    cucu_rent_response = fields.Text(string='Respuesta API Alquileres', readonly=True, copy=False)
    cucu_rent_state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviada a CUCU'),
        ('validated', 'Validada por SIN'),
        ('rejected', 'Rechazada'),
        ('cancelled', 'Anulada'),
    ], string='Estado CUCU Alquileres', default='draft', readonly=True, copy=False)

    def create_invoice_account(self):
        if self.is_rent_invoice:
            return None
        return super().create_invoice_account()

    @api.onchange('is_rent_invoice')
    def _onchange_is_rent_invoice(self):
        if self.is_rent_invoice and not self.rent_billed_period:
            from datetime import datetime
            month_names = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }
            now = datetime.now()
            self.rent_billed_period = f"{month_names[now.month]} {now.year}"

    # ========== OVERRIDE render_invoice() ==========
    def render_invoice(self):
        """
        Override completo para facturas de alquiler.

        El modulo base cucu_fact_report solo procesa doc_sector 1 y 24.
        Las facturas de alquiler tienen doc_sector=2 en el JSON, por lo
        que el base deja header={} y falla. Este override lee el
        invoice_json directamente y construye el header correcto,
        forzando doc_sector=1 para que el template base muestre
        la tabla de detalle (invoice_sale).

        Se aplican _HEADER_DEFAULTS primero para garantizar que todos los
        campos que el template accede con header['clave'] (sin .get())
        existan, incluso si la API CUCU rent no los devuelve.
        """
        if not self.is_rent_invoice:
            return super().render_invoice()

        from odoo.addons.cucu_fact_report.lib.qr_image import generate_qr
        from odoo.addons.cucu_fact_report.lib.string_utils import number_to_date

        if not self.invoice_id:
            return None

        invoice = self.invoice_id[-1]

        try:
            invoice_json = json.loads(invoice.invoice_json or '{}')
        except Exception:
            invoice_json = {}

        cabecera = invoice_json.get('cabecera', {})
        detalle = invoice_json.get('detalle', [])

        # QR
        qr_raw = invoice.qr_code or ''
        try:
            qr_b64 = 'data:image/png;base64,' + generate_qr(qr_raw) if qr_raw else ''
        except Exception:
            qr_b64 = ''

        # Fecha con formato legible
        fecha_raw = cabecera.get('fechaEmision', str(self.invoice_date or ''))
        try:
            fecha = number_to_date(fecha_raw)
        except Exception:
            fecha = str(fecha_raw)

        # numeroDocumento con complemento
        doc_type = int(cabecera.get('codigoTipoDocumentoIdentidad', 5))
        nro_doc = cabecera.get('numeroDocumento', self.partner_id.vat or '')
        complemento = cabecera.get('complemento', '')
        if doc_type == 1 and complemento:
            nro_doc = f'{nro_doc}-{complemento}'

        # Periodo facturado: sincronizar move <-> JSON
        periodo = cabecera.get('periodoFacturado', '') or self.rent_billed_period or ''
        if periodo and not self.rent_billed_period:
            try:
                self.sudo().write({'rent_billed_period': periodo})
            except Exception:
                pass

        # Branch name
        branch_name = ''
        if self.pos_id and self.pos_id.cucu_pos_id and self.pos_id.cucu_pos_id.branch_id:
            branch_name = self.pos_id.cucu_pos_id.branch_id.name

        # Montos: 2 decimales + separador de miles  (ej: 25,000.00)
        def _fmt(val, default='0.00'):
            try:
                return f'{float(val):,.2f}'
            except Exception:
                return default

        header = {
            # 1. Defaults para todos los campos que el template usa sin .get()
            **_HEADER_DEFAULTS,
            # 2. Datos reales del JSON (sobreescriben defaults)
            **cabecera,
            # 3. Campos procesados/calculados (sobreescriben JSON crudo)
            'fechaEmision': fecha,
            'numeroDocumento': nro_doc,
            'codigoPuntoVenta': f'No. Punto de Venta {cabecera.get("codigoPuntoVenta", 0)}',
            'montoTotal': _fmt(cabecera.get('montoTotal', self.amount_total)),
            'montoTotalMoneda': _fmt(cabecera.get('montoTotalMoneda', self.amount_total)),
            'montoTotalSujetoIva': _fmt(cabecera.get('montoTotalSujetoIva', self.amount_total)),
            'descuentoAdicional': _fmt(cabecera.get('descuentoAdicional', 0)),
            'montoGiftCard': _fmt(cabecera.get('montoGiftCard', 0)),
            'montoLiteral': invoice.amount_literal or '',
            'observations': getattr(invoice, 'observations', '') or '',
            'qr': qr_b64,
            'qr_code': qr_raw,
            'invoice_url': invoice.url_cucu or '',
            'payment_key': 'ok' if self.is_sin else 'no',
            'branch_name': branch_name,
            'periodoFacturado': periodo,
            'dirInmueble': self.rent_property_address or '',
            # CRITICO: forzar doc_sector=1 para que el template muestre la tabla
            'doc_sector': 1,
        }

        detail = self._render_invoice_details(detalle)

        return {'header': header, 'detail': detail}

    def _get_cucu_rent_pos_data(self):
        if not self.pos_id:
            raise UserError('La factura no tiene un Punto de Venta (POS) asignado.')
        cucu_pos = self.pos_id.cucu_pos_id
        if not cucu_pos:
            raise UserError(f'El POS "{self.pos_id.name}" no tiene un POS CUCU configurado.')
        branch = cucu_pos.branch_id
        if not branch:
            raise UserError(f'El POS CUCU "{cucu_pos.name}" no tiene Sucursal asignada.')
        city = branch.municipality or branch.city
        if not city:
            raise UserError(f'La sucursal "{branch.name}" no tiene Municipality ni City configurados.')
        return {
            'posId': cucu_pos.pos_id,
            'branchId': branch.branch_id,
            'clientCity': city,
            'userPos': self.invoice_user_id.partner_id.name or self.env.user.partner_id.name,
            'cucu_pos': cucu_pos,
            'branch': branch,
        }

    def _prepare_cucu_rent_detail_line(self, line):
        product = line.product_id
        tmpl = product.product_tmpl_id
        activity_code = tmpl.code_type_activity or getattr(tmpl.code_activity_sin_id, 'code_type', None)
        if not activity_code:
            raise UserError(f'Producto "{product.display_name}": sin Actividad Económica SIN.')
        code_product_sin = tmpl.sin_code_product or product.sin_code_product
        if not code_product_sin:
            raise UserError(f'Producto "{product.display_name}": sin Código Producto SIN.')
        unit_measure = tmpl.unit_measure_id.code_type or product.unit_measure_id.code_type
        if not unit_measure:
            raise UserError(f'Producto "{product.display_name}": sin Unidad de Medida SIN.')
        if not product.default_code:
            raise UserError(f'Producto "{product.display_name}": sin Referencia Interna.')
        return {
            'activityEconomic': activity_code,
            'unitMeasure': unit_measure,
            'codeProductSin': int(code_product_sin),
            'codeProduct': product.default_code,
            'description': line.name or product.display_name,
            'qty': line.quantity,
            'priceUnit': line.price_unit,
        }

    def _prepare_cucu_rent_invoice_data(self):
        self.ensure_one()
        company = self.company_id
        if not company.cucu_rent_username:
            raise UserError('Configure las credenciales CUCU en: Configuración > Compañías > Facturación Alquileres.')
        if not self.rent_billed_period:
            raise UserError('El campo "Período Facturado" es obligatorio.')
        lines_with_product = self.invoice_line_ids.filtered(lambda l: l.product_id)
        if not lines_with_product:
            raise UserError('La factura debe tener al menos una línea con producto.')
        pos_data = self._get_cucu_rent_pos_data()
        partner = self.partner_id
        if not partner.vat:
            raise UserError(f'Cliente "{partner.name}": sin NIT/CI.')
        client_email = getattr(partner, 'cucu_email', None) or partner.email
        if not client_email:
            raise UserError(f'Cliente "{partner.name}": sin email.')
        detail_invoice = [self._prepare_cucu_rent_detail_line(l) for l in lines_with_product]

        payload = {
            'posId': pos_data['posId'],
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
            'userPos': pos_data['userPos'],
            'paramDocumentSector': '1',
            'paramCurrency': '1',
            'clientComplement': getattr(partner, 'complement', None) or '',
            'clientCity': pos_data['clientCity'],
            'clientEmail': client_email,
            'typeInvoice': 1,
            'typeOperation': int(self.rent_type_operation) if self.rent_type_operation else 2,
            # ---- Campos especificos sector alquileres ----
            'billedPeriod': self.rent_billed_period,
            'detailInvoice': detail_invoice,
        }

        # propertyAddress: campo opcional - se incluye solo si tiene valor
        if self.rent_property_address:
            payload['propertyAddress'] = self.rent_property_address.strip()

        return payload

    def _save_cucu_rent_response(self, data, pos_data):
        self.ensure_one()
        company = self.company_id
        cucu_pos = pos_data['cucu_pos']
        branch = pos_data['branch']
        invoice_json_raw = data.get('invoiceJson', '{}')
        try:
            invoice_json_parsed = json.loads(invoice_json_raw)
            json_cabecera = invoice_json_parsed.get('cabecera', {})
        except Exception:
            invoice_json_parsed = {}
            json_cabecera = {}

        doc_sector = int(json_cabecera.get('codigoDocumentoSector', 2))

        host = cucu_pos.manager_id.host if cucu_pos.manager_id else ''
        invoice_url = data.get('invoiceUrl', '')
        cucu_invoice_vals = {
            'account_move_id': self.id,
            'manager_id': cucu_pos.manager_id.id if cucu_pos.manager_id else False,
            'sin_code_state': data.get('siatCodeState', 0),
            'sin_code_reception': data.get('siatCodeReception', '0000'),
            'sin_description_status': data.get('siatDescriptionStatus', ''),
            'url_cucu': f"{host}{invoice_url}" if host and invoice_url else invoice_url,
            'exception_code': json_cabecera.get('codigoExcepcion', 0),
            'qr_code': data.get('qrCode', ''),
            'branch_id': branch.branch_id,
            'pos_id': cucu_pos.pos_id,
            'invoice_code': data.get('invoiceCode', ''),
            'date_emission': data.get('dateEmission', ''),
            'cuf': data.get('cuf', ''),
            'invoice_number': str(data.get('invoiceNumber', '')),
            'nit_emissor': str(data.get('nitEmissor', '')),
            'municipality': json_cabecera.get('municipio', branch.municipality or ''),
            'is_offline': data.get('siatCodeState', 0) == 901,
            'reason_social_emissor': json_cabecera.get('nombreRazonSocial', company.name),
            'invoice_xml': data.get('invoiceXml', ''),
            'invoice_json': invoice_json_raw,
            'amount_literal': data.get('amountLiteral', ''),
            'count_items': data.get('countItems', len(self.invoice_line_ids)),
            'amount_total': json_cabecera.get('montoTotal', self.amount_total),
            'amount_subject_iva': json_cabecera.get('montoTotalSujetoIva', 0),
            'amount_gift_card': json_cabecera.get('montoGiftCard', 0),
            'amount_total_currency': json_cabecera.get('montoTotalMoneda', self.amount_total),
            'additional_discount': json_cabecera.get('descuentoAdicional', 0),
            'doc_sector': doc_sector,
            'company_id': company.id,
        }
        existing = self.env['cucu.invoice'].search([('account_move_id', '=', self.id)], limit=1)
        if existing:
            existing.write(cucu_invoice_vals)
            cucu_invoice = existing
        else:
            cucu_invoice = self.env['cucu.invoice'].create(cucu_invoice_vals)
        self.write({
            'cucu_rent_cuf': data.get('cuf', ''),
            'cucu_rent_invoice_code': data.get('invoiceCode', ''),
            'cucu_rent_invoice_number': str(data.get('invoiceNumber', '')),
            'cucu_rent_response': json.dumps(data, indent=2, ensure_ascii=False),
            'cucu_rent_state': 'validated' if data.get('cuf') else 'rejected',
            'sin_code_state': data.get('siatCodeState', 0),
            'sin_code_reception': data.get('siatCodeReception', '0000'),
            'sin_description_status': data.get('siatDescriptionStatus', ''),
            'invoice_code': data.get('invoiceCode', ''),
            'invoice_number': str(data.get('invoiceNumber', '')),
            'invoice_id': [(4, cucu_invoice.id)],
        })
        return cucu_invoice

    # ========== ACCIÓN: ENVIAR ==========
    def action_send_rent_invoice_cucu(self):
        self.ensure_one()
        if not self.is_rent_invoice:
            raise UserError('Esta factura no está marcada como factura de alquileres.')
        if self.state != 'posted':
            raise UserError('Solo se pueden enviar facturas confirmadas.')
        if self.cucu_rent_cuf:
            raise UserError(f'Esta factura ya fue enviada a CUCU.\nCUF: {self.cucu_rent_cuf}')
        pos_data = self._get_cucu_rent_pos_data()
        try:
            result = self.env['cucu.rent.api'].send_rent_invoice(self)
            cucu_invoice = self._save_cucu_rent_response(result, pos_data)
            _logger.info('Factura %s enviada. CUF: %s | invoice_id: %s',
                         self.name, result.get('cuf'), cucu_invoice.id)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Factura Enviada a CUCU',
                    'message': f'CUF: {result.get("cuf")} | Número: {result.get("invoiceNumber", "")}',
                    'type': 'success',
                    'sticky': True,
                }
            }
        except Exception as e:
            self.write({'cucu_rent_response': f'ERROR: {str(e)}', 'cucu_rent_state': 'rejected'})
            raise UserError(f'❌ Error al enviar factura a CUCU:\n\n{str(e)}')

    # ========== ACCIÓN: RECUPERAR DATOS ==========
    def action_recover_rent_invoice_data(self):
        self.ensure_one()
        if not self.is_rent_invoice:
            raise UserError('Esta factura no está marcada como factura de alquileres.')
        invoice_code = self.cucu_rent_invoice_code or self.invoice_code
        if not invoice_code:
            raise UserError('Falta el Invoice Code (ej: B14C0F32). Intróducelo en "Invoice Code Alquileres" y guarda.')
        invoice_number = self.cucu_rent_invoice_number or self.invoice_number
        if not invoice_number:
            raise UserError('Falta el Número de Factura (ej: 2). Intróducelo en "Número Factura Alquileres" y guarda.')
        pos_data = self._get_cucu_rent_pos_data()
        try:
            result = self.env['cucu.rent.api'].get_rent_invoice_status(
                invoice=self, invoice_code=invoice_code, invoice_number=invoice_number)
            cucu_invoice = self._save_cucu_rent_response(result, pos_data)
            _logger.info('Datos recuperados para %s. cucu.invoice id: %s', self.name, cucu_invoice.id)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Datos Recuperados',
                    'message': 'invoice_json, invoice_xml, QR y URL recuperados correctamente.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.error('Error al recuperar datos de %s: %s', self.name, str(e))
            raise UserError(f'❌ Error al recuperar datos:\n\n{str(e)}')

    # ========== ACCIÓN: ANULAR (abre wizard) ==========
    def action_anulate_rent_invoice_wizard(self):
        self.ensure_one()
        if not self.cucu_rent_cuf:
            raise UserError('Esta factura no tiene CUF — no fue enviada a CUCU.')
        if self.cucu_rent_state == 'cancelled':
            raise UserError('Esta factura ya está anulada.')
        return {
            'type': 'ir.actions.act_window',
            'name': '🚫 Anular Factura Alquiler',
            'res_model': 'cucu.rent.anulation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_invoice_id': self.id, 'default_action': 'anulate'},
        }

    # ========== ACCIÓN: REVERTIR (abre wizard) ==========
    def action_revert_rent_invoice_wizard(self):
        self.ensure_one()
        if not self.cucu_rent_cuf:
            raise UserError('Esta factura no tiene CUF — no fue enviada a CUCU.')
        if self.cucu_rent_state == 'cancelled':
            raise UserError('Esta factura ya está anulada/revertida.')
        return {
            'type': 'ir.actions.act_window',
            'name': '↩️ Revertir Factura Alquiler',
            'res_model': 'cucu.rent.anulation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_invoice_id': self.id, 'default_action': 'revert'},
        }

    # ========== BOTONES DE REPORTE ==========
    def action_report_rent_invoice_a4(self):
        return self.invoice_id._get_url_open('A4')

    def action_report_rent_invoice_ticket(self):
        return self.invoice_id._get_url_open('TICKET')

    def action_report_rent_invoice_sin(self):
        return self.invoice_id._get_url_open('SIN')
