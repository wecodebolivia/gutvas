from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def get_discount_product(self):
        discount = self.discount / 100
        return round(discount, 2)
