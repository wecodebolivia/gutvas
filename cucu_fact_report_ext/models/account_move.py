from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('pos_config_id.phone', 'company_id.phone')
    def _compute_sucursal_phone(self):
        for rec in self:
            rec.sucursal_phone_display = rec.pos_config_id.phone or rec.company_id.phone or False

    sucursal_phone_display = fields.Char(compute='_compute_sucursal_phone', store=False)