# l10n_bo_purchase_book_line/models/account_move.py

from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

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
