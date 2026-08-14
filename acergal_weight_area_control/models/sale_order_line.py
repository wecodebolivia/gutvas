from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    weight_area_enabled = fields.Boolean(related='product_template_id.weight_area_control')
    weight_area_estimated_kg = fields.Float(
        string='Kg equivalentes estimados', compute='_compute_weight_area_estimated_kg',
        digits='Product Unit of Measure'
    )

    @api.depends('product_uom_qty', 'product_template_id.factor_kg_m_standard')
    def _compute_weight_area_estimated_kg(self):
        for line in self:
            line.weight_area_estimated_kg = (
                line.product_uom_qty * line.product_template_id.factor_kg_m_standard
                if line.weight_area_enabled else 0.0
            )
