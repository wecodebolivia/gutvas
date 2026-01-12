# -*- coding: utf-8 -*-

from odoo import models, fields
import io
import base64

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class SaleBookWizard(models.TransientModel):
    _name = 'sale.book.wizard'
    _description = 'Libro de Ventas'

    fecha_inicio = fields.Date(string='Fecha Inicio', required=True)
    fecha_fin = fields.Date(string='Fecha Fin', required=True)
    company_id = fields.Many2one('res.company', string='Compañía', 
                                  required=True, default=lambda self: self.env.company)

    def generar_excel(self):
        self.ensure_one()
        
        if not xlsxwriter:
            from odoo.exceptions import UserError
            raise UserError('xlsxwriter no está instalado')
        
        invoices = self.env['account.move'].search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('invoice_date', '>=', self.fecha_inicio),
            ('invoice_date', '<=', self.fecha_fin),
            ('state', '=', 'posted'),
            ('company_id', '=', self.company_id.id),
        ], order='invoice_date, name')
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Ventas')
        
        hdr_fmt = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        num_fmt = workbook.add_format({'num_format': '#,##0.00'})
        
        headers = [
            'N', 'ESPECIFICACION', 'FECHA', 'FACTURA', 'AUTORIZACION',
            'NIT', 'COMPLEMENTO', 'RAZON SOCIAL', 'TOTAL', 'ICE', 'IEHD', 'IPJ',
            'TASAS', 'OTROS', 'EXENTAS', 'TASA CERO', 'SUBTOTAL', 'DESCUENTOS',
            'GIFT CARD', 'BASE DF', 'DEBITO FISCAL', 'ESTADO', 'COD CONTROL', 'TIPO'
        ]
        
        for col, hdr in enumerate(headers):
            sheet.write(0, col, hdr, hdr_fmt)
        
        row = 1
        for idx, inv in enumerate(invoices, 1):
            ice = getattr(inv, 'lv_importe_ice', 0) or 0
            iehd = getattr(inv, 'lv_importe_iehd', 0) or 0
            ipj = getattr(inv, 'lv_importe_ipj', 0) or 0
            tasas = getattr(inv, 'lv_tasas', 0) or 0
            otros = getattr(inv, 'lv_otros_no_iva', 0) or 0
            exentas = getattr(inv, 'lv_exportaciones_exentas', 0) or 0
            tcero = getattr(inv, 'lv_ventas_tasa_cero', 0) or 0
            desc = getattr(inv, 'lv_descuentos', 0) or 0
            gift = getattr(inv, 'lv_importe_gift_card', 0) or 0
            
            total = inv.amount_total
            subtotal = total - ice - iehd - ipj - tasas - otros - exentas - tcero
            base_df = subtotal - desc - gift
            df = base_df * 0.13
            
            sheet.write(row, 0, idx)
            sheet.write(row, 1, '2')
            sheet.write(row, 2, inv.invoice_date.strftime('%d/%m/%Y') if inv.invoice_date else '')
            sheet.write(row, 3, inv.name or '')
            sheet.write(row, 4, getattr(inv, 'lv_codigo_autorizacion', '0') or '0')
            sheet.write(row, 5, inv.partner_id.vat or '0')
            sheet.write(row, 6, getattr(inv.partner_id, 'l10n_bo_id_extension', '') or '')
            sheet.write(row, 7, inv.partner_id.name or '')
            sheet.write(row, 8, total, num_fmt)
            sheet.write(row, 9, ice, num_fmt)
            sheet.write(row, 10, iehd, num_fmt)
            sheet.write(row, 11, ipj, num_fmt)
            sheet.write(row, 12, tasas, num_fmt)
            sheet.write(row, 13, otros, num_fmt)
            sheet.write(row, 14, exentas, num_fmt)
            sheet.write(row, 15, tcero, num_fmt)
            sheet.write(row, 16, subtotal, num_fmt)
            sheet.write(row, 17, desc, num_fmt)
            sheet.write(row, 18, gift, num_fmt)
            sheet.write(row, 19, base_df, num_fmt)
            sheet.write(row, 20, df, num_fmt)
            sheet.write(row, 21, getattr(inv, 'lv_estado', 'V') or 'V')
            sheet.write(row, 22, getattr(inv, 'lv_codigo_control', '0') or '0')
            sheet.write(row, 23, getattr(inv, 'lv_tipo_venta', '0') or '0')
            row += 1
        
        workbook.close()
        output.seek(0)
        
        filename = 'LibroVentas_{0}_{1}.xlsx'.format(
            self.fecha_inicio.strftime('%Y%m%d'),
            self.fecha_fin.strftime('%Y%m%d')
        )
        
        att = self.env['ir.attachment'].create({
            'name': filename,
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{0}?download=true'.format(att.id),
            'target': 'self',
        }
