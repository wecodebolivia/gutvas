# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    display_phone = fields.Char(
        string="Teléfono para Reporte",
        compute='_compute_display_phone',
        store=False
    )

    @api.depends('pos_config_id.phone', 'company_id.phone')
    def _compute_display_phone(self):
        for move in self:
            if move.pos_config_id and move.pos_config_id.phone:
                move.display_phone = move.pos_config_id.phone
            else:
                move.display_phone = move.company_id.phone or ''
