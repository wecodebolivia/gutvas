# -*- coding: utf-8 -*-
from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _prepare_cucu_header_data(self):
        """ 
        Intercepta el diccionario que usa el reporte A4 
        y reemplaza el teléfono antiguo por el de la sucursal activa.
        """
        res = super(AccountMove, self)._prepare_cucu_header_data()
        
        # Obtenemos el teléfono del Branch vinculado al Punto de Venta (pos_id)
        if self.pos_id and self.pos_id.branch_id and self.pos_id.branch_id.phone:
            res['telefono'] = self.pos_id.branch_id.phone
        elif self.pos_id and self.pos_id.phone:
            res['telefono'] = self.pos_id.phone
            
        return res
