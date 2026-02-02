# CUCU Facturación Core - Extendido

## Descripción

Módulo de extensión para `cucu_fact_core` que trunca las descripciones de productos a 150 caracteres antes de enviarlas al webservice de facturación SIN de Bolivia.

## Problema

El servicio web de facturación del SIN (Servicio de Impuestos Nacionales) de Bolivia tiene una limitación de **150 caracteres** para el campo `descripción` en las líneas de factura.

Cuando las descripciones de productos son más extensas (por ejemplo, descripciones detalladas o con notas del cliente), el webservice rechaza la factura con un error.

## Solución

Este módulo:

1. ✅ Extiende el método `_get_detail_move_line()` de `account.move`
2. ✅ Trunca automáticamente cualquier descripción que exceda 150 caracteres
3. ✅ Mantiene el texto original en Odoo (solo trunca para el webservice)
4. ✅ No modifica el código original de CUCU
5. ✅ Genera logs informativos cuando trunca descripciones (opcional)

## Características

- **Truncamiento inteligente**: Solo modifica descripciones que excedan el límite
- **No destructivo**: El texto original permanece en Odoo
- **Compatible**: Usa herencia de métodos Python
- **Mantenible**: No requiere modificar código de CUCU
- **Trazable**: Genera logs cuando trunca (puede deshabilitarse)

## Instalación

1. Asegurar que `cucu_fact_core` esté instalado
2. Actualizar lista de aplicaciones
3. Buscar "CUCU Facturación Core - Extendido"
4. Instalar el módulo

## Uso

Una vez instalado, el módulo funciona automáticamente:

- Cuando se emite una factura con `is_sin = True`
- El método `_get_detail_move_line()` trunca descripciones largas
- La factura se envía al webservice SIN sin errores
- En el PDF de CUCU aparece la descripción completa (si no se usa cucu_fact_report_ext)

## Ejemplo

**Antes:**
```
Descripción: "Lámina Galvanizada FH ACERGAL Ondulada Standard 0.27mm x 900mm (2400mm) estas son las descripciones adicionales muy largas que exceden el límite permitido por el sistema"
Longitud: 175 caracteres ❌ Error en webservice
```

**Después:**
```
Descripción: "Lámina Galvanizada FH ACERGAL Ondulada Standard 0.27mm x 900mm (2400mm) estas son las descripciones adicionales muy largas que exceden el límite permitido por"
Longitud: 150 caracteres ✅ Aceptado por webservice
```

## Desinstalación

Si desinstala este módulo, las descripciones volverán a enviarse completas al webservice, lo que puede causar errores si exceden 150 caracteres.

## Compatibilidad

- **Odoo**: 18.0
- **CUCU**: Todas las versiones que usen `cucu_fact_core`
- **Módulos relacionados**: 
  - `cucu_fact_core` (requerido)
  - `cucu_fact_report_ext` (opcional, para ocultar descripciones en PDF)

## Logs

Cuando se trunca una descripción, el módulo genera un log informativo:

```
INFO: Descripción truncada de 175 a 150 caracteres. Original: 'Lámina Galvanizada FH ACERGAL Ondulada Standard...'
```

Para deshabilitar los logs, comente la línea `_logger.info()` en `models/account_move.py`.

## Soporte

**Desarrollado por:** Largotek SRL  
**Autor:** Juan Luis Garvía  
**Versión:** 18.0.1.0.0  
**Licencia:** LGPL-3

## Estructura del módulo

```
cucu_fact_core_ext/
├── __init__.py
├── __manifest__.py
├── README.md
└── models/
    ├── __init__.py
    └── account_move.py
```

## Notas técnicas

### Método extendido

```python
def _get_detail_move_line(self, type_sector: int = 1):
    # Llama al método original
    detail = super(AccountMove, self)._get_detail_move_line(type_sector)
    
    # Trunca descripciones largas
    for item in detail:
        if item['description'] and len(item['description']) > 150:
            item['description'] = item['description'][:150]
    
    return detail
```

### ¿Por qué 150 caracteres?

Según la documentación del SIN Bolivia, el campo `descripcion` en el webservice de facturación electrónica tiene una longitud máxima de 150 caracteres.
