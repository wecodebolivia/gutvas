# -*- coding: utf-8 -*-
###################################################################################
# Copyright (c) 2021-Present cucu | soluciones digitales (https://cucu.bo)
###################################################################################

from odoo import models, fields, api
from ..lib.date_utils import convert_date_str, convert_date_event
from odoo.exceptions import ValidationError


def _join_invoices(arr_invoices):
    invoices = arr_invoices
    return ",".join(invoices)


class CucuEvent(models.Model):
    _name = "cucu.event"

    description = fields.Char("Evento Descripcion")
    code_motive = fields.Many2one("cucu.catalogs.event.significant")
    description_motive = fields.Char("Motivo Descripcion")
    event_code = fields.Char("Codigo de Evento")
    date_init_event = fields.Datetime("Fecha Inicio de evento")
    date_end_event = fields.Datetime("Fecha Fin de evento")

    siat_status_description = fields.Char("Siat Status description")
    siat_status = fields.Integer("Siat Status")
    siat_code_reception = fields.Char("Siat Code Reception")

    siat_reception_code = fields.Char("Codigo de Recepcion Siat")
    cuf_event = fields.Char("Cuf evento")
    control_code_event = fields.Char("Codigo de control envento")
    cafc = fields.Char("cafc")
    pos_config_id = fields.Many2one("pos.config", "Pos")
    invoices_code = fields.Char("Invoices")
    pos_id = fields.Integer("Pos Id")
    branch_id = fields.Integer("Branch")

    is_save = fields.Boolean("Save", default=False)
    is_offline = fields.Boolean("Offline", default=False)
    is_online = fields.Boolean("Online", default=False)

    is_rate = fields.Boolean("Is Rate", default=False)
    is_free_zone = fields.Boolean("Is Free Zone", default=False)
    company_id = fields.Many2one("res.company", "Company")

    @api.model
    def create(self, vals_list):
        vals_list["is_offline"] = True
        vals_list["is_save"] = True
        vals_list["is_online"] = False
        return super(CucuEvent, self).create(vals_list)

    def _get_params(self):
        pos_config = self.pos_config_id.cucu_pos_id
        pos_id = pos_config.pos_id
        branch_id = pos_config.branch_id.branch_id
        date_start = convert_date_event(self.date_init_event, self._get_utc())
        date_end = convert_date_event(self.date_end_event, self._get_utc())
        return {
            "posId": pos_id,
            "branchId": branch_id,
            "description": self.description,
            "codeMotive": self.code_motive.code_type,
            "dateInitEvent": date_start,
            "dateEndEvent": date_end,
        }

    def get_create_event(self):
        params = self._get_params()
        data = self.env["cucu.core"].create_event(**params)
        self.write(
            {
                "description": data["description"],
                "description_motive": data["descriptionMotive"],
                "date_init_event": convert_date_str(data["dateInitEvent"]),
                "date_end_event": convert_date_str(data["dateEndEvent"]),
                "siat_reception_code": data["siatReceptionCode"],
                "cuf_event": data["cufEvent"],
                "event_code": data["eventCode"],
                "control_code_event": data["controlCodeEvent"],
                "cafc": data["cafc"],
                "is_offline": False,
                "is_online": True,
                "pos_id": params["posId"],
                "branch_id": params["branchId"],
                "company_id": self.env.company.id,
            }
        )

    def get_end_event(self):
        params = self._get_params()
        account_move = self.env["account.move"]
        if not account_move.count_pending(**params):
            raise ValidationError("NOT INVOICES PENDING")

        body = {**params, "eventCode": self.event_code}
        data = self.env["cucu.core"].end_event(**body)
        if data[0]["siatStatus"] == 908:
            vals_cucu = data[0]
            self.write(
                {
                    "invoices_code": _join_invoices(vals_cucu["crc32"]),
                    "siat_status_description": vals_cucu["siatStatusDescription"],
                    "siat_status": vals_cucu["siatStatus"],
                    "siat_code_reception": vals_cucu["siatCodeReception"],
                    "is_offline": False,
                    "is_online": False,
                }
            )
            return self.env["account.move"].update_invoice_event(
                vals_cucu["crc32"], vals_cucu["siatCodeReception"]
            )

    def _get_utc(self):
        return self._context.get("tz") or self.env.user.tz or "UTC"
