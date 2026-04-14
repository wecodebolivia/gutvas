# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

# Motivos de anulación según catálogo SIN Bolivia
MOTIVE_SELECTION = [
    ('1', '1 - Factura mal emitida'),
    ('2', '2 - Nota de crédito-débito'),
    ('3', '3 - Devolución de bienes'),
]


class CucuRentAnulationWizard(models.TransientModel):
    _name = 'cucu.rent.anulation.wizard'
    _description = 'Wizard Anulación / Reversión Factura Alquileres'

    invoice_id = fields.Many2one(
        'account.move',
        string='Factura',
        readonly=True,
    )

    action = fields.Selection(
        [
            ('anulate', 'Anular'),
            ('revert', 'Revertir'),
        ],
        string='Operación',
        default='anulate',
        readonly=True,
    )

    motive = fields.Selection(
        MOTIVE_SELECTION,
        string='Motivo de anulación',
        default='1',
        required=True,
    )

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

        if not self.motive:
            raise UserError('Debe seleccionar el Motivo de Anulación antes de continuar.')

        invoice = self.invoice_id
        api = self.env['cucu.rent.api']

        try:
            if self.action == 'anulate':
                api.anulate_rent_invoice(invoice, motive=int(self.motive))
            else:
                api.revert_rent_invoice(invoice, motive=int(self.motive))

            # Si todo va bien, cerrar el popup
            return {'type': 'ir.actions.act_window_close'}

        except UserError:
            # Dejar que el UserError se muestre en el wizard (no se cierra)
            raise
        except Exception as e:
            # Cualquier otro error también se muestra en el wizard
            raise UserError(f'❌ Error en operación:\n\n{str(e)}')