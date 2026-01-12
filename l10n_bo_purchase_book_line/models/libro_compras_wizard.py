# l10n_bo_purchase_book_line/models/libro_compras_wizard.py

from odoo import models, fields, api


class LibroComprasWizard(models.TransientModel):
    _name = 'libro.compras.wizard'
    _description = 'Wizard para el Libro de Compras'

    move_line_id = fields.Many2one(
        'account.move.line',
        string='Línea de Asiento',
        required=True,
    )

    # Datos del proveedor (solo lectura)
    lc_nit = fields.Char(
        string='NIT',
        related='move_line_id.partner_id.lc_nit',
        readonly=True,
    )
    lc_razon_social = fields.Char(
        string='Razón Social',
        related='move_line_id.partner_id.lc_razon_social',
        readonly=True,
    )

    # Datos generales
    lc_codigo_autorizacion = fields.Char(string='Código de Autorización')
    lc_numero_factura = fields.Char(string='Número de Factura')
    lc_numero_dui_dim = fields.Char(string='Número DUI/DIM')
    lc_fecha_factura = fields.Date(string='Fecha de Factura')

    # Montos
    lc_importe_total_compra = fields.Float(string='Importe Total Compra', digits=(16, 2))
    lc_importe_ice = fields.Float(string='Importe ICE', digits=(16, 2))
    lc_importe_iehd = fields.Float(string='Importe IEHD', digits=(16, 2))
    lc_importe_ipj = fields.Float(string='Importe IPJ', digits=(16, 2))
    lc_tasas = fields.Float(string='Tasas', digits=(16, 2))
    lc_otros_no_sujeto_cf = fields.Float(string='Otros No Sujeto a CF', digits=(16, 2))
    lc_importes_exentos = fields.Float(string='Importes Exentos', digits=(16, 2))
    lc_compras_gravadas_tasa_cero = fields.Float(string='Compras Gravadas a Tasa Cero', digits=(16, 2))
    lc_descuentos_bonificaciones = fields.Float(string='Descuentos / Bonificaciones', digits=(16, 2))
    lc_importe_gift_card = fields.Float(string='Importe Gift Card', digits=(16, 2))

    lc_tipo_compra = fields.Selection([
        ('1', 'Actividad gravada'),
        ('2', 'Actividad no gravada'),
        ('3', 'Sujetas a proporcionalidad'),
        ('4', 'Exportaciones'),
        ('5', 'Interno/Exportaciones'),
    ], string='Tipo de Compra', default='1')

    lc_codigo_control = fields.Char(string='Código de Control')

    # Cálculos
    lc_subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        digits=(16, 2)
    )
    lc_importe_base_cf = fields.Float(
        string='Importe Base CF',
        compute='_compute_importe_base_cf',
        store=True,
        digits=(16, 2)
    )
    lc_credito_fiscal = fields.Float(
        string='Crédito Fiscal',
        compute='_compute_credito_fiscal',
        store=True,
        digits=(16, 2)
    )

    @api.model
    def default_get(self, fields_list):
        """Cargar datos existentes si la línea ya tiene información guardada"""
        res = super().default_get(fields_list)
        move_line_id = self._context.get('default_move_line_id')

        if move_line_id:
            line = self.env['account.move.line'].browse(move_line_id)

            # Si ya existen datos guardados, cargarlos
            if line.lc_codigo_autorizacion or line.lc_numero_factura or line.lc_fecha_factura:
                res.update({
                    'lc_codigo_autorizacion': line.lc_codigo_autorizacion,
                    'lc_numero_factura': line.lc_numero_factura,
                    'lc_numero_dui_dim': line.lc_numero_dui_dim,
                    'lc_fecha_factura': line.lc_fecha_factura,
                    'lc_importe_total_compra': line.lc_importe_total_compra,
                    'lc_importe_ice': line.lc_importe_ice,
                    'lc_importe_iehd': line.lc_importe_iehd,
                    'lc_importe_ipj': line.lc_importe_ipj,
                    'lc_tasas': line.lc_tasas,
                    'lc_otros_no_sujeto_cf': line.lc_otros_no_sujeto_cf,
                    'lc_importes_exentos': line.lc_importes_exentos,
                    'lc_compras_gravadas_tasa_cero': line.lc_compras_gravadas_tasa_cero,
                    'lc_descuentos_bonificaciones': line.lc_descuentos_bonificaciones,
                    'lc_importe_gift_card': line.lc_importe_gift_card,
                    'lc_tipo_compra': line.lc_tipo_compra,
                    'lc_codigo_control': line.lc_codigo_control,
                })
            else:
                # Primera vez: inicializar con datos básicos
                res.update({
                    'lc_importe_total_compra': line.debit or line.credit or 0.0,
                })

        return res

    # Cálculos
    @api.depends(
        'lc_importe_total_compra', 'lc_importe_ice', 'lc_importe_iehd',
        'lc_importe_ipj', 'lc_tasas', 'lc_otros_no_sujeto_cf',
        'lc_importes_exentos', 'lc_compras_gravadas_tasa_cero',
    )
    def _compute_subtotal(self):
        for w in self:
            w.lc_subtotal = (
                (w.lc_importe_total_compra or 0.0)
                - (w.lc_importe_ice or 0.0)
                - (w.lc_importe_iehd or 0.0)
                - (w.lc_importe_ipj or 0.0)
                - (w.lc_tasas or 0.0)
                - (w.lc_otros_no_sujeto_cf or 0.0)
                - (w.lc_importes_exentos or 0.0)
                - (w.lc_compras_gravadas_tasa_cero or 0.0)
            )

    @api.depends('lc_subtotal', 'lc_descuentos_bonificaciones', 'lc_importe_gift_card')
    def _compute_importe_base_cf(self):
        for w in self:
            w.lc_importe_base_cf = (
                (w.lc_subtotal or 0.0)
                - (w.lc_descuentos_bonificaciones or 0.0)
                - (w.lc_importe_gift_card or 0.0)
            )

    @api.depends('lc_importe_base_cf')
    def _compute_credito_fiscal(self):
        for w in self:
            w.lc_credito_fiscal = (w.lc_importe_base_cf or 0.0) * 0.13

    # Acciones
    def action_guardar(self):
        """Acción original que escribe en la línea contable."""
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

    def action_confirm(self):
        """Alias usado por el botón XML name="action_confirm"."""
        return self.action_guardar()
