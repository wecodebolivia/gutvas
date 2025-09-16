# l10n_bo_purchase_book_line/models/report_libro_compras.py
from odoo import models, fields
import io
import base64
import xlsxwriter

class ReportLibroCompras(models.TransientModel):
    _name = 'report.libro.compras'
    _description = 'Reporte de Libro de Compras'

    fecha_inicio = fields.Date(string='Fecha de Inicio', required=True)
    fecha_fin = fields.Date(string='Fecha de Fin', required=True)

    def exportar_excel(self):
        self.ensure_one()
        domain = []
        if self.fecha_inicio:
            domain.append(('lc_fecha_factura', '>=', self.fecha_inicio))
        if self.fecha_fin:
            domain.append(('lc_fecha_factura', '<=', self.fecha_fin))

        lines = self.env['account.move.line'].search(domain, order='lc_fecha_factura asc, id asc')

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = workbook.add_worksheet('Libro de Compras')

        # Formats
        fmt_header = workbook.add_format({'bold': True, 'border': 1, 'align': 'center'})
        fmt_text = workbook.add_format({'border': 1})
        fmt_date = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
        fmt_num = workbook.add_format({'num_format': '#,##0.00', 'border': 1})

        headers = [
            'Nº','ESPECIFICACIÓN','NIT PROVEEDOR','RAZÓN SOCIAL PROVEEDOR',
            'CÓDIGO AUTORIZACIÓN','NÚM. FACTURA','NÚM. DUI/DIM','FECHA FACTURA',
            'IMPORTE TOTAL COMPRA','ICE','IEHD','IPJ','TASAS','NO SUJETO CF',
            'EXENTOS','GRAVADA 0%','DESCUENTOS','GIFT CARD','BASE CF','CRÉDITO FISCAL',
            'TIPO COMPRA','CÓDIGO CONTROL',
        ]

        for col, h in enumerate(headers):
            ws.write(0, col, h, fmt_header)

        row = 1
        for idx, l in enumerate(lines, start=1):
            ws.write(row, 0, idx, fmt_text)
            ws.write(row, 1, '1', fmt_text)
            ws.write(row, 2, l.partner_id.lc_nit or '', fmt_text)
            ws.write(row, 3, l.partner_id.lc_razon_social or l.partner_id.name or '', fmt_text)
            ws.write(row, 4, l.lc_codigo_autorizacion or '', fmt_text)
            ws.write(row, 5, l.lc_numero_factura or '', fmt_text)
            ws.write(row, 6, l.lc_numero_dui_dim or '', fmt_text)
            if l.lc_fecha_factura:
                ws.write_datetime(row, 7, fields.Date.to_datetime(l.lc_fecha_factura), fmt_date)
            else:
                ws.write(row, 7, '', fmt_text)

            ws.write_number(row, 8, l.lc_importe_total_compra or 0.0, fmt_num)
            ws.write_number(row, 9, l.lc_importe_ice or 0.0, fmt_num)
            ws.write_number(row,10, l.lc_importe_iehd or 0.0, fmt_num)
            ws.write_number(row,11, l.lc_importe_ipj or 0.0, fmt_num)
            ws.write_number(row,12, l.lc_tasas or 0.0, fmt_num)
            ws.write_number(row,13, l.lc_otros_no_sujeto_cf or 0.0, fmt_num)
            ws.write_number(row,14, l.lc_importes_exentos or 0.0, fmt_num)
            ws.write_number(row,15, l.lc_compras_gravadas_tasa_cero or 0.0, fmt_num)
            ws.write_number(row,16, l.lc_descuentos_bonificaciones or 0.0, fmt_num)
            ws.write_number(row,17, l.lc_importe_gift_card or 0.0, fmt_num)
            ws.write_number(row,18, l.lc_importe_base_cf or 0.0, fmt_num)
            ws.write_number(row,19, l.lc_credito_fiscal or 0.0, fmt_num)
            ws.write(row,20, l.lc_tipo_compra or '', fmt_text)
            ws.write(row,21, l.lc_codigo_control or '', fmt_text)
            row += 1

        ws.autofilter(0, 0, max(row-1,0), len(headers)-1)
        ws.freeze_panes(1, 0)
        for c in range(len(headers)):
            ws.set_column(c, c, 18)

        workbook.close()
        output.seek(0)
        fname = f"libro_compras_{self.fecha_inicio or ''}_{self.fecha_fin or ''}.xlsx"

        attachment = self.env['ir.attachment'].create({
            'name': fname,
            'datas': base64.b64encode(output.read()),
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
