# -*- coding: utf-8 -*-
from odoo import api, models


class ReportAccountMovePayment(models.AbstractModel):
    _name = "report.cucu_fact_report.cucu_report_account"
    _description = "Account report with payment lines cucu"
    _inherit = "report.account.report_invoice_with_payments"

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data)
        invoice = res["docs"].render_invoice()
        res["header"] = invoice["header"]
        res["detail"] = invoice["detail"]
        res["is_valid"] = invoice["docs"].sin_code_state
        return res


class ReportAccountMove(models.AbstractModel):
    _name = "report.cucu_fact_report.cucu_report_account"
    _description = "Account report with payment lines cucu"
    _inherit = "report.account.report_invoice"

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data)
        invoice = res["docs"].render_invoice()
        res["header"] = invoice["header"]
        res["detail"] = invoice["detail"]
        res["is_valid"] = res["docs"].sin_code_state
        return res
