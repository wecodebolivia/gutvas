# -*- coding: utf-8 -*-
{
    "name": "Libro de Compras - Línea por Línea (BO)",
    "version": "18.0.1.0.0",
    "summary": "Campos y asistente para capturar datos del Libro de Compras por línea",
    "author": "Tu Equipo",
    "license": "LGPL-3",
    "category": "Accounting/Localizations",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        # vistas del asistente (formulario modal)
        "views/libro_compras_wizard_views.xml",
        # (opcional) tus otras vistas heredadas para el botón en account.move.line
        # "views/account_move_line_views.xml",
    ],
    "installable": True,
}
