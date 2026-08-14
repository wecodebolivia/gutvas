# Guía de Pruebas de Usuario

## Control Peso-Área de Rollos de Metal

**Módulo:** `acergal_weight_area_control`  
**Versión objetivo:** Odoo 18  
**Ambiente:** Staging  
**Propósito:** validar que el control auxiliar por kilogramos y metros funcione correctamente para rollos trazados por lote.

> Esta guía debe ejecutarse primero en Staging. No use productos, lotes ni pedidos de producción.

---

## 1. Preparación

Antes de comenzar, confirme que el módulo está instalado y que tiene permisos de Inventario. Para las pruebas de configuración también necesita permisos de Administrador de Inventario.

### Datos de prueba sugeridos

Cree o identifique un producto de prueba con estos valores:

| Dato | Valor sugerido |
|---|---:|
| Nombre | Rollo metálico prueba PA |
| Tipo de producto | Almacenable |
| Unidad de medida | Metro(s) |
| Seguimiento | Por lotes |
| Control peso-área | Activado |
| Factor estándar | 2.50 kg/m |
| Umbral de variación | 5 % |

Use como lote de prueba: `RPA-TEST-001`.

---

## 2. Prueba 1: Configuración del producto

### Objetivo
Comprobar que un producto solo puede usar Control Peso-Área si tiene seguimiento por lote y factor estándar válido.

### Pasos

1. Abra **Inventario > Productos > Productos**.
2. Cree o abra el producto de prueba.
3. Configure la unidad de medida en metros.
4. En la pestaña de Inventario, seleccione **Seguimiento: Por lotes**.
5. Abra la pestaña **Peso-Área**.
6. Active **Control peso-área**.
7. Registre `2.50` en **Factor estándar (kg/m)**.
8. Guarde el producto.

### Resultado esperado

- El producto se guarda correctamente.
- La pestaña Peso-Área muestra el factor estándar configurado.
- Si se intenta activar el control sin seguimiento por lote o con factor igual a cero, el sistema debe impedir guardar e informar el motivo.

**Resultado:** ☐ Conforme  ☐ No conforme  
**Observaciones:** ________________________________________________

---

## 3. Prueba 2: Inicialización del rollo

### Objetivo
Validar el registro de peso y metraje inicial, el factor real y la desviación.

### Pasos

1. Abra **Inventario > Productos > Lotes/Números de serie**.
2. Cree o abra el lote `RPA-TEST-001` del producto de prueba.
3. En el bloque **Control peso-área**, registre:
   - Peso inicial: `500 kg`.
   - Metraje inicial: `190 m`.
4. Pulse **Inicializar control**.

### Resultado esperado

| Indicador | Resultado esperado |
|---|---:|
| Factor real | 2.631579 kg/m aproximadamente |
| Desviación | 5.263158 % aproximadamente |
| Estado de variación | Advertencia, porque supera 5 % |
| Saldo inicial | 500 kg y 190 m |
| Estado de inicialización | Activo |

**Resultado:** ☐ Conforme  ☐ No conforme  
**Observaciones:** ________________________________________________

---

## 4. Prueba 3: Metraje calculado

### Objetivo
Confirmar que el sistema calcula metros cuando solo se conoce el peso inicial.

### Pasos

1. Cree un segundo lote: `RPA-TEST-002`.
2. Registre peso inicial de `500 kg`.
3. Deje vacío el metraje inicial.
4. Pulse **Inicializar control**.

### Resultado esperado

- El sistema calcula `200 m`, usando `500 / 2.50`.
- El factor real es `2.50 kg/m`.
- La desviación es `0 %`.
- El estado de variación es Normal.

**Resultado:** ☐ Conforme  ☐ No conforme  
**Observaciones:** ________________________________________________

---

## 5. Prueba 4: Información en venta

### Objetivo
Comprobar que la orden de venta muestra una estimación de kg sin alterar precio, impuestos ni cantidad comercial.

### Pasos

1. Abra **Ventas > Pedidos > Cotizaciones**.
2. Cree una cotización para un cliente de prueba.
3. Agregue el producto de prueba.
4. Registre una cantidad de `20 m`.
5. Abra el detalle de la línea.

### Resultado esperado

- Se muestra **Kg equivalentes estimados**.
- El valor esperado es `50 kg`, calculado con el factor estándar: `20 × 2.50`.
- La cantidad de la venta se mantiene en `20 m`.
- El campo es informativo y no modifica precio, descuentos, impuestos ni facturación.

**Resultado:** ☐ Conforme  ☐ No conforme  
**Observaciones:** ________________________________________________

---

## 6. Prueba 5: Consulta de saldo

### Objetivo
Confirmar que la ficha del lote permite consultar el control dual.

### Pasos

1. Abra el lote `RPA-TEST-001`.
2. Revise el bloque **Control peso-área**.

### Resultado esperado antes de realizar salidas

| Campo | Valor esperado |
|---|---:|
| Peso inicial | 500 kg |
| Metraje inicial | 190 m |
| Factor real | 2.631579 kg/m aproximadamente |
| Kg consumidos | 0 kg |
| Metros consumidos | 0 m |
| Saldo kg | 500 kg |
| Saldo m | 190 m |

**Resultado:** ☐ Conforme  ☐ No conforme  
**Observaciones:** ________________________________________________

---

## 7. Prueba 6: Validaciones de datos

### Objetivo
Confirmar que no se pueden inicializar rollos con datos inválidos.

### Casos

| Caso | Acción | Resultado esperado |
|---|---|---|
| Sin peso | Intentar inicializar con peso vacío o 0 | El sistema muestra un error y no inicializa |
| Peso negativo | Registrar un valor menor que 0 | El sistema impide guardar |
| Metraje negativo | Registrar un valor menor que 0 | El sistema impide guardar |
| Producto sin lote | Activar control en producto sin trazabilidad por lote | El sistema impide guardar |
| Factor cero | Activar control con factor estándar 0 | El sistema impide guardar |

**Resultado:** ☐ Conforme  ☐ No conforme  
**Observaciones:** ________________________________________________

---

## 8. Evidencias requeridas

Por cada prueba conforme, adjunte o conserve:

- Captura del producto configurado.
- Captura de la ficha de cada lote de prueba.
- Captura de la línea de venta con kg equivalentes estimados.
- Captura de cualquier mensaje de validación o error.
- Fecha, usuario que ejecutó la prueba y resultado.

---

## 9. Registro de ejecución

| Prueba | Ejecutada por | Fecha | Resultado | Incidencia / observación |
|---|---|---|---|---|
| 1. Configuración del producto |  |  | ☐ OK ☐ Error |  |
| 2. Inicialización del rollo |  |  | ☐ OK ☐ Error |  |
| 3. Metraje calculado |  |  | ☐ OK ☐ Error |  |
| 4. Información en venta |  |  | ☐ OK ☐ Error |  |
| 5. Consulta de saldo |  |  | ☐ OK ☐ Error |  |
| 6. Validaciones de datos |  |  | ☐ OK ☐ Error |  |

---

## 10. Alcance de esta versión

Esta guía cubre la base actualmente disponible: configuración del producto, inicialización manual del lote, cálculos del factor y consulta informativa en ventas.

Las siguientes funciones deben probarse cuando se incorporen en una iteración posterior: inicialización directa desde recepción, bloqueo de salida por saldo dual, cálculo congelado al validar despacho, devoluciones, ajustes auditados y kardex dual PDF.
