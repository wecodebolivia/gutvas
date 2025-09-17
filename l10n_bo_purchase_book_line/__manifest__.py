# l10n_bo_purchase_book_line/__manifest__.py
{
    'name': 'Libro de Compras Línea por Línea (BO)',
    'version': '18.0.1.0.1',
    'category': 'Accounting/Localizations',
    'summary': 'Campos del Libro de Compras por línea en facturas de proveedor.',
    'description': """
Extiende las líneas de factura de proveedor (account.move.line) para capturar
los campos del Libro de Compras exigidos por el SIN (Bolivia), agrega un
asistente por línea, y un reporte XLSX por rango de fechas.
    """,
    'author': 'Largotek SRL',
    'website': 'https://largotek.com',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/report_libro_compras_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
