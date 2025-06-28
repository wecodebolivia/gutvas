# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


# Record the net weight of the order line
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'product_id.weight', 'product_uom', 'product_uom_qty')
    def _compute_weight(self):
        for line in self:
            weight_unit = 0
            weight = 0
            if line.product_id and line.product_id.weight and line.product_uom:
                try:
                    #     todo: 会算两次，第二次会报错？？？
                    weight_unit = line.product_id.weight / line.product_uom.factor
                    weight = (weight_unit * line.product_uom_qty)
                except:
                    pass
            line.write({
                'weight_unit': weight_unit,
                'weight': weight,
            })


    # 显示的单位，影响性能暂时不使用
    # weight_uom_name = fields.Char(string='Weight Measure', related='product_id.weight_uom_id.name', readonly=True)
    # 调整，根据 delivery 模块，将 weight 作为 该行合计，weight_unit 作为该单位的
    # weight_unit = fields.Float(string='Weight Unit', compute='_compute_weight', digits=('Stock Weight'), store=True)
    weight_unit = fields.Float(string='Weight Unit', digits='Stock Weight', store=True, readonly=True, copy=False,
                               compute='_compute_weight')
    weight = fields.Float(string='Weight Subtotal', digits='Stock Weight', store=True, readonly=True, copy=False,
                          compute='_compute_weight')

    def _set_weight(self):
        for rec in self:
            if rec.product_id and rec.weight_unit:
                try:
                    rec.product_id.weight = rec.weight_unit * rec.product_uom.factor
                except:
                    rec.product_id.weight = rec.weight_unit
