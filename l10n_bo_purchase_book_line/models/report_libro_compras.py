# l10n_bo_purchase_book_line/models/report_libro_compras.py
from odoo import models, fields
import io
import base64
import xlsxwriter

class ReportLibroCompras(models.TransientModel):
    _name = 'report.libro.compras'
    _description = 'Reporte XLSX: Libro de Compras'

    fecha_inicio = fields.Date(string='Fecha de Inicio', required=True)
    fecha_fin = fields.Date(string='Fecha de Fin', required=True)

    def exportar_excel(self):
        self.ensure_one()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = workbook.add_worksheet('Libro de Compras')

        header = [
            'Fecha', 'Proveedor (Razón Social)', 'NIT', 'N° Factura', 'Cod. Autorización',
            'DUI/DIM', 'Importe Total', 'ICE', 'IEHD', 'IPJ', 'Tasas', 'Otros No Sujetos', 'Exentos',
            'Tasa Cero', 'Desc./Bonif.', 'Gift Card', 'Base CF', 'Crédito Fiscal', 'Tipo Compra', 'Código Control'
        ]
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})

        for col, name in enumerate(header):
            ws.write(0, col, name, bold)

        domain = [
            ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'in_receipt')),
            ('move_id.state', '=', 'posted'),
            ('move_id.invoice_date', '>=', self.fecha_inicio),
            ('move_id.invoice_date', '<=', self.fecha_fin),
        ]
        lines = self.env['account.move.line'].search(domain, order='move_id.invoice_date, id')

        row = 1
        for line in lines:
            partner = line.partner_id
            ws.write(row, 0, line.move_id.invoice_date and line.move_id.invoice_date.strftime('%Y-%m-%d') or '')
            ws.write(row, 1, partner.lc_razon_social or partner.name or '')
            ws.write(row, 2, partner.lc_nit or partner.vat or '')
            ws.write(row, 3, line.lc_numero_factura or '')
            ws.write(row, 4, line.lc_codigo_autorizacion or '')
            ws.write(row, 5, line.lc_numero_dui_dim or '')

            def w_money(c, value):
                ws.write_number(row, c, float(value or 0.0), money)

            w_money(6, line.lc_importe_total_compra)
            w_money(7, line.lc_importe_ice)
            w_money(8, line.lc_importe_iehd)
            w_money(9, line.lc_importe_ipj)
            w_money(10, line.lc_tasas)
            w_money(11, line.lc_otros_no_sujeto_cf)
            w_money(12, line.lc_importes_exentos)
            w_money(13, line.lc_compras_gravadas_tasa_cero)
            w_money(14, line.lc_descuentos_bonificaciones)
            w_money(15, line.lc_importe_gift_card)
            w_money(16, line.lc_importe_base_cf)
            w_money(17, line.lc_credito_fiscal)

            tipo_map = dict(line._fields['lc_tipo_compra'].selection)
            ws.write(row, 18, tipo_map.get(line.lc_tipo_compra or 'cf', 'Con derecho a Crédito Fiscal'))
            ws.write(row, 19, line.lc_codigo_control or '')
            row += 1

        workbook.close()
        output.seek(0)

        nombre_archivo = f'libro_compras_{self.fecha_inicio}_{self.fecha_fin}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': nombre_archivo,
            'datas': base64.b64encode(output.read()).decode('ascii'),
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
