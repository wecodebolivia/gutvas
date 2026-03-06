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
        
        # URL completa sin modificar (igual que en JS funcional)
        auth_url = company.cucu_rent_auth_endpoint or 'https://sandbox.cucu.ai/auth/login'
        auth_url = auth_url.strip()
        
        # Payload exacto como en JS
        payload = {
            'username': company.cucu_rent_username.strip(),
            'password': company.cucu_rent_password.strip()
        }
        
        _logger.info('=== Autenticacion CUCU Alquileres ===')
        _logger.info('URL: %s', auth_url)
        _logger.info('Usuario: %s', payload['username'])
        _logger.info('Payload: %s', json.dumps(payload))
        
        try:
            # Headers identicos al JS funcional
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            _logger.info('Headers: %s', json.dumps(headers))
            
            # Request POST con timeout
            response = requests.post(
                auth_url,
                data=json.dumps(payload),  # Usar data en vez de json para control exacto
                headers=headers,
                timeout=30
            )
            
            _logger.info('Response Status: %d', response.status_code)
            _logger.info('Response Headers: %s', dict(response.headers))
            _logger.info('Response Body: %s', response.text[:500])
            
            # Parsear respuesta
            try:
                data = response.json()
            except:
                data = {'error': 'Respuesta no es JSON', 'raw': response.text}
            
            # Manejar error 401
            if response.status_code == 401:
                raise UserError(
                    f'Error de autenticacion CUCU:\n\n'
                    f'HTTP 401: {json.dumps(data, indent=2)}\n\n'
                    f'URL: {auth_url}\n'
                    f'Usuario: {payload["username"]}\n\n'
                    f'Credenciales sandbox:\n'
                    f'Usuario: demo.largotek.alquiler\n'
                    f'Password: bd3f2919c865452aaf48f3c596507e2c\n\n'
                    f'NOTA: Si el error dice "Not unauthorized", puede ser un problema\n'
                    f'de configuracion del servidor CUCU o firewall de Odoo.sh'
                )
            
            # Verificar otros errores HTTP
            if not response.ok:
                raise UserError(
                    f'Error HTTP {response.status_code}:\n\n'
                    f'{json.dumps(data, indent=2)}'
                )
            
            # Extraer token
            token = None
            if isinstance(data, dict):
                if data.get('success') and data.get('data'):
                    token = data['data'].get('token')
                elif data.get('token'):
                    token = data.get('token')
                elif data.get('data') and isinstance(data['data'], dict):
                    token = data['data'].get('token')
            
            if not token:
                raise UserError(
                    f'No se recibio token en la respuesta.\n\n'
                    f'Respuesta completa:\n{json.dumps(data, indent=2)}'
                )
            
            # Guardar token con expiracion
            expiry_date = datetime.now() + timedelta(days=60)
            company.sudo().write({
                'cucu_rent_token': token,
                'cucu_rent_token_expiry': expiry_date
            })
            
            _logger.info('Token JWT generado exitosamente - Expira: %s', expiry_date)
            return token
            
        except UserError:
            raise
        except requests.exceptions.Timeout:
            raise UserError(
                'Timeout al conectar con CUCU API.\n\n'
                'Posibles causas:\n'
                '- Firewall de Odoo.sh bloqueando conexiones\n'
                '- API CUCU no disponible\n'
                '- Problemas de red'
            )
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
        
        # Headers identicos al JS funcional
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cucukey': f'Token {token}'
        }
        
        payload = invoice._prepare_cucu_rent_invoice_data()
        endpoint = company.cucu_rent_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent'
        endpoint = endpoint.strip()
        
        _logger.info('=== Enviando factura %s a CUCU ===', invoice.name)
        _logger.info('Endpoint: %s', endpoint)
        _logger.info('Periodo: %s', invoice.rent_billed_period)
        _logger.info('Headers: %s', {k: v[:50] + '...' if k == 'cucukey' and len(v) > 50 else v for k, v in headers.items()})
        
        try:
            response = requests.post(
                endpoint,
                data=json.dumps(payload),
                headers=headers,
                timeout=60
            )
            
            _logger.info('Response Status: %d', response.status_code)
            _logger.info('Response Body: %s', response.text[:500])
            
            # Reintentar si token expiro
            if response.status_code == 401:
                _logger.warning('Token expirado, renovando...')
                company.sudo().write({'cucu_rent_token': False, 'cucu_rent_token_expiry': False})
                token = self._get_auth_token(company)
                headers['cucukey'] = f'Token {token}'
                
                response = requests.post(
                    endpoint,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=60
                )
                _logger.info('Retry Response Status: %d', response.status_code)
            
            # Verificar respuesta
            if not response.ok:
                try:
                    error_data = response.json()
                    error_msg = json.dumps(error_data, indent=2)
                except:
                    error_msg = response.text
                raise UserError(f'Error HTTP {response.status_code}:\n\n{error_msg}')
            
            result = response.json()
            
            if result.get('success'):
                _logger.info('Factura enviada exitosamente')
                return result.get('data', {})
            else:
                error_msg = result.get('message', 'Error desconocido')
                errors = result.get('errors', '')
                if errors:
                    error_msg += f'\n\nDetalles: {json.dumps(errors, indent=2)}'
                raise UserError(f'Error CUCU:\n\n{error_msg}')
                
        except UserError:
            raise
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
        endpoint = company.cucu_rent_anulation_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent/anulation'
        endpoint = endpoint.strip()
        
        _logger.info('=== Anulando factura CUF: %s ===', invoice.cucu_rent_cuf)
        
        try:
            response = requests.post(
                endpoint,
                data=json.dumps(payload),
                headers=headers,
                timeout=60
            )
            
            if not response.ok:
                try:
                    error_data = response.json()
                    error_msg = json.dumps(error_data, indent=2)
                except:
                    error_msg = response.text
                raise UserError(f'Error HTTP {response.status_code}:\n\n{error_msg}')
            
            result = response.json()
            
            if result.get('success'):
                invoice.write({'cucu_rent_state': 'cancelled'})
                return result.get('data', {})
            else:
                raise UserError(f'Error al anular:\n\n{result.get("message")}')
                
        except UserError:
            raise
        except requests.exceptions.RequestException as e:
            raise UserError(f'Error al anular:\n\n{str(e)}')
