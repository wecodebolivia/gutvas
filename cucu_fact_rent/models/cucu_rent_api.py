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
    
    def _create_header(self, token=''):
        """Crea headers EXACTAMENTE como cucu_fact_core"""
        if token:
            return {
                'content-type': 'application/json',
                'cucukey': f'Token {token}'
            }
        return {
            'content-type': 'application/json'
        }
    
    def _get_auth_token(self, company):
        """Obtiene o renueva el token JWT - METODO IDENTICO A cucu_fact_core"""
        if company.cucu_rent_token and company.cucu_rent_token_expiry:
            if datetime.now() < company.cucu_rent_token_expiry:
                _logger.info('Token JWT existente valido hasta %s', company.cucu_rent_token_expiry)
                return company.cucu_rent_token
        
        if not company.cucu_rent_username or not company.cucu_rent_password:
            raise UserError(
                'Configure las credenciales CUCU para sector alquileres en:\n'
                'Configuracion > Companias > Facturacion Alquileres'
            )
        
        # URL base (sin /api/v1, se agrega abajo)
        host = company.cucu_rent_auth_endpoint or 'https://sandbox.cucu.ai'
        host = host.strip().rstrip('/')
        
        # Si ya incluye /auth/login, usarlo directo. Si no, construir URL
        if '/auth/login' in host:
            url = host
        else:
            url = f'{host}/api/v1/auth/login'
        
        params_json = {
            'username': company.cucu_rent_username.strip(),
            'password': company.cucu_rent_password.strip()
        }
        
        _logger.info('=== Autenticacion CUCU Alquileres ===')
        _logger.info('URL: %s', url)
        _logger.info('Usuario: %s', params_json['username'])
        _logger.info('Params: %s', params_json)
        
        try:
            # REQUEST EXACTO como service_single.py que funciona
            headers = self._create_header()
            response = requests.post(
                url=url,
                json=params_json,  # IMPORTANTE: json= NO data=
                headers=headers,
                timeout=30
            )
            
            _logger.info('Response Status: %d', response.status_code)
            _logger.info('Response Body: %s', response.text[:500])
            
            result = response.json()
            
            # Validar respuesta exitosa
            if result.get('success') or result.get('message') == 'TOKEN CREADED':
                token = result['data']['token']
                
                # Guardar token
                expiry_date = datetime.now() + timedelta(days=60)
                company.sudo().write({
                    'cucu_rent_token': token,
                    'cucu_rent_token_expiry': expiry_date
                })
                
                _logger.info('Token JWT generado - Expira: %s', expiry_date)
                return token
            else:
                error_msg = result.get('message', 'Error desconocido')
                raise UserError(f'Error de autenticacion:\n\n{error_msg}\n\nRespuesta: {json.dumps(result, indent=2)}')
            
        except UserError:
            raise
        except requests.exceptions.Timeout:
            raise UserError(
                'Timeout al conectar con CUCU API.\n\n'
                'Posibles causas:\n'
                '- Firewall de Odoo.sh bloqueando conexiones\n'
                '- API CUCU no disponible'
            )
        except requests.exceptions.ConnectionError:
            raise UserError('API CUCU NOT CONNECT')
        except requests.exceptions.HTTPError as e:
            raise UserError(f'HTTP Error: {str(e)}')
        except Exception as e:
            _logger.error('Error inesperado: %s', str(e))
            raise UserError(f'Error de conexion:\n\n{str(e)}')
    
    def send_rent_invoice(self, invoice):
        """Envia factura de alquileres a CUCU API"""
        company = invoice.company_id
        
        if not invoice.rent_billed_period:
            raise UserError(
                'El campo "Periodo Facturado" es obligatorio.\n\n'
                'Ejemplo: "Mayo 2026"'
            )
        
        token = self._get_auth_token(company)
        headers = self._create_header(token)
        
        payload = invoice._prepare_cucu_rent_invoice_data()
        
        # URL del endpoint de emision
        endpoint = company.cucu_rent_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent'
        endpoint = endpoint.strip().rstrip('/')
        
        _logger.info('=== Enviando factura %s a CUCU ===', invoice.name)
        _logger.info('Endpoint: %s', endpoint)
        _logger.info('Periodo: %s', invoice.rent_billed_period)
        
        try:
            response = requests.post(
                url=endpoint,
                json=payload,  # json= NO data=
                headers=headers,
                timeout=60
            )
            
            _logger.info('Response Status: %d', response.status_code)
            
            # Reintentar si token expiro
            if response.status_code == 401:
                _logger.warning('Token expirado, renovando...')
                company.sudo().write({'cucu_rent_token': False, 'cucu_rent_token_expiry': False})
                token = self._get_auth_token(company)
                headers = self._create_header(token)
                
                response = requests.post(
                    url=endpoint,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                _logger.info('Retry Response Status: %d', response.status_code)
            
            result = response.json()
            
            # Validar respuesta
            if result.get('success'):
                _logger.info('Factura enviada exitosamente')
                data = result.get('data', {})
                cuf = data.get('cuf', 'N/A')
                _logger.info('CUF generado: %s', cuf)
                return data
            else:
                error_msg = result.get('message', 'Error desconocido')
                errors = result.get('errors', '')
                if errors:
                    error_msg += f'\n\nDetalles: {json.dumps(errors, indent=2)}'
                raise UserError(f'Error CUCU:\n\n{error_msg}')
                
        except UserError:
            raise
        except requests.exceptions.RequestException as e:
            _logger.error('Error de solicitud: %s', str(e))
            raise UserError(f'Error de conexion:\n\n{str(e)}')
    
    def anulate_rent_invoice(self, invoice, reason_code):
        """Anula una factura de alquileres"""
        company = invoice.company_id
        token = self._get_auth_token(company)
        
        if not invoice.cucu_rent_cuf:
            raise UserError('La factura no tiene CUF asignado')
        
        headers = self._create_header(token)
        payload = {'cuf': invoice.cucu_rent_cuf, 'reasonCode': reason_code}
        
        endpoint = company.cucu_rent_anulation_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent/anulation'
        endpoint = endpoint.strip().rstrip('/')
        
        _logger.info('=== Anulando factura CUF: %s ===', invoice.cucu_rent_cuf)
        
        try:
            response = requests.post(
                url=endpoint,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            result = response.json()
            
            if result.get('success'):
                invoice.write({'cucu_rent_state': 'cancelled'})
                _logger.info('Factura anulada exitosamente')
                return result.get('data', {})
            else:
                error_msg = result.get('message', 'Error desconocido')
                raise UserError(f'Error al anular:\n\n{error_msg}')
                
        except UserError:
            raise
        except requests.exceptions.RequestException as e:
            raise UserError(f'Error al anular:\n\n{str(e)}')
