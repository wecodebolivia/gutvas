# -*- coding: utf-8 -*-
"""
Cleanup Script for Warehouse Auto Routes
=========================================

Este script elimina todas las rutas y ubicaciones en tránsito creadas 
por versiones anteriores del módulo warehouse_auto_routes.

Uso:
----

### Opción 1: Desde Odoo Shell
```bash
odoo-bin shell -d tu_database --config=/etc/odoo/odoo.conf
```

Luego ejecuta:
```python
exec(open('/ruta/a/warehouse_auto_routes/scripts/cleanup_old_routes.py').read())
```

### Opción 2: Desde Studio/Notebook de Odoo
Copia y pega todo este código en un notebook.

### Opción 3: Como método en el modelo
Llama desde código: env['stock.warehouse'].cleanup_auto_routes()

"""

import logging

_logger = logging.getLogger(__name__)

def cleanup_auto_routes(env):
    """
    Elimina todas las rutas y ubicaciones creadas por warehouse_auto_routes.
    
    Args:
        env: Environment de Odoo
    
    Returns:
        dict: Estadísticas de eliminación
    """
    
    print("="*60)
    print("Warehouse Auto Routes - Cleanup Script")
    print("="*60)
    print()
    
    stats = {
        'routes_deleted': 0,
        'locations_deleted': 0,
        'xmlids_deleted': 0,
        'errors': []
    }
    
    # PASO 1: Buscar todas las rutas creadas por el módulo
    print("[1/4] Buscando rutas creadas por warehouse_auto_routes...")
    
    xmlids_routes = env['ir.model.data'].search([
        ('module', '=', 'warehouse_auto_routes'),
        ('model', '=', 'stock.route')
    ])
    
    print(f"      Encontradas: {len(xmlids_routes)} rutas")
    
    if xmlids_routes:
        routes = env['stock.route'].browse(xmlids_routes.mapped('res_id')).exists()
        print(f"      Rutas válidas: {len(routes)}")
        
        # Listar algunas rutas para confirmación
        if routes:
            print("\n      Ejemplos de rutas a eliminar:")
            for route in routes[:5]:
                print(f"      - {route.name} (ID: {route.id})")
            if len(routes) > 5:
                print(f"      ... y {len(routes) - 5} más")
        
        print("\n      ¿Eliminar estas rutas? (continuar con el script)")
        
        try:
            # Eliminar rutas
            routes.unlink()
            stats['routes_deleted'] = len(routes)
            print(f"      ✓ {len(routes)} rutas eliminadas")
            
            # Eliminar external IDs de rutas
            xmlids_routes.unlink()
            stats['xmlids_deleted'] += len(xmlids_routes)
            
        except Exception as e:
            error_msg = f"Error eliminando rutas: {str(e)}"
            print(f"      ✗ {error_msg}")
            stats['errors'].append(error_msg)
    else:
        print("      No se encontraron rutas para eliminar")
    
    print()
    
    # PASO 2: Buscar ubicaciones en tránsito creadas por el módulo
    print("[2/4] Buscando ubicaciones en tránsito...")
    
    xmlids_locs = env['ir.model.data'].search([
        ('module', '=', 'warehouse_auto_routes'),
        ('model', '=', 'stock.location')
    ])
    
    print(f"      Encontradas: {len(xmlids_locs)} ubicaciones")
    
    if xmlids_locs:
        locations = env['stock.location'].browse(xmlids_locs.mapped('res_id')).exists()
        print(f"      Ubicaciones válidas: {len(locations)}")
        
        # Verificar inventario en ubicaciones
        locations_with_stock = []
        locations_empty = []
        
        for loc in locations:
            if loc.quant_ids:
                locations_with_stock.append(loc)
            else:
                locations_empty.append(loc)
        
        if locations_with_stock:
            print(f"\n      ⚠ WARNING: {len(locations_with_stock)} ubicaciones tienen inventario:")
            for loc in locations_with_stock[:5]:
                total_qty = sum(loc.quant_ids.mapped('quantity'))
                print(f"      - {loc.name}: {total_qty} unidades")
            if len(locations_with_stock) > 5:
                print(f"      ... y {len(locations_with_stock) - 5} más")
            print("\n      Estas ubicaciones NO serán eliminadas por seguridad.")
            print("      Primero debes mover o ajustar el inventario.")
        
        if locations_empty:
            print(f"\n      {len(locations_empty)} ubicaciones vacías serán eliminadas")
            
            try:
                # Eliminar solo ubicaciones vacías
                env['stock.location'].browse([l.id for l in locations_empty]).unlink()
                stats['locations_deleted'] = len(locations_empty)
                print(f"      ✓ {len(locations_empty)} ubicaciones eliminadas")
                
                # Eliminar external IDs de ubicaciones eliminadas
                xmlids_to_delete = env['ir.model.data'].search([
                    ('module', '=', 'warehouse_auto_routes'),
                    ('model', '=', 'stock.location'),
                    ('res_id', 'in', [l.id for l in locations_empty])
                ])
                xmlids_to_delete.unlink()
                stats['xmlids_deleted'] += len(xmlids_to_delete)
                
            except Exception as e:
                error_msg = f"Error eliminando ubicaciones: {str(e)}"
                print(f"      ✗ {error_msg}")
                stats['errors'].append(error_msg)
    else:
        print("      No se encontraron ubicaciones para eliminar")
    
    print()
    
    # PASO 3: Limpiar external IDs huérfanos
    print("[3/4] Limpiando external IDs huérfanos...")
    
    orphan_xmlids = env['ir.model.data'].search([
        ('module', '=', 'warehouse_auto_routes'),
        '|',
        ('res_id', '=', False),
        '&',
        ('model', '=', 'stock.route'),
        ('res_id', 'not in', env['stock.route'].search([]).ids)
    ])
    
    if orphan_xmlids:
        try:
            orphan_xmlids.unlink()
            print(f"      ✓ {len(orphan_xmlids)} external IDs huérfanos eliminados")
        except Exception as e:
            error_msg = f"Error eliminando XMLIDs: {str(e)}"
            print(f"      ✗ {error_msg}")
            stats['errors'].append(error_msg)
    else:
        print("      No se encontraron external IDs huérfanos")
    
    print()
    
    # PASO 4: Reset flags en almacenes
    print("[4/4] Reseteando flags en almacenes...")
    
    try:
        warehouses = env['stock.warehouse'].search([('auto_routes_generated', '=', True)])
        if warehouses:
            warehouses.write({'auto_routes_generated': False})
            print(f"      ✓ Flag reseteado en {len(warehouses)} almacenes")
        else:
            print("      No hay almacenes con flag activo")
    except Exception as e:
        error_msg = f"Error reseteando flags: {str(e)}"
        print(f"      ✗ {error_msg}")
        stats['errors'].append(error_msg)
    
    print()
    print("="*60)
    print("Resumen de Limpieza")
    print("="*60)
    print(f"Rutas eliminadas:       {stats['routes_deleted']}")
    print(f"Ubicaciones eliminadas: {stats['locations_deleted']}")
    print(f"External IDs eliminados: {stats['xmlids_deleted']}")
    
    if stats['errors']:
        print(f"\nErrores encontrados:    {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"  - {error}")
    else:
        print("\n✓ Limpieza completada sin errores")
    
    print("="*60)
    print()
    print("Ahora puedes actualizar el módulo warehouse_auto_routes")
    print("Las nuevas rutas se generarán automáticamente al actualizar.")
    print()
    
    return stats


# EJECUTAR EL SCRIPT
if __name__ == '__main__':
    # Si se ejecuta desde shell o importa
    try:
        # Intentar obtener el environment
        if 'env' in globals():
            result = cleanup_auto_routes(env)
        else:
            print("Error: Variable 'env' no encontrada.")
            print("Este script debe ejecutarse desde Odoo shell o notebook.")
    except NameError:
        print("Error: Este script debe ejecutarse desde Odoo shell o notebook.")
        print("\nEjemplo de uso:")
        print("  odoo-bin shell -d database_name")
        print("  >>> exec(open('cleanup_old_routes.py').read())")
