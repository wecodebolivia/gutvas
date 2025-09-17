# l10n_bo_purchase_book_line/models/account_move_line.py
from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Campos del Libro de Compras
    lc_codigo_autorizacion = fields.Char(string='Código de Autorización')
    lc_numero_factura = fields.Char(string='Número de Factura')
    lc_numero_dui_dim = fields.Char(string='Número DUI/DIM')
    lc_fecha_factura = fields.Date(string='Fecha de Factura')

    lc_importe_total_compra = fields.Monetary(string='Importe Total Compra', currency_field='company_currency_id')
    lc_importe_ice = fields.Monetary(string='Importe ICE', currency_field='company_currency_id')
    lc_importe_iehd = fields.Monetary(string='Importe IEHD', currency_field='company_currency_id')
    lc_importe_ipj = fields.Monetary(string='Importe IPJ', currency_field='company_currency_id')
    lc_tasas = fields.Monetary(string='Tasas', currency_field='company_currency_id')
    lc_otros_no_sujeto_cf = fields.Monetary(string='Otros No Sujetos a CF', currency_field='company_currency_id')
    lc_importes_exentos = fields.Monetary(string='Importes Exentos', currency_field='company_currency_id')
    lc_compras_gravadas_tasa_cero = fields.Monetary(string='Compras Gravadas a Tasa Cero', currency_field='company_currency_id')
    lc_descuentos_bonificaciones = fields.Monetary(string='Descuentos y Bonificaciones', currency_field='company_currency_id')
    lc_importe_gift_card = fields.Monetary(string='Importe Gift Card', currency_field='company_currency_id')

    lc_importe_base_cf = fields.Monetary(string='Importe Base CF', currency_field='company_currency_id', compute='_compute_importe_base_cf', store=True, readonly=True)
    lc_credito_fiscal = fields.Monetary(string='Crédito Fiscal (13%)', currency_field='company_currency_id', compute='_compute_credito_fiscal', store=True, readonly=True)

    lc_tipo_compra = fields.Selection([
        ('cf', 'Con derecho a Crédito Fiscal'),
        ('sf', 'Sin derecho a Crédito Fiscal'),
        ('an', 'Anulación/Devolución'),
        ('tc', 'Tasa Cero'),
    ], string='Tipo de Compra', default='cf')

    lc_codigo_control = fields.Char(string='Código de Control')

    @api.depends(
        'lc_importe_total_compra', 'lc_importe_ice', 'lc_importe_iehd', 'lc_importe_ipj',
        'lc_tasas', 'lc_otros_no_sujeto_cf', 'lc_importes_exentos',
        'lc_compras_gravadas_tasa_cero', 'lc_descuentos_bonificaciones', 'lc_importe_gift_card'
    )
    def _compute_importe_base_cf(self):
        for line in self:
            total = line.lc_importe_total_compra or 0.0
            restas = sum([
                line.lc_importe_ice or 0.0,
                line.lc_importe_iehd or 0.0,
                line.lc_importe_ipj or 0.0,
                line.lc_tasas or 0.0,
                line.lc_otros_no_sujeto_cf or 0.0,
                line.lc_importes_exentos or 0.0,
                line.lc_compras_gravadas_tasa_cero or 0.0,
                line.lc_descuentos_bonificaciones or 0.0,
                line.lc_importe_gift_card or 0.0,
            ])
            line.lc_importe_base_cf = max(total - restas, 0.0)

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
