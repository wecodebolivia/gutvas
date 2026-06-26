# -*- coding: utf-8 -*-
{
    "name": "cucu | Fact Nota Débito/Crédito",
    "summary": """Emisión de Notas de Débito/Crédito electrónicas hacia SIAT - Bolivia""",
    "description": """Permite emitir Notas de Débito/Crédito electrónicas al SIAT desde facturas rectificadas en Odoo 18.""",
    "author": "Largotek SRL",
    "website": "https://largotek.com",
    "category": "Accounting",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
        "account",
        "cucu_fact_core",
        "cucu_fact_core_ext",
    ],
    "data": [
        "views/view_account_move_debit_credit.xml",
    ],
}
