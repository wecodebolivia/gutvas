# -*- coding: utf-8 -*-
from odoo import api, models


class ReportCucuTicket(models.AbstractModel):
    _name = "report.cucu_fact_report.cucu_report_ticket"
    _description = "Report ticket cucu"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["account.move"].browse(docids)
        invoice = docs.render_invoice()
        send_data = {
            "doc_ids": docids,
            "docs": docs,
            "doc_model": "account.move",
            "data": data,
            "header": invoice["header"],
            "detail": invoice["detail"],
        }
        return send_data
