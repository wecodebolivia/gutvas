# l10n_bo_purchase_book_line/__manifest__.py
{
    "name": "Libro de Compras Bolivia",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Agrega campos del libro de compras boliviano en facturas de proveedor",
    "depends": ["account"],
"data": [
    "views/account_move_views.xml",
    "views/res_partner_views.xml",
    "views/report_libro_compras_views.xml",
    # "security/ir.model.access.csv",  ← ← ← comenta esta línea por ahora
],
   
    "application": False,
    "installable": True,
}
