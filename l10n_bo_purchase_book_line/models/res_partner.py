# l10n_bo_purchase_book_line/models/res_partner.py
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    lc_razon_social = fields.Char(string='Razón Social (Libro de Compras)')
    lc_nit = fields.Char(string='NIT (Libro de Compras)')
