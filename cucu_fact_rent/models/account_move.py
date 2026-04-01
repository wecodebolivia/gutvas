# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ========== IDENTIFICACIÓN SECTOR ALQUILERES ==========
    is_rent_invoice = fields.Boolean(
        string='Factura Alquileres',
        help='Marcar si esta factura pertenece al sector alquileres'
    )

    # ========== CAMPOS ESPECÍFICOS SECTOR ALQUILERES ==========
    rent_billed_period = fields.Char(
        string='Período Facturado',
        help='Período de alquiler. Ejemplo: "mayo 2026"'
    )
    rent_property_address = fields.Text(
        string='Dirección Inmueble',
    )
    rent_type_operation = fields.Selection([
        ('1', 'Alquiler'),
        ('2', 'Venta'),
    ], string='Tipo Operación', default='2')

    # ========== RESPUESTA CUCU ALQUILERES ==========
    cucu_rent_cuf = fields.Char(string='CUF Alquileres', readonly=True, copy=False)
    cucu_rent_invoice_code = fields.Char(string='Invoice Code Alquileres', readonly=True, copy=False)
    cucu_rent_response = fields.Text(string='Respuesta API Alquileres', readonly=True, copy=False)
    cucu_rent_state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviada a CUCU'),
        ('validated', 'Validada por SIN'),
        ('rejected', 'Rechazada'),
        ('cancelled', 'Anulada'),
    ], string='Estado CUCU Alquileres', default='draft', readonly=True, copy=False)

    # ========== INTERCEPCIÓN PIPELINE cucu_fact_core ==========
    def create_invoice_account(self):
        if self.is_rent_invoice:
            return None
        return super().create_invoice_account()

    # ========== ONCHANGE ==========
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

    # ========== RESOLVER POS / SUCURSAL ==========
    def _get_cucu_rent_pos_data(self):
        """
        Resuelve posId, clientCity y userPos desde:
            invoice.pos_id -> cucu_pos_id -> branch_id -> municipality
        Análogo a cucu_fact_core._get_header()
        """
        if not self.pos_id:
            raise UserError(
                'La factura no tiene un Punto de Venta (POS) asignado.\n\n'
                'Asignálo en: Factura > campo "Point Of Sale".'
            )
        cucu_pos = self.pos_id.cucu_pos_id
        if not cucu_pos:
            raise UserError(
                f'El Punto de Venta "{self.pos_id.name}" no tiene un POS CUCU configurado.\n\n'
                f'Configúralo en: CUCU > Puntos de Venta.'
            )
        branch = cucu_pos.branch_id
        if not branch:
            raise UserError(
                f'El POS CUCU "{cucu_pos.name}" no tiene Sucursal asignada.\n\n'
                f'Configúrala en: CUCU > Puntos de Venta > "{cucu_pos.name}".'
            )
        city = branch.municipality or branch.city
        if not city:
            raise UserError(
                f'La sucursal "{branch.name}" no tiene Municipality ni City configurados.\n\n'
                f'Configúrala en: CUCU > Sucursales > "{branch.name}".'
            )
        return {
            'posId': cucu_pos.pos_id,
            'branchId': branch.branch_id,
            'clientCity': city,
            'userPos': self.invoice_user_id.partner_id.name or self.env.user.partner_id.name,
            'cucu_pos': cucu_pos,
            'branch': branch,
        }

    # ========== DETALLE DE LÍNEAS ==========
    def _prepare_cucu_rent_detail_line(self, line):
        product = line.product_id
        tmpl = product.product_tmpl_id

        activity_code = (
            tmpl.code_type_activity
            or getattr(tmpl.code_activity_sin_id, 'code_type', None)
        )
        if not activity_code:
            raise UserError(
                f'Producto "{product.display_name}": sin Actividad Económica SIN.\n'
                f'Configúralo en: Producto > SIN > "Actividad Económica".'
            )

        code_product_sin = tmpl.sin_code_product or product.sin_code_product
        if not code_product_sin:
            raise UserError(
                f'Producto "{product.display_name}": sin Código Producto SIN.\n'
                f'Configúralo en: Producto > SIN > "Código Producto SIN".'
            )

        unit_measure = (
            tmpl.unit_measure_id.code_type
            or product.unit_measure_id.code_type
        )
        if not unit_measure:
            raise UserError(
                f'Producto "{product.display_name}": sin Unidad de Medida SIN.\n'
                f'Configúralo en: Producto > SIN > "Unidad de Medida".'
            )

        if not product.default_code:
            raise UserError(
                f'Producto "{product.display_name}": sin Referencia Interna.\n'
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
        self.ensure_one()
        company = self.company_id

        if not company.cucu_rent_username:
            raise UserError(
                'Configure las credenciales CUCU para sector alquileres en:\n'
                'Configuración > Compañías > pestaña "Facturación Alquileres".'
            )
        if not self.rent_billed_period:
            raise UserError('El campo "Período Facturado" es obligatorio.')

        lines_with_product = self.invoice_line_ids.filtered(lambda l: l.product_id)
        if not lines_with_product:
            raise UserError('La factura debe tener al menos una línea con producto.')

        pos_data = self._get_cucu_rent_pos_data()

        partner = self.partner_id
        if not partner.vat:
            raise UserError(
                f'Cliente "{partner.name}": sin NIT/CI.\n'
                f'Configúralo en: Contacto > "NIT".'
            )
        client_email = getattr(partner, 'cucu_email', None) or partner.email
        if not client_email:
            raise UserError(
                f'Cliente "{partner.name}": sin email.\n'
                f'Configúralo en: Contacto > "Email CUCU" o "Email".'
            )

        detail_invoice = [
            self._prepare_cucu_rent_detail_line(line)
            for line in lines_with_product
        ]

        return {
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
            'billedPeriod': self.rent_billed_period,
            'detailInvoice': detail_invoice,
        }

    # ========== GUARDAR RESPUESTA ==========
    def _save_cucu_rent_response(self, data, pos_data):
        """
        Replica cucu_invoice.create_invoice():
        - Crea registro cucu.invoice con invoice_xml, invoice_json, qr_code, url_cucu, etc.
        - Vincula al account.move via invoice_id (4, id)
        - Actualiza campos SIN en account.move
        """
        self.ensure_one()
        company = self.company_id
        cucu_pos = pos_data['cucu_pos']
        branch = pos_data['branch']

        invoice_json_raw = data.get('invoiceJson', '{}')
        try:
            json_cabecera = json.loads(invoice_json_raw).get('cabecera', {})
        except Exception:
            json_cabecera = {}

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
            'doc_sector': 1,
            'company_id': company.id,
        }

        # Buscar si ya existe un cucu.invoice para este account.move
        existing = self.env['cucu.invoice'].search([
            ('account_move_id', '=', self.id)
        ], limit=1)

        if existing:
            existing.write(cucu_invoice_vals)
            cucu_invoice = existing
        else:
            cucu_invoice = self.env['cucu.invoice'].create(cucu_invoice_vals)

        # Vincular via invoice_id (igual que cucu_fact_core create_invoice_sale)
        self.write({
            'cucu_rent_cuf': data.get('cuf', ''),
            'cucu_rent_invoice_code': data.get('invoiceCode', ''),
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

    # ========== ACCIÓN: ENVIAR A CUCU ==========
    def action_send_rent_invoice_cucu(self):
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

        pos_data = self._get_cucu_rent_pos_data()
        api_service = self.env['cucu.rent.api']

        try:
            _logger.info('=== Enviando factura %s a CUCU (Alquileres) ===', self.name)
            result = api_service.send_rent_invoice(self)
            cucu_invoice = self._save_cucu_rent_response(result, pos_data)
            _logger.info('Factura %s enviada. CUF: %s | invoice_id: %s',
                         self.name, result.get('cuf'), cucu_invoice.id)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '\u2705 Factura Enviada a CUCU',
                    'message': f'CUF: {result.get("cuf")} | N\u00famero: {result.get("invoiceNumber", "")}',
                    'type': 'success',
                    'sticky': True,
                }
            }
        except Exception as e:
            error_msg = str(e)
            _logger.error('Error al enviar factura %s: %s', self.name, error_msg)
            self.write({
                'cucu_rent_response': f'ERROR: {error_msg}',
                'cucu_rent_state': 'rejected',
            })
            raise UserError(f'\u274c Error al enviar factura a CUCU:\n\n{error_msg}')

    # ========== ACCIÓN: RECUPERAR DATOS POST-EMISIÓN ==========
    def action_recover_rent_invoice_data(self):
        """
        Recupera invoice_json, invoice_xml, qr_code, url_cucu, invoice_number, etc.
        llamando al endpoint GET /api/v1/invoice/electronic/rent/status.

        Usar cuando la factura fue emitida pero los datos no se guardaron
        (solo existe el CUF). Requiere cucu_rent_invoice_code o se pide manual.
        """
        self.ensure_one()

        if not self.is_rent_invoice:
            raise UserError('Esta factura no está marcada como factura de alquileres.')

        invoice_code = self.cucu_rent_invoice_code or self.invoice_code
        if not invoice_code:
            raise UserError(
                'No se encontró el Invoice Code (código interno CUCU).\n\n'
                'Pídele al desarrollador de CUCU el invoiceCode de esta factura '
                '(ej: B14C0F32) e intróducelo en el campo "Invoice Code Alquileres".'
            )

        pos_data = self._get_cucu_rent_pos_data()
        api_service = self.env['cucu.rent.api']

        try:
            _logger.info('=== Recuperando datos de factura %s (invoiceCode: %s) ===',
                         self.name, invoice_code)

            result = api_service.get_rent_invoice_status(
                invoice=self,
                invoice_code=invoice_code,
            )

            cucu_invoice = self._save_cucu_rent_response(result, pos_data)

            _logger.info('Datos recuperados para factura %s. cucu.invoice id: %s',
                         self.name, cucu_invoice.id)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '\u2705 Datos Recuperados',
                    'message': 'invoice_json, invoice_xml, QR y URL recuperados correctamente.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            error_msg = str(e)
            _logger.error('Error al recuperar datos de factura %s: %s', self.name, error_msg)
            raise UserError(f'\u274c Error al recuperar datos:\n\n{error_msg}')

    # ========== BOTONES DE REPORTE (análogo a cucu_fact_core) ==========
    def action_report_rent_invoice_a4(self):
        return self.invoice_id._get_url_open('A4')

    def action_report_rent_invoice_ticket(self):
        return self.invoice_id._get_url_open('TICKET')

    def action_report_rent_invoice_sin(self):
        return self.invoice_id._get_url_open('SIN')
