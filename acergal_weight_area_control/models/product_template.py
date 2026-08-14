from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    weight_area_control = fields.Boolean(
        string='Control peso-área',
        help='Activa el control auxiliar de kilogramos y metros por lote/rollo.',
    )
    factor_kg_m_standard = fields.Float(
        string='Factor estándar (kg/m)',
        digits='Product Unit of Measure',
        help='Kilogramos teóricos por metro lineal.',
    )
    weight_area_variance_threshold_pct = fields.Float(
        string='Umbral de variación (%)',
        help='Si está vacío o es cero se utiliza el parámetro global.',
    )

    @api.constrains('weight_area_control', 'factor_kg_m_standard', 'tracking')
    def _check_weight_area_configuration(self):
        for product in self:
            if not product.weight_area_control:
                continue
            if product.factor_kg_m_standard <= 0:
                raise ValidationError(_('El factor estándar kg/m debe ser mayor que cero.'))
            if product.tracking != 'lot':
                raise ValidationError(_(
                    'Los productos con control peso-área deben usar trazabilidad por lote.'
                ))
