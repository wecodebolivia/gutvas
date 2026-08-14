from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockLot(models.Model):
    _inherit = 'stock.lot'

    weight_area_enabled = fields.Boolean(related='product_id.weight_area_control')
    initial_weight_kg = fields.Float(string='Peso inicial (kg)', digits='Product Unit of Measure', copy=False)
    initial_length_m = fields.Float(string='Metraje inicial (m)', digits='Product Unit of Measure', copy=False)
    real_factor_kg_m = fields.Float(
        string='Factor real (kg/m)',
        compute='_compute_weight_area_values',
        store=True,
        readonly=False,
        copy=False,
    )
    consumed_weight_kg = fields.Float(
        string='Kg consumidos', compute='_compute_weight_area_balances', digits='Product Unit of Measure'
    )
    consumed_length_m = fields.Float(
        string='Metros consumidos', compute='_compute_weight_area_balances', digits='Product Unit of Measure'
    )
    remaining_weight_kg = fields.Float(
        string='Saldo (kg)', compute='_compute_weight_area_balances', digits='Product Unit of Measure'
    )
    remaining_length_m = fields.Float(
        string='Saldo (m)', compute='_compute_weight_area_balances', digits='Product Unit of Measure'
    )
    variance_pct = fields.Float(string='Desviación (%)', compute='_compute_weight_area_values', store=True)
    variance_state = fields.Selection(
        [('normal', 'Normal'), ('warning', 'Advertencia')],
        compute='_compute_weight_area_values',
        string='Estado de variación',
        store=True,
    )
    weight_area_initialized = fields.Boolean(string='Control inicializado', copy=False, readonly=True)

    @api.depends('initial_weight_kg', 'initial_length_m', 'product_id.factor_kg_m_standard', 'product_id.weight_area_variance_threshold_pct')
    def _compute_weight_area_values(self):
        threshold = float(self.env['ir.config_parameter'].sudo().get_param(
            'acergal_weight_area_control.variance_threshold_pct', default='5.0'
        ))
        for lot in self:
            factor = 0.0
            if lot.initial_weight_kg > 0 and lot.initial_length_m > 0:
                factor = lot.initial_weight_kg / lot.initial_length_m
            lot.real_factor_kg_m = factor
            standard = lot.product_id.factor_kg_m_standard
            lot.variance_pct = ((factor - standard) / standard * 100.0) if standard else 0.0
            limit = lot.product_id.weight_area_variance_threshold_pct or threshold
            lot.variance_state = 'warning' if abs(lot.variance_pct) > limit else 'normal'

    @api.depends('initial_weight_kg', 'initial_length_m', 'move_line_ids.state', 'move_line_ids.weight_area_direction', 'move_line_ids.weight_area_length_m', 'move_line_ids.weight_area_equivalent_kg')
    def _compute_weight_area_balances(self):
        for lot in self:
            lines = lot.move_line_ids.filtered(
                lambda line: line.state == 'done' and line.weight_area_enabled
            )
            output_lines = lines.filtered(lambda line: line.weight_area_direction == 'out')
            input_lines = lines.filtered(lambda line: line.weight_area_direction == 'in')
            lot.consumed_length_m = sum(output_lines.mapped('weight_area_length_m')) - sum(input_lines.mapped('weight_area_length_m'))
            lot.consumed_weight_kg = sum(output_lines.mapped('weight_area_equivalent_kg')) - sum(input_lines.mapped('weight_area_equivalent_kg'))
            lot.remaining_length_m = lot.initial_length_m - lot.consumed_length_m
            lot.remaining_weight_kg = lot.initial_weight_kg - lot.consumed_weight_kg

    @api.constrains('initial_weight_kg', 'initial_length_m')
    def _check_initial_values(self):
        for lot in self.filtered('weight_area_enabled'):
            if lot.initial_weight_kg < 0 or lot.initial_length_m < 0:
                raise ValidationError(_('El peso y metraje iniciales no pueden ser negativos.'))

    def action_initialize_weight_area(self):
        for lot in self.filtered('weight_area_enabled'):
            if lot.initial_weight_kg <= 0:
                raise ValidationError(_('Debe registrar un peso inicial mayor que cero.'))
            if not lot.initial_length_m:
                lot.initial_length_m = lot.initial_weight_kg / lot.product_id.factor_kg_m_standard
            if lot.initial_length_m <= 0:
                raise ValidationError(_('El metraje inicial debe ser mayor que cero.'))
            lot.weight_area_initialized = True
