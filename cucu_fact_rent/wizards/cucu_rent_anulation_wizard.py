# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CucuRentAnulationWizard(models.TransientModel):
    _name = 'cucu.rent.anulation.wizard'
    _description = 'Wizard Anulación / Reversión Factura Alquileres'

    invoice_id = fields.Many2one('account.move', string='Factura', readonly=True)
    action = fields.Selection([
        ('anulate', 'Anular'),
        ('revert', 'Revertir'),
    ], string='Operación', default='anulate', readonly=True)
    confirm_message = fields.Char(
        string='Confirmación',
        compute='_compute_confirm_message',
    )

    def _compute_confirm_message(self):
        for rec in self:
            invoice = rec.invoice_id
            op = '⚠️ ANULAR' if rec.action == 'anulate' else '↩️ REVERTIR'
            rec.confirm_message = (
                f'{op} la factura {invoice.name} '
                f'| CUF: {invoice.cucu_rent_cuf} '
                f'| N°: {invoice.cucu_rent_invoice_number or "-"}'
            )

    def action_confirm(self):
        self.ensure_one()
        invoice = self.invoice_id
        api = self.env['cucu.rent.api']
        try:
            if self.action == 'anulate':
                api.anulate_rent_invoice(invoice)
                msg = f'✅ Factura {invoice.name} anulada correctamente en CUCU.'
            else:
                api.revert_rent_invoice(invoice)
                msg = f'✅ Factura {invoice.name} revertida correctamente en CUCU.'
            _logger.info(msg)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Operación exitosa',
                    'message': msg,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(f'❌ Error en operación:\n\n{str(e)}')
