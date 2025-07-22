from odoo import models, fields, api


class AccountMoveCancel(models.TransientModel):
    _name = "account.move.cancel"
    _description = "Account Move Cancel"

    code_type_motive = fields.Many2one("cucu.catalogs.cancel")
    invoice_code = fields.Char("Code invoice")
    number_invoice = fields.Char("Number invoice")
    cucu_email = fields.Char("Email")
    siat_code_state = fields.Char("Siat code state", default=0)
    branch_id_api = fields.Integer("Branch Id")
    pos_id_api = fields.Integer("Pos Id")

    @api.model
    def default_get(self, fields_list):
        res = super(AccountMoveCancel, self).default_get(fields_list)
        account_move = self.env["account.move"].browse(self._context.get("active_id"))
        res.update(
            {
                "code_type_motive": self.env["cucu.catalogs.cancel"].search(
                    [("code_type", "=", "1"), ("company_id", "=", self.env.company.id)]
                ),
                "invoice_code": account_move.invoice_code,
                "number_invoice": account_move.invoice_number,
                "cucu_email": account_move.client_email,
                "siat_code_state": account_move.sin_description_status,
                "branch_id_api": account_move.pos_id.branch_id.branch_id,
                "pos_id_api": account_move.pos_id.cucu_pos_id.pos_id,
            }
        )
        return res

    def handle_revert_cancel_invoice(self, is_revert=False):
        account_move = self.env["account.move"].browse(self._context.get("active_id"))
        doc_sector = account_move.pos_id.doc_sector
        params = {
            "posId": self.pos_id_api,
            "branchId": self.branch_id_api,
            "invoiceCode": self.invoice_code,
            "codeMotive": self.code_type_motive.code_type,
            "invoiceNumber": self.number_invoice,
            "docSector": str(doc_sector),
            "clientEmail": self.cucu_email,
            "is_revert": is_revert,
        }
        res = account_move.pos_id.manager_id.service_cancel_invoice(params)
        if res["siatCodeState"] == 905 and not is_revert:
            account_move.print_log(f"Factura anulada: -> {self.number_invoice}")
            return account_move.update_cancel_invoice(res)
        if res["siatCodeState"] == 907 and is_revert:
            account_move.print_log(f"Factura revertida: -> {self.number_invoice}")
            return account_move.update_cancel_invoice(res)
        else:
            account_move.print_log(f"Error al anular factura: -> {self.number_invoice}")

    def handle_create_cancel(self):
        self.handle_revert_cancel_invoice()

    def handle_revert_cancel(self):
        self.handle_revert_cancel_invoice(True)

    def handle_send_invoice(self):
        account_move = self.env["account.move"].browse(self._context.get("active_id"))
        params = {
            "invoiceCode": self.invoice_code,
            "sendEmail": self.cucu_email,
        }
        res = account_move.pos_id.manager_id.send_email(**params)
        account_move.print_log(
            f"Factura anulada: -> {self.number_invoice} {res['cuf']}"
        )
