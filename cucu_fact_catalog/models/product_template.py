from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = "Cucu Products"

    sin_ok = fields.Boolean("Product Sin", default=False, tracking=True)

    unit_measure_id = fields.Many2one(
        "cucu.catalogs.unit.measure", string="Unidad de medida"
    )
    unit_measure_description = fields.Char("Unidad medida descripcion")
    code_product_sin_id = fields.Many2one(
        "cucu.catalogs.product.service", string="Code Product Sin"
    )
    code_activity_sin_id = fields.Many2one(
        "cucu.catalogs.activities", string="Code Activity Sin"
    )
    sin_code_product = fields.Char("Code product")
    sin_code_type = fields.Char("Code type")
    number_serial = fields.Char("Number serial")
    number_imei = fields.Char("Number imei")
    code_type_activity = fields.Char(
        related="code_activity_sin_id.code_type", store=True
    )

    @api.model
    def default_get(self, fields):
        defaults = super().default_get(fields)
        default_activity = self.env["cucu.catalogs.activities"].search(
            [("code_type_activity", "=", "P")], limit=1
        )
        if default_activity:
            defaults["code_activity_sin_id"] = default_activity.id
        return defaults

    @api.model
    def create(self, vals):
        if vals.get("code_product_sin_id", False) and vals.get("sin_ok", False):
            code_product_sin_id = self._search_product_service(
                vals["code_product_sin_id"]
            )
            code_product = code_product_sin_id.code_product
            code_type = code_product_sin_id.code_type
            unit_measure = (
                self._search_unit_measure(vals["unit_measure_id"])
                if vals.get("unit_measure_id") is not None
                else self.unit_measure_id
            )
            vals["unit_measure_description"] = unit_measure["description"]
            vals["sin_code_product"] = code_product
            vals["sin_code_type"] = code_type
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        if vals.get("sin_ok", False):
            code_product_sin_id = (
                self._search_product_service(vals["code_product_sin_id"])
                if vals.get("code_product_sin_id") is not None
                else self.code_product_sin_id
            )
            code_product = code_product_sin_id.code_product
            code_type = code_product_sin_id.code_type
            vals["sin_code_product"] = code_product
            vals["sin_code_type"] = code_type
            unit_measure = (
                self._search_unit_measure(vals["unit_measure_id"])
                if vals.get("unit_measure_id") is not None
                else self.unit_measure_id
            )
            vals["unit_measure_description"] = unit_measure["description"]
            self.env["product.product"].search(
                [("product_tmpl_id", "=", self.id)]
            ).write(
                {
                    "sin_ok": vals.get("sin_ok", False) or self.sin_ok,
                    "unit_measure_id": unit_measure.id,
                    "unit_measure_description": unit_measure["description"],
                    "sin_code_product": code_product or self.sin_code_product,
                    "sin_code_type": code_type or self.sin_code_type,
                }
            )
        return super(ProductTemplate, self).write(vals)

    def _search_product_service(self, product_sin_id):
        return self.env["cucu.catalogs.product.service"].search(
            [("id", "=", product_sin_id)]
        )

    def _search_unit_measure(self, unit_measure_id):
        return self.env["cucu.catalogs.unit.measure"].search(
            [("id", "=", unit_measure_id)]
        )

    def get_data_detail_line(self):
        if not self.sin_code_product:
            product = self.env["product.product"].search(
                [("product_tmpl_id", "=", self.id)], limit=1
            )
            code_type = product.sin_code_type
            code_product = product.sin_code_product
            unit_measure = product.unit_measure_id.code_type
            sin = product.sin_ok
            imei = product.number_imei or None
            serial = product.number_serial or None
        else:
            code_type = self.sin_code_type
            code_product = self.sin_code_product
            unit_measure = self.unit_measure_id.code_type
            imei = self.number_imei or None
            serial = self.number_serial or None
            sin = self.sin_ok
        if sin:
            return {
                "activityEconomic": code_type,
                "codeProductSin": code_product,
                "unitMeasure": unit_measure,
                "numberSerial": serial,
                "numberImei": imei,
                "codeProduct": self.default_code,
                "unitMeasureDescription": self.unit_measure_description,
            }
        raise ValidationError(f"Product invoice not SIN {self.name}")
