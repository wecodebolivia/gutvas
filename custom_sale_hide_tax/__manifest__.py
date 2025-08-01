# -*- coding: utf-8 -*-
{
    "name": "Hide Tax from Sale Orders",
    "version": "1.0",
    "category": "Sales",
    "summary": "Oculta la columna de impuestos y el resumen de impuestos en cotizaciones",
    "depends": ["sale"],
    "data": [
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
