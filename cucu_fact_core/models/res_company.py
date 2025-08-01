# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"
    _description = "Company cucu"

    water_mark = fields.Binary(string="Water mark")
    color_primary = fields.Char(string="Color primary", default="#003566")
    color_border = fields.Char(string="Color border", default="#ffc300")
    color_shadow = fields.Char(string="Color shadow", default="#ffd60a")
    water_mark_width = fields.Integer(string="Water Mark Width", default=300)
    water_mark_top = fields.Integer(string="Water Mark Top", default=500)
