# -*- coding: utf-8 -*-
from odoo import api, fields, models

class LibroComprasWizard(models.TransientModel):
    _name = "libro.compras.wizard"
    _description = "Wizard para el Libro de Compras"

    move_line_id = fields.Many2one("account.move.line", string="Línea de Asiento", required=True, ondelete="cascade")

    # ---- Datos del contacto (solo lectura) ----
    lc_nit = fields.Char(string="NIT", readonly=True, compute="_compute_partner_info")
    lc_razon_social = fields.Char(string="Razón Social", readonly=True, compute="_compute_partner_info")

    # ---- Información (campos que vamos a escribir en la línea) ----
    lc_codigo_autorizacion = fields.Char(string="Código de Autorización")
    lc_numero_factura = fields.Char(string="Número de Factura")
    lc_numero_dui_dim = fields.Char(string="Número DUI/DIM")
    lc_fecha_factura = fields.Date(string="Fecha de Factura")

    currency_id = fields.Many2one(related="move_line_id.company_id.currency_id", readonly=True, store=False)

    lc_importe_total_compra = fields.Monetary(string="Importe Total Compra", currency_field="currency_id")
    lc_importe_ice = fields.Monetary(string="Importe ICE", currency_field="currency_id")
    lc_importe_iehd = fields.Monetary(string="Importe IEHD", currency_field="currency_id")
    lc_importe_ipj = fields.Monetary(string="Importe IPJ", currency_field="currency_id")
    lc_tasas = fields.Monetary(string="Tasas", currency_field="currency_id")
    lc_otros_no_sujeto_cf = fields.Monetary(string="Otros No Sujeto a CF", currency_field="currency_id")
    lc_importes_exentos = fields.Monetary(string="Importes Exentos", currency_field="currency_id")
    lc_compras_gravadas_tasa_cero = fields.Monetary(string="Compras Gravadas a Tasa Cero", currency_field="currency_id")
    lc_descuentos_bonificaciones = fields.Monetary(string="Descuentos y Bonificaciones", currency_field="currency_id")
    lc_importe_gift_card = fields.Monetary(string="Importe Gift Card", currency_field="currency_id")

    lc_tipo_compra = fields.Selection([
        ("CF", "Con Crédito Fiscal"),
        ("SF", "Sin Crédito Fiscal"),
        ("AN", "Anulada"),
    ], string="Tipo de Compra", default="CF")

    lc_codigo_control = fields.Char(string="Código de Control")

    # -------- Prefills --------
    @api.depends("move_line_id.partner_id", "move_line_id.partner_id.vat",
                 "move_line_id.partner_id.name",
                 "move_line_id.partner_id.lc_nit",
                 "move_line_id.partner_id.lc_razon_social")
    def _compute_partner_info(self):
        for wiz in self:
            partner = wiz.move_line_id.partner_id
            wiz.lc_nit = partner.lc_nit or partner.vat or ""
            wiz.lc_razon_social = partner.lc_razon_social or partner.name or ""

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        move_line = None
        if res.get("move_line_id"):
            move_line = self.env["account.move.line"].browse(res["move_line_id"])
        else:
            ml_id = self.env.context.get("default_move_line_id")
            if ml_id:
                move_line = self.env["account.move.line"].browse(ml_id)
                res["move_line_id"] = ml_id

        if move_line:
            move = move_line.move_id

            # Prefills típicos:
            res.setdefault("lc_fecha_factura", move.invoice_date or move_line.date or fields.Date.today())
            # En muchas localizaciones el número de factura suele guardarse en ref o payment_reference
            res.setdefault("lc_numero_factura", move.ref or move.payment_reference or move.name or "")
            # Monto total: si la línea es de gasto, usamos abs(balance) como aproximación
            # (ajústalo a tu lógica si ya distribuyes por línea)
            total = move_line.amount_currency if move_line.currency_id else move_line.balance
            res.setdefault("lc_importe_total_compra", abs(total))

            # Zeros por defecto para evitar compute vacíos
            for fname in [
                "lc_importe_ice", "lc_importe_iehd", "lc_importe_ipj", "lc_tasas",
                "lc_otros_no_sujeto_cf", "lc_importes_exentos",
                "lc_compras_gravadas_tasa_cero", "lc_descuentos_bonificaciones",
                "lc_importe_gift_card"
            ]:
                res.setdefault(fname, 0.0)

        return res

    # -------- Aplicar (guardar en la línea) --------
    def action_apply(self):
        self.ensure_one()
        self.move_line_id.write({
            "lc_codigo_autorizacion": self.lc_codigo_autorizacion,
            "lc_numero_factura": self.lc_numero_factura,
            "lc_numero_dui_dim": self.lc_numero_dui_dim,
            "lc_fecha_factura": self.lc_fecha_factura,
            "lc_importe_total_compra": self.lc_importe_total_compra,
            "lc_importe_ice": self.lc_importe_ice,
            "lc_importe_iehd": self.lc_importe_iehd,
            "lc_importe_ipj": self.lc_importe_ipj,
            "lc_tasas": self.lc_tasas,
            "lc_otros_no_sujeto_cf": self.lc_otros_no_sujeto_cf,
            "lc_importes_exentos": self.lc_importes_exentos,
            "lc_compras_gravadas_tasa_cero": self.lc_compras_gravadas_tasa_cero,
            "lc_descuentos_bonificaciones": self.lc_descuentos_bonificaciones,
            "lc_importe_gift_card": self.lc_importe_gift_card,
            "lc_tipo_compra": self.lc_tipo_compra,
            "lc_codigo_control": self.lc_codigo_control,
        })
        return {"type": "ir.actions.act_window_close"}
