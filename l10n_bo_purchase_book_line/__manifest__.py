# l10n_bo_purchase_book_line/__manifest__.py
{
    'name': 'Libro de Compras Línea por Línea',
    'version': '18.0.1.1.0',
    'category': 'Accounting',
    'summary': 'Campos del Libro de Compras en líneas contables + asistente y reporte Excel',
    'description': '''
Módulo para registrar campos del Libro de Compras por línea en asientos/ facturas,
editar desde un asistente, y generar un reporte en Excel por rango de fechas.
    ''',
    'author': 'Largotek SRL',
    'website': 'https://largotek.com',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/account_move_line_views.xml',
        'views/libro_compras_wizard_views.xml',
        'views/report_libro_compras_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
