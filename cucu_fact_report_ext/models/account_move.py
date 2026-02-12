# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _format_2_decimals(self, value):
        """Helper para formatear valores numéricos a 2 decimales como string."""
        try:
            return f"{float(value or 0.0):.2f}"
        except Exception:
            return "0.00"

    def _normalize_amount_keys_2d(self, data):
        """Formatea a 2 decimales un conjunto amplio de keys monetarias del header."""
        # keys más comunes en SIAT / CUCU
        keys = {
            'montoTotal',
            'descuentoAdicional',
            'montoTotalMoneda',
            'montoGiftCard',
            'montoTotalSujetoIva',
            'importeBaseCredFiscalComputable',
            'montoTotal2',
            # posibles alternos
            'montoTotalArrendamientoFinanciero',
            'montoTotalMoneda2',
            'montoTotalSujetoIva2',
        }
        # además, por seguridad, cualquier key que parezca monto/importe/descuento
        for k, v in list((data or {}).items()):
            if k in keys or any(token in k.lower() for token in ['monto', 'importe', 'descuento', 'total']):
                # solo si es número o string numérico
                try:
                    float(v)
                except Exception:
                    continue
                data[k] = self._format_2_decimals(v)
        return data

    def _prepare_cucu_header_data(self):
        res = super()._prepare_cucu_header_data()

        # Teléfono desde Branch vinculado al Punto de Venta
        if self.pos_id and self.pos_id.branch_id and self.pos_id.branch_id.phone:
            res['telefono'] = self.pos_id.branch_id.phone
        elif self.pos_id and self.pos_id.phone:
            res['telefono'] = self.pos_id.phone

        # Forzar 2 decimales en montos del header
        res = self._normalize_amount_keys_2d(res)
        return res

    def render_invoice(self):
        """Asegura 2 decimales también cuando el reporte usa render_invoice() (ticket y/o A4 según CUCU)."""
        res = super().render_invoice()
        if not res:
            return res
        header = res.get('header') or {}
        res['header'] = self._normalize_amount_keys_2d(header)
        return res

    def copy(self, default=None):
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

        return super().copy(default=default)

    def _check_electronic_invoice_already_issued(self):
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
        self._check_electronic_invoice_already_issued()
        return super()._post(soft=soft)
