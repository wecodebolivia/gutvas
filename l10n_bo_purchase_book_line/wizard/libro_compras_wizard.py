from odoo import api, fields, models

class LibroComprasLineWizard(models.TransientModel):
    _name = "libro.compras.line.wizard"
    _description = "Libro de Compras por línea"

    move_line_id = fields.Many2one(
        "account.move.line", required=True, readonly=True
    )
    lc_importe_base_cf = fields.Monetary(
        string="Importe base CF",
        currency_field="company_currency_id",
        required=True,
    )
    lc_credito_fiscal = fields.Monetary(
        string="Crédito fiscal",
        currency_field="company_currency_id",
        required=True,
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        related="move_line_id.company_currency_id",
        readonly=True,
    )

    def action_apply(self):
        self.ensure_one()
        self.move_line_id.write({
            "lc_importe_base_cf": self.lc_importe_base_cf,
            "lc_credito_fiscal": self.lc_credito_fiscal,
        })
        return {"type": "ir.actions.act_window_close"}
