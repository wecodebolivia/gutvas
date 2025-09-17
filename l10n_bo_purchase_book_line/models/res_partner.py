# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Campos específicos para Libro de Compras (cuando el documento es compra)
    lc_purchase_book_name = fields.Char(string="Razón Social para Libro de Compras")
    lc_purchase_book_nit = fields.Char(string="NIT para Libro de Compras")
