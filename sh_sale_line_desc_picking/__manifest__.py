# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Sale Order Line Description to Delivery Order",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Warehouse",
    "summary":
    "delivery address in sale order, invoice address delivery slip, customer address in quotation, manange quotation line module, sale order line description, manage sales order line odoo, invoice address in sale Odoo",
    "description": """
This module is useful to set invoice address, delivery address and customer address in delivery and set description from sale order line to picking operations.
delivery address in sale order, invoice address delivery slip, customer address in quotation, manange quotation line module, sale order line description, manage sales order line odoo, invoice address in sale app
                    """,
    "version": "15.0.4",
    "depends": ["sale_management", "stock"],
    "application": True,
    "data": ["views/stock_view.xml", "report/stock_report_templates.xml"],
    "images": [
        "static/description/background.png",
    ],
    "live_test_url": "https://youtu.be/QuOFHAgb_1I",
    "license": "OPL-1",
    "auto_install": False,
    "installable": True,
    "price": 25,
    "currency": "EUR"
}
