# l10n_bo_purchase_book_line/__manifest__.py
{
    "name": "Libro de Compras Línea por Línea (BO)",
    "version": "18.0.1.0.3",
    "category": "Accounting/Localizations",
    "summary": "Campos del Libro de Compras por línea en facturas de proveedor.",
    "author": "Largotek SRL",
    "website": "https://largotek.com",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_line_tree_views.xml",
        "wizard/libro_compras_wizard_views.xml",  # <- ruta correcta
    ],
    "installable": True,
    "application": False,
}
