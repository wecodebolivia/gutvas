from odoo import models, fields


class Product(models.Model):
    _inherit = "product.product"

    sin_ok = fields.Boolean("Sin Ok", related="product_tmpl_id.sin_ok", default=False)
    unit_measure_id = fields.Many2one(
        related="product_tmpl_id.unit_measure_id", string="Unidad de medida"
    )
    unit_measure_description = fields.Char(
        "Unit measure description", related="product_tmpl_id.unit_measure_description"
    )
    code_product_sin_id = fields.Many2one(
        related="product_tmpl_id.code_product_sin_id", string="Code Product Sin"
    )
    sin_code_product = fields.Char(
        "Code product", related="product_tmpl_id.sin_code_product"
    )
    sin_code_type = fields.Char("Code type", related="product_tmpl_id.sin_code_type")
    number_serial = fields.Char(
        "Number serial", related="product_tmpl_id.number_serial"
    )
    number_imei = fields.Char("Number imei", related="product_tmpl_id.number_imei")

    code_activity_sin_id = fields.Many2one(
        related="product_tmpl_id.code_activity_sin_id", string="Code Activity Sin"
    )

    code_type_activity = fields.Char(
        related="code_activity_sin_id.code_type", store=True
    )
