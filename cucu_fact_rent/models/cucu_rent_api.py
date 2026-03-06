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
    
    # ========== AUTENTICACIÓN JWT ==========
    def _get_auth_token(self, company):
        """
        Obtiene o renueva el token JWT para sector alquileres.
        
        El token se guarda en company.cucu_rent_token y se renueva automáticamente
        cuando expira (duración: 60 días según JWT estándar).
        
        Returns:
            str: Token JWT válido
        """
        # Verificar si token existente es válido
        if company.cucu_rent_token and company.cucu_rent_token_expiry:
            if datetime.now() < company.cucu_rent_token_expiry:
                _logger.info('Usando token JWT existente (válido hasta %s)', company.cucu_rent_token_expiry)
                return company.cucu_rent_token
        
        # Validar credenciales
        if not company.cucu_rent_username or not company.cucu_rent_password:
            raise UserError(
                'Configure las credenciales CUCU para sector alquileres en:\n'
                'Configuración > Compañías > Facturación Alquileres'
            )
        
        # Solicitar nuevo token
        auth_url = company.cucu_rent_auth_endpoint or 'https://sandbox.cucu.ai/auth/login'
        payload = {
            'username': company.cucu_rent_username,
            'password': company.cucu_rent_password
        }
        
        _logger.info('=== Solicitando token JWT para sector alquileres ===')
        _logger.info('URL: %s', auth_url)
        _logger.info('Usuario: %s', company.cucu_rent_username)
        
        try:
            response = requests.post(auth_url, json=payload, timeout=30)
            
            _logger.info('Auth Response Status: %d', response.status_code)
            _logger.debug('Auth Response Body: %s', response.text)
            
            response.raise_for_status()
            data = response.json()
            
            # Extraer token (estructuras posibles según CUCU API)
            token = None
            if data.get('success') and data.get('data'):
                token = data['data'].get('token')
            elif data.get('token'):
                token = data.get('token')
            
            if not token:
                raise UserError(
                    f'No se recibió token en la respuesta de autenticación.\n'
                    f'Respuesta: {json.dumps(data, indent=2)}'
                )
            
            # Guardar token con fecha de expiración
            expiry_date = datetime.now() + timedelta(days=60)
            company.sudo().write({
                'cucu_rent_token': token,
                'cucu_rent_token_expiry': expiry_date
            })
            
            _logger.info('✅ Token JWT generado exitosamente (expira: %s)', expiry_date)
            return token
            
        except requests.exceptions.HTTPError as e:
            error_msg = f'HTTP {e.response.status_code}: {e.response.text}'
            _logger.error('❌ Error HTTP al obtener token: %s', error_msg)
            raise UserError(f'Error de autenticación CUCU:\n\n{error_msg}')
            
        except requests.exceptions.RequestException as e:
            _logger.error('❌ Error de conexión al obtener token: %s', str(e))
            raise UserError(f'Error de conexión con CUCU API:\n\n{str(e)}')
    
    # ========== EMISIÓN DE FACTURAS ==========
    def send_rent_invoice(self, invoice):
        """
        Envía factura de alquileres a CUCU API.
        
        Args:
            invoice: Registro account.move con is_rent_invoice=True
            
        Returns:
            dict: Respuesta JSON de CUCU con CUF y datos de la factura
        """
        company = invoice.company_id
        token = self._get_auth_token(company)
        
        # Construir headers según especificación CUCU
        # IMPORTANTE: formato "cucukey: Token {jwt}" (no "Authorization: Bearer")
        headers = {
            'Content-Type': 'application/json',
            'cucukey': f'Token {token}'
        }
        
        # Obtener payload preparado
        payload = invoice._prepare_cucu_rent_invoice_data()
        
        endpoint = company.cucu_rent_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent'
        
        _logger.info('=== Enviando factura %s a CUCU (Alquileres) ===', invoice.name)
        _logger.info('Endpoint: %s', endpoint)
        _logger.debug('Payload: %s', json.dumps(payload, indent=2, ensure_ascii=False))
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            _logger.info('Response Status: %d', response.status_code)
            _logger.debug('Response Body: %s', response.text)
            
            # Manejo especial de error 401 (token expirado)
            if response.status_code == 401:
                _logger.warning('⚠️ Token expirado (401), renovando y reintentando...')
                
                # Forzar renovación de token
                company.sudo().write({'cucu_rent_token': False})
                token = self._get_auth_token(company)
                headers['cucukey'] = f'Token {token}'
                
                # Reintentar solicitud
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                
                _logger.info('Retry Response Status: %d', response.status_code)
                _logger.debug('Retry Response Body: %s', response.text)
            
            response.raise_for_status()
            result = response.json()
            
            # Validar respuesta exitosa
            if result.get('success'):
                _logger.info('✅ Factura enviada exitosamente')
                return result.get('data', {})
            else:
                error_msg = result.get('message', 'Error desconocido')
                errors = result.get('errors', '')
                full_error = f"{error_msg}\n\nDetalles: {errors}" if errors else error_msg
                
                _logger.error('❌ Error CUCU: %s', full_error)
                raise UserError(f'Error reportado por CUCU:\n\n{full_error}')
                
        except requests.exceptions.HTTPError as e:
            error_msg = f'HTTP {e.response.status_code}: {e.response.text}'
            _logger.error('❌ Error HTTP: %s', error_msg)
            raise UserError(f'Error HTTP al enviar factura:\n\n{error_msg}')
            
        except requests.exceptions.RequestException as e:
            _logger.error('❌ Error de solicitud: %s', str(e))
            raise UserError(f'Error de conexión con CUCU API:\n\n{str(e)}')
    
    # ========== ANULACIÓN DE FACTURAS ==========
    def anulate_rent_invoice(self, invoice, reason_code):
        """
        Anula una factura de alquileres ya emitida.
        
        Args:
            invoice: Registro account.move con cucu_rent_cuf
            reason_code: Código de motivo de anulación (catálogo SIN)
            
        Returns:
            dict: Respuesta JSON de CUCU
        """
        company = invoice.company_id
        token = self._get_auth_token(company)
        
        if not invoice.cucu_rent_cuf:
            raise UserError('No se puede anular: la factura no tiene CUF asignado')
        
        headers = {
            'Content-Type': 'application/json',
            'cucukey': f'Token {token}'
        }
        
        payload = {
            'cuf': invoice.cucu_rent_cuf,
            'reasonCode': reason_code
        }
        
        endpoint = company.cucu_rent_anulation_endpoint
        
        _logger.info('=== Anulando factura CUF: %s ===', invoice.cucu_rent_cuf)
        _logger.info('Motivo: %s', reason_code)
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                _logger.info('✅ Factura anulada exitosamente')
                invoice.write({'cucu_rent_state': 'cancelled'})
                return result.get('data', {})
            else:
                error_msg = result.get('message', 'Error desconocido')
                raise UserError(f'Error al anular factura:\n\n{error_msg}')
                
        except requests.exceptions.RequestException as e:
            _logger.error('❌ Error al anular factura: %s', str(e))
            raise UserError(f'Error al anular factura:\n\n{str(e)}')