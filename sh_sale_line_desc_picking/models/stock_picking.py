# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sh_line_desc_partner_id = fields.Many2one(
        "res.partner", string="Customer Address")
    sh_line_desc_partner_inv_id = fields.Many2one(
        "res.partner", string="Invoice Address")
