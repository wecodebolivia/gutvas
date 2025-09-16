# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # -------- Campos Libro de Compras (ingreso manual) --------
    lc_importe_total_compra = fields.Float(string='LC Importe total compra', default=0.0)
    lc_importe_ice = fields.Float(string='LC ICE', default=0.0)
    lc_importe_iehd = fields.Float(string='LC IEHD', default=0.0)
    lc_importe_ipj = fields.Float(string='LC IPJ', default=0.0)
    lc_tasas = fields.Float(string='LC Tasas', default=0.0)
    lc_otros_no_sujeto_cf = fields.Float(string='LC Otros no sujeto a CF', default=0.0)
    lc_importes_exentos = fields.Float(string='LC Importes exentos', default=0.0)
    lc_compras_gravadas_tasa_cero = fields.Float(string='LC Compras gravadas a 0%', default=0.0)
    lc_descuentos_bonificaciones = fields.Float(string='LC Descuentos/Bonificaciones', default=0.0)
    lc_importe_gift_card = fields.Float(string='LC Gift Card', default=0.0)

    # -------- Campos calculados --------
    lc_subtotal = fields.Float(string='LC Subtotal', compute='_compute_lc_totals', store=True)
    lc_importe_base_cf = fields.Float(string='LC Importe base CF', compute='_compute_lc_totals', store=True)
    lc_credito_fiscal = fields.Float(string='LC Crédito fiscal', compute='_compute_lc_totals', store=True)

    @api.depends(
        'lc_importe_total_compra',
        'lc_importe_ice', 'lc_importe_iehd', 'lc_importe_ipj', 'lc_tasas',
        'lc_otros_no_sujeto_cf', 'lc_importes_exentos', 'lc_compras_gravadas_tasa_cero',
        'lc_descuentos_bonificaciones', 'lc_importe_gift_card',
        'move_id.move_type', 'display_type'
    )
    def _compute_lc_totals(self):
        """Asignar SIEMPRE los 3 campos calculados para evitar errores de compute."""
        for line in self:
            subtotal = base_cf = cf = 0.0
            if line.move_id.move_type in ('in_invoice', 'in_refund') and not line.display_type:
                total = line.lc_importe_total_compra or 0.0
                restas = (
                    (line.lc_importe_ice or 0.0)
                    + (line.lc_importe_iehd or 0.0)
                    + (line.lc_importe_ipj or 0.0)
                    + (line.lc_tasas or 0.0)
                    + (line.lc_otros_no_sujeto_cf or 0.0)
                    + (line.lc_importes_exentos or 0.0)
                    + (line.lc_compras_gravadas_tasa_cero or 0.0)
                    + (line.lc_descuentos_bonificaciones or 0.0)
                    + (line.lc_importe_gift_card or 0.0)
                )
                subtotal = max(total - restas, 0.0)
                base_cf = subtotal
                cf = base_cf * 0.13

            line.lc_subtotal = subtotal
            line.lc_importe_base_cf = base_cf
            line.lc_credito_fiscal = cf

    # -------- Acción del botón: abrir nuestro form específico --------
    def action_open_lc_fields(self):
        self.ensure_one()
        view = self.env.ref('l10n_bo_purchase_book_line.view_account_move_line_form_lc')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Libro de Compras (Línea)',
            'res_model': 'account.move.line',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'target': 'new',
            'res_id': self.id,
            'context': dict(self.env.context or {}),
        }
