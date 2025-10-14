# -*- coding: utf-8 -*-
# Copyright (C) 2025 Largotek SRL - Transformación Digital y Consultoría Lean
# Autor: Juan Luis Garvía Ossio <juan.garvia@largotek.com>
# Licencia: LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.html)

{
    "name": "MRP Sale Info",
    "summary": "Agrega información de ventas a los modelos de fabricación",
    "version": "18.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://www.largotek.com",
    "author": "Largotek SRL, Juan Luis Garvía Ossio",
    "maintainers": ["juanluisgarvia"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp",
        "sale_stock",
    ],
    "data": [
        "views/mrp_production.xml",
        "views/mrp_workorder.xml",
    ],
    "description": """
        MRP Sale Info
        --------------------
        Este módulo extiende los modelos de Fabricación (MRP) para incluir información
        de pedidos de venta relacionados, permitiendo una trazabilidad completa entre
        la orden de fabricación y el documento comercial de origen.

        📦 Funcionalidades principales:
        - Visualización de información de venta directamente en las órdenes de producción.
        - Integración nativa con `sale_stock`.
        - Mejora la trazabilidad y control de pedidos fabricados desde ventas.

        🏢 Desarrollado por:
        Largotek SRL – Transformación Digital y Consultoría Lean
        https://www.largotek.com
    """,
}
