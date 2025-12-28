# -*- coding: utf-8 -*-
from odoo import api, models


class ReportCucuAccountInvoice(models.AbstractModel):
    """
    Report model used by QWeb template `cucu_fact_report.cucu_report_account`.

    IMPORTANT:
    Some invoices may NOT yet have CUCU/SIN data (self.invoice_id empty).
    In that case render_invoice() returns None and we must fallback gracefully
    so printing never crashes.
    """
    _name = "report.cucu_fact_report.cucu_report_account"
    _description = "CUCU - Account Invoice Report (fallback-safe)"
    _inherit = "report.account.report_invoice_with_payments"

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data=data)

        docs = res.get("docs")
        invoice_payload = None
        if docs:
            # render_invoice() returns dict {"header": {...}, "detail": [...]}
            # or None when CUCU data does not exist yet.
            invoice_payload = docs.render_invoice()

        # Fallback when CUCU/SIN data is not available
        if not invoice_payload:
            res["header"] = {}
            res["detail"] = []
            res["is_valid"] = False
            return res

        res["header"] = invoice_payload.get("header", {})
        res["detail"] = invoice_payload.get("detail", [])
        res["is_valid"] = bool(getattr(docs, "sin_code_state", False))
        return res
