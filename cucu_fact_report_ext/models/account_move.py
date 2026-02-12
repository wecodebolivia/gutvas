# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _format_2_decimals(self, value):
        """Helper para formatear valores numéricos a 2 decimales como string."""
        try:
            return f"{float(value or 0.0):.2f}"
        except Exception:
            return "0.00"

    def _prepare_cucu_header_data(self):
        """ 
        Intercepta el diccionario que usa el reporte A4
        y aplica ajustes desde la extensión:
        - Reemplaza el teléfono por el de la sucursal activa.
        - Fuerza formato de 2 decimales en montos del header.
        """
        res = super(AccountMove, self)._prepare_cucu_header_data()

        # Teléfono desde Branch vinculado al Punto de Venta
        if self.pos_id and self.pos_id.branch_id and self.pos_id.branch_id.phone:
            res['telefono'] = self.pos_id.branch_id.phone
        elif self.pos_id and self.pos_id.phone:
            res['telefono'] = self.pos_id.phone

        # Forzar 2 decimales para campos monetarios usados por los reportes
        for key in [
            'montoTotal',
            'descuentoAdicional',
            'montoTotalMoneda',
            'montoGiftCard',
            'montoTotalSujetoIva',
            # Campos alternos que pueden aparecer según doc sector/config
            'importeBaseCredFiscalComputable',
            'montoTotal2',
        ]:
            if key in res:
                res[key] = self._format_2_decimals(res.get(key))

        return res

    def copy(self, default=None):
        """
        Sobrescribe el método copy para evitar duplicar campos 
        de facturación electrónica al duplicar facturas.
        """
        if default is None:
            default = {}

        default.update({
            'invoice_id': False,
            'sin_code_state': 0,
            'sin_code_reception': '0000',
            'sin_description_status': 'Not invoice',
            'invoice_code': False,
            'invoice_number': False,
            'is_sin': False,
            'pos_session_id': False,
        })

        return super(AccountMove, self).copy(default=default)

    def _check_electronic_invoice_already_issued(self):
        """
        Valida que una factura no tenga facturación electrónica ya emitida.
        Previene la doble emisión de facturas cuando se vuelve a borrador
        y se intenta validar nuevamente.
        """
        for move in self:
            if not move.is_sin:
                continue

            valid_statuses = ['VALIDADA', 'VALIDA', 'OBSERVADA']

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

            if move.invoice_code or move.invoice_number:
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
        self._check_electronic_invoice_already_issued()
        return super(AccountMove, self)._post(soft=soft)
