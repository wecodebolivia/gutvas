import logging

from ..lib import number_util
from odoo import models, fields, api
from odoo.exceptions import ValidationError

from ..lib.string_utils import string_to_json

_logger = logging.getLogger(__name__)

re_email = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
re_empty = r"[^\s]*"

DOC_SECTOR = {1: "COMPRA Y VENTA", 24: "NOTA DEBITO CREDITO"}


class AccountMove(models.Model):
    _inherit = "account.move"

    is_sin = fields.Boolean("Is SIN", default=False)

    pos_id = fields.Many2one(
        "pos.config",
        string="Point Of Sale",
        default=lambda self: self.env.user.pos_id.id,
    )

    doc_sector = fields.Selection(
        "Document Sector", related="pos_id.doc_sector", tracking=True
    )

    client_doc_id = fields.Many2one(
        related="partner_id.doc_id", string="Document type", default=None
    )
    client_nro_document = fields.Char(
        "Number Document", related="partner_id.nit_client", default=None
    )
    client_complement = fields.Char(
        "Complement", size=2, related="partner_id.complement", default=None
    )
    client_reason_social = fields.Char(
        "Reason social", related="partner_id.reason_social", default=None
    )
    client_email = fields.Char("Email", related="partner_id.cucu_email", default=None)

    invoice_id = fields.One2many("cucu.invoice", "account_move_id", string="Invoice")

    payment_method_id = fields.Many2one(
        "cucu.catalogs.payment.method", string="Cucu Catalog Payment Method Id"
    )
    payment_method_code = fields.Char(
        string="Cucu Catalog Payment Method Code Type",
        related="payment_method_id.code_type",
    )
    additional_discount = fields.Float("Additional Discount")
    amount_gift_card = fields.Float("Amount Gift Card")
    number_card = fields.Char("Number card")
    observations = fields.Char("Observations")
    invoice_xml = fields.Text(string="Invoice XML", compute="_compute_invoice_xml")
    invoice_json = fields.Text(string="Invoice JSON", compute="_compute_invoice_json")
    sin_code_state = fields.Integer("Siat code state", default=0, tracking=True)
    sin_code_reception = fields.Char(
        "Siat code reception", default="0000", tracking=True
    )
    sin_description_status = fields.Char(
        "Siat description status", default="Not invoice", tracking=True
    )
    invoice_code = fields.Char("Invoice code", tracking=True)
    invoice_number = fields.Char("Invoice Number", tracking=True)
    amount_usd = fields.Float("Amount USD")
    pos_session_id = fields.Many2one("pos.session", "Pos Session")

    @api.depends("invoice_id.invoice_xml")
    def _compute_invoice_xml(self):
        for record in self:
            record.invoice_xml = (
                record.invoice_id[:1].invoice_xml if record.invoice_id else False
            )

    @api.depends("invoice_id.invoice_json")
    def _compute_invoice_json(self):
        for record in self:
            record.invoice_json = (
                string_to_json(record.invoice_id[:1].invoice_json)
                if record.invoice_id
                else False
            )

    def _get_payment_method(self, type_method: str):
        if not self.payment_method_id:
            raise ValidationError("Select payment method")
        return type_method in self.payment_method_id.description

    @api.onchange("is_sin")
    def _get_is_sin_onchange(self):
        if self.is_sin and not any(
            [
                self.client_doc_id,
                self.client_nro_document,
                self.client_reason_social,
                self.client_email,
            ]
        ):
            self.is_sin = False
            raise ValidationError("CONFIG CLIENT")

    def print_log(self, message):
        self.message_post(body=message)

    def _get_header(self):
        if not self.partner_id:
            _logger.error("Client not select")
            raise ValidationError("Client not select config")
        partner = self.partner_id
        if not any(
            [
                partner.doc_id,
                partner.nit_client,
                partner.reason_social,
                partner.cucu_email,
            ]
        ):
            raise ValidationError("Select client not found to invoice")

        number_card = None
        # if self._get_payment_method("TARJETA"):
        #    number_card = self.number_card
        pos_id = self.pos_id.cucu_pos_id
        if not pos_id:
            raise ValidationError("Pos config manager not selected")
        client_data = {
            "userPos": self.invoice_user_id.partner_id.name,
            "numberCard": number_card,
            "clientNroDocument": partner.nit_client,
            "clientCode": partner.nit_client,
            "clientReasonSocial": partner.reason_social,
            "clientDocumentType": partner.doc_id.code_type,
            "clientEmail": partner.cucu_email,
            "clientCity": pos_id.branch_id.municipality,
            "posId": pos_id.pos_id,
            "branchId": pos_id.branch_id.branch_id,
            "typeInvoice": 1,
            "paramCurrency": 1,
            "dateEmission": None,
        }
        return {
            **client_data,
            **self.valid_type_document(),
            **self._get_params_header(),
        }

    def _get_amount_usd(self, amount, discount, gift):
        exchange_rate = self.pos_id.manager_id.exchange_rate
        if exchange_rate == 0:
            return None

        amount_usd = (
            round((amount - (discount + gift)) / exchange_rate, 2)
            if amount is not None
            else 0
        )
        return amount_usd or None

    def _get_params_header_order(self):
        order = self.pos_order_ids
        _logger.info("Pos Order Id: %s", order.id or "No order found")
        _logger.info(
            "Pos Order Cucu Catalog Payment Method Id: %s",
            order.catalog_id or "No catalog ID",
        )
        _logger.info(
            "Pos Order Cucu Catalog Payment Method Code Type: %s",
            order.catalog_code or "No catalog code",
        )
        if order:
            params = {
                "paramPaymentMethod": order.catalog_code or "1",
                "userPos": self.invoice_user_id.partner_id.name,
                "numberCard": order.card_number or None,
                "giftCard": order.gift_card or 0,
                "dateEmission": None,
                "additionalDiscount": order.additional_discount or 0,
                "observations": order.observations or None,
                "typeInvoice": 1,
                "paramCurrency": 1,
                "paymentMethodId": order.catalog_id or "1",
            }
            return params

    def _get_params_header_account(self):
        number_card = None
        if self._get_payment_method("TARJETA"):
            number_card = self.number_card
        return {
            "paramPaymentMethod": self.payment_method_id.code_type or 1,
            "userPos": self.invoice_user_id.partner_id.name,
            "typeInvoice": 1,
            "paramCurrency": 1,
            "numberCard": number_card,
            "giftCard": self.amount_gift_card or 0,
            "dateEmission": None,
            "additionalDiscount": self.additional_discount or 0,
            "observations": self.observations or None,
            "exchangeRate": self.pos_id.manager_id.exchange_rate or None,
        }

    def _get_params_header(self):
        order = self.pos_order_ids
        if order:
            return self._get_params_header_order()
        return self._get_params_header_account()

    def valid_type_document(self):
        client = self.partner_id
        doc_type = client.doc_id.code_type
        complement = client.complement if doc_type == "1" else None
        exception_code = 0 if doc_type != "5" or client.nit_valid else 1
        return {"exceptionCode": exception_code, "clientComplement": complement or None}

    def _pos_refund_params(self, type_sector: int):
        refund_data = {}
        if type_sector == 24 and self.pos_order_ids:
            move_refund = self.pos_order_ids.refunded_order_ids.account_move
            refund_data["invoiceCode"] = move_refund.invoice_code or self.invoice_code

            refund_data["invoiceNumber"] = (
                move_refund.invoice_number or self.invoice_number
            )
            refund_data["exceptionCode"] = 1
        else:
            refund_data["invoiceCode"] = self.invoice_code
            refund_data["invoiceNumber"] = self.invoice_number
            refund_data["exceptionCode"] = 1 if type_sector == 24 else 0
        return refund_data

    def create_invoice_sale(self, type_sector: int = 1):
        body = {
            **self._get_header(),
            "detailInvoice": self._get_detail_move_line(type_sector),
            "docSector": str(type_sector),
            "amountUsd": self._get_amount_usd(
                self._calculate_sub_total_price(),
                self.additional_discount,
                self.amount_gift_card,
            )
            or None,
            **self._pos_refund_params(type_sector),
        }
        res = self.pos_id.manager_id.send_invoice(**body)
        res["accountMoveId"] = self.id
        res["managerId"] = self.pos_id.manager_id
        res["paymentMethodId"] = "1"
        res["partnerId"] = self.partner_id.id
        invoice_id = self.env["cucu.invoice"].create_invoice(
            {"invoice": body, "data": res}
        )
        self.write(
            {
                "sin_code_state": res["siatCodeState"],
                "sin_code_reception": res["siatCodeReception"],
                "sin_description_status": res["siatDescriptionStatus"],
                "invoice_code": res["invoiceCode"],
                "invoice_number": str(res["invoiceNumber"]),
            }
        )
        self.write({"invoice_id": [(4, invoice_id.id)]})

    def create_invoice_account(self):
        account_move = self.env["account.move"].search([("id", "=", self.id)], limit=1)
        doc_sector = self.pos_id.doc_sector
        if doc_sector == "1":
            is_refund = (
                account_move.sin_description_status == "Not invoice"
                and account_move.is_sin
            )
            if is_refund and account_move.move_type in (
                "out_invoice",
                "out_refund",
                "in_invoice",
            ):
                return account_move.create_invoice_sale(1)
            if self.is_sin and self.sin_description_status in ["VALIDADA", "VALIDA"]:
                move = self.line_ids[0].move_id
                return move.create_invoice_sale(24)
        return None

    def _get_header_invoice(self):
        pass

    def _calculate_sub_total_price(self):
        line_product = self.invoice_line_ids
        price_subtotal = sum(line.price_subtotal for line in line_product)
        return price_subtotal

    def _get_detail_move_line(self, type_sector: int = 1):
        detail = []
        line_product = self.invoice_line_ids
        move_lines = self.env["account.move.line"].search([("move_id", "in", self.ids)])
        order = self.pos_order_ids
        for line in line_product:
            note = None
            discount = 0
            product = line.product_id.product_tmpl_id
            price_unit = 0
            if line in move_lines and product:
                discount = line.quantity * line.price_unit * (line.discount / 100)
                price_unit = line.price_unit
            if order and product:
                pos_order_line = self.env["pos.order.line"].search(
                    [
                        ("order_id", "=", order.id),
                        ("product_id", "=", line.product_id.id),
                    ],
                    limit=1,
                )
                note = (
                    pos_order_line.customer_note.strip().replace("\n", "")
                    if pos_order_line.customer_note
                    else None
                )
                if line.discount > 0:
                    discount = line.quantity * line.price_unit * (line.discount / 100)
                    price_unit = line.price_unit
                else:
                    price_unit = line.price_unit
            if product:
                product_data = product.get_data_detail_line()
                product_data["priceUnit"] = number_util.halfup_convert(price_unit)
                product_data["qty"] = line.quantity
                product_data["amountDiscount"] = number_util.halfup_convert(discount)
                product_data["codeProduct"] = line.product_id.default_code
                product_data["description"] = (
                    f"{line.name} ({note})" if note else line.name
                )
                if type_sector == 24:
                    product_data["detailId"] = 1
                    product_data["returnProduct"] = True
                detail.append(product_data)
        return detail

    def update_cancel_invoice(self, data):
        self.write(
            {
                "sin_code_state": data["siatCodeState"],
                "sin_description_status": data["siatDescriptionStatus"],
                # 'auto_post': False
            }
        )
        self.invoice_id[-1].write(
            {
                "sin_code_state": data["siatCodeState"],
                "sin_description_status": data["siatDescriptionStatus"],
            }
        )
        self.env.cr.commit()

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        first_sin_move = self.filtered(lambda m: m.is_sin)[:1]
        if first_sin_move and self.state != "invoiced":
            first_sin_move.create_invoice_account()
        return res

    def report_invoice_view(self, type_report="SIN"):
        return self.invoice_id._get_url_open(type_report)

    def action_report_invoice_sin(self):
        return self.report_invoice_view()

    def action_report_invoice_a4(self):
        return self.report_invoice_view("A4")

    def action_report_invoice_ticket(self):
        return self.report_invoice_view("TICKET")
