from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_open_libro_compras(self):
        return True
