# -*- coding: utf-8 -*-
import logging
import requests

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class AccountMoveDebitCredit(models.Model):
    _inherit = "account.move"

    is_sin_debit_credit = fields.Boolean(
        string="Emitir Nota D/C SIAT",
        default=False,
        tracking=True,
        help="Activa la emisión de Nota de Débito/Crédito electrónica hacia SIAT para esta factura rectificada.",
    )

    # ------------------------------------------------------------------ #
    #  Validación: solo aplica a facturas rectificadas con origen emitido  #
    # ------------------------------------------------------------------ #
    @api.onchange("is_sin_debit_credit")
    def _onchange_is_sin_debit_credit(self):
        if not self.is_sin_debit_credit:
            return
        if self.move_type != "out_refund":
            self.is_sin_debit_credit = False
            raise ValidationError(
                "La emisión de Nota D/C SIAT solo aplica a facturas rectificadas (notas de crédito)."
            )
        origin = self.reversed_move_id
        if not origin:
            self.is_sin_debit_credit = False
            raise ValidationError(
                "No se encontró la factura origen. Asegúrate de que esta nota esté vinculada a una factura."
            )
        if origin.sin_description_status not in ("VALIDADA", "VALIDA"):
            self.is_sin_debit_credit = False
            raise ValidationError(
                f"La factura origen debe estar VALIDADA en SIAT. Estado actual: {origin.sin_description_status}"
            )

    # ------------------------------------------------------------------ #
    #  Construcción del payload para /api/v1/invoice/electronic/debit     #
    # ------------------------------------------------------------------ #
    def _build_debit_credit_payload(self):
        """Construye el payload para el endpoint de Nota D/C de cucu.ai."""
        self.ensure_one()
        origin = self.reversed_move_id
        if not origin:
            raise UserError("No se encontró la factura origen para construir la Nota D/C.")

        # Datos de cabecera: se toman de la factura ORIGEN ya emitida
        pos_cucu = origin.pos_id.cucu_pos_id
        if not pos_cucu:
            raise UserError("La factura origen no tiene un POS cucu configurado.")

        user_pos = origin.invoice_user_id.partner_id.name
        pos_id = pos_cucu.pos_id
        invoice_number = int(origin.invoice_number) if origin.invoice_number else 0
        invoice_code = origin.invoice_code or ""

        # Token del usuario: recuperado desde el manager del POS
        manager = origin.pos_id.manager_id
        token = getattr(manager, "token", None) or getattr(manager, "api_token", None)

        # Detalle de líneas
        detail = []
        for idx, line in enumerate(self.invoice_line_ids.filtered(lambda l: l.product_id), start=1):
            product = line.product_id
            tmpl = product.product_tmpl_id

            # Datos del catálogo SIN (reutiliza el método del core)
            product_data = tmpl.get_data_detail_line()

            qty = abs(line.quantity)  # las notas de crédito tienen qty negativa en Odoo
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

        payload = {
            "posId": pos_id,
            "invoiceNumber": invoice_number,
            "invoiceCode": invoice_code,
            "userPos": user_pos,
            "detailInvoice": detail,
        }
        return payload, token

    # ------------------------------------------------------------------ #
    #  Acción principal: botón "Emitir Nota D/C SIAT"                     #
    # ------------------------------------------------------------------ #
    def action_send_debit_credit_siat(self):
        """Envía la Nota de Débito/Crédito al endpoint de cucu.ai y guarda la respuesta."""
        self.ensure_one()

        if not self.is_sin_debit_credit:
            raise UserError("Activa primero la opción 'Emitir Nota D/C SIAT'.")

        payload, token = self._build_debit_credit_payload()

        # URL base del manager
        manager = self.reversed_move_id.pos_id.manager_id
        base_url = getattr(manager, "url", None) or getattr(manager, "host", None) or ""
        base_url = base_url.rstrip("/")
        endpoint = f"{base_url}/api/v1/invoice/electronic/debit"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        _logger.info("[cucu_fact_debit_credit] Enviando Nota D/C a %s | payload: %s", endpoint, payload)

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            res_json = response.json()
        except requests.exceptions.Timeout:
            raise UserError("Timeout al conectar con el servicio de facturación cucu. Intenta nuevamente.")
        except requests.exceptions.ConnectionError as e:
            raise UserError(f"No se pudo conectar con el servicio cucu: {e}")
        except requests.exceptions.HTTPError as e:
            raise UserError(f"Error HTTP al emitir la Nota D/C: {e}\nRespuesta: {response.text}")
        except ValueError:
            raise UserError(f"Respuesta inesperada del servidor cucu: {response.text}")

        _logger.info("[cucu_fact_debit_credit] Respuesta cucu: %s", res_json)

        # Guardar los campos SIAT en la nota de crédito
        self.write({
            "sin_code_state": res_json.get("siatCodeState", 0),
            "sin_code_reception": res_json.get("siatCodeReception", "0000"),
            "sin_description_status": res_json.get("siatDescriptionStatus", "Not invoice"),
            "invoice_code": res_json.get("invoiceCode", ""),
            "invoice_number": str(res_json.get("invoiceNumber", "")),
        })

        self.message_post(
            body=f"Nota D/C emitida al SIAT. "
                 f"Estado: {res_json.get('siatDescriptionStatus')} | "
                 f"Recepción: {res_json.get('siatCodeReception')} | "
                 f"Nro. Factura: {res_json.get('invoiceNumber')}"
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Nota D/C SIAT emitida",
                "message": f"Estado: {res_json.get('siatDescriptionStatus')} | Nro: {res_json.get('invoiceNumber')}",
                "type": "success",
                "sticky": False,
            },
        }
