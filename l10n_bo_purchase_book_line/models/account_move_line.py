from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Campos del libro de compras (sin compute/store para no colgar instalación)
    lc_importe_base_cf = fields.Monetary(
        string="Importe base CF",
        currency_field="company_currency_id",
        help="Importe base para crédito fiscal (Libro de Compras).",
    )
    lc_credito_fiscal = fields.Monetary(
        string="Crédito fiscal",
        currency_field="company_currency_id",
        help="Crédito fiscal de la línea (Libro de Compras).",
    )

    def action_open_libro_compras_wizard(self):
        """Abre el wizard para editar los campos de la línea."""
        self.ensure_one()
        view = self.env.ref(
            "l10n_bo_purchase_book_line.view_libro_compras_wizard_form"
        )
        ctx = {
            "default_move_line_id": self.id,
            "default_lc_importe_base_cf": self.lc_importe_base_cf,
            "default_lc_credito_fiscal": self.lc_credito_fiscal,
        }
        return {
            "name": "Libro de Compras (Línea)",
            "type": "ir.actions.act_window",
            "res_model": "libro.compras.line.wizard",
            "view_mode": "form",
            "view_id": view.id,
            "target": "new",
            "context": ctx,
        }
