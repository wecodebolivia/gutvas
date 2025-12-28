# -*- coding: utf-8 -*-
from odoo import api, models


class ReportCucuAccountInvoice(models.AbstractModel):
    _name = "report.cucu_fact_report.cucu_report_account"
    _description = "CUCU - Account Invoice Report (safe render)"
    _inherit = "report.account.report_invoice_with_payments"

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data=data)

        docs = res.get("docs")
        invoice_payload = None

        if docs:
            # render_invoice() devuelve dict o None
            invoice_payload = docs.render_invoice()

        if invoice_payload:
            res["header"] = invoice_payload.get("header", {}) or {}
            res["detail"] = invoice_payload.get("detail", []) or []
            res["is_valid"] = bool(getattr(docs, "sin_code_state", False))
        else:
            # Fallback: dejamos estructuras válidas (no reventar QWeb)
            res["header"] = {}
            res["detail"] = []
            res["is_valid"] = False

        return res
