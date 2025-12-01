from odoo import models, fields, api
from ..lib.service_single import (
    service_login,
    get_service_branchs,
    get_service_pos_regenerate,
    get_service_catalogs,
    send_email,
    send_invoice,
    send_status_invoice,
    send_cancel_invoice,
    send_revert_invoice,
)
from ..lib.string_utils import valid_token
from odoo.exceptions import ValidationError

from ..lib import const


def get_token(**params):
    res = service_login(**params)
    return res["data"]["token"]


def create_token_init(vals):
    body = {
        "username": vals["username"],
        "password": vals["password"],
        "host": vals["host"],
    }
    return get_token(**body)


class ApiManagerUser(models.Model):
    _name = "cucu.manager"
    _description = "Api manager user"
    _rec_name = "username"
    _inherit = ["mail.thread"]

    host = fields.Char(string="Url", required=True)
    username = fields.Char(string="Username", required=True)
    password = fields.Char(string="Password", required=True)
    token = fields.Char(string="Token")
    doc_sector_id = fields.Selection(const.CODE_DOC_SECTOR, "Doc Sector", default="1")
    is_electronic = fields.Boolean("Is Electronic", default=True)
    is_ticket = fields.Boolean(string="Is Ticket", default=False)
    is_send_email = fields.Boolean(string="Is Send Email", default=False)

    exchange_rate = fields.Float(string="Exchange Rate", default=0.0)

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    branch_ids = fields.One2many("cucu.branch.office", "manager_id", string="Branch")
    partner_id = fields.Many2one(
        "res.partner", string="Partner", default=lambda self: self.env.user.id
    )

    _sql_constraints = [("username_unique", "unique(username)", "username exist")]

    def to_json(self):
        if self.username and self.password and self.host:
            return {
                "host": self.host,
                "username": self.username,
                "password": self.password,
                "isElectronic": self.is_electronic,
                "docSector": self.doc_sector_id,
                "isSendEmail": self.is_send_email,
            }
        raise ValidationError("CONFIG LOGIN")

    def sync_token(self):
        token_value = self.token
        if not token_value or valid_token(token_value):
            # Solo crear nuevo token si no existe o ha expirado
            token_value = get_token(**self.to_json())
            self.write({"token": token_value})
        return token_value

    def create_token_user(self):
        return get_token(**self.to_json())

    def get_params_with_token(self):
        params = self.to_json()
        params["token"] = self.sync_token()
        return params

    @api.model
    def create(self, vals):
        if vals.get("username") and vals.get("password") and vals.get("host"):
            vals["token"] = create_token_init(vals)
        return super().create(vals)

    def _get_message(self, message, type_message="success"):
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success",
                "message": message,
                "sticky": False,
                "type": type_message,
            },
        }

    def get_message_ok(self, message):
        return self._get_message(message, "success")

    def get_message_danger(self, message):
        return self._get_message(message, "danger")

    def get_message_warning(self, message):
        return self._get_message(message, "warning")

    def token_renew(self):
        token_value = self.create_token_user()
        self.write({"token": token_value})

    def sync_branch_office(self):
        # params = self.to_json()
        params = self.get_params_with_token()
        res = get_service_branchs(**params)
        return res["data"]

    def sync_pos(self, branch_id):
        # params = self.to_json()
        params = self.get_params_with_token()
        params["branchId"] = branch_id
        res = get_service_pos_regenerate(**params)
        return res["data"]

    def action_sync_branch_office(self):
        res = self.sync_branch_office()
        for branch in res:
            branch["manager_id"] = self.id
        self.env["cucu.branch.office"].create_branchs(res)

    def open_view_cucu_branch(self):
        return {
            "name": "Branch Office",
            "type": "ir.actions.act_window",
            "res_model": "cucu.branch.office",
            "view_mode": "list,form",
            "context": {
                "default_manager_id": self.id,
            },
            "target": "current",
            "domain": [("manager_id", "=", self.id)],
        }

    def sync_catalogs(self):
        # params = self.to_json()
        params = self.get_params_with_token()
        params["posId"] = 1
        params["branchId"] = 1
        res = get_service_catalogs(**params)
        return res["data"]

    def sync_catalog(self):
        sync_catalog = self.sync_catalogs()
        for model_name, catalog_key in const.CATALOGS_MAP.items():
            self.env[model_name].create_catalog(sync_catalog[catalog_key])
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Éxito",
                "message": "CATALOG SYNC OK",
                "sticky": True,
            },
        }

    def send_email(self, **data):
        # params = self.to_json()
        params = self.get_params_with_token()
        body = {
            **params,
            **data,
            "subject": "CORREO ENVIADO AUTOMATICAMENTE",
        }
        res = send_email(**body)
        return res["data"]

    def send_invoice(self, **data):
        # params = self.to_json()
        params = self.get_params_with_token()
        body = {**params, **data}
        res = send_invoice(**body)
        if self.is_send_email:
            email_body = {
                "invoiceCode": res["data"]["invoiceCode"],
                "sendEmail": data["clientEmail"],
            }
            self.send_email(**email_body)
        return res["data"]

    def send_status_invoice(self, data, doc_sector):
        # params = self.to_json()
        params = self.get_params_with_token()
        body = {**params, **data, "docSector": str(doc_sector)}
        res = send_status_invoice(**body)
        return res["data"]

    def service_cancel_invoice(self, params):
        # body = {**params, **self.to_json()}
        body = {**params, **self.get_params_with_token()}
        if not params.get("is_revert", False):
            res = send_cancel_invoice(**body)
        else:
            res = send_revert_invoice(**body)
        if self.is_send_email:
            email_body = {
                "invoiceCode": params["invoiceCode"],
                "sendEmail": params["clientEmail"],
            }
            self.send_email(**email_body)
        return res["data"]
