# -*- coding: utf-8 -*-
{
    "name": "Libro de Compras - Línea por línea",
    "version": "18.0.1.1.1",
    "summary": "Modal del Libro de Compras por línea con identidad resuelta (NIT/Razón Social).",
    "category": "Accounting",
    "author": "Largotek",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        # vistas de bajo riesgo primero
        "security/ir.model.access.csv",
        "views/libro_compras_wizard_views.xml",
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
}
