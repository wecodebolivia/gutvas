# l10n_bo_purchase_book_line/models/libro_compras_wizard.py
from odoo import models, fields, api

class LibroComprasWizard(models.TransientModel):
    _name = 'libro.compras.wizard'
    _description = 'Asistente: Libro de Compras por Línea'

    move_line_id = fields.Many2one('account.move.line', string='Línea de Factura', required=True)

    # Lectura de proveedor
    lc_nit = fields.Char(string='NIT Proveedor', related='move_line_id.partner_id.lc_nit', readonly=True)
    lc_razon_social = fields.Char(string='Razón Social Proveedor', related='move_line_id.partner_id.lc_razon_social', readonly=True)

    # Copiamos los mismos campos del modelo para editar en el wizard
    lc_codigo_autorizacion = fields.Char(string='Código de Autorización')
    lc_numero_factura = fields.Char(string='Número de Factura')
    lc_numero_dui_dim = fields.Char(string='Número DUI/DIM')
    lc_fecha_factura = fields.Date(string='Fecha de Factura')

    lc_importe_total_compra = fields.Monetary(string='Importe Total Compra', currency_field='company_currency_id')
    lc_importe_ice = fields.Monetary(string='Importe ICE', currency_field='company_currency_id')
    lc_importe_iehd = fields.Monetary(string='Importe IEHD', currency_field='company_currency_id')
    lc_importe_ipj = fields.Monetary(string='Importe IPJ', currency_field='company_currency_id')
    lc_tasas = fields.Monetary(string='Tasas', currency_field='company_currency_id')
    lc_otros_no_sujeto_cf = fields.Monetary(string='Otros No Sujetos a CF', currency_field='company_currency_id')
    lc_importes_exentos = fields.Monetary(string='Importes Exentos', currency_field='company_currency_id')
    lc_compras_gravadas_tasa_cero = fields.Monetary(string='Compras Gravadas a Tasa Cero', currency_field='company_currency_id')
    lc_descuentos_bonificaciones = fields.Monetary(string='Descuentos y Bonificaciones', currency_field='company_currency_id')
    lc_importe_gift_card = fields.Monetary(string='Importe Gift Card', currency_field='company_currency_id')

    lc_importe_base_cf = fields.Monetary(string='Importe Base CF', currency_field='company_currency_id', readonly=True)
    lc_credito_fiscal = fields.Monetary(string='Crédito Fiscal (13%)', currency_field='company_currency_id', readonly=True)

    lc_tipo_compra = fields.Selection([
        ('cf', 'Con derecho a Crédito Fiscal'),
        ('sf', 'Sin derecho a Crédito Fiscal'),
        ('an', 'Anulación/Devolución'),
        ('tc', 'Tasa Cero'),
    ], string='Tipo de Compra', default='cf')

    lc_codigo_control = fields.Char(string='Código de Control')

    company_currency_id = fields.Many2one(related='move_line_id.company_currency_id', comodel_name='res.currency', readonly=True)

    @api.onchange(
        'lc_importe_total_compra', 'lc_importe_ice', 'lc_importe_iehd', 'lc_importe_ipj',
        'lc_tasas', 'lc_otros_no_sujeto_cf', 'lc_importes_exentos',
        'lc_compras_gravadas_tasa_cero', 'lc_descuentos_bonificaciones', 'lc_importe_gift_card'
    )
    def _onchange_recompute_totals(self):
        # Recalcular los totales en el wizard para vista previa
        total = self.lc_importe_total_compra or 0.0
        restas = sum([
            self.lc_importe_ice or 0.0,
            self.lc_importe_iehd or 0.0,
            self.lc_importe_ipj or 0.0,
            self.lc_tasas or 0.0,
            self.lc_otros_no_sujeto_cf or 0.0,
            self.lc_importes_exentos or 0.0,
            self.lc_compras_gravadas_tasa_cero or 0.0,
            self.lc_descuentos_bonificaciones or 0.0,
            self.lc_importe_gift_card or 0.0,
        ])
        base = max(total - restas, 0.0)
        self.lc_importe_base_cf = base
        self.lc_credito_fiscal = base * 0.13

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        line = self.env['account.move.line'].browse(res.get('move_line_id'))
        if line and line.exists():
            # precargar valores actuales de la línea
            for fname in [
                'lc_codigo_autorizacion', 'lc_numero_factura', 'lc_numero_dui_dim', 'lc_fecha_factura',
                'lc_importe_total_compra', 'lc_importe_ice', 'lc_importe_iehd', 'lc_importe_ipj', 'lc_tasas',
                'lc_otros_no_sujeto_cf', 'lc_importes_exentos', 'lc_compras_gravadas_tasa_cero',
                'lc_descuentos_bonificaciones', 'lc_importe_gift_card',
                'lc_importe_base_cf', 'lc_credito_fiscal', 'lc_tipo_compra', 'lc_codigo_control'
            ]:
                res[fname] = getattr(line, fname)
        return res

    def action_apply(self):
        self.ensure_one()
        self.move_line_id.write({
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
        })
        return {'type': 'ir.actions.act_window_close'}
