# l10n_bo_purchase_book_line/__manifest__.py

{
    'name': 'Libro de Compras Línea por Línea',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Registro de campos del libro de compras línea por línea en asientos contables.',
    'description': """
        Este módulo permite registrar los campos del libro de compras línea por línea en los asientos contables.
    """,
    'author': 'Tu Nombre',
    'website': 'https://tusitio.com',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/report_libro_compras_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
