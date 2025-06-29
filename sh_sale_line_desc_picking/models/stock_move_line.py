# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api
from odoo.tools import float_is_zero


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self,vals):
        res = super(StockMove,self).create(vals)
        for rec in res:
            if rec.sale_line_id:
                rec.description_picking = rec.sale_line_id.name
        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    sh_so_line_desc_sml = fields.Char(
        related="move_id.name", string="Description")

    def _get_aggregated_product_quantities(self, **kwargs):
        """ Returns a dictionary of products (key = id+name+description+uom) and corresponding values of interest.

        Allows aggregation of data across separate move lines for the same product. This is expected to be useful
        in things such as delivery reports. Dict key is made as a combination of values we expect to want to group
        the products by (i.e. so data is not lost). This function purposely ignores lots/SNs because these are
        expected to already be properly grouped by line.

        returns: dictionary {product_id+name+description+uom: {product, name, description, qty_done, product_uom}, ...}
        """
        aggregated_move_lines = {}

        def get_aggregated_properties(move_line=False, move=False):
            move = move or move_line.move_id
            uom = move.product_uom or move_line.product_uom_id
            name = move.product_id.display_name
            description = move.description_picking
            if description == name or description == move.product_id.name:
                description = False
            product = move.product_id
            line_key = f'{product.id}_{product.display_name}_{description or ""}_{uom.id}'
            return (line_key, name, description, uom)

        # Loops to get backorders, backorders' backorders, and so and so...
        backorders = self.env['stock.picking']
        pickings = self.picking_id
        while pickings.backorder_ids:
            backorders |= pickings.backorder_ids
            pickings = pickings.backorder_ids

        for move_line in self:
            if kwargs.get('except_package') and move_line.result_package_id:
                continue
            line_key, name, description, uom = get_aggregated_properties(
                move_line=move_line)

            qty_done = move_line.product_uom_id._compute_quantity(
                move_line.qty_done, uom)
            if line_key not in aggregated_move_lines:
                qty_ordered = None
                if backorders and not kwargs.get('strict'):
                    qty_ordered = move_line.move_id.product_uom_qty
                    # Filters on the aggregation key (product, description and uom) to add the
                    # quantities delayed to backorders to retrieve the original ordered qty.
                    following_move_lines = backorders.move_line_ids.filtered(
                        lambda ml: get_aggregated_properties(
                            move=ml.move_id)[0] == line_key
                    )
                    qty_ordered += sum(following_move_lines.move_id.mapped('product_uom_qty'))
                    # Remove the done quantities of the other move lines of the stock move
                    previous_move_lines = move_line.move_id.move_line_ids.filtered(
                        lambda ml: get_aggregated_properties(move=ml.move_id)[
                            0] == line_key and ml.id != move_line.id
                    )
                    qty_ordered -= sum(map(lambda m: m.product_uom_id._compute_quantity(
                        m.qty_done, uom), previous_move_lines))
                aggregated_move_lines[line_key] = {'name': move_line.sh_so_line_desc_sml,
                                                   'description': move_line.sh_so_line_desc_sml,
                                                   'qty_done': qty_done,
                                                   'qty_ordered': qty_ordered or qty_done,
                                                   'product_uom': uom.name,
                                                   'product_uom_rec': uom,
                                                   'product': move_line.product_id,
                                                   'sh_so_line_desc_sml': move_line.sh_so_line_desc_sml}
            else:
                aggregated_move_lines[line_key]['qty_ordered'] += qty_done
                aggregated_move_lines[line_key]['qty_done'] += qty_done

        # Does the same for empty move line to retrieve the ordered qty. for partially done moves
        # (as they are splitted when the transfer is done and empty moves don't have move lines).
        if kwargs.get('strict'):
            return aggregated_move_lines
        pickings = (self.picking_id | backorders)
        for empty_move in pickings.move_lines:
            if not (empty_move.state == "cancel" and empty_move.product_uom_qty
                    and float_is_zero(empty_move.quantity_done, precision_rounding=empty_move.product_uom.rounding)):
                continue
            line_key, name, description, uom = get_aggregated_properties(
                move=empty_move)

            if line_key not in aggregated_move_lines:
                qty_ordered = empty_move.product_uom_qty
                aggregated_move_lines[line_key] = {
                    'name': empty_move.sh_so_line_desc_sml,
                    'description': move_line.sh_so_line_desc_sml,
                    'qty_done': False,
                    'qty_ordered': qty_ordered,
                    'product_uom': uom.name,
                    'product_uom_rec': uom,
                    'product': empty_move.product_id,
                    'sh_so_line_desc_sml': empty_move.sh_so_line_desc_sml,
                }
            else:
                aggregated_move_lines[line_key]['qty_ordered'] += empty_move.product_uom_qty

        return aggregated_move_lines
