# l10n_bo_purchase_book_line/models/report_libro_compras.py

from odoo import models, fields, api
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
        # Filtrar las líneas del libro de compras dentro del rango de fechas
        lineas = self.env['account.move.line'].search([
            ('lc_fecha_factura', '>=', self.fecha_inicio),
            ('lc_fecha_factura', '<=', self.fecha_fin),
        ])

        datos_reporte = []
        for linea in lineas:
            datos_reporte.append({
                'Nº': len(datos_reporte) + 1,
                'ESPECIFICACION': '1',
                'NIT PROVEEDOR': linea.partner_id.lc_nit or '',
                'RAZON SOCIAL PROVEEDOR': linea.partner_id.lc_razon_social or '',
                'CODIGO DE AUTORIZACION': linea.lc_codigo_autorizacion or '',
                'NUMERO FACTURA': linea.lc_numero_factura or '',
                'NUMERO DUI/DIM': linea.lc_numero_dui_dim or '',
                'FECHA DE FACTURA/DUI/DIM': linea.lc_fecha_factura.strftime('%d/%m/%Y') if linea.lc_fecha_factura else '',
                'IMPORTE TOTAL COMPRA': linea.lc_importe_total_compra or 0.0,
                'IMPORTE ICE': linea.lc_importe_ice or 0.0,
                'IMPORTE IEHD': linea.lc_importe_iehd or 0.0,
                'IMPORTE IPJ': linea.lc_importe_ipj or 0.0,
                'TASAS': linea.lc_tasas or 0.0,
                'OTRO NO SUJETO A CREDITO FISCAL': linea.lc_otros_no_sujeto_cf or 0.0,
                'IMPORTES EXENTOS': linea.lc_importes_exentos or 0.0,
                'IMPORTE COMPRAS GRAVADAS A TASA CERO': linea.lc_compras_gravadas_tasa_cero or 0.0,
                'SUBTOTAL': linea.lc_subtotal or 0.0,
                'DESCUENTOS/BONIFICACIONES/REBAJAS SUJETAS AL IVA': linea.lc_descuentos_bonificaciones or 0.0,
                'IMPORTE GIFT CARD': linea.lc_importe_gift_card or 0.0,
                'IMPORTE BASE CF': linea.lc_importe_base_cf or 0.0,
                'CREDITO FISCAL': linea.lc_credito_fiscal or 0.0,
                'TIPO COMPRA': linea.lc_tipo_compra or '',
                'CODIGO DE CONTROL': linea.lc_codigo_control or '',
            })

        return datos_reporte

    def exportar_excel(self):
        self.ensure_one()
        datos_reporte = self.generar_reporte()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Libro de Compras')

        headers = [
            'Nº', 'ESPECIFICACION', 'NIT PROVEEDOR', 'RAZON SOCIAL PROVEEDOR', 'CODIGO DE AUTORIZACION',
            'NUMERO FACTURA', 'NUMERO DUI/DIM', 'FECHA DE FACTURA/DUI/DIM', 'IMPORTE TOTAL COMPRA',
            'IMPORTE ICE', 'IMPORTE IEHD', 'IMPORTE IPJ', 'TASAS', 'OTRO NO SUJETO A CREDITO FISCAL',
            'IMPORTES EXENTOS', 'IMPORTE COMPRAS GRAVADAS A TASA CERO', 'SUBTOTAL',
            'DESCUENTOS/BONIFICACIONES/REBAJAS SUJETAS AL IVA', 'IMPORTE GIFT CARD', 'IMPORTE BASE CF',
            'CREDITO FISCAL', 'TIPO COMPRA', 'CODIGO DE CONTROL'
        ]

        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        for row, data in enumerate(datos_reporte, start=1):
            for col, key in enumerate(headers):
                worksheet.write(row, col, data.get(key, ''))

        workbook.close()
        output.seek(0)

        nombre_archivo = f"Libro_de_Compras_{self.fecha_inicio.strftime('%Y%m%d')}_{self.fecha_fin.strftime('%Y%m%d')}.xlsx"

        attachment = self.env['ir.attachment'].create({
            'name': nombre_archivo,
            'datas': base64.b64encode(output.read()),
            'res_model': 'report.libro.compras',
            'res_id': self.id,
            'type': 'binary',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
