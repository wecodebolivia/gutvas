# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_weight = fields.Float(
        string='Peso Total',
        compute='_compute_total_weight',
        store=True,
        digits='Stock Weight',
        help='Peso total de todos los productos en esta orden de venta (cantidad × peso unitario)'
    )

    @api.depends('order_line.product_id', 'order_line.product_uom_qty')
    def _compute_total_weight(self):
        """Calcula el peso total sumando (cantidad × peso) de cada línea."""
        for order in self:
            total = 0.0
            for line in order.order_line:
                if line.product_id:
                    # El peso del producto está en product.weight
                    # Multiplicamos por la cantidad pedida
                    product_weight = line.product_id.weight or 0.0
                    total += product_weight * line.product_uom_qty
            order.total_weight = total
