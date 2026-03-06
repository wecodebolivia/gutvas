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
    
    def _log_request_details(self, method, url, headers, payload):
        """Log detallado de la request"""
        _logger.info('\n' + '='*80)
        _logger.info('CUCU API REQUEST')
        _logger.info('='*80)
        _logger.info('Method: %s', method)
        _logger.info('URL: %s', url)
        _logger.info('-'*80)
        _logger.info('HEADERS:')
        for key, value in headers.items():
            if key.lower() == 'cucukey' and value:
                _logger.info('  %s: %s...', key, value[:30])
            else:
                _logger.info('  %s: %s', key, value)
        _logger.info('-'*80)
        _logger.info('PAYLOAD:')
        _logger.info('%s', json.dumps(payload, indent=2, ensure_ascii=False))
        _logger.info('='*80 + '\n')
    
    def _log_response_details(self, response):
        """Log detallado de la response"""
        _logger.info('\n' + '='*80)
        _logger.info('CUCU API RESPONSE')
        _logger.info('='*80)
        _logger.info('Status Code: %s', response.status_code)
        _logger.info('-'*80)
        _logger.info('RESPONSE HEADERS:')
        for key, value in response.headers.items():
            _logger.info('  %s: %s', key, value)
        _logger.info('-'*80)
        _logger.info('RESPONSE BODY:')
        try:
            data = response.json()
            _logger.info('%s', json.dumps(data, indent=2, ensure_ascii=False))
        except:
            _logger.info('%s', response.text)
        _logger.info('='*80 + '\n')
        return response
    
    def _get_auth_token(self, company):
        """Obtiene o renueva el token JWT - METODO IDENTICO A cucu_fact_core"""
        if company.cucu_rent_token and company.cucu_rent_token_expiry:
            if datetime.now() < company.cucu_rent_token_expiry:
                _logger.info('[TOKEN] Usando token existente - Expira: %s', company.cucu_rent_token_expiry)
                return company.cucu_rent_token
        
        _logger.info('[AUTH] Iniciando autenticacion...')
        
        if not company.cucu_rent_username or not company.cucu_rent_password:
            raise UserError(
                'Configure las credenciales CUCU para sector alquileres en:\n'
                'Configuracion > Companias > Facturacion Alquileres'
            )
        
        # URL base
        host = company.cucu_rent_auth_endpoint or 'https://sandbox.cucu.ai'
        host = host.strip().rstrip('/')
        
        # Construir URL completa
        if '/auth/login' in host:
            url = host
        else:
            url = f'{host}/api/v1/auth/login'
        
        params_json = {
            'username': company.cucu_rent_username.strip(),
            'password': company.cucu_rent_password.strip()
        }
        
        _logger.info('[AUTH] Configuracion:')
        _logger.info('  - Host configurado: %s', company.cucu_rent_auth_endpoint or '(default)')
        _logger.info('  - URL final: %s', url)
        _logger.info('  - Usuario: %s', params_json['username'])
        _logger.info('  - Password: %s', '*' * len(params_json['password']))
        
        try:
            headers = self._create_header()
            
            # Log detallado ANTES de la request
            self._log_request_details('POST', url, headers, params_json)
            
            # REQUEST
            _logger.info('[HTTP] Enviando POST request...')
            response = requests.post(
                url=url,
                json=params_json,
                headers=headers,
                timeout=30
            )
            _logger.info('[HTTP] Request completada')
            
            # Log detallado DESPUES de la response
            self._log_response_details(response)
            
            # Parsear respuesta
            try:
                result = response.json()
            except Exception as e:
                _logger.error('[ERROR] No se pudo parsear JSON: %s', str(e))
                _logger.error('[ERROR] Response text: %s', response.text)
                raise UserError(
                    f'Respuesta invalida del servidor CUCU.\n\n'
                    f'Status: {response.status_code}\n'
                    f'Body: {response.text[:500]}'
                )
            
            # Validar respuesta exitosa
            _logger.info('[AUTH] Validando respuesta...')
            _logger.info('  - success: %s', result.get('success'))
            _logger.info('  - message: %s', result.get('message'))
            
            if result.get('success') or result.get('message') == 'TOKEN CREADED':
                if 'data' in result and 'token' in result['data']:
                    token = result['data']['token']
                    _logger.info('[AUTH] Token recibido: %s...', token[:30])
                    
                    # Guardar token
                    expiry_date = datetime.now() + timedelta(days=60)
                    company.sudo().write({
                        'cucu_rent_token': token,
                        'cucu_rent_token_expiry': expiry_date
                    })
                    
                    _logger.info('[AUTH] Token guardado - Expira: %s', expiry_date)
                    return token
                else:
                    _logger.error('[ERROR] Respuesta exitosa pero sin token')
                    _logger.error('[ERROR] Estructura: %s', json.dumps(result, indent=2))
                    raise UserError(
                        f'Respuesta exitosa pero sin token.\n\n'
                        f'Respuesta completa:\n{json.dumps(result, indent=2)}'
                    )
            else:
                _logger.error('[ERROR] Autenticacion fallida')
                _logger.error('[ERROR] Mensaje: %s', result.get('message'))
                _logger.error('[ERROR] Errores: %s', result.get('errors'))
                
                error_msg = result.get('message', 'Error desconocido')
                raise UserError(
                    f'Error de autenticacion CUCU:\n\n'
                    f'{error_msg}\n\n'
                    f'Usuario: {params_json["username"]}\n'
                    f'URL: {url}\n\n'
                    f'Respuesta completa:\n{json.dumps(result, indent=2)}'
                )
            
        except UserError:
            raise
        except requests.exceptions.Timeout:
            _logger.error('[ERROR] Timeout al conectar')
            raise UserError(
                'Timeout al conectar con CUCU API (30 segundos).\n\n'
                f'URL: {url}\n\n'
                'Posibles causas:\n'
                '- Firewall de Odoo.sh bloqueando la conexion\n'
                '- API CUCU no disponible\n'
                '- Problemas de red'
            )
        except requests.exceptions.ConnectionError as e:
            _logger.error('[ERROR] Connection error: %s', str(e))
            raise UserError(
                f'No se pudo conectar con CUCU API.\n\n'
                f'URL: {url}\n'
                f'Error: {str(e)}'
            )
        except requests.exceptions.HTTPError as e:
            _logger.error('[ERROR] HTTP error: %s', str(e))
            raise UserError(f'HTTP Error: {str(e)}')
        except Exception as e:
            _logger.error('[ERROR] Error inesperado: %s', str(e), exc_info=True)
            raise UserError(f'Error inesperado:\n\n{str(e)}')
    
    def send_rent_invoice(self, invoice):
        """Envia factura de alquileres a CUCU API"""
        company = invoice.company_id
        
        _logger.info('[INVOICE] Iniciando envio de factura %s', invoice.name)
        
        if not invoice.rent_billed_period:
            raise UserError(
                'El campo "Periodo Facturado" es obligatorio.\n\n'
                'Ejemplo: "Mayo 2026"'
            )
        
        token = self._get_auth_token(company)
        headers = self._create_header(token)
        payload = invoice._prepare_cucu_rent_invoice_data()
        
        endpoint = company.cucu_rent_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent'
        endpoint = endpoint.strip().rstrip('/')
        
        _logger.info('[INVOICE] Configuracion:')
        _logger.info('  - Endpoint: %s', endpoint)
        _logger.info('  - Factura: %s', invoice.name)
        _logger.info('  - Periodo: %s', invoice.rent_billed_period)
        _logger.info('  - Cliente: %s', invoice.partner_id.name)
        
        try:
            # Log detallado ANTES
            self._log_request_details('POST', endpoint, headers, payload)
            
            # REQUEST
            _logger.info('[HTTP] Enviando POST request...')
            response = requests.post(
                url=endpoint,
                json=payload,
                headers=headers,
                timeout=60
            )
            _logger.info('[HTTP] Request completada')
            
            # Log detallado DESPUES
            self._log_response_details(response)
            
            # Reintentar si token expiro
            if response.status_code == 401:
                _logger.warning('[AUTH] Token expirado (401), renovando...')
                company.sudo().write({'cucu_rent_token': False, 'cucu_rent_token_expiry': False})
                token = self._get_auth_token(company)
                headers = self._create_header(token)
                
                _logger.info('[HTTP] Reintentando con nuevo token...')
                response = requests.post(
                    url=endpoint,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                self._log_response_details(response)
            
            # Parsear respuesta
            try:
                result = response.json()
            except:
                raise UserError(
                    f'Respuesta invalida del servidor.\n\n'
                    f'Status: {response.status_code}\n'
                    f'Body: {response.text[:500]}'
                )
            
            # Validar respuesta
            if result.get('success'):
                data = result.get('data', {})
                cuf = data.get('cuf', 'N/A')
                _logger.info('[INVOICE] Factura enviada exitosamente')
                _logger.info('[INVOICE] CUF generado: %s', cuf)
                return data
            else:
                error_msg = result.get('message', 'Error desconocido')
                errors = result.get('errors', '')
                if errors:
                    error_msg += f'\n\nDetalles: {json.dumps(errors, indent=2)}'
                _logger.error('[ERROR] Envio fallido: %s', error_msg)
                raise UserError(f'Error CUCU:\n\n{error_msg}')
                
        except UserError:
            raise
        except requests.exceptions.RequestException as e:
            _logger.error('[ERROR] Request exception: %s', str(e))
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
        
        _logger.info('[ANULATION] Anulando factura CUF: %s', invoice.cucu_rent_cuf)
        
        try:
            self._log_request_details('POST', endpoint, headers, payload)
            
            response = requests.post(
                url=endpoint,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            self._log_response_details(response)
            
            result = response.json()
            
            if result.get('success'):
                invoice.write({'cucu_rent_state': 'cancelled'})
                _logger.info('[ANULATION] Factura anulada exitosamente')
                return result.get('data', {})
            else:
                error_msg = result.get('message', 'Error desconocido')
                raise UserError(f'Error al anular:\n\n{error_msg}')
                
        except UserError:
            raise
        except requests.exceptions.RequestException as e:
            raise UserError(f'Error al anular:\n\n{str(e)}')
