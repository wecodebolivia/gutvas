# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campos para Libro de Ventas V2
    lv_codigo_autorizacion = fields.Char(string='Código de Autorización', copy=False)
    lv_codigo_control = fields.Char(string='Código de Control', copy=False)
    lv_estado = fields.Selection([
        ('V', 'VALIDA'),
        ('A', 'ANULADA'),
        ('C', 'EMITIDA EN CONTINGENCIA'),
        ('L', 'LIBRE CONSIGNACIÓN'),
    ], string='Estado Factura', default='V', copy=False)
    lv_tipo_venta = fields.Selection([
        ('0', 'OTROS'),
        ('1', 'GIFT CARD'),
    ], string='Tipo de Venta', default='0', copy=False)
    
    # Campos de montos específicos
    lv_importe_ice = fields.Monetary(string='Importe ICE', currency_field='currency_id', default=0.0)
    lv_importe_iehd = fields.Monetary(string='Importe IEHD', currency_field='currency_id', default=0.0)
    lv_importe_ipj = fields.Monetary(string='Importe IPJ', currency_field='currency_id', default=0.0)
    lv_tasas = fields.Monetary(string='Tasas', currency_field='currency_id', default=0.0)
    lv_otros_no_iva = fields.Monetary(string='Otros no sujetos al IVA', currency_field='currency_id', default=0.0)
    lv_exportaciones_exentas = fields.Monetary(string='Exportaciones y Operaciones Exentas', currency_field='currency_id', default=0.0)
    lv_ventas_tasa_cero = fields.Monetary(string='Ventas Gravadas a Tasa Cero', currency_field='currency_id', default=0.0)
    lv_descuentos = fields.Monetary(string='Descuentos, Bonificaciones y Rebajas', currency_field='currency_id', default=0.0)
    lv_importe_gift_card = fields.Monetary(string='Importe Gift Card', currency_field='currency_id', default=0.0)
