# -*- coding: utf-8 -*-
{
    "name": "cucu | Report PDF",
    "summary": """REPORT PDF CUCU""",
    "description": """Long description of module's purpose""",
    "author": "CUCU API LLC",
    "website": "https://cucuapi.com/shop/modulo-facturacion-electronica-siat-bolivia-13#attr=15",
    "category": "Uncategorized",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base", "cucu_fact_core"],
    "data": [
        "reports/report_a4_action.xml",
        "reports/report_ticket_action.xml",
        "reports/report_template_a4.xml",
        "reports/report_template_a4_note.xml",
        "reports/ticket_template.xml",
        "reports/ticket_template_note.xml",
        "reports/report_template_account.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "cucu_fact_report/static/src/css/fonts/font.css",
            "cucu_fact_report/static/src/css/tail.css",
        ],
    },
    "application": False,
}
