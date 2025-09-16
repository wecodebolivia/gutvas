# l10n_bo_purchase_book_line/models/libro_compras_wizard.py
from odoo import models, fields, api

class LibroComprasWizard(models.TransientModel):
    _name = 'libro.compras.wizard'
    _description = 'Wizard para el Libro de Compras'

    move_line_id = fields.Many2one('account.move.line', string='Línea contable', required=True)

    # Datos del proveedor (solo lectura desde partner)
    lc_nit = fields.Char(string='NIT', related='move_line_id.partner_id.lc_nit', readonly=True)
    lc_razon_social = fields.Char(string='Razón Social', related='move_line_id.partner_id.lc_razon_social', readonly=True)

    # Información de la factura/compra
    lc_codigo_autorizacion = fields.Char(string='Código de Autorización')
    lc_numero_factura = fields.Char(string='Número de Factura')
    lc_numero_dui_dim = fields.Char(string='Número DUI/DIM')
    lc_fecha_factura = fields.Date(string='Fecha de Factura')

    lc_importe_total_compra = fields.Monetary(string='Importe Total Compra', currency_field='currency_id')
    lc_importe_ice = fields.Monetary(string='Importe ICE', currency_field='currency_id')
    lc_importe_iehd = fields.Monetary(string='Importe IEHD', currency_field='currency_id')
    lc_importe_ipj = fields.Monetary(string='Importe IPJ', currency_field='currency_id')
    lc_tasas = fields.Monetary(string='Tasas', currency_field='currency_id')
    lc_otros_no_sujeto_cf = fields.Monetary(string='No Sujetos a CF', currency_field='currency_id')
    lc_importes_exentos = fields.Monetary(string='Importes Exentos', currency_field='currency_id')
    lc_compras_gravadas_tasa_cero = fields.Monetary(string='Compras Gravadas 0%', currency_field='currency_id')
    lc_descuentos_bonificaciones = fields.Monetary(string='Descuentos/Bonificaciones', currency_field='currency_id')
    lc_importe_gift_card = fields.Monetary(string='Importe Gift Card', currency_field='currency_id')

    lc_importe_base_cf = fields.Monetary(string='Importe Base CF', currency_field='currency_id', compute='_compute_importe_base_cf')
    lc_credito_fiscal = fields.Monetary(string='Crédito Fiscal (13%)', currency_field='currency_id', compute='_compute_credito_fiscal')

    lc_tipo_compra = fields.Selection([
        ('1', 'Con Derecho a Crédito Fiscal'),
        ('2', 'Sin Derecho a Crédito Fiscal'),
        ('3', 'Gastos No Deducibles'),
    ], string='Tipo de Compra', default='1')

    lc_codigo_control = fields.Char(string='Código de Control')

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        line = self.env['account.move.line'].browse(self.env.context.get('default_move_line_id'))
        if line and line.exists():
            for fname in [
                'lc_codigo_autorizacion','lc_numero_factura','lc_numero_dui_dim','lc_fecha_factura',
                'lc_importe_total_compra','lc_importe_ice','lc_importe_iehd','lc_importe_ipj','lc_tasas',
                'lc_otros_no_sujeto_cf','lc_importes_exentos','lc_compras_gravadas_tasa_cero',
                'lc_descuentos_bonificaciones','lc_importe_gift_card','lc_tipo_compra','lc_codigo_control'
            ]:
                res[fname] = line[fname]
        return res

    def _compute_importe_base_cf(self):
        for w in self:
            base = (w.lc_importe_total_compra or 0.0)
            base -= (w.lc_importe_ice or 0.0)
            base -= (w.lc_importe_iehd or 0.0)
            base -= (w.lc_importe_ipj or 0.0)
            base -= (w.lc_tasas or 0.0)
            base -= (w.lc_otros_no_sujeto_cf or 0.0)
            base -= (w.lc_importes_exentos or 0.0)
            base -= (w.lc_compras_gravadas_tasa_cero or 0.0)
            base -= (w.lc_descuentos_bonificaciones or 0.0)
            base -= (w.lc_importe_gift_card or 0.0)
            w.lc_importe_base_cf = base

    def _compute_credito_fiscal(self):
        for w in self:
            w.lc_credito_fiscal = (w.lc_importe_base_cf or 0.0) * 0.13

    def action_guardar(self):
        self.ensure_one()
        if not self.move_line_id:
            return
        vals = {
            'lc_codigo_autorizacion': self.lc_codigo_autorizacion,
            'lc_numero_factura': self.lc_numero_factura,
            'lc_numero_dui_dim': self.lc_numero_dui_dim,
            'lc_fecha_factura': self.lc_fecha_factura,
            'lc_importe_total_compra': self.lc_importe_total_compra,
            'lc_importe_ice': self.lc_importe_ice,
            'lc_importe_iehd': self.lc_importe_iehd,
            'lc_importe_ipj': self.lc_importe_ipj,
            'lc_tasas': self.lc_tasas,
            'lc_otros_no_sujeto_cf': self.lc_otros_no_sujeto_cf,
            'lc_importes_exentos': self.lc_importes_exentos,
            'lc_compras_gravadas_tasa_cero': self.lc_compras_gravadas_tasa_cero,
            'lc_descuentos_bonificaciones': self.lc_descuentos_bonificaciones,
            'lc_importe_gift_card': self.lc_importe_gift_card,
            'lc_tipo_compra': self.lc_tipo_compra,
            'lc_codigo_control': self.lc_codigo_control,
        }
        self.move_line_id.write(vals)
        return {'type': 'ir.actions.act_window_close'}
