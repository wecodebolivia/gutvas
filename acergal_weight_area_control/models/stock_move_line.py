from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    weight_area_enabled = fields.Boolean(related='product_id.product_tmpl_id.weight_area_control')
    weight_area_length_m = fields.Float(
        string='Longitud controlada (m)', compute='_compute_weight_area_values', store=True,
        digits='Product Unit of Measure'
    )
    weight_area_equivalent_kg = fields.Float(
        string='Kg equivalentes', compute='_compute_weight_area_values', store=True,
        digits='Product Unit of Measure'
    )
    weight_area_factor_kg_m = fields.Float(
        string='Factor aplicado (kg/m)', compute='_compute_weight_area_values', store=True,
        digits='Product Unit of Measure'
    )
    weight_area_direction = fields.Selection(
        [('in', 'Entrada'), ('out', 'Salida'), ('adjustment', 'Ajuste')],
        compute='_compute_weight_area_values', store=True
    )

    @api.depends('qty_done', 'quantity', 'product_uom_id', 'product_id', 'lot_id', 'picking_id.picking_type_id.code')
    def _compute_weight_area_values(self):
        for line in self:
            if not line.weight_area_enabled:
                line.weight_area_length_m = 0.0
                line.weight_area_factor_kg_m = 0.0
                line.weight_area_equivalent_kg = 0.0
                line.weight_area_direction = False
                continue
            qty = line.qty_done if 'qty_done' in line._fields else line.quantity
            line.weight_area_length_m = qty
            code = line.picking_id.picking_type_id.code
            direction = 'in' if code == 'incoming' else 'out' if code == 'outgoing' else 'adjustment'
            line.weight_area_direction = direction
            factor = line.lot_id.real_factor_kg_m or line.product_id.product_tmpl_id.factor_kg_m_standard
            line.weight_area_factor_kg_m = factor
            line.weight_area_equivalent_kg = qty * factor

    def _check_weight_area_availability(self):
        precision = self.env['uom.precision'].precision_get('Product Unit of Measure')
        for line in self.filtered(lambda row: row.weight_area_enabled and row.weight_area_direction == 'out'):
            if not line.lot_id or not line.lot_id.weight_area_initialized:
                raise ValidationError(_('Debe asignar un lote/rollo inicializado para el producto %s.') % line.product_id.display_name)
            remaining_m = line.lot_id.remaining_length_m
            remaining_kg = line.lot_id.remaining_weight_kg
            if float_compare(line.weight_area_length_m, remaining_m, precision_digits=precision) > 0:
                raise ValidationError(_('El rollo %s no dispone de metros suficientes.') % line.lot_id.name)
            if float_compare(line.weight_area_equivalent_kg, remaining_kg, precision_digits=precision) > 0:
                raise ValidationError(_('El rollo %s no dispone de kg equivalentes suficientes.') % line.lot_id.name)
