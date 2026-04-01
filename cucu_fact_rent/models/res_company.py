# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class ResCompany(models.Model):
    _inherit = 'res.company'

    # ========== CREDENCIALES SECTOR ALQUILERES ==========
    cucu_rent_username = fields.Char(
        string='CUCU Usuario Alquileres',
        help='Usuario específico para endpoint de alquileres. Ej: demo.largotek.alquiler'
    )
    cucu_rent_password = fields.Char(
        string='CUCU Password Alquileres',
        help='Contraseña específica para endpoint de alquileres'
    )
    cucu_rent_token = fields.Char(
        string='Token JWT Alquileres',
        readonly=True,
        help='Token de autenticación generado automáticamente'
    )
    cucu_rent_token_expiry = fields.Datetime(
        string='Vencimiento Token',
        readonly=True,
        help='Fecha de expiración del token (renovación automática)'
    )

    # ========== SUCURSAL / PUNTO DE VENTA ALQUILERES ==========
    cucu_rent_branch_id = fields.Many2one(
        'cucu.branch.office',
        string='Sucursal Alquileres',
        help='Sucursal CUCU asociada al sector alquileres. '
             'La ciudad (municipality) de esta sucursal se usa como clientCity en el payload.'
    )

    # ========== CAFC SECTOR ALQUILERES ==========
    cucu_rent_cafc_online = fields.Char(
        string='CAFC Alquileres (Electrónica en línea)',
        default='10228BFCF149E',
        help='CAFC asignado por SIN para facturación electrónica sector alquileres.\n'
             'Sandbox: 10228BFCF149E (rango 1-1000)\n'
             'Producción: Solicitar a SIN'
    )

    # ========== ENDPOINTS API ALQUILERES ==========
    cucu_rent_endpoint = fields.Char(
        string='Endpoint Emisión',
        default='https://sandbox.cucu.ai/api/v1/invoice/electronic/rent',
        help='Endpoint POST para emitir facturas de alquileres'
    )
    cucu_rent_anulation_endpoint = fields.Char(
        string='Endpoint Anulación',
        default='https://sandbox.cucu.ai/api/v1/invoice/electronic/rent/anulation',
        help='Endpoint POST para anular facturas de alquileres'
    )
    cucu_rent_revert_endpoint = fields.Char(
        string='Endpoint Reversión',
        default='https://sandbox.cucu.ai/api/v1/invoice/electronic/rent/revert',
        help='Endpoint POST para revertir facturas de alquileres'
    )
    cucu_rent_auth_endpoint = fields.Char(
        string='Endpoint Autenticación',
        default='https://sandbox.cucu.ai/auth/login',
        help='Endpoint POST para obtener token JWT'
    )

    def action_test_rent_connection(self):
        """Acción de botón: Probar conexión con API de alquileres"""
        self.ensure_one()

        if not self.cucu_rent_username or not self.cucu_rent_password:
            raise UserError(
                'Configure primero el usuario y contraseña CUCU para sector alquileres'
            )

        api_service = self.env['cucu.rent.api']

        try:
            token = api_service._get_auth_token(self)

            if token:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Conexión Exitosa',
                        'message': f'Token JWT generado correctamente.\nExpira: {self.cucu_rent_token_expiry}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
        except Exception as e:
            raise UserError(f'❌ Error de conexión CUCU:\n\n{str(e)}')
