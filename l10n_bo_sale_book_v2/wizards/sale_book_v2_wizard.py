# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleBookV2Wizard(models.TransientModel):
    _name = 'sale.book.v2.wizard'
    _description = 'Asistente para Libro de Ventas V2'

    fecha_inicio = fields.Date(string='Fecha de Inicio', required=True)
    fecha_fin = fields.Date(string='Fecha de Fin', required=True)
    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)

    def generar_reporte_excel(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Libro de Ventas V2',
                'message': 'Funcionalidad en desarrollo. Fechas: %s - %s' % (self.fecha_inicio, self.fecha_fin),
                'type': 'info',
                'sticky': False,
            }
        }
