# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMoveLineDebitCredit(models.Model):
    _inherit = "account.move.line"

    return_product = fields.Boolean(
        string="Devolver producto",
        default=False,
        help="Marca esta línea como producto a devolver (returnProduct: true en SIAT). "
             "Solo cambia la cantidad, no el precio.",
    )
