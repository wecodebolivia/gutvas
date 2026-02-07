# -*- coding: utf-8 -*-
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _prepare_cucu_header_data(self):
        """Override para modificar teléfono en header de CUCU"""
        res = super()._prepare_cucu_header_data()
        
        # Reemplazar teléfono con el del Branch/POS Config
        if self.pos_config_id and self.pos_config_id.phone:
            res['telefono'] = self.pos_config_id.phone
        
        return res
