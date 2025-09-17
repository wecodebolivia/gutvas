# l10n_bo_purchase_book_line/__manifest__.py
{
    "name": "Libro de Compras Bolivia",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Agrega campos del libro de compras boliviano en facturas de proveedor",
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
        "security/ir.model.access.csv",
    ],
    "application": False,
    "installable": True,
}
