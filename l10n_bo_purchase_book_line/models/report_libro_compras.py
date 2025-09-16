# l10n_bo_purchase_book_line/models/report_libro_compras.py
from odoo import models, fields, api, _
import io
import base64
import xlsxwriter

class ReportLibroCompras(models.TransientModel):
    _name = 'report.libro.compras'
    _description = 'Reporte de Libro de Compras'

    fecha_inicio = fields.Date(string='Fecha de Inicio', required=True)
    fecha_fin = fields.Date(string='Fecha de Fin', required=True)

    def generar_reporte(self):
        self.ensure_one()
        # Buscar por lc_fecha_factura si está, si no, por move.date
        domain = [
            '|', ('lc_fecha_factura', '>=', self.fecha_inicio), '&', ('lc_fecha_factura', '=', False), ('date', '>=', self.fecha_inicio),
            '|', ('lc_fecha_factura', '<=', self.fecha_fin),   '&', ('lc_fecha_factura', '=', False), ('date', '<=', self.fecha_fin),
        ]
        lines = self.env['account.move.line'].search(domain, limit=50000)  # límite defensivo

        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = wb.add_worksheet(_('Libro de Compras'))

        header = wb.add_format({'bold': True})
        num = wb.add_format({'num_format': '#,##0.00'})

        cols = [
            ('Fecha', 12),
            ('Proveedor', 30),
            ('NIT', 18),
            ('Nro Factura', 15),
            ('Autorización', 18),
            ('Subtotal', 14),
            ('Base CF', 14),
            ('Crédito Fiscal', 14),
        ]
        for idx, (title, width) in enumerate(cols):
            ws.write(0, idx, title, header)
            ws.set_column(idx, idx, width)

        row = 1
        for l in lines:
            date_val = l.lc_fecha_factura or l.move_id.date
            ws.write(row, 0, date_val and date_val.strftime('%Y-%m-%d'))
            ws.write(row, 1, l.partner_id.display_name or '')
            ws.write(row, 2, l.partner_id.lc_nit or '')
            ws.write(row, 3, l.lc_numero_factura or '')
            ws.write(row, 4, l.lc_codigo_autorizacion or '')
            ws.write_number(row, 5, l.lc_subtotal or 0.0, num)
            ws.write_number(row, 6, l.lc_importe_base_cf or 0.0, num)
            ws.write_number(row, 7, l.lc_credito_fiscal or 0.0, num)
            row += 1

        wb.close()
        output.seek(0)
        nombre_archivo = f"libro_compras_{self.fecha_inicio}_{self.fecha_fin}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': nombre_archivo,
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
