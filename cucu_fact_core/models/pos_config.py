# -*- coding: utf-8 -*-
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    is_cucu_invoice = fields.Boolean("Active invoice", default=False)
    cucu_pos_id = fields.Many2one("cucu.pos", "Cucu Pos")
    cucu_city = fields.Char("City")
    branch_id = fields.Many2one("cucu.branch.office", related="cucu_pos_id.branch_id")
    manager_id = fields.Many2one("cucu.manager", related="branch_id.manager_id")
    doc_sector = fields.Selection("Document Sector", related="manager_id.doc_sector_id")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_cucu_invoice = fields.Boolean(
        related="pos_config_id.is_cucu_invoice", readonly=False
    )
    cucu_pos_id = fields.Many2one(
        "cucu.pos", related="pos_config_id.cucu_pos_id", readonly=False, store=True
    )
    cucu_city = fields.Char("City", related="pos_config_id.cucu_city", readonly=False)
    doc_sector_id = fields.Selection(
        "Doc Sector", related="pos_config_id.doc_sector", readonly=False
    )
    manager_id = fields.Many2one(
        "cucu.manager", related="pos_config_id.manager_id", readonly=False, store=True
    )
