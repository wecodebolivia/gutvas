{
    "name": "Libro de Compras - Línea por Línea",
    "version": "16.0.1.0.0",  # o tu versión
    "summary": "Campos y acción para libro de compras en facturas de proveedor",
    "author": "Tu Empresa",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/libro_compras_wizard_views.xml",
        "views/account_move_form_lines_lc.xml",
        "views/account_move_form_button_lc.xml",
    ],
    "installable": True,
    "application": False,
}
