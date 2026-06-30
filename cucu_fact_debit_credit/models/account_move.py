# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class AccountMoveDebitCredit(models.Model):
    _inherit = "account.move"

    is_sin_debit_credit = fields.Boolean(
        string="Emitir Nota D/C SIAT",
        default=False,
        tracking=True,
        help="Activa la emisión de Nota de Débito/Crédito electrónica hacia SIAT.",
    )

    origin_move_id = fields.Many2one(
        comodel_name="account.move",
        string="Factura Origen (SIAT)",
        domain="[('move_type', 'in', ['out_invoice', 'in_invoice']), ('sin_description_status', 'in', ['VALIDADA', 'VALIDA'])]",
        tracking=True,
        help="Factura original ya validada en SIAT sobre la que se emite esta Nota D/C.",
    )

    @api.onchange("is_sin_debit_credit")
    def _onchange_is_sin_debit_credit(self):
        if not self.is_sin_debit_credit:
            return
        if self.move_type != "out_refund":
            self.is_sin_debit_credit = False
            raise ValidationError(
                "La emisión de Nota D/C SIAT solo aplica a facturas rectificadas (notas de crédito)."
            )

    @api.onchange("origin_move_id")
    def _onchange_origin_move_id(self):
        if not self.origin_move_id:
            return
        if self.origin_move_id.sin_description_status not in ("VALIDADA", "VALIDA"):
            self.origin_move_id = False
            raise ValidationError(
                f"La factura origen debe estar VALIDADA en SIAT. "
                f"Estado actual: {self.origin_move_id.sin_description_status}"
            )

    def _build_debit_credit_payload(self):
        self.ensure_one()
        origin = self.origin_move_id
        if not origin:
            raise UserError("Selecciona la Factura Origen (SIAT) antes de emitir la Nota D/C.")

        pos_cucu = origin.pos_id.cucu_pos_id
        if not pos_cucu:
            raise UserError("La factura origen no tiene un POS cucu configurado.")

        manager = origin.pos_id.manager_id
        if not manager:
            raise UserError("No se encontró el ApiManager (cucu.manager) del POS de origen.")

        user_pos = origin.invoice_user_id.partner_id.name
        pos_id = pos_cucu.pos_id
        invoice_number = int(origin.invoice_number) if origin.invoice_number else 0
        invoice_code = origin.invoice_code or ""

        detail = []
        for idx, line in enumerate(
            self.invoice_line_ids.filtered(lambda l: l.product_id), start=1
        ):
            product = line.product_id
            tmpl = product.product_tmpl_id
            product_data = tmpl.get_data_detail_line()

            qty = abs(line.quantity)
            price_unit = line.price_unit
            discount = qty * price_unit * (line.discount / 100) if line.discount else 0.0
            sub_total = round(qty * price_unit - discount, 2)

            detail.append({
                "detailId": idx,
                "activityEconomic": str(product_data.get("activityEconomic", "")),
                "codeProductSin": str(product_data.get("codeProductSin", "")),
                "codeProduct": product.default_code or "",
                "description": (line.name or tmpl.name)[:150],
                "qty": qty,
                "unitMeasure": product_data.get("unitMeasure", 62),
                "priceUnit": price_unit,
                "amountDiscount": round(discount, 2),
                "subTotal": sub_total,
                "returnProduct": line.return_product,
            })

        # docSector="24" -> manager.send_invoice() construye /debit y usa cucukey: Token {token}
        payload = {
            "posId": pos_id,
            "invoiceNumber": invoice_number,
            "invoiceCode": invoice_code,
            "userPos": user_pos,
            "detailInvoice": detail,
            "docSector": "24",
        }
        return payload, manager

    def action_send_debit_credit_siat(self):
        self.ensure_one()

        if not self.is_sin_debit_credit:
            raise UserError("Activa primero la opción 'Emitir Nota D/C SIAT'.")

        payload, manager = self._build_debit_credit_payload()

        _logger.info("[cucu_fact_debit_credit] Enviando Nota D/C | payload: %s", payload)

        # manager.send_invoice() del core:
        # - header: {"cucukey": "Token {token}"}  ← corrige el 401
        # - URL:    {host}/api/v1/invoice/electronic/debit
        # - renueva JWT automáticamente si expiró
        res = manager.send_invoice(**payload)

        _logger.info("[cucu_fact_debit_credit] Respuesta cucu: %s", res)

        self.write({
            "sin_code_state": res.get("siatCodeState", 0),
            "sin_code_reception": res.get("siatCodeReception", "0000"),
            "sin_description_status": res.get("siatDescriptionStatus", "Not invoice"),
            "invoice_code": res.get("invoiceCode", ""),
            "invoice_number": str(res.get("invoiceNumber", "")),
        })

        self.message_post(
            body=(
                f"Nota D/C emitida al SIAT. "
                f"Estado: {res.get('siatDescriptionStatus')} | "
                f"Recepción: {res.get('siatCodeReception')} | "
                f"Nro. Factura: {res.get('invoiceNumber')}"
            )
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Nota D/C SIAT emitida",
                "message": (
                    f"Estado: {res.get('siatDescriptionStatus')} | "
                    f"Nro: {res.get('invoiceNumber')}"
                ),
                "type": "success",
                "sticky": False,
            },
        }
