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

    # === Nuevo campo para el reporte ===
    sale_line_description = fields.Text(
        string="Sale Line Description",
        compute="_compute_sale_line_description",
        store=False,
        help="Descripción consolidada de las líneas de venta relacionadas "
             "con este producto en el pedido de venta de origen."
    )

    @api.depends("sale_id", "product_id",
                 "sale_id.order_line.product_id", "sale_id.order_line.name")
    def _compute_sale_line_description(self):
        """
        Construye una descripción a partir de las líneas del SO que
        coinciden con el producto de la MO. Si no hay coincidencias,
        deja vacío (esto evita KeyError en QWeb).
        """
        for mo in self:
            desc = ""
            if mo.sale_id and mo.product_id:
                # Filtra líneas del pedido vinculadas al producto fabricado
                lines = mo.sale_id.order_line.filtered(
                    lambda l: l.product_id == mo.product_id
                )
                # Si hay varias líneas (mismo producto con distintas descripciones),
                # concatenamos cada 'name' en líneas separadas.
                names = [ln.name.strip() for ln in lines if (ln.name or "").strip()]
                if names:
                    desc = "\n".join(names)
            mo.sale_line_description = desc
