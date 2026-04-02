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
        if token:
            return {'content-type': 'application/json', 'cucukey': f'Token {token}'}
        return {'content-type': 'application/json'}

    def _log_request_details(self, method, url, headers, payload):
        _logger.info('\n' + '='*80)
        _logger.info('CUCU API REQUEST: %s %s', method, url)
        _logger.info('PAYLOAD: %s', json.dumps(payload, indent=2, ensure_ascii=False))
        _logger.info('='*80)

    def _log_response_details(self, response):
        _logger.info('\n' + '='*80)
        _logger.info('CUCU API RESPONSE: %s', response.status_code)
        try:
            _logger.info('%s', json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception:
            _logger.info('%s', response.text)
        _logger.info('='*80)
        return response

    def _get_auth_token(self, company):
        if company.cucu_rent_token and company.cucu_rent_token_expiry:
            if datetime.now() < company.cucu_rent_token_expiry:
                return company.cucu_rent_token

        if not company.cucu_rent_username or not company.cucu_rent_password:
            raise UserError(
                'Configure las credenciales CUCU para sector alquileres en:\n'
                'Configuracion > Companias > Facturacion Alquileres'
            )

        host = company.cucu_rent_auth_endpoint or 'https://sandbox.cucu.ai'
        host = host.strip().rstrip('/')
        if host.endswith('/api/v1/auth/login'):
            url = host
        elif '/api/v1/' in host:
            url = f'{host}/auth/login' if not host.endswith('/') else f'{host}auth/login'
        else:
            host = host.replace('/auth/login', '')
            url = f'{host}/api/v1/auth/login'

        params_json = {
            'username': company.cucu_rent_username.strip(),
            'password': company.cucu_rent_password.strip()
        }

        try:
            response = requests.post(url=url, json=params_json,
                                     headers=self._create_header(), timeout=30)
            self._log_response_details(response)
            result = response.json()

            if result.get('success') or result.get('message') == 'TOKEN CREADED':
                token = result['data']['token']
                expiry_date = datetime.now() + timedelta(days=60)
                company.sudo().write({
                    'cucu_rent_token': token,
                    'cucu_rent_token_expiry': expiry_date
                })
                return token
            else:
                raise UserError(f'Error de autenticacion CUCU:\n{result.get("message", "Error desconocido")}')
        except UserError:
            raise
        except requests.exceptions.Timeout:
            raise UserError(f'Timeout al conectar con CUCU API.\nURL: {url}')
        except requests.exceptions.ConnectionError as e:
            raise UserError(f'No se pudo conectar con CUCU API.\nURL: {url}\nError: {str(e)}')
        except Exception as e:
            raise UserError(f'Error inesperado en autenticacion:\n{str(e)}')

    def _get_rent_base_url(self, company):
        endpoint = company.cucu_rent_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent'
        endpoint = endpoint.strip().rstrip('/')
        if '/api/v1/invoice/electronic/rent' in endpoint:
            return endpoint.replace('/api/v1/invoice/electronic/rent', '')
        return endpoint.replace('/api/v1', '')

    def send_rent_invoice(self, invoice):
        company = invoice.company_id
        _logger.info('[INVOICE] Iniciando envio de factura %s', invoice.name)
        token = self._get_auth_token(company)
        headers = self._create_header(token)
        payload = invoice._prepare_cucu_rent_invoice_data()
        endpoint = company.cucu_rent_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent'
        endpoint = endpoint.strip().rstrip('/')
        try:
            self._log_request_details('POST', endpoint, headers, payload)
            response = requests.post(url=endpoint, json=payload, headers=headers, timeout=60)
            self._log_response_details(response)
            if response.status_code == 401:
                company.sudo().write({'cucu_rent_token': False, 'cucu_rent_token_expiry': False})
                token = self._get_auth_token(company)
                headers = self._create_header(token)
                response = requests.post(url=endpoint, json=payload, headers=headers, timeout=60)
                self._log_response_details(response)
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                _logger.info('[INVOICE] CUF: %s | invoiceCode: %s', data.get('cuf'), data.get('invoiceCode'))
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
            raise UserError(f'Error de conexion:\n\n{str(e)}')

    def get_rent_invoice_status(self, invoice, invoice_code, invoice_number):
        """
        GET /api/v1/invoice/electronic/rent/status
        Params: invoiceCode, invoiceNumber, posId, branchId
        """
        company = invoice.company_id
        token = self._get_auth_token(company)
        headers = self._create_header(token)
        pos_data = invoice._get_cucu_rent_pos_data()
        host = self._get_rent_base_url(company)
        url = f'{host}/api/v1/invoice/electronic/rent/status'
        params = {
            'invoiceCode': invoice_code,
            'invoiceNumber': int(invoice_number),
            'posId': pos_data['posId'],
            'branchId': pos_data['branchId'],
        }
        _logger.info('[STATUS] GET %s | params: %s', url, params)
        try:
            response = requests.get(url=url, json=params, headers=headers, timeout=30)
            self._log_response_details(response)
            if response.status_code == 401:
                company.sudo().write({'cucu_rent_token': False, 'cucu_rent_token_expiry': False})
                token = self._get_auth_token(company)
                headers = self._create_header(token)
                response = requests.get(url=url, json=params, headers=headers, timeout=30)
                self._log_response_details(response)
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                _logger.info('[STATUS] Datos recuperados para invoiceCode: %s', invoice_code)
                return data
            else:
                error_msg = result.get('message', 'Error desconocido')
                errors = result.get('errors', [])
                if errors:
                    error_msg += '\n\nCampos requeridos faltantes:\n'
                    for e in errors:
                        error_msg += f'  - {e.get("field")}: {e.get("message")}\n'
                raise UserError(
                    f'Error al recuperar datos de la factura:\n\n{error_msg}\n'
                    f'invoiceCode: {invoice_code} | invoiceNumber: {invoice_number}'
                )
        except UserError:
            raise
        except requests.exceptions.RequestException as e:
            raise UserError(f'Error de conexion al recuperar factura:\n\n{str(e)}')

    def _build_anulation_payload(self, invoice):
        """Payload comun para anulacion y reversion."""
        pos_data = invoice._get_cucu_rent_pos_data()
        invoice_number = invoice.cucu_rent_invoice_number or invoice.invoice_number
        invoice_code = invoice.cucu_rent_invoice_code or invoice.invoice_code
        if not invoice_number:
            raise UserError(
                'Falta el Numero de Factura (cucu_rent_invoice_number).\n'
                'Introdúcelo manualmente en el campo "Número Factura Alquileres".'
            )
        if not invoice_code:
            raise UserError(
                'Falta el Invoice Code (cucu_rent_invoice_code).\n'
                'Introdúcelo manualmente en el campo "Invoice Code Alquileres".'
            )
        return {
            'cuf': invoice.cucu_rent_cuf,
            'invoiceNumber': int(invoice_number),
            'invoiceCode': invoice_code,
            'posId': pos_data['posId'],
        }

    def anulate_rent_invoice(self, invoice):
        """
        POST /api/v1/invoice/electronic/rent/anulation
        Payload: cuf, invoiceNumber, invoiceCode, posId
        """
        company = invoice.company_id
        if not invoice.cucu_rent_cuf:
            raise UserError('La factura no tiene CUF asignado.')
        token = self._get_auth_token(company)
        headers = self._create_header(token)
        payload = self._build_anulation_payload(invoice)
        endpoint = company.cucu_rent_anulation_endpoint or \
            f'{self._get_rent_base_url(company)}/api/v1/invoice/electronic/rent/anulation'
        endpoint = endpoint.strip().rstrip('/')
        try:
            self._log_request_details('POST', endpoint, headers, payload)
            response = requests.post(url=endpoint, json=payload, headers=headers, timeout=60)
            self._log_response_details(response)
            if response.status_code == 401:
                company.sudo().write({'cucu_rent_token': False, 'cucu_rent_token_expiry': False})
                token = self._get_auth_token(company)
                headers = self._create_header(token)
                response = requests.post(url=endpoint, json=payload, headers=headers, timeout=60)
                self._log_response_details(response)
            result = response.json()
            if result.get('success'):
                invoice.write({'cucu_rent_state': 'cancelled'})
                _logger.info('[ANULATION] Factura %s anulada correctamente.', invoice.name)
                return result.get('data', {})
            else:
                raise UserError(f'Error al anular:\n\n{result.get("message", "Error desconocido")}')
        except UserError:
            raise
        except requests.exceptions.RequestException as e:
            raise UserError(f'Error de conexion al anular:\n\n{str(e)}')

    def revert_rent_invoice(self, invoice):
        """
        POST /api/v1/invoice/electronic/rent/revert
        Payload: cuf, invoiceNumber, invoiceCode, posId
        """
        company = invoice.company_id
        if not invoice.cucu_rent_cuf:
            raise UserError('La factura no tiene CUF asignado.')
        token = self._get_auth_token(company)
        headers = self._create_header(token)
        payload = self._build_anulation_payload(invoice)
        host = self._get_rent_base_url(company)
        endpoint = f'{host}/api/v1/invoice/electronic/rent/revert'
        try:
            self._log_request_details('POST', endpoint, headers, payload)
            response = requests.post(url=endpoint, json=payload, headers=headers, timeout=60)
            self._log_response_details(response)
            if response.status_code == 401:
                company.sudo().write({'cucu_rent_token': False, 'cucu_rent_token_expiry': False})
                token = self._get_auth_token(company)
                headers = self._create_header(token)
                response = requests.post(url=endpoint, json=payload, headers=headers, timeout=60)
                self._log_response_details(response)
            result = response.json()
            if result.get('success'):
                invoice.write({'cucu_rent_state': 'cancelled'})
                _logger.info('[REVERT] Factura %s revertida correctamente.', invoice.name)
                return result.get('data', {})
            else:
                raise UserError(f'Error al revertir:\n\n{result.get("message", "Error desconocido")}')
        except UserError:
            raise
        except requests.exceptions.RequestException as e:
            raise UserError(f'Error de conexion al revertir:\n\n{str(e)}')
