# l10n_bo_purchase_book_line/__manifest__.py
{
    'name': 'Libro de Compras Línea por Línea (BO)',
    'version': '18.0.1.0.2',
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
        # Wizard y acción en modal
        'views/libro_compras_wizard_views.xml',
        # Botón en el tree base de account.move.line (robusto)
        'views/account_move_line_tree_views.xml',
        # Datos en partner (si los usas)
        'views/res_partner_views.xml',
        # Menú/acción del reporte
        'views/report_libro_compras_views.xml',
        # ⚠️ Omitimos el heredado del form para evitar xpath frágil:
        # 'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
