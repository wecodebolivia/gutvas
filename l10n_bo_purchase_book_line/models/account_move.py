from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_open_libro_compras(self):
        # Este es solo un ejemplo temporal para confirmar que el botón funciona
        return {
            'type': 'ir.actions.act_window',
            'name': 'Libro de Compras',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('move_type', '=', 'in_invoice')],
        }