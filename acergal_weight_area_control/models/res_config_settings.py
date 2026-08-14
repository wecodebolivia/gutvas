from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    weight_area_variance_threshold_pct = fields.Float(
        string='Umbral global de variación (%)',
        config_parameter='acergal_weight_area_control.variance_threshold_pct',
        default=5.0,
    )
