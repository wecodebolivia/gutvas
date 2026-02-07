# -*- coding: utf-8 -*-
{
    'name': 'CUCU Facturación - Reportes Extendidos',
    'version': '18.0.1.0.1',
    'category': 'Accounting/Localizations/Reporting',
    'summary': 'Extensión de reportes CUCU para ocultar descripciones en impresiones',
    'description': """
Extensión para módulo cucu_fact_report
======================================

Funcionalidades:
- Oculta el campo de descripción en facturas formato A4
- Oculta el campo de descripción en facturas formato ticket
- No modifica el código original de CUCU
- Mantiene compatibilidad con futuras actualizaciones de CUCU

Desarrollado por: Largotek SRL
Autor: Juan Luis Garvía
    """,
    'author': 'Largotek SRL',
    'website': 'https://largotek.com',
    'depends': ['cucu_fact_report'],
    'data': [
        'views/report_template_a4_ext.xml',
        'views/ticket_template_ext.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
