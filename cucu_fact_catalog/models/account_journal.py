from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"
    payment_method = fields.Many2one("cucu.catalogs.payment.method")
