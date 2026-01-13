# -*- coding: utf-8 -*-
{
    "name": "Sale Order Total Weight",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Muestra el peso total de productos en cotizaciones y órdenes de venta",
    "description": """
        Sale Order Total Weight
        =======================
        Este módulo calcula y muestra el peso total de todos los productos
        incluidos en una cotización u orden de venta.
        
        El peso se obtiene del campo 'weight' configurado en la pestaña
        Inventario de cada producto.
        
        Características:
        ----------------
        - Cálculo automático del peso total basado en cantidad × peso unitario
        - Campo visible en la vista de formulario de cotización/orden de venta
        - Actualización en tiempo real al agregar/modificar líneas
    """,
    "author": "Juan Luis Garvía - Largotek SRL",
    "website": "https://www.largotek.com",
    "maintainer": "info@largotek.com",
    "depends": ["sale_management", "stock"],
    "data": [
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "LGPL-3",
}
