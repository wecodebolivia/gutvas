from odoo import fields, models


class InvoiceReport(models.TransientModel):
    _name = "invoice.report"

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")

    pos_configs = fields.Many2many(string="POS Config", comodel_name="pos.config")

    branch_configs = fields.Many2many(
        string="Branch Office Config", comodel_name="cucu.branch.office"
    )

    pos = fields.Boolean(string="POS", default=True)
    branch_office = fields.Boolean(string="BRANCH OFFICE")
    contingency = fields.Boolean(string="Contigencia")
    doc_id = fields.Many2many("cucu.catalogs.documents", string="Document type")
    canceled_invoices = fields.Boolean(string="Facturas Anuladas")

    def generate_report(self):
        return {
            "type": "ir.actions.act_url",
            "url": "/cucu/report/sales?id=%s" % self.id,
            "target": "self",
        }
