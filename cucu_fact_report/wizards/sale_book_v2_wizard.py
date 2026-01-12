# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime


class SaleBookV2Wizard(models.TransientModel):
    _name = 'sale.book.v2.wizard'
    _description = 'Libro de Ventas V2 - Formato Estándar SIN'

    date_from = fields.Date(
        string='Fecha Desde',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='Fecha Hasta',
        required=True,
        default=fields.Date.today
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    excel_file = fields.Binary(
        string='Archivo Excel',
        readonly=True
    )
    file_name = fields.Char(
        string='Nombre del Archivo',
        readonly=True
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Generado')
    ], default='draft', string='Estado')

    def _get_invoices(self):
        """Obtener facturas de venta del periodo seleccionado"""
        domain = [
            ('company_id', '=', self.company_id.id),
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted')
        ]
        return self.env['account.move'].search(domain, order='invoice_date, name')

    def _prepare_invoice_data(self, invoice, sequence):
        """Preparar datos de una factura para el formato V2"""
        # Valores por defecto
        especificacion = 2  # Facturas Estándar
        
        # Datos del cliente
        partner = invoice.partner_id
        nit_ci = partner.vat or '0'
        complemento = partner.l10n_bo_complement or ''
        nombre = partner.name or 'SIN NOMBRE'
        
        # Código de autorización
        codigo_autorizacion = getattr(invoice, 'l10n_bo_authorization_code', '') or '0'
        
        # Código de control
        codigo_control = getattr(invoice, 'l10n_bo_control_code', '') or '0'
        
        # Estado de la factura
        estado = 'V'  # VALIDA por defecto
        if invoice.state == 'cancel':
            estado = 'A'  # ANULADA
        
        # Cálculos de montos
        amount_total = invoice.amount_total
        amount_untaxed = invoice.amount_untaxed
        amount_tax = invoice.amount_tax
        
        # Impuestos especiales (por defecto en 0)
        importe_ice = 0.0
        importe_iehd = 0.0
        importe_ipj = 0.0
        tasas = 0.0
        otros_no_sujetos_iva = 0.0
        exportaciones_exentas = 0.0
        ventas_tasa_cero = 0.0
        
        # Buscar impuestos específicos en las líneas
        for line in invoice.invoice_line_ids:
            for tax in line.tax_ids:
                tax_name_upper = (tax.name or '').upper()
                if 'ICE' in tax_name_upper:
                    importe_ice += line.price_subtotal * (tax.amount / 100)
                elif 'IEHD' in tax_name_upper:
                    importe_iehd += line.price_subtotal * (tax.amount / 100)
                elif 'IPJ' in tax_name_upper:
                    importe_ipj += line.price_subtotal * (tax.amount / 100)
        
        # Subtotal
        subtotal = amount_total - importe_ice - importe_iehd - importe_ipj - tasas - otros_no_sujetos_iva - exportaciones_exentas - ventas_tasa_cero
        
        # Descuentos
        descuentos = 0.0
        for line in invoice.invoice_line_ids:
            if line.discount > 0:
                descuentos += (line.price_unit * line.quantity * line.discount / 100)
        
        # Gift card
        importe_gift_card = 0.0
        
        # Base para débito fiscal
        importe_base_debito = subtotal - descuentos - importe_gift_card
        
        # Débito fiscal (13% del IVA)
        debito_fiscal = importe_base_debito * 0.13
        
        # Tipo de venta
        tipo_venta = 0  # OTROS por defecto
        
        return [
            sequence,  # N
            especificacion,  # ESPECIFICACION
            invoice.invoice_date.strftime('%d/%m/%Y') if invoice.invoice_date else '',  # FECHA DE LA FACTURA
            invoice.name or '',  # N DE LA FACTURA
            codigo_autorizacion,  # CODIGO DE AUTORIZACION
            nit_ci,  # NIT CI CLIENTE
            complemento,  # COMPLEMENTO
            nombre,  # NOMBRE O RAZON SOCIAL
            round(amount_total, 2),  # IMPORTE TOTAL DE LA VENTA
            round(importe_ice, 2),  # IMPORTE ICE
            round(importe_iehd, 2),  # IMPORTE IEHD
            round(importe_ipj, 2),  # IMPORTE IPJ
            round(tasas, 2),  # TASAS
            round(otros_no_sujetos_iva, 2),  # OTROS NO SUJETOS AL IVA
            round(exportaciones_exentas, 2),  # EXPORTACIONES Y OPERACIONES EXENTAS
            round(ventas_tasa_cero, 2),  # VENTAS GRAVADAS A TASA CERO
            round(subtotal, 2),  # SUBTOTAL
            round(descuentos, 2),  # DESCUENTOS, BONIFICACIONES Y REBAJAS
            round(importe_gift_card, 2),  # IMPORTE GIFT CARD
            round(importe_base_debito, 2),  # IMPORTE BASE PARA DEBITO FISCAL
            round(debito_fiscal, 2),  # DEBITO FISCAL
            estado,  # ESTADO
            codigo_control,  # CODIGO DE CONTROL
            tipo_venta,  # TIPO DE VENTA
        ]

    def action_generate_excel(self):
        """Generar el archivo Excel con el formato V2"""
        self.ensure_one()
        
        # Crear archivo Excel
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Hoja1')
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'bg_color': '#D9E1F2',
            'font_size': 10
        })
        
        data_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'font_size': 9
        })
        
        number_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00',
            'font_size': 9
        })
        
        # Encabezados
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
            'TIPO DE VENTA'
        ]
        
        # Escribir encabezados
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Ajustar anchos de columna
        column_widths = [
            5,   # N
            13,  # ESPECIFICACION
            18,  # FECHA DE LA FACTURA
            15,  # N DE LA FACTURA
            20,  # CODIGO DE AUTORIZACION
            15,  # NIT CI CLIENTE
            12,  # COMPLEMENTO
            30,  # NOMBRE O RAZON SOCIAL
            18,  # IMPORTE TOTAL DE LA VENTA
            12,  # IMPORTE ICE
            12,  # IMPORTE IEHD
            12,  # IMPORTE IPJ
            12,  # TASAS
            20,  # OTROS NO SUJETOS AL IVA
            25,  # EXPORTACIONES Y OPERACIONES EXENTAS
            23,  # VENTAS GRAVADAS A TASA CERO
            15,  # SUBTOTAL
            25,  # DESCUENTOS
            15,  # IMPORTE GIFT CARD
            23,  # IMPORTE BASE PARA DEBITO FISCAL
            15,  # DEBITO FISCAL
            10,  # ESTADO
            20,  # CODIGO DE CONTROL
            12   # TIPO DE VENTA
        ]
        
        for col, width in enumerate(column_widths):
            worksheet.set_column(col, col, width)
        
        # Obtener facturas
        invoices = self._get_invoices()
        
        # Escribir datos
        row = 1
        for idx, invoice in enumerate(invoices, start=1):
            data = self._prepare_invoice_data(invoice, idx)
            for col, value in enumerate(data):
                # Determinar formato según el tipo de dato
                if col in [0, 1, 21, 23]:  # Columnas de texto/números enteros
                    worksheet.write(row, col, value, data_format)
                elif col in [2, 3, 4, 5, 6, 7, 22]:  # Texto
                    worksheet.write(row, col, value, data_format)
                else:  # Números con decimales
                    worksheet.write(row, col, value, number_format)
            row += 1
        
        # Cerrar el workbook
        workbook.close()
        output.seek(0)
        
        # Guardar el archivo
        file_name = f'Libro_Ventas_V2_{self.date_from.strftime("%Y%m%d")}_{self.date_to.strftime("%Y%m%d")}.xlsx'
        self.write({
            'excel_file': base64.b64encode(output.read()),
            'file_name': file_name,
            'state': 'done'
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.book.v2.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context
        }

    def action_back_to_draft(self):
        """Volver al estado borrador para generar nuevo reporte"""
        self.write({
            'excel_file': False,
            'file_name': False,
            'state': 'draft'
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.book.v2.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
