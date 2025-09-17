# l10n_bo_purchase_book_line/models/account_move_line.py
from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_purchase_book_line = fields.Boolean(
        string="Es línea de libro de compras", 
        help="Indica si esta línea debe considerarse en el libro de compras."
    )
    nit = fields.Char(string="NIT Proveedor")
    invoice_number = fields.Char(string="Número de Factura")
    authorization_number = fields.Char(string="Número de Autorización")
    control_code = fields.Char(string="Código de Control")
    purchase_amount = fields.Monetary(string="Monto de la Compra")
    fiscal_credit = fields.Monetary(string="Crédito Fiscal", help="13% del monto si aplica")
    currency_id = fields.Many2one("res.currency", string="Moneda")
