# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    # Datos propios que usaremos en el Libro de Compras
    lc_nit = fields.Char(string="NIT", help="NIT usado en el Libro de Compras")
    lc_razon_social = fields.Char(string="Razón Social", help="Razón social para Libro de Compras")
