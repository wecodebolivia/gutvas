# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    auto_routes_generated = fields.Boolean(
        string='Auto Routes Generated',
        default=False,
        help='Indicates if automatic routes have been generated for this warehouse'
    )
    
    @api.model
    def _get_inter_warehouse_route_xmlid(self, wh_from_id, wh_to_id):
        """Generate a unique external ID for inter-warehouse route."""
        return f'warehouse_auto_routes.route_wh_{wh_from_id}_to_wh_{wh_to_id}'
    
    @api.model
    def _route_exists(self, wh_from_id, wh_to_id):
        """Check if route already exists using external_id."""
        xmlid = self._get_inter_warehouse_route_xmlid(wh_from_id, wh_to_id)
        return self.env['ir.model.data'].search([
            ('name', '=', xmlid.split('.')[-1]),
            ('module', '=', 'warehouse_auto_routes'),
            ('model', '=', 'stock.route')
        ], limit=1)
    
    @api.model
    def _create_inter_warehouse_route(self, wh_from, wh_to):
        """Create a route from wh_from to wh_to if it doesn't exist."""
        # Safeguard: Check if route already exists
        if self._route_exists(wh_from.id, wh_to.id):
            _logger.info(f'Route from {wh_from.name} to {wh_to.name} already exists, skipping.')
            return None
        
        route_name = f'{wh_from.code} → {wh_to.code}'
        xmlid = self._get_inter_warehouse_route_xmlid(wh_from.id, wh_to.id)
        
        _logger.info(f'Creating route: {route_name}')
        
        # Create the route
        route = self.env['stock.route'].create({
            'name': route_name,
            'active': True,
            'warehouse_selectable': True,
            'product_selectable': False,
            'sequence': 10,
        })
        
        # Create external_id for the route
        self.env['ir.model.data'].create({
            'name': xmlid.split('.')[-1],
            'module': 'warehouse_auto_routes',
            'model': 'stock.route',
            'res_id': route.id,
            'noupdate': True,
        })
        
        # Step 1: Pick from wh_from stock location
        pick_rule = self.env['stock.rule'].create({
            'name': f'{wh_from.code} → Transit: Pick',
            'route_id': route.id,
            'location_src_id': wh_from.lot_stock_id.id,
            'location_dest_id': wh_from.wh_output_stock_loc_id.id or wh_from.lot_stock_id.id,
            'action': 'pull',
            'picking_type_id': wh_from.out_type_id.id,
            'procure_method': 'make_to_stock',
            'sequence': 10,
            'company_id': wh_from.company_id.id,
        })
        
        # Step 2: Transfer from wh_from to wh_to (transit location)
        transfer_rule = self.env['stock.rule'].create({
            'name': f'{wh_from.code} → {wh_to.code}: Transfer',
            'route_id': route.id,
            'location_src_id': wh_from.wh_output_stock_loc_id.id or wh_from.lot_stock_id.id,
            'location_dest_id': wh_to.wh_input_stock_loc_id.id or wh_to.lot_stock_id.id,
            'action': 'pull',
            'picking_type_id': wh_from.int_type_id.id,
            'procure_method': 'make_to_order',
            'sequence': 20,
            'company_id': wh_from.company_id.id,
        })
        
        # Step 3: Receive in wh_to
        receive_rule = self.env['stock.rule'].create({
            'name': f'Transit → {wh_to.code}: Receive',
            'route_id': route.id,
            'location_src_id': wh_to.wh_input_stock_loc_id.id or wh_to.lot_stock_id.id,
            'location_dest_id': wh_to.lot_stock_id.id,
            'action': 'pull',
            'picking_type_id': wh_to.in_type_id.id,
            'procure_method': 'make_to_order',
            'sequence': 30,
            'company_id': wh_to.company_id.id,
        })
        
        _logger.info(f'Route {route_name} created successfully with {len([pick_rule, transfer_rule, receive_rule])} rules')
        
        return route
    
    @api.model
    def generate_all_inter_warehouse_routes(self):
        """Generate routes between all active warehouses."""
        warehouses = self.search([('active', '=', True)])
        
        if len(warehouses) < 2:
            _logger.warning('Less than 2 warehouses found, no routes to create')
            return
        
        created_routes = 0
        skipped_routes = 0
        
        for wh_from in warehouses:
            for wh_to in warehouses:
                if wh_from.id != wh_to.id:
                    route = self._create_inter_warehouse_route(wh_from, wh_to)
                    if route:
                        created_routes += 1
                    else:
                        skipped_routes += 1
        
        # Mark all warehouses as having routes generated
        warehouses.write({'auto_routes_generated': True})
        
        _logger.info(f'Route generation complete: {created_routes} created, {skipped_routes} skipped')
        
        return {
            'created': created_routes,
            'skipped': skipped_routes,
            'total': created_routes + skipped_routes
        }
    
    @api.model
    def create(self, vals):
        """Generate routes for new warehouse automatically."""
        warehouse = super(StockWarehouse, self).create(vals)
        
        # Get all other active warehouses
        other_warehouses = self.search([
            ('active', '=', True),
            ('id', '!=', warehouse.id)
        ])
        
        if other_warehouses:
            _logger.info(f'New warehouse {warehouse.name} created, generating routes...')
            
            created_routes = 0
            # Create routes FROM new warehouse TO others
            for wh_to in other_warehouses:
                route = self._create_inter_warehouse_route(warehouse, wh_to)
                if route:
                    created_routes += 1
            
            # Create routes FROM others TO new warehouse
            for wh_from in other_warehouses:
                route = self._create_inter_warehouse_route(wh_from, warehouse)
                if route:
                    created_routes += 1
            
            warehouse.auto_routes_generated = True
            _logger.info(f'{created_routes} routes created for new warehouse {warehouse.name}')
        
        return warehouse
    
    def action_regenerate_routes(self):
        """Manual action to regenerate routes for this warehouse."""
        self.ensure_one()
        
        other_warehouses = self.search([
            ('active', '=', True),
            ('id', '!=', self.id)
        ])
        
        created_routes = 0
        skipped_routes = 0
        
        # Create routes FROM this warehouse TO others
        for wh_to in other_warehouses:
            route = self._create_inter_warehouse_route(self, wh_to)
            if route:
                created_routes += 1
            else:
                skipped_routes += 1
        
        # Create routes FROM others TO this warehouse
        for wh_from in other_warehouses:
            route = self._create_inter_warehouse_route(wh_from, self)
            if route:
                created_routes += 1
            else:
                skipped_routes += 1
        
        self.auto_routes_generated = True
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Routes Regenerated'),
                'message': _('%d routes created, %d already existed') % (created_routes, skipped_routes),
                'type': 'success',
                'sticky': False,
            }
        }
