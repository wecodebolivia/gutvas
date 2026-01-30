# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Generate inter-warehouse routes after module installation."""
    _logger.info('Starting automatic inter-warehouse route generation...')
    
    try:
        warehouse_obj = env['stock.warehouse']
        result = warehouse_obj.generate_all_inter_warehouse_routes()
        
        _logger.info(
            f"Route generation completed: "
            f"{result.get('created', 0)} created, "
            f"{result.get('skipped', 0)} skipped"
        )
    except Exception as e:
        _logger.error(f'Error generating inter-warehouse routes: {str(e)}')
        # Don't fail installation if route generation fails
