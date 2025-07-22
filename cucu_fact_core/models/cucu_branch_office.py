# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError


class CucuBranchOffice(models.Model):
    _name = "cucu.branch.office"
    _description = "Cucu branch office"
    _order = "branch_id"

    siat_code = fields.Integer(string="Siat code")
    branch_id = fields.Integer(string="Branch Office Id")
    name = fields.Char(string="Name")
    phone = fields.Char(string="Phone")
    city = fields.Char(string="City")
    address = fields.Char(string="Address")
    municipality = fields.Char(string="Municipality")
    description = fields.Char(string="Description")
    cafc = fields.Char(string="Cafc")
    pos_id = fields.One2many("cucu.pos", "branch_id", string="Pos lines")
    company_id = fields.Many2one("res.company", "Company")
    manager_id = fields.Many2one("cucu.manager", "Manager")

    def create_branchs(self, branch):
        try:
            company_id = self.env.company.id  # current company
            db_branch = self.env["cucu.branch.office"].search(
                [("company_id", "=", company_id)]
            )
            if len(db_branch) > 0:
                map_ids = list(map(lambda branch_id: branch_id["branch_id"], db_branch))
                for rec in branch:
                    if rec["branchId"] not in map_ids:
                        self._create_data_branch(rec, company_id)
            else:
                for rec in branch:
                    self._create_data_branch(rec, company_id)
            self.env.cr.commit()
            return True
        except Exception as e:  # noqa: F841
            raise UserError("SYNC BRANCH ERROR")

    def _create_data_branch(self, rec, company_id):
        self.create(
            {
                "siat_code": rec["siatCode"],
                "branch_id": rec["branchId"],
                "name": rec["name"],
                "phone": rec["phone"],
                "city": rec["city"],
                "address": rec["address"],
                "municipality": rec["municipality"],
                "description": rec["description"],
                "cafc": rec["siatCafc"],
                "manager_id": rec["manager_id"],
                "company_id": company_id,
            }
        )

    def action_sync_pos(self):
        company_id = self.env.company.id
        pos = self.manager_id.sync_pos(self.branch_id)
        db_pos = self.env["cucu.pos"].search(
            [("branch_id", "=", self.id), ("company_id", "=", company_id)]
        )
        if len(db_pos) > 0:
            map_ids = list(map(lambda pos_id: pos_id["pos_id"], db_pos))
            for rec in pos:
                if rec["posId"] not in map_ids:
                    rec["branchId"] = self.id
                    self.env["cucu.pos"].create_data_pos(rec)
        else:
            for rec in pos:
                rec["branchId"] = self.id
                self.env["cucu.pos"].create_data_pos(rec)
        return True
