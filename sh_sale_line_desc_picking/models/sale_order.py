# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.picking_ids:
            if self.partner_invoice_id:
                for picking in self.picking_ids:
                    picking.sudo().write({
                        'sh_line_desc_partner_inv_id': self.partner_invoice_id.id
                    })
            if self.partner_id:
                for picking in self.picking_ids:
                    picking.sudo().write({
                        'sh_line_desc_partner_id': self.partner_id.id
                    })
        return res
