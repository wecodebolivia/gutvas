# Warehouse Auto Routes

## Descripción

Módulo para Odoo 18 que automatiza la creación de rutas de transporte entre almacenes usando **transferencias internas** y **ubicaciones en tránsito**. Ideal para bases de datos con múltiples almacenes (10+) donde configurar rutas manualmente sería extremadamente tedioso.

## Características

### ✅ Creación Automática
- **Instalación inicial**: Genera automáticamente rutas bidireccionales entre todos los almacenes existentes
- **Nuevos almacenes**: Cuando creas un nuevo almacén, las rutas desde/hacia ese almacén se crean automáticamente
- **32 almacenes** = **992 rutas** + **992 ubicaciones en tránsito** creadas automáticamente

### 🛡️ Sistema Safeguard
- **No duplicación**: El módulo usa `ir.model.data` (external_id) para rastrear rutas y ubicaciones creadas
- **Actualizaciones seguras**: Si actualizas o reinstalar el módulo, no creará rutas ni ubicaciones duplicadas
- **Idempotente**: Puedes ejecutar la generación múltiples veces sin problemas

### 🔄 Flujo de Trabajo

Cada ruta implementa un **flujo de 2 pasos con transferencias internas**:

```
Almacén A                    Transit Location                  Almacén B
    │                               │                               │
    v                               v                               v
[Stock A] ────────────────> [Tránsito: A→B] ────────────────> [Stock B]
    │                               │                               │
    └─ Paso 1: Internal Transfer   └─ Paso 2: Internal Transfer
       (Origen envía)                 (Destino recibe y valida)
```

#### Paso 1: Envío desde Origen
- **Operación**: Transferencia Interna (Internal Transfer)
- **Desde**: Stock del Almacén A
- **Hacia**: Ubicación en Tránsito "Tránsito: A→B"
- **Responsable**: Usuario en Almacén A
- **Acción**: Validar el envío

#### Paso 2: Recepción en Destino
- **Operación**: Transferencia Interna (Internal Transfer)
- **Desde**: Ubicación en Tránsito "Tránsito: A→B"
- **Hacia**: Stock del Almacén B
- **Responsable**: Usuario en Almacén B
- **Acción**: Recibir y validar el ingreso

### 🎯 Ventajas de este Flujo

1. **Visibilidad total**: Los productos "en tránsito" tienen una ubicación específica
2. **Control bidireccional**: Tanto origen como destino validan las operaciones
3. **Trazabilidad**: Historial completo de movimientos entre almacenes
4. **Solo transferencias internas**: No mezcla con recepciones o entregas
5. **Múltiples tránsitos**: Cada ruta A→B tiene su propia ubicación en tránsito

## Instalación

### Requisitos
- Odoo 18.0
- Módulo `stock` (Inventario)

### Pasos

1. **Clonar o descargar el módulo** en tu directorio de addons

2. **Actualizar lista de módulos**:
   ```bash
   # Modo desarrollo
   odoo-bin -u all -d tu_database
   
   # O desde la interfaz: Apps → Update Apps List
   ```

3. **Instalar el módulo**:
   - Ir a `Apps`
   - Buscar "Warehouse Auto Routes"
   - Hacer clic en `Install`

4. **Verificación automática**:
   - El hook `post_init_hook` se ejecuta automáticamente
   - Revisa los logs para confirmar la creación:
   ```
   INFO: Starting automatic inter-warehouse route generation...
   INFO: Created transit location: Tránsito: WH01 → WH02
   INFO: Creating route: WH01 → WH02
   INFO: Route generation complete: 992 created, 0 skipped
   ```

## Uso

### Flujo Operativo Diario

#### Escenario: Transferir productos de Almacén La Paz a Almacén Santa Cruz

1. **Crear Transferencia**:
   - En Almacén La Paz, seleccionar la ruta "LPAZ → SCZ"
   - Agregar productos
   - Confirmar

2. **Se generan 2 operaciones**:

   **Operación 1 - Envío (La Paz)**:
   - Tipo: Transferencia Interna
   - Desde: WH/Stock (La Paz)
   - Hacia: Tránsito: LPAZ → SCZ
   - Estado: Esperando disponibilidad
   - **Acción del responsable en La Paz**: Validar cuando los productos salgan

   **Operación 2 - Recepción (Santa Cruz)**:
   - Tipo: Transferencia Interna
   - Desde: Tránsito: LPAZ → SCZ
   - Hacia: WH/Stock (Santa Cruz)
   - Estado: Esperando otra operación
   - **Acción del responsable en Santa Cruz**: Aparece cuando La Paz valida. Validar al recibir los productos

3. **Vista en Transferencias Internas**:
   - Responsable en La Paz ve: Transferencias internas salientes
   - Responsable en Santa Cruz ve: Transferencias internas entrantes

### Rutas Automáticas

Las rutas se generan automáticamente en estos escenarios:

1. **Primera instalación**: Todas las rutas entre almacenes existentes + ubicaciones en tránsito
2. **Nuevo almacén**: Rutas bidireccionales con todos los almacenes existentes
3. **Reinstalación**: Solo crea rutas faltantes (gracias al safeguard)

### Wizard Manual

Si necesitas generar/regenerar rutas manualmente:

1. Ir a: `Inventario → Configuración → Generate Routes`
2. Seleccionar modo:
   - **All Warehouses**: Genera rutas entre todos los almacenes
   - **Selected Warehouses**: Solo almacenes seleccionados
3. Opción: **Regenerate Existing Routes**
   - ⚠️ **CUIDADO**: Elimina y recrea todas las rutas y ubicaciones en tránsito
   - Usar solo si necesitas resetear completamente

### Botón en Almacén

Cada almacén tiene un botón "Regenerate Routes" en el formulario:

- Regenera solo las rutas para ese almacén específico
- No afecta rutas de otros almacenes
- Muestra notificación con resultados

## Estructura Técnica

```
warehouse_auto_routes/
├── __init__.py              # Imports principales + post_init_hook
├── __init_hook__.py         # Hook de inicialización
├── __manifest__.py          # Configuración del módulo
├── README.md                # Este archivo
├── models/
│   ├── __init__.py
│   ├── stock_warehouse.py   # Lógica principal de generación
│   └── stock_route.py       # Extensión de rutas
├── wizard/
│   ├── __init__.py
│   ├── warehouse_route_generator.py
│   └── warehouse_route_generator_views.xml
├── views/
│   └── stock_warehouse_views.xml
└── security/
    └── ir.model.access.csv
```

### Modelos Principales

#### `stock.warehouse` (Extendido)

**Campos nuevos**:
- `auto_routes_generated`: Boolean que indica si las rutas fueron generadas

**Métodos clave**:
- `_get_inter_warehouse_route_xmlid(wh_from_id, wh_to_id)`: Genera external_id único para ruta
- `_get_transit_location_xmlid(wh_from_id, wh_to_id)`: Genera external_id único para ubicación
- `_route_exists(wh_from_id, wh_to_id)`: Verifica si ruta ya existe (safeguard)
- `_get_or_create_transit_location(wh_from, wh_to)`: Obtiene o crea ubicación en tránsito
- `_create_inter_warehouse_route(wh_from, wh_to)`: Crea ruta con 2 reglas
- `generate_all_inter_warehouse_routes()`: Genera todas las rutas
- `create()`: Override para auto-generar rutas en nuevos almacenes
- `action_regenerate_routes()`: Acción manual para regenerar

#### `stock.route` (Extendido)

**Campos nuevos**:
- `is_inter_warehouse`: Computed field que identifica rutas del módulo

### External IDs

#### Rutas
Cada ruta creada tiene un external_id con formato:
```
warehouse_auto_routes.route_wh_{id_origen}_to_wh_{id_destino}
```

#### Ubicaciones en Tránsito
Cada ubicación tiene un external_id con formato:
```
warehouse_auto_routes.transit_loc_wh_{id_origen}_to_wh_{id_destino}
```

Ejemplo para WH1 → WH2:
- Ruta: `warehouse_auto_routes.route_wh_1_to_wh_2`
- Ubicación: `warehouse_auto_routes.transit_loc_wh_1_to_wh_2`
- Nombre visible: "Tránsito: WH1 → WH2"

## Ubicaciones en Tránsito

### Características
- **Tipo**: `transit` (uso interno de Odoo para tránsitos)
- **Ubicación padre**: "Physical Locations" (stock.stock_location_locations)
- **Una por ruta**: Cada combinación A→B tiene su propia ubicación
- **Automáticas**: Creadas junto con las rutas
- **Persistentes**: No se eliminan al desinstalar (por seguridad de datos)

### Consultar Ubicaciones en Tránsito

```python
# Desde shell de Odoo
transit_locs = env['stock.location'].search([('usage', '=', 'transit')])
for loc in transit_locs:
    print(f"{loc.name} - Quants: {len(loc.quant_ids)}")
```

## Casos de Uso

### Escenario 1: Nueva Implementación

```python
# Tienes 32 almacenes
# Instalar módulo genera automáticamente:
# - 992 rutas bidireccionales
# - 992 ubicaciones en tránsito
# - 1,984 reglas de stock (2 por ruta)
```

### Escenario 2: Crecimiento Orgánico

```python
# Semana 1: 32 almacenes
#   → 992 rutas, 992 ubicaciones tránsito
# Semana 2: Crear almacén #33
#   → +64 rutas, +64 ubicaciones (32*2)
#   → Total: 1,056 rutas, 1,056 ubicaciones
# Semana 3: Crear almacén #34
#   → +66 rutas, +66 ubicaciones (33*2)
#   → Total: 1,122 rutas, 1,122 ubicaciones
```

### Escenario 3: Transferencia en Proceso

```python
# Día 1: La Paz envía 100 unidades de Producto X a Santa Cruz
#   → Valida envío
#   → 100 unidades en "Tránsito: LPAZ → SCZ"

# Día 2: Camión en ruta
#   → 100 unidades siguen en tránsito
#   → Visibles en inventario de ubicación tránsito

# Día 3: Santa Cruz recibe
#   → Valida recepción
#   → 100 unidades en "WH/Stock (Santa Cruz)"
```

## Configuración de Picking Types

El módulo usa `int_type_id` (Internal Transfers) de cada almacén:

- **Paso 1**: `wh_from.int_type_id` para envío a tránsito
- **Paso 2**: `wh_to.int_type_id` para recepción desde tránsito

Asegúrate de que cada almacén tenga configurado correctamente su tipo de operación de transferencias internas.

## Logging

El módulo registra todas las operaciones importantes:

```python
_logger.info('Created transit location: Tránsito: WH01 → WH02')
_logger.info('Creating route: WH01 → WH02')
_logger.info('Route WH01 → WH02 created successfully:')
_logger.info('  - Step 1: WH01 → Transit (Internal Transfer)')
_logger.info('  - Step 2: Transit → WH02 (Internal Transfer)')
_logger.info('Route generation complete: 992 created, 0 skipped')
```

Revisa los logs de Odoo para debugging:
```bash
tail -f /var/log/odoo/odoo.log | grep "warehouse_auto_routes"
```

## Desinstalación

Si desinstalas el módulo:

1. Las rutas creadas **NO** se eliminan automáticamente
2. Las ubicaciones en tránsito **NO** se eliminan automáticamente (pueden tener inventario)
3. Los external_ids se mantienen en `ir.model.data`
4. Para limpiar completamente:

```python
# Desde Python shell o notebook
# 1. Eliminar rutas
xmlids_routes = env['ir.model.data'].search([
    ('module', '=', 'warehouse_auto_routes'),
    ('model', '=', 'stock.route')
])
routes = env['stock.route'].browse(xmlids_routes.mapped('res_id'))
routes.unlink()
xmlids_routes.unlink()

# 2. Eliminar ubicaciones en tránsito (¡solo si están vacías!)
xmlids_locs = env['ir.model.data'].search([
    ('module', '=', 'warehouse_auto_routes'),
    ('model', '=', 'stock.location')
])
locs = env['stock.location'].browse(xmlids_locs.mapped('res_id'))
# Verificar que no tengan inventario
for loc in locs:
    if loc.quant_ids:
        print(f"WARNING: {loc.name} has inventory, cannot delete")
    else:
        loc.unlink()
xmlids_locs.unlink()
```

## Troubleshooting

### Problema: No veo las transferencias internas

**Solución**:
1. Verificar que la ruta esté asignada al producto o pedido
2. Ir a: `Inventario → Operaciones → Transferencias`
3. Filtrar por almacén origen/destino

### Problema: Productos "atascados" en tránsito

**Solución**:
1. Ir a: `Inventario → Productos → {Producto}`
2. Ver "On Hand"
3. Buscar ubicaciones tipo "Tránsito"
4. Identificar la transferencia pendiente de validación
5. Validar la recepción en el almacén destino

### Problema: Rutas no se crean automáticamente

**Solución**:
1. Revisar logs para errores
2. Verificar que almacenes estén activos (`active=True`)
3. Ejecutar wizard manual: `Inventario → Configuración → Generate Routes`

### Problema: Muchas ubicaciones en tránsito vacías

**Esto es normal**:
- Cada ruta tiene su ubicación dedicada
- 32 almacenes = 992 ubicaciones en tránsito
- La mayoría estarán vacías la mayor parte del tiempo
- Solo tienen inventario cuando hay transferencias en proceso

## Rendimiento

Para 32 almacenes:
- **Rutas totales**: 992
- **Ubicaciones en tránsito**: 992
- **Reglas por ruta**: 2
- **Total reglas**: 1,984
- **Tiempo estimado instalación**: ~3-7 segundos (depende del servidor)

## Ventajas vs Flujo de 3 Pasos

| Aspecto | 2 Pasos (Este módulo) | 3 Pasos (Pick/Ship/Receive) |
|---------|----------------------|-----------------------------|
| Tipos de operación | Solo Internal Transfers | Out + Internal + In |
| Complejidad | Menor | Mayor |
| Configuración | Automática | Requiere más setup |
| Visibilidad tránsito | Ubicación dedicada | Entre operaciones |
| Para usuarios | Más intuitivo | Más complejo |
| Apropiado para | Transferencias inter-almacén | Logística completa |

## Licencia

LGPL-3

## Autor

**WeCode Bolivia**
- Website: https://www.wecodebolivia.com
- GitHub: https://github.com/wecodebolivia

## Soporte

Para reportar bugs o solicitar features:
- Crear issue en: https://github.com/wecodebolivia/gutvas/issues
- Incluir versión de Odoo y logs relevantes

---

¡Disfruta de tus rutas automatizadas con transferencias internas! 🚀
