# l10n_bo_purchase_book_line/models/libro_compras_wizard.py

from odoo import models, fields, api

class LibroComprasWizard(models.TransientModel):
    _name = 'libro.compras.wizard'
    _description = 'Wizard para el Libro de Compras'

    move_line_id = fields.Many2one('account.move.line', string='Línea de Asiento', required=True)

    # Campos del proveedor
    lc_nit = fields.Char(string='NIT', related='move_line_id.partner_id.lc_nit', readonly=True)
    lc_razon_social = fields.Char(string='Razón Social', related='move_line_id.partner_id.lc_razon_social', readonly=True)

    # Grupo 1: Información General
    lc_codigo_autorizacion = fields.Char(string='Código de Autorización')
    lc_numero_factura = fields.Char(string='Número de Factura')
    lc_numero_dui_dim = fields.Char(string='Número DUI/DIM')
    lc_fecha_factura = fields.Date(string='Fecha de Factura')
    lc_importe_total_compra = fields.Float(string='Importe Total Compra', digits=(16, 2))
    lc_importe_ice = fields.Float(string='Importe ICE', digits=(16, 2))
    lc_importe_iehd = fields.Float(string='Importe IEHD', digits=(16, 2))
    lc_importe_ipj = fields.Float(string='Importe IPJ', digits=(16, 2))
    lc_tasas = fields.Float(string='Tasas', digits=(16, 2))
    lc_otros_no_sujeto_cf = fields.Float(string='Otros No Sujeto a CF', digits=(16, 2))

    # Grupo 2: Detalles Adicionales
    lc_importes_exentos = fields.Float(string='Importes Exentos', digits=(16, 2))
    lc_compras_gravadas_tasa_cero = fields.Float(string='Compras Gravadas a Tasa Cero', digits=(16, 2))
    lc_descuentos_bonificaciones = fields.Float(string='Descuentos/Bonificaciones', digits=(16, 2))
    lc_importe_gift_card = fields.Float(string='Importe Gift Card', digits=(16, 2))
    lc_tipo_compra = fields.Selection([
        ('1', 'Actividad gravada'),
        ('2', 'Actividad no gravada'),
        ('3', 'Sujetas a proporcionalidad'),
        ('4', 'Exportaciones'),
        ('5', 'Interno/Exportaciones')
    ], string='Tipo de Compra', default='1')
    lc_codigo_control = fields.Char(string='Código de Control')

    # Campos calculados
    lc_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True, digits=(16, 2))
    lc_importe_base_cf = fields.Float(string='Importe Base CF', compute='_compute_importe_base_cf', store=True, digits=(16, 2))
    lc_credito_fiscal = fields.Float(string='Crédito Fiscal', compute='_compute_credito_fiscal', store=True, digits=(16, 2))

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get('default_move_line_id'):
            move_line = self.env['account.move.line'].browse(self._context['default_move_line_id'])
            res['lc_importe_total_compra'] = move_line.debit or move_line.credit
            if move_line.partner_id:
                res['lc_nit'] = move_line.partner_id.lc_nit
                res['lc_razon_social'] = move_line.partner_id.lc_razon_social
        return res

    @api.depends(
        'lc_importe_total_compra', 'lc_importe_ice', 'lc_importe_iehd', 
        'lc_importe_ipj', 'lc_tasas', 'lc_otros_no_sujeto_cf', 
        'lc_importes_exentos', 'lc_compras_gravadas_tasa_cero'
    )
    def _compute_subtotal(self):
        for line in self:
            line.lc_subtotal = (
                line.lc_importe_total_compra
                - line.lc_importe_ice
                - line.lc_importe_iehd
                - line.lc_importe_ipj
                - line.lc_tasas
                - line.lc_otros_no_sujeto_cf
                - line.lc_importes_exentos
                - line.lc_compras_gravadas_tasa_cero
            )

    @api.depends('lc_subtotal', 'lc_descuentos_bonificaciones', 'lc_importe_gift_card')
    def _compute_importe_base_cf(self):
        for line in self:
            line.lc_importe_base_cf = (
                line.lc_subtotal
                - line.lc_descuentos_bonificaciones
                - line.lc_importe_gift_card
            )

    @api.depends('lc_importe_base_cf')
    def _compute_credito_fiscal(self):
        for line in self:
            line.lc_credito_fiscal = line.lc_importe_base_cf * 0.13

    def action_guardar(self):
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
