{
    'name': 'Libro de Compras Línea por Línea',
    'version': '18.0.1.1.0',
    'category': 'Accounting',
    'summary': 'Campos de Libro de Compras por línea con identidad resuelta (NIT/Razón Social).',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
        'views/res_partner_views.xml',          # <-- asegurar que esté
        'views/report_libro_compras_views.xml',
        'views/libro_compras_wizard_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
