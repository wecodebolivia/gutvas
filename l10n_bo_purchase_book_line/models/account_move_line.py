# l10n_bo_purchase_book_line/models/account_move_line.py

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Campos específicos para el libro de compras
    lc_codigo_autorizacion = fields.Char(string='Código de Autorización')
    lc_numero_factura = fields.Char(string='Número de Factura')
    lc_numero_dui_dim = fields.Char(string='Número DUI/DIM')
    lc_fecha_factura = fields.Date(string='Fecha de Factura')
    lc_importe_total_compra = fields.Float(string='Importe Total Compra', digits=(16, 2))
    lc_importe_ice = fields.Float(string='Importe ICE', digits=(16, 2))
    lc_importe_iehd = fields.Float(string='Importe IEHD', digits=(16, 2))
    lc_importe_ipj = fields.Float(string='Importe IPJ', digits=(16, 2))
    lc_tasas = fields.Float(string='Tasas', digits=(16, 2))
    lc_otros_no_sujeto_cf = fields.Float(string='Otros No Sujeto a CF', digits=(16, 2))
    lc_importes_exentos = fields.Float(string='Importes Exentos', digits=(16, 2))
    lc_compras_gravadas_tasa_cero = fields.Float(string='Compras Gravadas a Tasa Cero', digits=(16, 2))
    lc_descuentos_bonificaciones = fields.Float(string='Descuentos/Bonificaciones', digits=(16, 2))
    lc_importe_gift_card = fields.Float(string='Importe Gift Card', digits=(16, 2))
    lc_tipo_compra = fields.Selection([
        ('1', 'Actividad gravada'),
        ('2', 'Actividad no gravada'),
        ('3', 'Sujetas a proporcionalidad'),
        ('4', 'Exportaciones'),
        ('5', 'Interno/Exportaciones')
    ], string='Tipo de Compra', default='1')
    lc_codigo_control = fields.Char(string='Código de Control')

    # Campos calculados
    # OJO: sin store=True para no recalcular masivamente en instalación
    lc_subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        digits=(16, 2),
    )
    lc_importe_base_cf = fields.Float(
        string='Importe Base CF',
        compute='_compute_importe_base_cf',
        digits=(16, 2),
    )
    lc_credito_fiscal = fields.Float(
        string='Crédito Fiscal',
        compute='_compute_credito_fiscal',
        digits=(16, 2),
    )

    # Métodos para cálculos automáticos
    @api.depends(
        'lc_importe_total_compra',
        'lc_importe_ice',
        'lc_importe_iehd',
        'lc_importe_ipj',
        'lc_tasas',
        'lc_otros_no_sujeto_cf',
        'lc_importes_exentos',
        'lc_compras_gravadas_tasa_cero',
    )
    def _compute_subtotal(self):
        for line in self:
            line.lc_subtotal = (
                (line.lc_importe_total_compra or 0.0)
                - (line.lc_importe_ice or 0.0)
                - (line.lc_importe_iehd or 0.0)
                - (line.lc_importe_ipj or 0.0)
                - (line.lc_tasas or 0.0)
                - (line.lc_otros_no_sujeto_cf or 0.0)
                - (line.lc_importes_exentos or 0.0)
                - (line.lc_compras_gravadas_tasa_cero or 0.0)
            )

    @api.depends(
        'lc_subtotal',
        'lc_descuentos_bonificaciones',
        'lc_importe_gift_card',
    )
    def _compute_importe_base_cf(self):
        for line in self:
            line.lc_importe_base_cf = (
                (line.lc_subtotal or 0.0)
                - (line.lc_descuentos_bonificaciones or 0.0)
                - (line.lc_importe_gift_card or 0.0)
            )

    @api.depends('lc_importe_base_cf')
    def _compute_credito_fiscal(self):
        for line in self:
            line.lc_credito_fiscal = (line.lc_importe_base_cf or 0.0) * 0.13

    def action_open_libro_compras_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Libro de Compras',
            'res_model': 'libro.compras.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_move_line_id': self.id},
        }
