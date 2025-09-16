# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # --- Campos base que el usuario captura (del Libro de Compras) ---
    lc_codigo_autorizacion = fields.Char(string="Código de Autorización")
    lc_numero_factura = fields.Char(string="Número de Factura")
    lc_numero_dui_dim = fields.Char(string="Número DUI/DIM")
    lc_fecha_factura = fields.Date(string="Fecha de Factura")

    lc_importe_total_compra = fields.Monetary(string="Importe Total Compra", currency_field="currency_id")
    lc_importe_ice = fields.Monetary(string="Importe ICE", currency_field="currency_id")
    lc_importe_iehd = fields.Monetary(string="Importe IEHD", currency_field="currency_id")
    lc_importe_ipj = fields.Monetary(string="Importe IPJ", currency_field="currency_id")
    lc_tasas = fields.Monetary(string="Tasas", currency_field="currency_id")
    lc_otros_no_sujeto_cf = fields.Monetary(string="Otros No Sujeto a CF", currency_field="currency_id")
    lc_importes_exentos = fields.Monetary(string="Importes Exentos", currency_field="currency_id")
    lc_compras_gravadas_tasa_cero = fields.Monetary(string="Compras Gravadas a Tasa Cero", currency_field="currency_id")
    lc_descuentos_bonificaciones = fields.Monetary(string="Descuentos y Bonificaciones", currency_field="currency_id")
    lc_importe_gift_card = fields.Monetary(string="Importe Gift Card", currency_field="currency_id")

    lc_tipo_compra = fields.Selection([
        ("CF", "Con Crédito Fiscal"),
        ("SF", "Sin Crédito Fiscal"),
        ("AN", "Anulada"),
    ], string="Tipo de Compra", default="CF")

    lc_codigo_control = fields.Char(string="Código de Control")

    # --- Derivados / computados ---
    lc_subtotal = fields.Monetary(string="Subtotal", currency_field="currency_id", compute="_compute_lc_totales", store=True)
    lc_importe_base_cf = fields.Monetary(string="Importe Base CF", currency_field="currency_id", compute="_compute_lc_totales", store=True)
    lc_credito_fiscal = fields.Monetary(string="Crédito Fiscal", currency_field="currency_id", compute="_compute_lc_totales", store=True)

    # Nos aseguramos de tener siempre una moneda para los Monetary
    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        default=lambda self: self.company_currency_id.id,  # fallback
        readonly=True
    )
    company_currency_id = fields.Many2one(related="company_id.currency_id", string="Moneda de la Compañía", store=False, readonly=True)

    @api.depends(
        "lc_importe_total_compra", "lc_importe_ice", "lc_importe_iehd", "lc_importe_ipj",
        "lc_tasas", "lc_otros_no_sujeto_cf", "lc_importes_exentos",
        "lc_compras_gravadas_tasa_cero", "lc_descuentos_bonificaciones", "lc_importe_gift_card",
        "lc_tipo_compra"
    )
    def _compute_lc_totales(self):
        for line in self:
            # Subtotal = Importe Total - (ICE + IEHD + IPJ + Tasas + Otros No Sujeto CF + Exentos + Tasa Cero + Gift Card + Descuentos)
            subtotal = (line.lc_importe_total_compra or 0.0) \
                - (line.lc_importe_ice or 0.0) \
                - (line.lc_importe_iehd or 0.0) \
                - (line.lc_importe_ipj or 0.0) \
                - (line.lc_tasas or 0.0) \
                - (line.lc_otros_no_sujeto_cf or 0.0) \
                - (line.lc_importes_exentos or 0.0) \
                - (line.lc_compras_gravadas_tasa_cero or 0.0) \
                - (line.lc_importe_gift_card or 0.0) \
                - (line.lc_descuentos_bonificaciones or 0.0)

            line.lc_subtotal = max(subtotal, 0.0)

            # Base CF aplica solo cuando es con crédito fiscal
            base_cf = line.lc_subtotal if line.lc_tipo_compra == "CF" else 0.0
            line.lc_importe_base_cf = base_cf

            # Crédito fiscal = 13% de la base CF
            line.lc_credito_fiscal = round(base_cf * 0.13, 2)

    # Acción para abrir el wizard desde la línea de asiento
    def action_open_libro_compras_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Libro de Compras (Línea)",
            "res_model": "libro.compras.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_move_line_id": self.id,
            },
        }
