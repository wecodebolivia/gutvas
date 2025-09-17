from odoo import api, fields, models
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Entradas manuales (valores del Libro de Compras)
    lc_importe_total_compra = fields.Float(string="Importe Total Compra", default=0.0)
    lc_importe_ice = fields.Float(string="ICE", default=0.0)
    lc_importe_iehd = fields.Float(string="IEHD", default=0.0)
    lc_importe_ipj = fields.Float(string="IPJ", default=0.0)
    lc_tasas = fields.Float(string="Tasas", default=0.0)
    lc_otros_no_sujeto_cf = fields.Float(string="Otros no sujeto a CF", default=0.0)
    lc_importes_exentos = fields.Float(string="Importes Exentos", default=0.0)
    lc_compras_gravadas_tasa_cero = fields.Float(string="Compras Gravadas Tasa Cero", default=0.0)
    lc_descuentos_bonificaciones = fields.Float(string="Descuentos/Bonificaciones", default=0.0)
    lc_importe_gift_card = fields.Float(string="Importe Gift Card", default=0.0)

    # Calculados
    lc_subtotal = fields.Float(string="Subtotal LC", compute="_compute_lc_totals", store=False)
    lc_importe_base_cf = fields.Float(string="Base Crédito Fiscal", compute="_compute_lc_totals", store=False)
    lc_credito_fiscal = fields.Float(string="Crédito Fiscal", compute="_compute_lc_totals", store=False)

    @api.depends(
        'lc_importe_total_compra',
        'lc_importe_ice',
        'lc_importe_iehd',
        'lc_importe_ipj',
        'lc_tasas',
        'lc_otros_no_sujeto_cf',
        'lc_importes_exentos',
        'lc_compras_gravadas_tasa_cero',
        'lc_descuentos_bonificaciones',
        'lc_importe_gift_card',
        'move_id.move_type',
    )
    def _compute_lc_totals(self):
        """
        Asigna SIEMPRE valores a los 3 campos computados.
        La fórmula de ejemplo:
          subtotal = total_compra
                     - (ice + iehd + ipj + tasas + otros_no_sujeto_cf
                        + importes_exentos + compras_gravadas_tasa_cero
                        + descuentos_bonificaciones + gift_card)
          base_cf: por ahora = 0.0 (hasta que definamos regla exacta)
          credito_fiscal: por ahora = 0.0 (hasta que definamos regla exacta)
        """
        for line in self:
            # Asegurar que todos existan como floats
            total = float(line.lc_importe_total_compra or 0.0)
            ice = float(line.lc_importe_ice or 0.0)
            iehd = float(line.lc_importe_iehd or 0.0)
            ipj = float(line.lc_importe_ipj or 0.0)
            tasas = float(line.lc_tasas or 0.0)
            otros = float(line.lc_otros_no_sujeto_cf or 0.0)
            exentos = float(line.lc_importes_exentos or 0.0)
            tasa_cero = float(line.lc_compras_gravadas_tasa_cero or 0.0)
            desc = float(line.lc_descuentos_bonificaciones or 0.0)
            gift = float(line.lc_importe_gift_card or 0.0)

            subtotal = total - (ice + iehd + ipj + tasas + otros + exentos + tasa_cero + desc + gift)

            # Si no es vendor bill o refund, igual asignamos, pero podrías condicionar si lo prefieres
            # if line.move_id.move_type not in ('in_invoice', 'in_refund'):
            #     subtotal = 0.0

            # Por ahora dejamos la base y el crédito en 0.0 hasta definir reglas
            base_cf = 0.0
            credito = 0.0

            # Asignar SIEMPRE
            line.lc_subtotal = subtotal
            line.lc_importe_base_cf = base_cf
            line.lc_credito_fiscal = credito