# l10n_bo_purchase_book_line/models/libro_compras_wizard.py
from odoo import models, fields

class LibroComprasWizard(models.TransientModel):
    _name = 'libro.compras.wizard'
    _description = 'Wizard para el Libro de Compras'

    move_line_id = fields.Many2one('account.move.line', string='Línea de Asiento', required=True)

    # Encabezado (solo lectura)
    lc_nit = fields.Char(string='NIT', related='move_line_id.partner_id.lc_nit', readonly=True)
    lc_razon_social = fields.Char(string='Razón Social', related='move_line_id.partner_id.name', readonly=True)

    # Datos del documento de compra
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

    # Totales (se recalculan en la línea)
    lc_subtotal = fields.Float(related='move_line_id.lc_subtotal', string='Subtotal', readonly=True)
    lc_importe_base_cf = fields.Float(related='move_line_id.lc_importe_base_cf', string='Importe Base CF', readonly=True)
    lc_credito_fiscal = fields.Float(related='move_line_id.lc_credito_fiscal', string='Crédito Fiscal', readonly=True)

    def action_confirm(self):
        """Persistir en la línea los valores editados y cerrar modal."""
        self.ensure_one()
        vals = {
            'lc_codigo_autorizacion': self.lc_codigo_autorizacion,
            'lc_numero_factura': self.lc_numero_factura,
            'lc_numero_dui_dim': self.lc_numero_dui_dim,
            'lc_fecha_factura': self.lc_fecha_factura,
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
            'lc_tipo_compra': self.lc_tipo_compra,
            'lc_codigo_control': self.lc_codigo_control,
        }
        self.move_line_id.write(vals)
        return {'type': 'ir.actions.act_window_close'}
