# Limpieza Rápida de Rutas Antiguas

## Opción 1: Script Completo (Recomendado)

### Desde Odoo Shell:
```bash
odoo-bin shell -d tu_database
```

Luego ejecuta:
```python
exec(open('/ruta/completa/a/warehouse_auto_routes/scripts/cleanup_old_routes.py').read())
```

---

## Opción 2: Copiar y Pegar (Más Rápido)

### Desde Odoo Shell, Studio o Notebook:

Copia y pega este código completo:

```python
# ============================================
# CLEANUP: Warehouse Auto Routes
# ============================================

print("Iniciando limpieza de rutas antiguas...")

# 1. Eliminar rutas
print("\n[1/4] Eliminando rutas...")
xmlids_routes = env['ir.model.data'].search([
    ('module', '=', 'warehouse_auto_routes'),
    ('model', '=', 'stock.route')
])

if xmlids_routes:
    routes = env['stock.route'].browse(xmlids_routes.mapped('res_id')).exists()
    print(f"  Rutas encontradas: {len(routes)}")
    if routes:
        print(f"  Ejemplos: {', '.join(routes[:3].mapped('name'))}...")
        routes.unlink()
        print(f"  ✓ {len(routes)} rutas eliminadas")
    xmlids_routes.unlink()
else:
    print("  No hay rutas para eliminar")

# 2. Eliminar ubicaciones en tránsito (solo vacías)
print("\n[2/4] Eliminando ubicaciones en tránsito...")
xmlids_locs = env['ir.model.data'].search([
    ('module', '=', 'warehouse_auto_routes'),
    ('model', '=', 'stock.location')
])

if xmlids_locs:
    locations = env['stock.location'].browse(xmlids_locs.mapped('res_id')).exists()
    print(f"  Ubicaciones encontradas: {len(locations)}")
    
    # Separar vacías de las que tienen stock
    empty_locs = locations.filtered(lambda l: not l.quant_ids)
    with_stock = locations.filtered(lambda l: l.quant_ids)
    
    if with_stock:
        print(f"  ⚠ {len(with_stock)} ubicaciones tienen inventario (NO eliminadas):")
        for loc in with_stock[:3]:
            qty = sum(loc.quant_ids.mapped('quantity'))
            print(f"    - {loc.name}: {qty} unidades")
    
    if empty_locs:
        empty_locs.unlink()
        print(f"  ✓ {len(empty_locs)} ubicaciones vacías eliminadas")
        
        # Eliminar XMLIDs de ubicaciones eliminadas
        xmlids_to_del = env['ir.model.data'].search([
            ('module', '=', 'warehouse_auto_routes'),
            ('model', '=', 'stock.location'),
            ('res_id', 'in', empty_locs.ids)
        ])
        xmlids_to_del.unlink()
else:
    print("  No hay ubicaciones para eliminar")

# 3. Limpiar external IDs huérfanos
print("\n[3/4] Limpiando external IDs huérfanos...")
orphan_xmlids = env['ir.model.data'].search([
    ('module', '=', 'warehouse_auto_routes'),
    ('res_id', '=', False)
])
if orphan_xmlids:
    orphan_xmlids.unlink()
    print(f"  ✓ {len(orphan_xmlids)} XMLIDs eliminados")
else:
    print("  No hay XMLIDs huérfanos")

# 4. Resetear flags
print("\n[4/4] Reseteando flags en almacenes...")
warehouses = env['stock.warehouse'].search([('auto_routes_generated', '=', True)])
if warehouses:
    warehouses.write({'auto_routes_generated': False})
    print(f"  ✓ {len(warehouses)} almacenes reseteados")
else:
    print("  No hay flags para resetear")

print("\n" + "="*50)
print("✓ LIMPIEZA COMPLETADA")
print("="*50)
print("\nAhora puedes actualizar el módulo warehouse_auto_routes")
print("Las nuevas rutas se generarán automáticamente.\n")
```

---

## Opción 3: Una Línea (Super Rápido)

**⚠️ CUIDADO**: Elimina TODO sin confirmación. Usar solo si estás seguro.

```python
env['stock.route'].browse(env['ir.model.data'].search([('module','=','warehouse_auto_routes'),('model','=','stock.route')]).mapped('res_id')).unlink(); env['stock.location'].browse(env['ir.model.data'].search([('module','=','warehouse_auto_routes'),('model','=','stock.location')]).mapped('res_id')).filtered(lambda l: not l.quant_ids).unlink(); env['ir.model.data'].search([('module','=','warehouse_auto_routes')]).unlink(); env['stock.warehouse'].search([('auto_routes_generated','=',True)]).write({'auto_routes_generated': False}); print("✓ Limpieza completada")
```

---

## Después de la Limpieza

### Actualizar el Módulo:

```bash
# Desde terminal
odoo-bin -u warehouse_auto_routes -d tu_database
```

O desde interfaz:
1. Apps → Buscar "Warehouse Auto Routes"
2. Upgrade

El `post_init_hook` generará automáticamente las nuevas rutas con el flujo de 2 pasos.

---

## Verificación

Después de actualizar, verifica:

```python
# Contar rutas nuevas
routes = env['stock.route'].search([('is_inter_warehouse', '=', True)])
print(f"Rutas creadas: {len(routes)}")

# Contar ubicaciones en tránsito
transit_locs = env['stock.location'].search([('usage', '=', 'transit')])
print(f"Ubicaciones en tránsito: {len(transit_locs)}")

# Listar ejemplos
if routes:
    print("\nEjemplos de rutas:")
    for r in routes[:5]:
        print(f"  - {r.name}")
```

Deberías ver:
- **32 almacenes** = 992 rutas
- **992 ubicaciones en tránsito**
- Cada ruta con **2 reglas** (send + receive)

---

## Troubleshooting

### Error: "Record does not exist"
```python
# Limpiar XMLIDs huérfanos primero
env['ir.model.data'].search([
    ('module', '=', 'warehouse_auto_routes'),
    ('res_id', '=', False)
]).unlink()
```

### Ubicaciones con inventario
```python
# Listar ubicaciones con stock
locs = env['stock.location'].search([
    ('usage', '=', 'transit'),
    ('quant_ids', '!=', False)
])

for loc in locs:
    print(f"{loc.name}:")
    for quant in loc.quant_ids:
        print(f"  - {quant.product_id.name}: {quant.quantity} {quant.product_uom_id.name}")

# Mover inventario a otra ubicación antes de eliminar
```

### Commit cambios (si usas transacciones)
```python
env.cr.commit()
```
