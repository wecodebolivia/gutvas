# -*- coding: utf-8 -*-
{
    'name': 'CUCU Facturación Core - Extendido',
    'version': '18.0.1.1.0',
    'category': 'Accounting/Localizations',
    'summary': 'Extensión de CUCU para truncar descripciones a 150 caracteres',
    'description': """
Extensión para módulo cucu_fact_core
====================================

Funcionalidades:
- Trunca descripciones de productos a 150 caracteres max
- Cumple con requisitos del webservice SIN de Bolivia
- No modifica el código original de CUCU
- Mantiene compatibilidad con futuras actualizaciones de CUCU
- Usa herencia de métodos para extender funcionalidad
- Validación numérica para campo Number Document (nit_client)

Problema resuelto:
------------------
El servicio web de facturación SIN tiene un límite de 150 caracteres
para el campo descripción. Cuando las descripciones son más largas,
el webservice rechaza la factura.

Esta extensión trunca automáticamente cualquier descripción que exceda
los 150 caracteres antes de enviarla al webservice.

Además valida que el campo Number Document solo contenga números.

Desarrollado por: Largotek SRL
Autor: Juan Luis Garvía
    """,
    'author': 'Largotek SRL',
    'website': 'https://largotek.com',
    'depends': ['cucu_fact_core', 'cucu_fact_partner'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
