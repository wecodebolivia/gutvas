# -*- coding: utf-8 -*-
# Copyright (C) 2025
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # ---- Campos manuales (NO usar default para evitar UPDATE masivo al instalar) ----
    lc_importe_total_compra = fields.Float(
        string='Importe Total Compra', digits=(16, 2),
        help='Importe total de la compra según documento del proveedor.'
    )
    lc_importe_ice = fields.Float(
        string='Importe ICE', digits=(16, 2),
        help='Impuesto al Consumo Específico (ICE) no sujeto a crédito fiscal.'
    )
    lc_importe_iehd = fields.Float(
        string='Importe IEHD', digits=(16, 2),
        help='Impuesto a los Hidrocarburos y sus Derivados (IEHD).'
    )
    lc_importe_ipj = fields.Float(
        string='Importe IPJ', digits=(16, 2),
        help='Impuesto a la Participación en Juegos (IPJ).'
    )
    lc_tasas = fields.Float(
        string='Tasas', digits=(16, 2),
        help='Tasas y otros tributos no sujetos a crédito fiscal.'
    )
    lc_otros_no_sujeto_cf = fields.Float(
        string='Otros No Sujetos a CF', digits=(16, 2),
        help='Otros importes no sujetos a crédito fiscal.'
    )
    lc_importes_exentos = fields.Float(
        string='Importes Exentos', digits=(16, 2),
        help='Importes exentos según normativa.'
    )
    lc_compras_gravadas_tasa_cero = fields.Float(
        string='Compras Gravadas Tasa Cero', digits=(16, 2),
        help='Compras gravadas a tasa cero.'
    )
    lc_descuentos_bonificaciones = fields.Float(
        string='Descuentos y Bonificaciones', digits=(16, 2),
        help='Descuentos, bonificaciones y rebajas sujetas al documento.'
    )
    lc_importe_gift_card = fields.Float(
        string='Importe Gift Card', digits=(16, 2),
        help='Importe cancelado mediante gift card (no sujeto a CF).'
    )

    # ---- Campos calculados (sin store para no llenar la tabla al instalar) ----
    lc_subtotal = fields.Float(
        string='Subtotal', digits=(16, 2),
        compute='_compute_l10n_bo_purchase_book',
        help='Subtotal sujeto a base de cálculo, luego de restar conceptos no CF.'
    )
    lc_importe_base_cf = fields.Float(
        string='Importe Base CF', digits=(16, 2),
        compute='_compute_l10n_bo_purchase_book',
        help='Base de crédito fiscal (referencial).'
    )
    lc_credito_fiscal = fields.Float(
        string='Crédito Fiscal', digits=(16, 2),
        compute='_compute_l10n_bo_purchase_book',
        help='Crédito fiscal estimado sobre la base (13% por defecto).'
    )

    @api.depends(
        'lc_importe_total_compra',
        'lc_importe_ice', 'lc_importe_iehd', 'lc_importe_ipj',
        'lc_tasas', 'lc_otros_no_sujeto_cf',
        'lc_importes_exentos', 'lc_compras_gravadas_tasa_cero',
        'lc_descuentos_bonificaciones', 'lc_importe_gift_card',
    )
    def _compute_l10n_bo_purchase_book(self):
        """
        Cálculo simple y seguro (no persistido):
        subtotal = total_compra - (rubros no CF, exentos, tasa cero, descuentos, gift card)
        base_cf = subtotal
        crédito_fiscal = 13% de base_cf (ajusta la tasa si tu normativa exige otra)
        """
        VAT_RATE = 0.13  # Ajusta si corresponde a tu localización

        def v(x):
            return x or 0.0
