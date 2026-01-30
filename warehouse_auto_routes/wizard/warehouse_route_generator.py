# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WarehouseRouteGenerator(models.TransientModel):
    _name = 'warehouse.route.generator'
    _description = 'Warehouse Route Generator'

    mode = fields.Selection([
        ('all', 'All Warehouses'),
        ('selected', 'Selected Warehouses'),
    ], string='Mode', default='all', required=True)
    
    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string='Warehouses',
        help='Select warehouses to generate routes for'
    )
    
    regenerate_existing = fields.Boolean(
        string='Regenerate Existing Routes',
        default=False,
        help='If checked, will delete and recreate existing routes'
    )
    
    def action_generate_routes(self):
        """Generate inter-warehouse routes based on selected mode."""
        self.ensure_one()
        
        if self.mode == 'all':
            warehouses = self.env['stock.warehouse'].search([('active', '=', True)])
        else:
            if not self.warehouse_ids:
                raise UserError(_('Please select at least one warehouse.'))
            warehouses = self.warehouse_ids
        
        if len(warehouses) < 2:
            raise UserError(_('At least 2 warehouses are required to generate routes.'))
        
        # If regenerate_existing, delete old routes first
        if self.regenerate_existing:
            xmlids = self.env['ir.model.data'].search([
                ('module', '=', 'warehouse_auto_routes'),
                ('model', '=', 'stock.route')
            ])
            
            routes_to_delete = self.env['stock.route'].browse(xmlids.mapped('res_id'))
            routes_to_delete.unlink()
            xmlids.unlink()
            
            # Reset auto_routes_generated flag
            warehouses.write({'auto_routes_generated': False})
        
        # Generate routes
        created_routes = 0
        skipped_routes = 0
        
        for wh_from in warehouses:
            for wh_to in warehouses:
                if wh_from.id != wh_to.id:
                    route = self.env['stock.warehouse']._create_inter_warehouse_route(wh_from, wh_to)
                    if route:
                        created_routes += 1
                    else:
                        skipped_routes += 1
        
        # Mark warehouses as having routes generated
        warehouses.write({'auto_routes_generated': True})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Routes Generated'),
                'message': _('%d routes created, %d already existed. Total warehouses: %d') % (
                    created_routes, 
                    skipped_routes,
                    len(warehouses)
                ),
                'type': 'success',
                'sticky': False,
            }
        }
