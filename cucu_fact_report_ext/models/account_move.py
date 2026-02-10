# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError

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
    
    def _check_electronic_invoice_already_issued(self):
        """
        Valida que una factura no tenga facturación electrónica ya emitida.
        Previene la doble emisión de facturas cuando se vuelve a borrador
        y se intenta validar nuevamente.
        """
        for move in self:
            # Solo verificar si está marcada para emitir factura electrónica
            if not move.is_sin:
                continue
                
            # Estados que indican que ya existe una factura electrónica válida
            valid_statuses = ['VALIDADA', 'VALIDA', 'OBSERVADA']
            
            # Verificar por estado de descripción SIAT
            if move.sin_description_status in valid_statuses:
                raise UserError(
                    f"No se puede emitir la factura electrónica.\n\n"
                    f"Esta factura ya tiene una factura electrónica emitida:\n"
                    f"- Estado: {move.sin_description_status}\n"
                    f"- Código: {move.invoice_code or 'N/A'}\n"
                    f"- Número: {move.invoice_number or 'N/A'}\n\n"
                    f"Si necesita anular esta factura, use la opción de anulación "
                    f"en lugar de volver a borrador."
                )
            
            # Verificación adicional: si tiene código de factura o número
            # (puede haber casos donde el estado no se actualizó correctamente)
            if move.invoice_code or move.invoice_number:
                # Verificar que no sea el estado inicial por defecto
                if move.sin_description_status != 'Not invoice':
                    raise UserError(
                        f"No se puede emitir la factura electrónica.\n\n"
                        f"Esta factura tiene datos de una emisión previa:\n"
                        f"- Código: {move.invoice_code}\n"
                        f"- Número: {move.invoice_number}\n"
                        f"- Estado actual: {move.sin_description_status}\n\n"
                        f"Verifique el estado de la factura antes de continuar."
                    )
    
    def _post(self, soft=True):
        """
        Sobrescribe _post para agregar validación de doble emisión
        antes de procesar la factura electrónica.
        """
        # Validar que no se esté intentando emitir dos veces
        self._check_electronic_invoice_already_issued()
        
        # Continuar con el proceso normal
        return super(AccountMove, self)._post(soft=soft)
