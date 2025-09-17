from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_open_libro_compras(self):
        # Aquí puedes poner lógica más adelante
        return {
            'type': 'ir.actions.act_window',
            'name': 'Libro de Compras',
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id,
        }
