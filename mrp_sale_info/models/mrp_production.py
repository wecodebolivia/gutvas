# -*- coding: utf-8 -*-
# Copyright 2016 Antiun Ingenieria S.L.
# Copyright 2019 Rubén Bravo
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Modificaciones 2025 Largotek SRL - Juan Luis Garvía Ossio
# Licencia: LGPL-3

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    source_procurement_group_id = fields.Many2one(
        comodel_name="procurement.group",
        readonly=True,
    )

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale order",
        readonly=True,
        store=True,
        related="source_procurement_group_id.sale_id",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_id.partner_id",
        string="Customer",
        store=True,
        readonly=True,
    )

    commitment_date = fields.Datetime(
        related="sale_id.commitment_date",
        string="Commitment Date",
        store=True,
        readonly=True,
    )

    client_order_ref = fields.Char(
        related="sale_id.client_order_ref",
        string="Customer Reference",
        store=True,
        readonly=True,
    )

    # === NUEVO: Vendedor (para evitar KeyError en QWeb) ===
    custom_sale_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        related="sale_id.user_id",
        store=True,
        readonly=True,
        help="Vendedor del pedido de venta de origen.",
    )

    # === Opcional/NUEVO: Texto para impresión tomado del SO ===
    sale_line_description = fields.Text(
        string="Sale Line Description",
        compute="_compute_sale_line_description",
        store=False,
        help="Descripción consolidada de las líneas del pedido de venta "
             "que corresponden al producto fabricado.",
    )

    @api.depends(
        "sale_id",
        "product_id",
        "sale_id.order_line.product_id",
        "sale_id.order_line.name",
    )
    def _compute_sale_line_description(self):
        """Concatena las 'name' de las líneas del SO cuyo product_id coincide con el de la MO."""
        for mo in self:
            desc = ""
            if mo.sale_id and mo.product_id:
                lines = mo.sale_id.order_line.filtered(
                    lambda l: l.product_id == mo.product_id
                )
                names = [ (l.name or "").strip() for l in lines if (l.name or "").strip() ]
                if names:
                    desc = "\n".join(names)
            mo.sale_line_description = desc
