from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_partner(self):
        res = super()._loader_params_res_partner()
        add_fields = [
            "is_sin",
            "nit_client",
            "client_code",
            "reason_social",
            "complement",
            "cucu_email",
            "nit_valid",
            "doc_id",
        ]
        for field in add_fields:
            res["search_params"]["fields"].append(field)
        return res

    def get_pos_ui_documents(self):
        documents = self.env["cucu.catalogs.documents"].search_read(
            fields=["code_type", "description"],
            domain=[("code_type", "!=", "")],
        )
        return documents
