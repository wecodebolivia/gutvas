# -*- coding: utf-8 -*-
{
    'name': 'Libro de Ventas Bolivia V2',
    'version': '18.0.1.0.1',
    'category': 'Accounting/Localizations',
    'summary': 'Reporte de Libro de Ventas formato estándar Impuestos Bolivia V2',
    'description': '''
        Módulo para generar el Libro de Ventas en formato Excel
        según especificaciones del Servicio de Impuestos Nacionales de Bolivia.
        Versión 2 con formato estándar actualizado.
    ''',
    'author': 'WeCode Bolivia',
    'website': 'https://wecode.bo',
    'depends': ['account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/sale_book_v2_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
