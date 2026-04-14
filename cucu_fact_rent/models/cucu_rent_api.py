# -*- coding: utf-8 -*-
import requests
import json
import logging
import traceback
from datetime import datetime, timedelta
from odoo import models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

SEP = '=' * 80
SEP_THIN = '-' * 80


class CucuRentAPI(models.AbstractModel):
    _name = 'cucu.rent.api'
    _description = 'Servicio API CUCU para Sector Alquileres'

    def _create_header(self, token=''):
        if token:
            return {'content-type': 'application/json', 'cucukey': f'Token {token}'}
        return {'content-type': 'application/json'}

    def _log_request(self, method, url, payload):
        """Log COMPLETO del payload enviado a CUCU/SIAT.

        Muestra todos los campos incluyendo detailInvoice expandido
        para facilitar debug y verificar que propertyAddress y
        billedPeriod se envian correctamente.
        """
        # Copia del payload ocultando password si existiera
        safe_payload = {k: v for k, v in payload.items() if k not in ('password',)}

        # Resumen ejecutivo de campos clave
        summary_lines = [
            f"  ▶ Endpoint      : {method} {url}",
            f"  ▶ posId          : {payload.get('posId', 'N/A')}",
            f"  ▶ clientNro      : {payload.get('clientNroDocument', 'N/A')}",
            f"  ▶ clientRazon    : {payload.get('clientReasonSocial', 'N/A')}",
            f"  ▶ billedPeriod   : {payload.get('billedPeriod', '*** AUSENTE ***')}",
            f"  ▶ propertyAddress: {payload.get('propertyAddress', '(no incluido)')} ",
            f"  ▶ typeOperation  : {payload.get('typeOperation', 'N/A')}",
            f"  ▶ dateEmission   : {payload.get('dateEmission', 'N/A')}",
            f"  ▶ lines          : {len(payload.get('detailInvoice', []))}",
        ]

        _logger.info(
            '\n%s\n[CUCU-RENT] REQUEST  %s %s\n%s\nSUMMARY:\n%s\n%s\nPAYLOAD COMPLETO:\n%s\n%s',
            SEP, method, url, SEP_THIN,
            '\n'.join(summary_lines),
            SEP_THIN,
            json.dumps(safe_payload, indent=2, ensure_ascii=False),
            SEP
        )

    def _log_response(self, response, context=''):
        tag = f'[{context}] ' if context else ''
        try:
            body = json.dumps(response.json(), indent=2, ensure_ascii=False)
        except Exception:
            body = response.text or '(sin cuerpo)'
        level = _logger.info if response.status_code < 400 else _logger.warning
        level(
            '\n%s\n[CUCU-RENT] %sRESPONSE  HTTP %s  |  %s ms\n%s\n%s\n%s',
            SEP, tag, response.status_code,
            int(response.elapsed.total_seconds() * 1000),
            SEP_THIN, body, SEP
        )
        return response

    def _log_error(self, context, exc):
        _logger.error(
            '\n%s\n[CUCU-RENT] ERROR en %s\n%s\n%s\n%s',
            SEP, context, SEP_THIN,
            traceback.format_exc(),
            SEP
        )

    def _handle_401(self, company, url, method_fn):
        """Renueva token y reintenta una vez."""
        _logger.warning('[CUCU-RENT] 401 recibido — renovando token y reintentando: %s', url)
        company.sudo().write({'cucu_rent_token': False, 'cucu_rent_token_expiry': False})
        token = self._get_auth_token(company)
        return method_fn(token)

    def _get_auth_token(self, company):
        if company.cucu_rent_token and company.cucu_rent_token_expiry:
            if datetime.now() < company.cucu_rent_token_expiry:
                _logger.debug('[CUCU-RENT] Token en cache válido para %s', company.name)
                return company.cucu_rent_token

        if not company.cucu_rent_username or not company.cucu_rent_password:
            raise UserError(
                'Configure las credenciales CUCU para sector alquileres en:\n'
                'Configuración > Compañías > Facturación Alquileres'
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

        payload = {
            'username': company.cucu_rent_username.strip(),
            'password': '***OCULTO***'
        }
        _logger.info(
            '\n%s\n[CUCU-RENT] AUTH LOGIN  %s\n%s\nUser: %s  |  Company: %s\n%s',
            SEP, url, SEP_THIN, company.cucu_rent_username, company.name, SEP
        )

        real_payload = {
            'username': company.cucu_rent_username.strip(),
            'password': company.cucu_rent_password.strip()
        }
        try:
            response = requests.post(url=url, json=real_payload,
                                     headers=self._create_header(), timeout=30)
            self._log_response(response, 'AUTH')
            result = response.json()

            if result.get('success') or result.get('message') == 'TOKEN CREADED':
                token = result['data']['token']
                expiry_date = datetime.now() + timedelta(days=60)
                company.sudo().write({
                    'cucu_rent_token': token,
                    'cucu_rent_token_expiry': expiry_date
                })
                _logger.info('[CUCU-RENT] Token obtenido correctamente. Expira: %s', expiry_date)
                return token
            else:
                raise UserError(f'Error de autenticación CUCU:\n{result.get("message", "Error desconocido")}')

        except UserError:
            raise
        except requests.exceptions.Timeout:
            raise UserError(f'Timeout al conectar con CUCU API (login).\nURL: {url}')
        except requests.exceptions.ConnectionError as e:
            raise UserError(f'No se pudo conectar con CUCU API.\nURL: {url}\nError: {str(e)}')
        except Exception as e:
            self._log_error('AUTH', e)
            raise UserError(f'Error inesperado en autenticación:\n{str(e)}')

    def _get_rent_base_url(self, company):
        endpoint = company.cucu_rent_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent'
        endpoint = endpoint.strip().rstrip('/')
        if '/api/v1/invoice/electronic/rent' in endpoint:
            return endpoint.replace('/api/v1/invoice/electronic/rent', '')
        return endpoint.replace('/api/v1', '')

    # ========================= EMISIÓN =========================

    def send_rent_invoice(self, invoice):
        company = invoice.company_id
        _logger.info(
            '\n%s\n[CUCU-RENT] EMISIÓN  Factura: %s  |  Compañía: %s\n%s',
            SEP, invoice.name, company.name, SEP
        )
        token = self._get_auth_token(company)
        headers = self._create_header(token)
        payload = invoice._prepare_cucu_rent_invoice_data()

        endpoint = company.cucu_rent_endpoint or 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent'
        endpoint = endpoint.strip().rstrip('/')

        try:
            self._log_request('POST', endpoint, payload)
            response = requests.post(url=endpoint, json=payload, headers=headers, timeout=60)
            self._log_response(response, 'EMISION')

            if response.status_code == 401:
                response = self._handle_401(company, endpoint,
                    lambda t: requests.post(url=endpoint, json=payload,
                                            headers=self._create_header(t), timeout=60))
                self._log_response(response, 'EMISION-RETRY')

            result = response.json()

            if result.get('success'):
                data = result.get('data', {})
                _logger.info(
                    '[CUCU-RENT] EMISIÓN OK  CUF: %s | invoiceCode: %s | invoiceNumber: %s',
                    data.get('cuf'), data.get('invoiceCode'), data.get('invoiceNumber')
                )
                return data
            else:
                error_msg = result.get('message', 'Error desconocido')
                errors = result.get('errors', '')
                if errors:
                    error_msg += f'\n\nDetalles: {json.dumps(errors, indent=2)}'
                _logger.error('[CUCU-RENT] EMISIÓN FALLIDA: %s', error_msg)
                raise UserError(f'Error CUCU (emisión):\n\n{error_msg}')

        except UserError:
            raise
        except requests.exceptions.Timeout:
            self._log_error('EMISION-TIMEOUT', Exception('timeout'))
            raise UserError(f'Timeout enviando factura a CUCU.\nURL: {endpoint}')
        except requests.exceptions.RequestException as e:
            self._log_error('EMISION-CONNECTION', e)
            raise UserError(f'Error de conexión al enviar factura:\n\n{str(e)}')

    # ========================= STATUS / RECUPERACIÓN =========================

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

        _logger.info(
            '\n%s\n[CUCU-RENT] STATUS  GET %s\n%s\nParams: %s\n%s',
            SEP, url, SEP_THIN, json.dumps(params, indent=2), SEP
        )

        try:
            response = requests.get(url=url, json=params, headers=headers, timeout=30)
            self._log_response(response, 'STATUS')

            if response.status_code == 401:
                response = self._handle_401(company, url,
                    lambda t: requests.get(url=url, json=params,
                                           headers=self._create_header(t), timeout=30))
                self._log_response(response, 'STATUS-RETRY')

            result = response.json()

            if result.get('success'):
                data = result.get('data', {})
                _logger.info(
                    '[CUCU-RENT] STATUS OK  CUF: %s | invoiceCode: %s | invoiceNumber: %s | siatState: %s',
                    data.get('cuf'), data.get('invoiceCode'),
                    data.get('invoiceNumber'), data.get('siatCodeState')
                )
                return data
            else:
                error_msg = result.get('message', 'Error desconocido')
                errors = result.get('errors', [])
                detail = ''
                if errors:
                    detail = '\n\nCampos con error:\n' + ''.join(
                        f'  - {e.get("field", "?")}: {e.get("message", "?")}\n' for e in errors
                    )
                _logger.warning(
                    '[CUCU-RENT] STATUS FALLIDO  invoiceCode=%s invoiceNumber=%s\nError: %s%s',
                    invoice_code, invoice_number, error_msg, detail
                )
                raise UserError(
                    f'Error al recuperar datos de la factura:\n\n{error_msg}{detail}\n'
                    f'invoiceCode: {invoice_code} | invoiceNumber: {invoice_number} | '
                    f'posId: {params["posId"]} | branchId: {params["branchId"]}'
                )

        except UserError:
            raise
        except requests.exceptions.Timeout:
            self._log_error('STATUS-TIMEOUT', Exception('timeout'))
            raise UserError(f'Timeout al recuperar datos de la factura.\nURL: {url}')
        except requests.exceptions.RequestException as e:
            self._log_error('STATUS-CONNECTION', e)
            raise UserError(f'Error de conexión al recuperar factura:\n\n{str(e)}')

    # ========================= PAYLOAD ANULACIÓN / REERSIÓN =========================

    def _build_anulation_payload(self, invoice):
        pos_data = invoice._get_cucu_rent_pos_data()
        invoice_number = invoice.cucu_rent_invoice_number or invoice.invoice_number
        invoice_code = invoice.cucu_rent_invoice_code or invoice.invoice_code

        _logger.info(
            '[CUCU-RENT] _build_anulation_payload  cuf=%s | invoiceCode=%s | invoiceNumber=%s | posId=%s',
            invoice.cucu_rent_cuf, invoice_code, invoice_number, pos_data['posId']
        )

        if not invoice_number:
            raise UserError(
                'Falta el Número de Factura (cucu_rent_invoice_number).\n'
                'Intróducelo en el campo "Número Factura" y guarda.'
            )
        if not invoice_code:
            raise UserError(
                'Falta el Invoice Code (cucu_rent_invoice_code).\n'
                'Intróducelo en el campo "Invoice Code" y guarda.'
            )
        return {
            'cuf': invoice.cucu_rent_cuf,
            'invoiceNumber': int(invoice_number),
            'invoiceCode': invoice_code,
            'posId': pos_data['posId'],
        }

    # ========================= ANULACIÓN =========================

    def anulate_rent_invoice(self, invoice):
        """
        POST /api/v1/invoice/electronic/rent/anulation
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

        _logger.info(
            '\n%s\n[CUCU-RENT] ANULACIÓN  Factura: %s\n%s\nEndpoint: %s\nPayload: %s\n%s',
            SEP, invoice.name, SEP_THIN, endpoint,
            json.dumps(payload, indent=2, ensure_ascii=False), SEP
        )

        try:
            response = requests.post(url=endpoint, json=payload, headers=headers, timeout=60)
            self._log_response(response, 'ANULACION')

            if response.status_code == 401:
                response = self._handle_401(company, endpoint,
                    lambda t: requests.post(url=endpoint, json=payload,
                                            headers=self._create_header(t), timeout=60))
                self._log_response(response, 'ANULACION-RETRY')

            result = response.json()

            if result.get('success'):
                invoice.write({'cucu_rent_state': 'cancelled'})
                _logger.info('[CUCU-RENT] ANULACIÓN OK  Factura %s anulada.', invoice.name)
                return result.get('data', {})
            else:
                error_msg = result.get('message', 'Error desconocido')
                _logger.error('[CUCU-RENT] ANULACIÓN FALLIDA: %s', error_msg)
                raise UserError(f'Error al anular:\n\n{error_msg}')

        except UserError:
            raise
        except requests.exceptions.Timeout:
            self._log_error('ANULACION-TIMEOUT', Exception('timeout'))
            raise UserError(f'Timeout al anular factura.\nURL: {endpoint}')
        except requests.exceptions.RequestException as e:
            self._log_error('ANULACION-CONNECTION', e)
            raise UserError(f'Error de conexión al anular:\n\n{str(e)}')

    # ========================= REERSIÓN =========================

    def revert_rent_invoice(self, invoice):
        """
        POST /api/v1/invoice/electronic/rent/revert
        """
        company = invoice.company_id
        if not invoice.cucu_rent_cuf:
            raise UserError('La factura no tiene CUF asignado.')

        token = self._get_auth_token(company)
        headers = self._create_header(token)
        payload = self._build_anulation_payload(invoice)

        host = self._get_rent_base_url(company)
        endpoint = f'{host}/api/v1/invoice/electronic/rent/revert'

        _logger.info(
            '\n%s\n[CUCU-RENT] REERSIÓN  Factura: %s\n%s\nEndpoint: %s\nPayload: %s\n%s',
            SEP, invoice.name, SEP_THIN, endpoint,
            json.dumps(payload, indent=2, ensure_ascii=False), SEP
        )

        try:
            response = requests.post(url=endpoint, json=payload, headers=headers, timeout=60)
            self._log_response(response, 'REVERSION')

            if response.status_code == 401:
                response = self._handle_401(company, endpoint,
                    lambda t: requests.post(url=endpoint, json=payload,
                                            headers=self._create_header(t), timeout=60))
                self._log_response(response, 'REVERSION-RETRY')

            result = response.json()

            if result.get('success'):
                invoice.write({'cucu_rent_state': 'cancelled'})
                _logger.info('[CUCU-RENT] REERSIÓN OK  Factura %s revertida.', invoice.name)
                return result.get('data', {})
            else:
                error_msg = result.get('message', 'Error desconocido')
                _logger.error('[CUCU-RENT] REERSIÓN FALLIDA: %s', error_msg)
                raise UserError(f'Error al revertir:\n\n{error_msg}')

        except UserError:
            raise
        except requests.exceptions.Timeout:
            self._log_error('REVERSION-TIMEOUT', Exception('timeout'))
            raise UserError(f'Timeout al revertir factura.\nURL: {endpoint}')
        except requests.exceptions.RequestException as e:
            self._log_error('REVERSION-CONNECTION', e)
            raise UserError(f'Error de conexión al revertir:\n\n{str(e)}')
