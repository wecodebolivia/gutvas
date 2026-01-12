# -*- coding: utf-8 -*-
{
    'name': 'Libro de Compras Bolivia',
    'version': '18.0.1.0.1',
    'category': 'Accounting/Localizations',
    'summary': 'Libro de Compras para Bolivia con campos extendidos',
    'description': '''
        Módulo para gestionar el Libro de Compras de Bolivia.
        Agrega campos específicos del libro de compras en las líneas contables
        y permite generar reportes en formato Excel.
    ''',
    'author': 'WeCode Bolivia',
    'website': 'https://wecode.bo',
    'depends': ['account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_line_views.xml',
        'views/libro_compras_wizard_views.xml',
        'views/res_partner_views.xml',
        'views/report_libro_compras_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
