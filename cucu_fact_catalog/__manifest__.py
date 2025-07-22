# -*- coding: utf-8 -*-
#################################################################################
# Author      : cucu (https://cucu.bo)
# Copyright(c): 2021-Present cucu | soluciones digitales
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#################################################################################
{
    "name": "cucu | Fact Catalog",
    "summary": """Facturacion en Linea - Bolivia - CUCU""",
    "description": """Modulo de facturacion en linea para Bolivia - CUCU""",
    "author": "cucu",
    "website": "https://cucu.bo",
    "category": "Uncategorized",
    "version": "1.0",
    "depends": ["base", "product", "account"],
    "data": [
        "security/rule_security.xml",
        "security/ir.model.access.csv",
        "views/view_catalog_unit_measure.xml",
        "views/view_catalog_event_significant.xml",
        "views/view_catalog_point_of_sale.xml",
        "views/view_catalog_product_service.xml",
        "views/view_catalog_activities.xml",
        "views/view_catalog_method_payment.xml",
        "views/view_catalog_currency.xml",
        "views/view_product_template.xml",
        "views/view_product_product.xml",
        "views/view_account_journal.xml",
    ],
}
