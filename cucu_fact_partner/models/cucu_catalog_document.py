from odoo import models, fields


class CucuCatalogsDocuments(models.Model):
    _name = "cucu.catalogs.documents"
    _rec_name = "description"
    _order = "id"

    code_type = fields.Char("Code type")
    description = fields.Char("Description")
