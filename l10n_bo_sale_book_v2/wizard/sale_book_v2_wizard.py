# -*- coding: utf-8 -*-
from odoo import models, fields, api
import io
import base64
import xlsxwriter

class SaleBookV2Wizard(models.TransientModel):
    _name = 'sale.book.v2.wizard'
    _description = 'Asistente para Libro de Ventas V2'

    fecha_inicio = fields.Date(string='Fecha de Inicio', required=True)
    fecha_fin = fields.Date(string='Fecha de Fin', required=True)
    company_id = fields.Many2one('res.company', string='Compañía', 
                                  default=lambda self: self.env.company, required=True)

    def _get_invoices(self):
        """Obtener facturas de venta en el rango de fechas"""
        return self.env['account.move'].search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('invoice_date', '>=', self.fecha_inicio),
            ('invoice_date', '<=', self.fecha_fin),
            ('state', '=', 'posted'),
            ('company_id', '=', self.company_id.id),
        ], order='invoice_date, name')

    def _calcular_montos(self, invoice):
        """Calcular montos según formato de Impuestos Bolivia"""
        # Importe total de la venta
        importe_total = invoice.amount_total
        
        # Obtener valores de campos específicos
        importe_ice = invoice.lv_importe_ice or 0.0
        importe_iehd = invoice.lv_importe_iehd or 0.0
        importe_ipj = invoice.lv_importe_ipj or 0.0
        tasas = invoice.lv_tasas or 0.0
        otros_no_iva = invoice.lv_otros_no_iva or 0.0
        exportaciones = invoice.lv_exportaciones_exentas or 0.0
        ventas_tasa_cero = invoice.lv_ventas_tasa_cero or 0.0
        
        # Calcular SUBTOTAL
        subtotal = (importe_total - importe_ice - importe_iehd - importe_ipj - 
                   tasas - otros_no_iva - exportaciones - ventas_tasa_cero)
        
        # Descuentos y Gift Card
        descuentos = invoice.lv_descuentos or 0.0
        gift_card = invoice.lv_importe_gift_card or 0.0
        
        # Importe base para débito fiscal
        importe_base_df = subtotal - descuentos - gift_card
        
        # Débito fiscal (13%)
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
        
        # Crear archivo Excel
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
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        
        # Encabezados (Fila 0)
        headers = [
            'N',
            'ESPECIFICACION',
            'FECHA DE LA FACTURA',
            'N DE LA FACTURA',
            'CODIGO DE AUTORIZACION',
            'NIT CI CLIENTE',
            'COMPLEMENTO',
            'NOMBRE O RAZON SOCIAL',
            'IMPORTE TOTAL DE LA VENTA',
            'IMPORTE ICE',
            'IMPORTE IEHD',
            'IMPORTE IPJ',
            'TASAS',
            'OTROS NO SUJETOS AL IVA',
            'EXPORTACIONES Y OPERACIONES EXENTAS',
            'VENTAS GRAVADAS A TASA CERO',
            'SUBTOTAL',
            'DESCUENTOS, BONIFICACIONES Y REBAJAS SUJETAS AL IVA',
            'IMPORTE GIFT CARD',
            'IMPORTE BASE PARA DEBITO FISCAL',
            'DEBITO FISCAL',
            'ESTADO',
            'CODIGO DE CONTROL',
            'TIPO DE VENTA',
        ]
        
        # Escribir encabezados
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Obtener facturas
        invoices = self._get_invoices()
        
        # Escribir datos
        row = 1
        for idx, invoice in enumerate(invoices, start=1):
            montos = self._calcular_montos(invoice)
            
            # Obtener datos del cliente
            partner = invoice.partner_id
            nit_ci = partner.vat or '0'
            complemento = partner.l10n_bo_id_extension or ''
            razon_social = partner.name or 'Sin Nombre'
            
            # Número correlativo
            worksheet.write(row, 0, idx)
            
            # Especificación (2 para facturas estándar)
            worksheet.write(row, 1, '2')
            
            # Fecha de factura
            if invoice.invoice_date:
                worksheet.write(row, 2, invoice.invoice_date.strftime('%d/%m/%Y'))
            else:
                worksheet.write(row, 2, '')
            
            # Número de factura
            worksheet.write(row, 3, invoice.name or '')
            
            # Código de autorización
            worksheet.write(row, 4, invoice.lv_codigo_autorizacion or '0')
            
            # NIT/CI Cliente
            worksheet.write(row, 5, nit_ci)
            
            # Complemento
            worksheet.write(row, 6, complemento)
            
            # Nombre o Razón Social
            worksheet.write(row, 7, razon_social)
            
            # Importe total de la venta
            worksheet.write(row, 8, montos['importe_total'], number_format)
            
            # Importe ICE
            worksheet.write(row, 9, montos['importe_ice'], number_format)
            
            # Importe IEHD
            worksheet.write(row, 10, montos['importe_iehd'], number_format)
            
            # Importe IPJ
            worksheet.write(row, 11, montos['importe_ipj'], number_format)
            
            # Tasas
            worksheet.write(row, 12, montos['tasas'], number_format)
            
            # Otros no sujetos al IVA
            worksheet.write(row, 13, montos['otros_no_iva'], number_format)
            
            # Exportaciones y operaciones exentas
            worksheet.write(row, 14, montos['exportaciones'], number_format)
            
            # Ventas gravadas a tasa cero
            worksheet.write(row, 15, montos['ventas_tasa_cero'], number_format)
            
            # Subtotal
            worksheet.write(row, 16, montos['subtotal'], number_format)
            
            # Descuentos, bonificaciones y rebajas
            worksheet.write(row, 17, montos['descuentos'], number_format)
            
            # Importe Gift Card
            worksheet.write(row, 18, montos['gift_card'], number_format)
            
            # Importe base para débito fiscal
            worksheet.write(row, 19, montos['importe_base_df'], number_format)
            
            # Débito fiscal
            worksheet.write(row, 20, montos['debito_fiscal'], number_format)
            
            # Estado
            estado = dict(invoice._fields['lv_estado'].selection).get(invoice.lv_estado, 'V')
            worksheet.write(row, 21, invoice.lv_estado or 'V')
            
            # Código de control
            worksheet.write(row, 22, invoice.lv_codigo_control or '0')
            
            # Tipo de venta
            worksheet.write(row, 23, invoice.lv_tipo_venta or '0')
            
            row += 1
        
        # Ajustar ancho de columnas
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
        
        # Crear nombre del archivo
        nombre_archivo = f"Libro_Ventas_V2_{self.fecha_inicio.strftime('%Y%m%d')}_{self.fecha_fin.strftime('%Y%m%d')}.xlsx"
        
        # Crear adjunto
        attachment = self.env['ir.attachment'].create({
            'name': nombre_archivo,
            'datas': base64.b64encode(output.read()),
            'res_model': 'sale.book.v2.wizard',
            'res_id': self.id,
            'type': 'binary',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
