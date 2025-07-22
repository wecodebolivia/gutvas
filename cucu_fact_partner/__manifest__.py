# -*- coding: utf-8 -*-
{
    "name": "cucu | Fact Partner",
    "summary": """cucu | Fact Partner""",
    "author": "Daniel",
    "website": "https://cucu.bo",
    "category": "Point of Sale",
    "version": "1.0",
    "depends": ["base", "point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "data/documents.xml",
        "views/view_res_users.xml",
        "views/view_res_partner.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [],
    },
}
