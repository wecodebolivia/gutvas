from odoo import models, fields
import json


def _update_sin_response(res):
    return {
        "sin_code_state": res["codigoEstado"],
        "sin_code_reception": res["codigoRecepcion"],
        "sin_description_status": res["codigoDescripcion"],
    }


class AccountMove(models.Model):
    _name = "cucu.invoice"
    _rec_name = "invoice_code"

    account_move_id = fields.Many2one("account.move", "Account Move")
    manager_id = fields.Many2one("cucu.manager", "Manager")
    payment_method_id = fields.Many2one("cucu.catalogs.payment.method")
    payment_method_code = fields.Char(
        string="Payment Method", related="payment_method_id.code_type"
    )

    partner_id = fields.Many2one(
        "res.partner", related="account_move_id.partner_id", string="Partner"
    )

    client_email = fields.Char(string="Client Email", related="partner_id.cucu_email")

    # Sin response
    sin_code_state = fields.Integer("Siat code state", default=0)
    sin_code_reception = fields.Char("Siat code reception", default="0000")
    sin_description_status = fields.Char(
        "Siat description status", default="Not invoice"
    )

    # Cucu params
    url_cucu = fields.Char("Invoice Url")
    exception_code = fields.Integer("Invoice Exception Code", size=1)
    qr_code = fields.Char("QR Code")
    branch_id = fields.Integer("Branch Id", tracking=True)
    pos_id = fields.Integer("Pos Id", tracking=True)
    invoice_code = fields.Char("Invoice code", tracking=True)
    date_emission = fields.Char("Date Emission")
    cuf = fields.Char("Cuf", tracking=True, default="")
    invoice_number = fields.Char("Invoice Number", tracking=True)
    nit_emissor = fields.Char("Nit")
    municipality = fields.Char("Municipality", tracking=True)
    is_offline = fields.Boolean("Is Offline", default=False, tracking=True)
    reason_social_emissor = fields.Char("Reason social")

    # amount totals
    amount_total = fields.Float("Amount total", tracking=True)
    amount_total_discount = fields.Float("Amount total discount")
    amount_subject_iva = fields.Float("Amount total discount")
    amount_gift_card = fields.Float("Amount Gift Card")
    amount_total_currency = fields.Float("Amount total currency")
    additional_discount = fields.Float("Additional Discount")

    invoice_xml = fields.Char("Invoice xml")
    invoice_json = fields.Char("Invoice json")
    observations = fields.Char("Observations")
    count_items = fields.Integer("Count items")

    exchange_rate = fields.Float("Exchange rate")
    amount_usd = fields.Float("Amount USD")

    card_number = fields.Char("Number card")

    amount_literal = fields.Char("Amount Literal")
    doc_sector = fields.Integer("Doc sector")
    company_id = fields.Many2one("res.company", "Company")
    log_ids = fields.One2many("cucu.log", "invoice_id", string="Logs")

    def _get_url_open(self, type_url="SIN"):
        if self.cuf:
            if type_url == "SIN":
                url = self.qr_code
            else:
                url = (
                    self.url_cucu
                    if type_url == "A4"
                    else f"{self.url_cucu}&type=ticket"
                )
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }

    def get_url_sin(self):
        return self._get_url_open()

    def get_url_a4(self):
        return self._get_url_open("A4")

    def get_url_ticket(self):
        return self._get_url_open("TICKET")

    def create_invoice(self, payload):
        invoice = payload["invoice"]  # Original Data
        data = payload["data"]
        json_invoice = json.loads(data["invoiceJson"])["cabecera"]
        manager_id = data["managerId"]
        host = manager_id.host
        doc_sector = int(invoice["docSector"])
        invoice = {
            "account_move_id": data["accountMoveId"],
            "manager_id": manager_id.id if manager_id else None,
            "payment_method_id": data["paymentMethodId"],
            "partner_id": data["partnerId"],
            "sin_code_state": data["siatCodeState"],
            "sin_code_reception": data["siatCodeReception"],
            "sin_description_status": data["siatDescriptionStatus"],
            "url_cucu": f"{host}{data['invoiceUrl']}",
            "exception_code": json_invoice["codigoExcepcion"],
            "qr_code": data["qrCode"],
            "branch_id": invoice["branchId"],
            "pos_id": invoice["posId"],
            "invoice_code": data["invoiceCode"],
            "date_emission": data["dateEmission"],
            "cuf": data["cuf"],
            "invoice_number": str(data["invoiceNumber"]),
            "nit_emissor": str(data["nitEmissor"]),
            "municipality": json_invoice["municipio"],
            "is_offline": data["siatCodeState"] == 901,
            "reason_social_emissor": json_invoice["nombreRazonSocial"],
            "invoice_xml": data["invoiceXml"],
            "invoice_json": data["invoiceJson"],
            "observations": data.get("observations", None),
            "count_items": data["countItems"],
            "amount_usd": data.get("amountUsd", None),
            "amount_literal": data["amountLiteral"],
            "doc_sector": doc_sector,
            "company_id": self.env.company.id,
        }
        if doc_sector == 1:
            invoice["amount_total"] = json_invoice["montoTotal"]
            invoice["amount_subject_iva"] = json_invoice["montoTotalSujetoIva"]
            invoice["amount_gift_card"] = json_invoice["montoGiftCard"]
            invoice["amount_total_currency"] = json_invoice["montoTotalMoneda"]
            invoice["additional_discount"] = json_invoice["descuentoAdicional"]
            invoice["card_number"] = json_invoice["numeroTarjeta"]
            invoice_id = self.create([invoice])
            return invoice_id
        if doc_sector == 24:
            invoice["amount_total"] = json_invoice["montoTotalOriginal"]
            invoice["amount_total_discount"] = json_invoice[
                "montoDescuentoCreditoDebito"
            ]
            invoice["amount_subject_iva"] = json_invoice["montoEfectivoCreditoDebito"]
            invoice_id = self.create([invoice])
            return invoice_id

    def handle_cancel_invoice(self):
        pass

    def handle_status_invoice(self):
        data = {
            "invoiceCode": self.invoice_code,
            "invoiceNumber": self.invoice_number,
            "posId": self.pos_id,
            "branchId": self.branch_id,
        }
        res = self.manager_id.send_status_invoice(data, self.doc_sector)
        log = {
            "type_event": "STATUS",
            "json_response": json.dumps(res),
            "invoice_id": self.id,
        }
        self.write({"log_ids": [(0, 0, log)], **_update_sin_response(res)})
        self.account_move_id.write({**_update_sin_response(res)})
