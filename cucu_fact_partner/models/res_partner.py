# -*- coding: utf-8 -*-
###################################################################################
# Copyright (c) 2021-Present cucu | soluciones digitales (https://cucu.bo)
###################################################################################

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Cucu Clients"

    nit_client = fields.Char("Number Document")
    client_code = fields.Char(string="Client code")
    reason_social = fields.Char("Reason social")
    complement = fields.Char("Complement", size=2)
    cucu_email = fields.Char(string="Email")
    nit_valid = fields.Boolean("Nit valid", default=False)
    is_sin = fields.Boolean("Is Sin", default=False)

    doc_id = fields.Many2one("cucu.catalogs.documents", string="Document type")
