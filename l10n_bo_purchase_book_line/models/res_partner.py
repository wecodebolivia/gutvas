# l10n_bo_purchase_book_line/models/res_partner.py

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campos adicionales para el Libro de Compras
    lc_razon_social = fields.Char(string='Razón Social para Libro de Compras')
    lc_nit = fields.Char(string='NIT para Libro de Compras')
