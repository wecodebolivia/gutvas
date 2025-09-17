# -*- coding: utf-8 -*-
from odoo import models, fields

class LibroComprasWizard(models.TransientModel):
    _name = 'libro.compras.wizard'
    _description = 'Wizard para el Libro de Compras'

    move_line_id = fields.Many2one('account.move.line', string='Línea de Asiento', required=True)

    # Encabezado (desde la línea ya resuelto)
    lc_header_nit = fields.Char(string='NIT', related='move_line_id.lc_partner_nit_display', readonly=True)
    lc_header_razon_social = fields.Char(string='Razón Social', related='move_line_id.lc_partner_name_display', readonly=True)

    # --- ALIAS backward-compatible (por si alguna vista antigua los usa) ---
    lc_nit = fields.Char(string='NIT (alias)', related='lc_header_nit', readonly=True)
    lc_razon_social = fields.Char(string='Razón Social (alias)', related='lc_header_razon_social', readonly=True)

    # Documento
    lc_codigo_autorizacion = fields.Char(string='Código de Autorización')
    lc_numero_factura = fields.Char(string='Número de Factura')
    lc_numero_dui_dim = fields.Char(string='Número DUI/DIM')
    lc_fecha_factura = fields.Date(string='Fecha de Factura')

    # Montos
    lc_importe_total_compra = fields.Float(string='Importe Total Compra', digits=(16, 2), default=0.0)
    lc_importe_ice = fields.Float(string='Importe ICE', digits=(16, 2), default=0.0)
    lc_importe_iehd = fields.Float(string='Importe IEHD', digits=(16, 2), default=0.0)
    lc_importe_ipj = fields.Float(string='Importe IPJ', digits=(16, 2), default=0.0)
    lc_tasas = fields.Float(string='Tasas', digits=(16, 2), default=0.0)
    lc_otros_no_sujeto_cf = fields.Float(string='Otros No Sujeto a CF', digits=(16, 2), default=0.0)
    lc_importes_exentos = fields.Float(string='Importes Exentos', digits=(16, 2), default=0.0)
    lc_compras_gravadas_tasa_cero = fields.Float(string='Compras Gravadas a Tasa Cero', digits=(16, 2), default=0.0)
    lc_descuentos_bonificaciones = fields.Float(string='Descuentos/Bonificaciones', digits=(16, 2), default=0.0)
    lc_importe_gift_card = fields.Float(string='Importe Gift Card', digits=(16, 2), default=0.0)

    lc_tipo_compra = fields.Selection([
        ('1', 'Actividad gravada'),
        ('2', 'Actividad no gravada'),
        ('3', 'Sujetas a proporcionalidad'),
        ('4', 'Exportaciones'),
        ('5', 'Interno/Exportaciones'),
    ], string='Tipo de Compra', default='1')
    lc_codigo_control = fields.Char(string='Código de Control')

    # Totales (solo lectura)
    lc_subtotal = fields.Float(related='move_line_id.lc_subtotal', string='Subtotal', readonly=True)
    lc_importe_base_cf = fields.Float(related='move_line_id.lc_importe_base_cf', string='Importe Base CF', readonly=True)
    lc_credito_fiscal = fields.Float(related='move_line_id.lc_credito_fiscal', string='Crédito Fiscal', readonly=True)

    def action_confirm(self):
        self.ensure_one()
        self.move_line_id.write({
            'lc_importe_total_compra': self.lc_importe_total_compra,
            'lc_importe_ice': self.lc_importe_ice,
            'lc_importe_iehd': self.lc_importe_iehd,
            'lc_importe_ipj': self.lc_importe_ipj,
            'lc_tasas': self.lc_tasas,
            'lc_otros_no_sujeto_cf': self.lc_otros_no_sujeto_cf,
            'lc_importes_exentos': self.lc_importes_exentos,
            'lc_compras_gravadas_tasa_cero': self.lc_compras_gravadas_tasa_cero,
            'lc_descuentos_bonificaciones': self.lc_descuentos_bonificaciones,
            'lc_importe_gift_card': self.lc_importe_gift_card,
        })
        return {'type': 'ir.actions.act_window_close'}
