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
    
    def copy(self, default=None):
        """
        Sobrescribe el método copy para evitar duplicar campos 
        de facturación electrónica al duplicar facturas.
        """
        if default is None:
            default = {}
        
        # Excluir campos de facturación electrónica de la duplicación
        default.update({
            'invoice_id': False,  # Relación One2many con cucu.invoice
            'sin_code_state': 0,  # Código de estado SIAT
            'sin_code_reception': '0000',  # Código de recepción SIAT
            'sin_description_status': 'Not invoice',  # Estado de facturación
            'invoice_code': False,  # Código de factura electrónica
            'invoice_number': False,  # Número de factura electrónica
            'is_sin': False,  # Bandera de facturación electrónica
            'pos_session_id': False,  # Sesión de punto de venta
        })
        
        return super(AccountMove, self).copy(default=default)
