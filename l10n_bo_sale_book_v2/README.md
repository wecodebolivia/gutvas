# Libro de Ventas Bolivia V2

## Descripción

Módulo de Odoo 18 para generar el Libro de Ventas en formato Excel según las especificaciones del Servicio de Impuestos Nacionales de Bolivia.

**Versión 2** - Formato estándar actualizado con todas las columnas requeridas por Impuestos.

## Características

- Genera archivo Excel con formato estándar de Impuestos Bolivia
- 24 columnas según plantilla oficial
- Cálculos automáticos de:
  - Subtotal
  - Importe base para débito fiscal
  - Débito fiscal (13%)
- Soporta todos los tipos de impuestos especiales:
  - ICE (Impuesto al Consumo Específico)
  - IEHD (Impuesto Especial a los Hidrocarburos y Derivados)
  - IPJ (Impuesto a los Juegos)
  - Tasas
- Manejo de conceptos especiales:
  - Exportaciones y operaciones exentas
  - Ventas gravadas a tasa cero
  - Gift Cards
  - Descuentos y bonificaciones

## Columnas del Reporte

1. **N** - Número correlativo
2. **ESPECIFICACION** - Tipo de factura (2 = Estándar)
3. **FECHA DE LA FACTURA**
4. **N DE LA FACTURA**
5. **CODIGO DE AUTORIZACION**
6. **NIT CI CLIENTE**
7. **COMPLEMENTO**
8. **NOMBRE O RAZON SOCIAL**
9. **IMPORTE TOTAL DE LA VENTA**
10. **IMPORTE ICE**
11. **IMPORTE IEHD**
12. **IMPORTE IPJ**
13. **TASAS**
14. **OTROS NO SUJETOS AL IVA**
15. **EXPORTACIONES Y OPERACIONES EXENTAS**
16. **VENTAS GRAVADAS A TASA CERO**
17. **SUBTOTAL**
18. **DESCUENTOS, BONIFICACIONES Y REBAJAS SUJETAS AL IVA**
19. **IMPORTE GIFT CARD**
20. **IMPORTE BASE PARA DEBITO FISCAL**
21. **DEBITO FISCAL**
22. **ESTADO** (V=Válida, A=Anulada, C=Contingencia, L=Libre consignación)
23. **CODIGO DE CONTROL**
24. **TIPO DE VENTA** (0=Otros, 1=Gift Card)

## Instalación

1. Copiar el módulo en el directorio de addons de Odoo
2. Actualizar lista de aplicaciones
3. Buscar "Libro de Ventas Bolivia V2"
4. Instalar el módulo

## Uso

### Configuración de Facturas

1. Ir a Contabilidad > Clientes > Facturas
2. Abrir una factura de cliente
3. En la pestaña "Libro de Ventas V2" completar:
   - Código de Autorización
   - Código de Control
   - Estado de la factura
   - Importes de impuestos especiales (si aplica)
   - Tipo de venta

### Generar Reporte

1. Ir a Contabilidad > Reportes > Libro de Ventas V2
2. Seleccionar rango de fechas
3. Seleccionar compañía (si es multicompañía)
4. Hacer clic en "Generar Reporte Excel"
5. Descargar archivo Excel generado

## Fórmulas de Cálculo

### Subtotal
```
SUBTOTAL = IMPORTE TOTAL - ICE - IEHD - IPJ - TASAS - OTROS NO IVA - EXPORTACIONES - VENTAS TASA CERO
```

### Importe Base para Débito Fiscal
```
IMPORTE BASE DF = SUBTOTAL - DESCUENTOS - GIFT CARD
```

### Débito Fiscal
```
DEBITO FISCAL = IMPORTE BASE DF * 0.13
```

## Dependencias

- `account` - Módulo de Contabilidad de Odoo
- `base` - Módulo base de Odoo

## Autor

WeCode Bolivia - [https://wecode.bo](https://wecode.bo)

## Licencia

LGPL-3

## Versión

18.0.1.0.0

## Notas

- Este módulo genera el reporte en formato Excel (.xlsx)
- Los montos se formatean con separador de miles (coma) y decimales (punto)
- Las fechas se formatean como DD/MM/YYYY
- El archivo generado cumple con las especificaciones de Impuestos Bolivia
