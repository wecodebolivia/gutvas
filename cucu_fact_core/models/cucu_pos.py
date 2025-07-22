# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CucuPos(models.Model):
    _name = "cucu.pos"
    _description = "Cucu pos"
    _order = "pos_id"

    siat_code = fields.Integer(string="Siat code")
    pos_id = fields.Integer(string="Pos Id")
    siat_branch_code = fields.Integer(string="Siat branch code")
    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    siat_description = fields.Char(string="Description")
    cuis = fields.Char(string="Cuis")
    cufd = fields.Char(string="Cufd")
    branch_id = fields.Many2one("cucu.branch.office", string="Branch Id")
    siat_type_pos = fields.Many2one("cucu.catalogs.point.of.sale")
    pos_name = fields.Char(string="Pos Name")
    company_id = fields.Many2one("res.company", "Company")
    manager_id = fields.Many2one("cucu.manager", related="branch_id.manager_id")
    doc_sector = fields.Selection("Document Sector", related="manager_id.doc_sector_id")

    @api.depends("branch_id", "siat_code")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s - %s (%s)" % (
                rec.branch_id.municipality or "",
                rec.branch_id.name,
                rec.siat_code,
            )

    def create_data_pos(self, rec):
        self.create(
            {
                "siat_code": rec["siatCode"],
                "pos_id": rec["posId"],
                "siat_branch_code": rec["siatBranchCode"],
                "name": rec["name"],
                "description": rec["siatDescription"],
                "siat_description": rec["siatDescription"],
                "cuis": rec["cuis"],
                "cufd": rec["cufd"],
                "branch_id": rec["branchId"],
                "company_id": self.env.company.id,
            }
        )
