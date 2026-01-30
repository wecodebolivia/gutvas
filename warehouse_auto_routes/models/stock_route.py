# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class StockRoute(models.Model):
    _inherit = 'stock.route'

    is_inter_warehouse = fields.Boolean(
        string='Inter-Warehouse Route',
        compute='_compute_is_inter_warehouse',
        store=True,
        help='Indicates if this is an automatically generated inter-warehouse route'
    )
    
    @api.depends('name')
    def _compute_is_inter_warehouse(self):
        """Mark routes created by this module."""
        for route in self:
            # Check if this route has an external_id from our module
            xmlid = self.env['ir.model.data'].search([
                ('model', '=', 'stock.route'),
                ('res_id', '=', route.id),
                ('module', '=', 'warehouse_auto_routes')
            ], limit=1)
            route.is_inter_warehouse = bool(xmlid)
