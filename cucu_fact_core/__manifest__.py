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
    "name": "cucu | Fact Core",
    "summary": """Facturacion en Linea - Bolivia -CUCU""",
    "description": """Modulo de facturacion en linea para Bolivia - CUCU""",
    "author": "cucu",
    "website": "https://cucu.bo",
    "category": "Uncategorized",
    "version": "1.0",
    "depends": [
        "base",
        "point_of_sale",
        "account",
        "product",
        "cucu_fact_partner",
        "cucu_fact_catalog",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/rule_security.xml",
        "wizard/invoice_report.xml",
        "wizard/account_move_anulation.xml",
        "views/view_cucu_manager.xml",
        "views/view_branch_office.xml",
        "views/view_pos.xml",
        "views/view_res_company.xml",
        "views/view_pos_config_setting.xml",
        "views/view_account_move.xml",
        # "views/view_event.xml",
        "views/menu_fact.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cucu_fact_core/static/src/js/card_field/card_field.js",
            "cucu_fact_core/static/src/js/card_field/card_field.xml",
            # "cucu_fact_core/static/src/js/tree_branch_button.js",
            # 'cucu_fact_core/static/src/js/kanban_branch_button.js',
            # "cucu_fact_core/static/src/xml/tree_branch_button.xml",
            # 'cucu_fact_core/static/src/xml/kanban_branch_button.xml',
        ]
    },
    "external_dependencies": {
        "python": ["xmltodict", "XlsxWriter"],
    },
}
