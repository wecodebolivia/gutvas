# -*- coding: utf-8 -*-
{
    'name': 'Libro de Ventas Bolivia V2',
    'version': '18.0.1.0.3',
    'category': 'Accounting/Localizations',
    'summary': 'Reporte de Libro de Ventas Bolivia',
    'description': 'Módulo para generar reportes de Libro de Ventas en Excel',
    'author': 'WeCode Bolivia',
    'website': 'https://wecode.bo',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/sale_book_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
