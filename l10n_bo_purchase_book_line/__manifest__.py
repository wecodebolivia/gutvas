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
    "wizard/libro_compras_wizard_views.xml",   # debe existir (ya lo tienes)
    "views/account_move_form_lines_lc.xml",
    "views/account_move_form_button_lc.xml",
],

    "installable": True,
    "application": False,
}
