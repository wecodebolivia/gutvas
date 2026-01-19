# -*- coding: utf-8 -*-

from odoo import models, fields, api
import io
import base64

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class SaleBookV2Wizard(models.TransientModel):
    _name = 'sale.book.v2.wizard'
    _description = 'Asistente para Libro de Ventas V2'

    fecha_inicio = fields.Date(
        string='Fecha de Inicio',
        required=True
    )
    fecha_fin = fields.Date(
        string='Fecha de Fin',
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )

    def _get_invoices(self):
        """Obtener facturas de venta en el rango de fechas"""
        domain = [
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('invoice_date', '>=', self.fecha_inicio),
            ('invoice_date', '<=', self.fecha_fin),
            ('state', '=', 'posted'),
            ('company_id', '=', self.company_id.id),
        ]
        return self.env['account.move'].search(domain, order='invoice_date, name')

    def _calcular_montos(self, invoice):
        """Calcular montos según formato de Impuestos Bolivia"""
        importe_total = invoice.amount_total
        importe_ice = getattr(invoice, 'lv_importe_ice', 0.0) or 0.0
        importe_iehd = getattr(invoice, 'lv_importe_iehd', 0.0) or 0.0
        importe_ipj = getattr(invoice, 'lv_importe_ipj', 0.0) or 0.0
        tasas = getattr(invoice, 'lv_tasas', 0.0) or 0.0
        otros_no_iva = getattr(invoice, 'lv_otros_no_iva', 0.0) or 0.0
        exportaciones = getattr(invoice, 'lv_exportaciones_exentas', 0.0) or 0.0
        ventas_tasa_cero = getattr(invoice, 'lv_ventas_tasa_cero', 0.0) or 0.0
        descuentos = getattr(invoice, 'lv_descuentos', 0.0) or 0.0
        gift_card = getattr(invoice, 'lv_importe_gift_card', 0.0) or 0.0
        
        subtotal = (importe_total - importe_ice - importe_iehd - importe_ipj - 
                   tasas - otros_no_iva - exportaciones - ventas_tasa_cero)
        importe_base_df = subtotal - descuentos - gift_card
        debito_fiscal = importe_base_df * 0.13
        
        return {
            'importe_total': importe_total,
            'importe_ice': importe_ice,
            'importe_iehd': importe_iehd,
            'importe_ipj': importe_ipj,
            'tasas': tasas,
            'otros_no_iva': otros_no_iva,
            'exportaciones': exportaciones,
            'ventas_tasa_cero': ventas_tasa_cero,
            'subtotal': subtotal,
            'descuentos': descuentos,
            'gift_card': gift_card,
            'importe_base_df': importe_base_df,
            'debito_fiscal': debito_fiscal,
        }

    def generar_reporte_excel(self):
        """Genera el archivo Excel del Libro de Ventas V2"""
        self.ensure_one()
        
        if not xlsxwriter:
            raise UserError('La librería xlsxwriter no está instalada. Contacte al administrador.')
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Hoja1')
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
        })
        number_format = workbook.add_format({'num_format': '#,##0.00'})
        
        # Encabezados
        headers = [
            'N', 'ESPECIFICACION', 'FECHA DE LA FACTURA', 'N DE LA FACTURA',
            'CODIGO DE AUTORIZACION', 'NIT CI CLIENTE', 'COMPLEMENTO',
            'NOMBRE O RAZON SOCIAL', 'IMPORTE TOTAL DE LA VENTA', 'IMPORTE ICE',
            'IMPORTE IEHD', 'IMPORTE IPJ', 'TASAS', 'OTROS NO SUJETOS AL IVA',
            'EXPORTACIONES Y OPERACIONES EXENTAS', 'VENTAS GRAVADAS A TASA CERO',
            'SUBTOTAL', 'DESCUENTOS, BONIFICACIONES Y REBAJAS SUJETAS AL IVA',
            'IMPORTE GIFT CARD', 'IMPORTE BASE PARA DEBITO FISCAL', 'DEBITO FISCAL',
            'ESTADO', 'CODIGO DE CONTROL', 'TIPO DE VENTA',
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        invoices = self._get_invoices()
        
        row = 1
        for idx, invoice in enumerate(invoices, start=1):
            montos = self._calcular_montos(invoice)
            partner = invoice.partner_id
            
            worksheet.write(row, 0, idx)
            worksheet.write(row, 1, '2')
            worksheet.write(row, 2, invoice.invoice_date.strftime('%d/%m/%Y') if invoice.invoice_date else '')
            worksheet.write(row, 3, invoice.name or '')
            worksheet.write(row, 4, getattr(invoice, 'lv_codigo_autorizacion', '0') or '0')
            worksheet.write(row, 5, partner.vat or '0')
            worksheet.write(row, 6, getattr(partner, 'l10n_bo_id_extension', '') or '')
            worksheet.write(row, 7, partner.name or 'Sin Nombre')
            worksheet.write(row, 8, montos['importe_total'], number_format)
            worksheet.write(row, 9, montos['importe_ice'], number_format)
            worksheet.write(row, 10, montos['importe_iehd'], number_format)
            worksheet.write(row, 11, montos['importe_ipj'], number_format)
            worksheet.write(row, 12, montos['tasas'], number_format)
            worksheet.write(row, 13, montos['otros_no_iva'], number_format)
            worksheet.write(row, 14, montos['exportaciones'], number_format)
            worksheet.write(row, 15, montos['ventas_tasa_cero'], number_format)
            worksheet.write(row, 16, montos['subtotal'], number_format)
            worksheet.write(row, 17, montos['descuentos'], number_format)
            worksheet.write(row, 18, montos['gift_card'], number_format)
            worksheet.write(row, 19, montos['importe_base_df'], number_format)
            worksheet.write(row, 20, montos['debito_fiscal'], number_format)
            worksheet.write(row, 21, getattr(invoice, 'lv_estado', 'V') or 'V')
            worksheet.write(row, 22, getattr(invoice, 'lv_codigo_control', '0') or '0')
            worksheet.write(row, 23, getattr(invoice, 'lv_tipo_venta', '0') or '0')
            row += 1
        
        # Ajustar columnas
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 18)
        worksheet.set_column('D:D', 18)
        worksheet.set_column('E:E', 25)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 12)
        worksheet.set_column('H:H', 35)
        worksheet.set_column('I:X', 18)
        
        workbook.close()
        output.seek(0)
        
        nombre_archivo = "Libro_Ventas_V2_{0}_{1}.xlsx".format(
            self.fecha_inicio.strftime('%Y%m%d'),
            self.fecha_fin.strftime('%Y%m%d')
        )
        
        attachment = self.env['ir.attachment'].create({
            'name': nombre_archivo,
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{0}?download=true'.format(attachment.id),
            'target': 'self',
        }
