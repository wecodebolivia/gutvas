# CUCU Facturación - Reportes Extendidos

## Descripción

Módulo de extensión para `cucu_fact_report` que oculta el campo de descripción del producto en las facturas impresas.

## Características

- ✅ Oculta descripciones en formato A4
- ✅ Oculta descripciones en formato ticket
- ✅ No modifica código original de CUCU
- ✅ Compatible con futuras actualizaciones
- ✅ Usa herencia de vistas con XPath

## Instalación

1. Asegurar que `cucu_fact_report` esté instalado
2. Actualizar lista de aplicaciones
3. Buscar "CUCU Facturación - Reportes Extendidos"
4. Instalar el módulo

## Uso

Una vez instalado, el módulo automáticamente:
- Oculta las descripciones en facturas formato A4
- Oculta las descripciones en facturas formato ticket

No requiere configuración adicional.

## Desinstalación

Si desinstala este módulo, las descripciones volverán a mostrarse en las facturas sin afectar el módulo base de CUCU.

## Soporte

**Desarrollado por:** Largotek SRL  
**Autor:** Juan Luis Garvía  
**Versión:** 18.0.1.0.0  
**Licencia:** LGPL-3

## Estructura del módulo

```
cucu_fact_report_ext/
├── __init__.py
├── __manifest__.py
├── README.md
└── views/
    ├── report_template_a4_ext.xml
    └── ticket_template_ext.xml
```
