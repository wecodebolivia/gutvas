# -*- coding: utf-8 -*-
import requests
import json
import logging
from datetime import datetime, timedelta
from odoo import models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class CucuRentAPI(models.AbstractModel):
    _name = 'cucu.rent.api'
    _description = 'Servicio API CUCU para Sector Alquileres'
    
    def _get_auth_token(self, company):
        """Obtiene o renueva el token JWT para sector alquileres"""
        if company.cucu_rent_token and company.cucu_rent_token_expiry:
            if datetime.now() < company.cucu_rent_token_expiry:
                _logger.info('Token JWT existente valido hasta %s', company.cucu_rent_token_expiry)
                return company.cucu_rent_token
        
        if not company.cucu_rent_username or not company.cucu_rent_password:
            raise UserError(
                'Configure las credenciales CUCU para sector alquileres en:\n'
                'Configuracion > Companias > Facturacion Alquileres'
            )
        
        auth_url = (company.cucu_rent_auth_endpoint or 'https://sandbox.cucu.ai/auth/login').strip().rstrip('/')
        
        payload = {
            'username': company.cucu_rent_username.strip(),
            'password': company.cucu_rent_password.strip()
        }
        
        _logger.info('=== Autenticacion CUCU Alquileres ===')
        _logger.info('URL: %s', auth_url)
        _logger.info('Usuario: %s', payload['username'])
        
        try:
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            response = requests.post(auth_url, json=payload, headers=headers, timeout=30)
            
            _logger.info('Response Status: %d', response.status_code)
            
            try:
                data = response.json()
            except:
                data = {'error': 'Respuesta no es JSON', 'raw': response.text}
            
            if response.status_code == 401:
                raise UserError(
                    f'Error de autenticacion CUCU:\n\n'
                    f'HTTP 401: {json.dumps(data, indent=2)}\n\n'
                    f'Usuario usado: {payload["username"]}\n\n'
                    f'Credenciales sandbox:\n'
                    f'Usuario: demo.largotek.alquiler\n'
                    f'Password: bd3f2919c865452aaf48f3c596507e2c'
                )
            
            response.raise_for_status()
            
            token = None
            if isinstance(data, dict):
                if data.get('success') and data.get('data'):
                    token = data['data'].get('token')
                elif data.get('token'):
                    token = data.get('token')
            
            if not token:
                raise UserError(f'No se recibio token.\n\nRespuesta:\n{json.dumps(data, indent=2)}')
            
            expiry_date = datetime.now() + timedelta(days=60)
            company.sudo().write({
                'cucu_rent_token': token,
                'cucu_rent_token_expiry': expiry_date
            })
            
            _logger.info('Token JWT generado - Expira: %s', expiry_date)
            return token
            
        except UserError:
            raise
        except requests.exceptions.RequestException as e:
            _logger.error('Error de conexion: %s', str(e))
            raise UserError(f'Error de conexion con CUCU API:\n\n{str(e)}')
    
    def send_rent_invoice(self, invoice):
        """Envia factura de alquileres a CUCU API"""
        company = invoice.company_id
        
        if not invoice.rent_billed_period:
            raise UserError(
                'El campo "Periodo Facturado" es obligatorio.\n\n'
                'Ejemplo: "Mayo 2026"'
            )
        
        token = self._get_auth_token(company)
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cucukey': f'Token {token}'
        }
        
        payload = invoice._prepare_cucu_rent_invoice_data()
        endpoint = (company.cucu_rent_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent').strip().rstrip('/')
        
        _logger.info('=== Enviando factura %s a CUCU ===', invoice.name)
        _logger.info('Endpoint: %s', endpoint)
        _logger.info('Periodo: %s', invoice.rent_billed_period)
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            
            _logger.info('Response Status: %d', response.status_code)
            
            if response.status_code == 401:
                _logger.warning('Token expirado, renovando...')
                company.sudo().write({'cucu_rent_token': False})
                token = self._get_auth_token(company)
                headers['cucukey'] = f'Token {token}'
                response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                _logger.info('Factura enviada exitosamente')
                return result.get('data', {})
            else:
                error_msg = result.get('message', 'Error desconocido')
                raise UserError(f'Error CUCU:\n\n{error_msg}')
                
        except UserError:
            raise
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_msg = json.dumps(error_data, indent=2)
            except:
                error_msg = e.response.text
            raise UserError(f'Error HTTP {e.response.status_code}:\n\n{error_msg}')
        except requests.exceptions.RequestException as e:
            raise UserError(f'Error de conexion:\n\n{str(e)}')
    
    def anulate_rent_invoice(self, invoice, reason_code):
        """Anula una factura de alquileres"""
        company = invoice.company_id
        token = self._get_auth_token(company)
        
        if not invoice.cucu_rent_cuf:
            raise UserError('La factura no tiene CUF asignado')
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cucukey': f'Token {token}'
        }
        
        payload = {'cuf': invoice.cucu_rent_cuf, 'reasonCode': reason_code}
        endpoint = (company.cucu_rent_anulation_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent/anulation').strip().rstrip('/')
        
        _logger.info('=== Anulando factura CUF: %s ===', invoice.cucu_rent_cuf)
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                invoice.write({'cucu_rent_state': 'cancelled'})
                return result.get('data', {})
            else:
                raise UserError(f'Error al anular:\n\n{result.get("message")}')
        except requests.exceptions.RequestException as e:
            raise UserError(f'Error al anular:\n\n{str(e)}')
