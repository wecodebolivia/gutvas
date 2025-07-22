from odoo import models, fields


class CucuLog(models.Model):
    _name = "cucu.log"
    _description = "Cucu Log"
    _order = "id"

    type_event = fields.Char("Type Event")
    json_response = fields.Text("Response")

    invoice_id = fields.Many2one("cucu.invoice", string="Invoice")
