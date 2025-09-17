# l10n_bo_purchase_book_line/models/account_move.py
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Conservamos este método por si se quiere abrir el asistente desde la factura completa,
    # pero por defecto el botón está en cada línea de factura.
    def action_open_libro_compras_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Libro de Compras',
            'res_model': 'libro.compras.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
