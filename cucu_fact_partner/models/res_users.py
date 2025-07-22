# -*- coding: utf-8 -*-
###################################################################################
# Copyright (c) 2021-Present cucu | soluciones digitales (https://cucu.bo)
###################################################################################

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    company_id = fields.Many2one("res.company", string="Company", required=False)
    pos_id = fields.Many2one("pos.config", string="Point Of Sale", required=False)
