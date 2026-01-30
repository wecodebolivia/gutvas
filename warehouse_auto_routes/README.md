# Warehouse Auto Routes

## Descripción

Módulo para Odoo 18 que automatiza la creación de rutas de transporte entre almacenes. Ideal para bases de datos con múltiples almacenes (10+) donde configurar rutas manualmente sería extremadamente tedioso.

## Características

### ✅ Creación Automática
- **Instalación inicial**: Genera automáticamente rutas bidireccionales entre todos los almacenes existentes
- **Nuevos almacenes**: Cuando creas un nuevo almacén, las rutas desde/hacia ese almacén se crean automáticamente
- **32 almacenes** = **992 rutas** creadas automáticamente (32 * 31 combinaciones bidireccionales)

### 🛡️ Sistema Safeguard
- **No duplicación**: El módulo usa `ir.model.data` (external_id) para rastrear rutas creadas
- **Actualizaciones seguras**: Si actualizas o reinstalar el módulo, no creará rutas duplicadas
- **Idempotente**: Puedes ejecutar la generación múltiples veces sin problemas

### 🔄 Flujo de Trabajo

Cada ruta creada implementa un flujo de 3 pasos:

```
Almacén A                    Almacén B
    │                           │
    v                           v
[Stock A] ───> [Output A] ───> [Input B] ───> [Stock B]
    │              │              │
  Pick          Transfer        Receive
```

1. **Pick**: Salida del almacén origen (Delivery Order)
2. **Transfer**: Tránsito entre almacenes (Internal Transfer)
3. **Receive**: Recepción en almacén destino (Receipt)

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
   INFO: Creating route: WH01 → WH02
   INFO: Route generation complete: 992 created, 0 skipped
   ```

## Uso

### Rutas Automáticas

Las rutas se generan automáticamente en estos escenarios:

1. **Primera instalación**: Todas las rutas entre almacenes existentes
2. **Nuevo almacén**: Rutas bidireccionales con todos los almacenes existentes
3. **Reinstalación**: Solo crea rutas faltantes (gracias al safeguard)

### Wizard Manual

Si necesitas generar/regenerar rutas manualmente:

1. Ir a: `Inventario → Configuración → Generate Routes`
2. Seleccionar modo:
   - **All Warehouses**: Genera rutas entre todos los almacenes
   - **Selected Warehouses**: Solo almacenes seleccionados
3. Opción: **Regenerate Existing Routes**
   - ⚠️ **CUIDADO**: Elimina y recrea todas las rutas existentes
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
│   ├── stock_warehouse.py   # Lógica principal de generación de rutas
│   └── stock_route.py        # Extensión de rutas
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
- `_get_inter_warehouse_route_xmlid(wh_from_id, wh_to_id)`: Genera external_id único
- `_route_exists(wh_from_id, wh_to_id)`: Verifica si ruta ya existe (safeguard)
- `_create_inter_warehouse_route(wh_from, wh_to)`: Crea ruta con 3 reglas
- `generate_all_inter_warehouse_routes()`: Genera todas las rutas
- `create()`: Override para auto-generar rutas en nuevos almacenes
- `action_regenerate_routes()`: Acción manual para regenerar

#### `stock.route` (Extendido)

**Campos nuevos**:
- `is_inter_warehouse`: Computed field que identifica rutas del módulo

### External IDs

Cada ruta creada tiene un external_id con formato:
```
warehouse_auto_routes.route_wh_{id_origen}_to_wh_{id_destino}
```

Ejemplo:
- `warehouse_auto_routes.route_wh_1_to_wh_2`
- `warehouse_auto_routes.route_wh_2_to_wh_1`

Esto permite:
- Rastreo preciso de rutas creadas por el módulo
- Evitar duplicación en actualizaciones
- Eliminación selectiva si es necesario

## Casos de Uso

### Escenario 1: Nueva Implementación
```python
# Tienes 32 almacenes
# Instalar módulo genera automáticamente:
# 32 * 31 = 992 rutas bidireccionales
```

### Escenario 2: Crecimiento Orgánico

```python
# Semana 1: 32 almacenes, 992 rutas
# Semana 2: Crear almacén #33
#   → Automáticamente crea 64 rutas nuevas (32*2)
#   → Total: 1,056 rutas
# Semana 3: Crear almacén #34
#   → Automáticamente crea 66 rutas nuevas (33*2)
#   → Total: 1,122 rutas
```

### Escenario 3: Actualización de Módulo

```python
# Actualizar el módulo a una nueva versión:
# → post_init_hook se ejecuta
# → Detecta rutas existentes por external_id
# → Solo crea rutas que falten (si es que hay)
# → No duplica nada
```

## Configuración de Picking Types

El módulo usa los picking types estándar de cada almacén:

- `out_type_id`: Para el paso de salida (Pick)
- `int_type_id`: Para transferencia interna (Transfer)
- `in_type_id`: Para recepción (Receive)

Asegúrate de que estos estén correctamente configurados en cada almacén.

## Logging

El módulo registra todas las operaciones importantes:

```python
_logger.info('Creating route: WH01 → WH02')
_logger.info('Route from WH03 to WH04 already exists, skipping.')
_logger.info('Route generation complete: 992 created, 0 skipped')
```

Revisa los logs de Odoo para debugging:
```bash
tail -f /var/log/odoo/odoo.log | grep "warehouse_auto_routes"
```

## Desinstalación

Si desinstalas el módulo:

1. Las rutas creadas **NO** se eliminan automáticamente
2. Los external_ids se mantienen en `ir.model.data`
3. Para limpiar completamente:

```python
# Desde Python shell o notebook
xmlids = env['ir.model.data'].search([
    ('module', '=', 'warehouse_auto_routes'),
    ('model', '=', 'stock.route')
])
routes = env['stock.route'].browse(xmlids.mapped('res_id'))
routes.unlink()
xmlids.unlink()
```

## Troubleshooting

### Problema: Rutas no se crean automáticamente

**Solución**:
1. Revisar logs para errores
2. Verificar que almacenes estén activos (`active=True`)
3. Ejecutar wizard manual: `Inventario → Configuración → Generate Routes`

### Problema: Rutas duplicadas

**Solución**:
1. Verificar external_ids:
   ```sql
   SELECT * FROM ir_model_data 
   WHERE module = 'warehouse_auto_routes' AND model = 'stock.route';
   ```
2. Si hay duplicados sin external_id, eliminarlos manualmente
3. Usar wizard con "Regenerate Existing Routes" marcado

### Problema: Error en post_init_hook

**Solución**:
- El hook está envuelto en try/except
- No debería fallar la instalación
- Revisar logs para ver el error específico
- Ejecutar generación manual después

## Rendimiento

Para 32 almacenes:
- **Rutas totales**: 992
- **Reglas por ruta**: 3
- **Total reglas**: 2,976
- **Tiempo estimado**: ~2-5 segundos (depende del servidor)

## Personalización

### Modificar flujo de trabajo

Edita `stock_warehouse.py`, método `_create_inter_warehouse_route()`:

```python
# Ejemplo: Agregar un 4to paso
quality_check_rule = self.env['stock.rule'].create({
    'name': f'{wh_to.code}: Quality Check',
    'route_id': route.id,
    'location_src_id': wh_to.wh_input_stock_loc_id.id,
    'location_dest_id': wh_to.wh_qc_stock_loc_id.id,  # Locación QC
    'action': 'pull',
    'picking_type_id': wh_to.qc_type_id.id,  # Picking type QC
    'procure_method': 'make_to_order',
    'sequence': 25,  # Entre transfer y receive
    'company_id': wh_to.company_id.id,
})
```

### Filtrar almacenes

Para solo generar rutas para ciertos almacenes:

```python
# En generate_all_inter_warehouse_routes()
warehouses = self.search([
    ('active', '=', True),
    ('code', 'not in', ['VIRT', 'TEMP'])  # Excluir virtuales
])
```

## Contribuciones

Para contribuir al módulo:

1. Fork el repositorio
2. Crear branch: `git checkout -b feature/mejora`
3. Commit cambios: `git commit -am 'Add: nueva funcionalidad'`
4. Push: `git push origin feature/mejora`
5. Crear Pull Request

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

¡Disfruta de tus rutas automatizadas! 🚀
