# 🔧 Guía Técnica - Facturación Electrónica Sector Alquileres

**Módulo:** CUCU - Facturación Electrónica Sector Alquileres  
**Versión:** 1.0.0  
**Público objetivo:** Administradores de sistemas y desarrolladores

---

## 📑 Tabla de Contenidos

1. [Arquitectura del Módulo](#1-arquitectura-del-módulo)
2. [Instalación y Dependencias](#2-instalación-y-dependencias)
3. [Configuración Avanzada](#3-configuración-avanzada)
4. [API CUCU - Especificaciones](#4-api-cucu---especificaciones)
5. [Estructura de Base de Datos](#5-estructura-de-base-de-datos)
6. [Logs y Debugging](#6-logs-y-debugging)
7. [Seguridad](#7-seguridad)
8. [Optimización y Performance](#8-optimización-y-performance)
9. [Migración y Actualizaciones](#9-migración-y-actualizaciones)
10. [Personalización](#10-personalización)

---

## 1. Arquitectura del Módulo

### 1.1. Estructura de Archivos

```
cucu_fact_rent/
├── __init__.py                    # Punto de entrada del módulo
├── __manifest__.py                # Metadatos y dependencias
├── README.md                      # Documentación general
├── MANUAL_USUARIO.md              # Manual para usuarios finales
├── GUIA_TECNICA.md                # Esta guía
├── models/
│   ├── __init__.py
│   ├── res_company.py             # Configuración de credenciales
│   ├── account_move.py            # Lógica de facturación
│   └── cucu_rent_api.py           # Servicio API
├── views/
│   ├── res_company_views.xml      # Vista de configuración
│   └── account_move_views.xml     # Vista de facturas
├── security/
│   └── ir.model.access.csv        # Permisos de acceso
└── static/
    └── description/
        └── icon.png                  # Icono del módulo
```

### 1.2. Modelos Principales

#### `res.company` (Extensión)
Almacena credenciales y configuración por compañía:
- Credenciales API (username, password)
- Token JWT y expiración
- Códigos CAFC
- URLs de endpoints

#### `account.move` (Extensión)
Añade campos específicos del sector alquileres:
- `is_rent_invoice`: Booleano identificador
- `rent_billed_period`: Período facturado
- `rent_property_address`: Dirección del inmueble
- `cucu_rent_cuf`: Código único generado
- `cucu_rent_state`: Estado de la factura
- `cucu_rent_response`: Respuesta JSON de CUCU

#### `cucu.rent.api` (AbstractModel)
Servicio de comunicación con CUCU API:
- Autenticación JWT
- Emisión de facturas
- Anulación
- Manejo de errores

### 1.3. Flujo de Datos

```
[Usuario] 
   ↓
[Odoo UI] → account.move.action_send_rent_invoice_cucu()
   ↓
[account_move.py] → _prepare_cucu_rent_invoice_data()
   ↓
[cucu_rent_api.py] → _get_auth_token()
   ↓
[CUCU API] ← POST /auth/login
   ↓
[Token JWT]
   ↓
[cucu_rent_api.py] → send_rent_invoice()
   ↓
[CUCU API] ← POST /api/v1/invoice/electronic/rent
   ↓
[Respuesta JSON + CUF]
   ↓
[account_move] ← Guardar CUF y respuesta
   ↓
[Usuario] ← Notificación éxito/error
```

---

## 2. Instalación y Dependencias

### 2.1. Dependencias de Odoo

```python
'depends': [
    'account',           # Módulo de contabilidad
    'l10n_bo',          # Localización Bolivia
    'cucu_fact_core',   # Módulo base CUCU
]
```

### 2.2. Dependencias de Python

```python
'external_dependencies': {
    'python': ['requests'],
}
```

**Instalación:**
```bash
pip3 install requests
```

### 2.3. Instalación en Odoo.sh

```bash
# 1. Clonar rama
git checkout feature/cucu-rent-invoicing
git pull origin feature/cucu-rent-invoicing

# 2. Actualizar Odoo.sh
# El sistema detectará automáticamente el nuevo módulo

# 3. Instalar desde UI
# Apps > Actualizar lista > Buscar "CUCU rent" > Instalar
```

### 2.4. Instalación en servidor local

```bash
# 1. Copiar módulo a addons
cd /opt/odoo/addons
cp -r /path/to/cucu_fact_rent .

# 2. Cambiar permisos
chown -R odoo:odoo cucu_fact_rent

# 3. Reiniciar Odoo
sudo systemctl restart odoo

# 4. Actualizar lista de aplicaciones desde UI
```

---

## 3. Configuración Avanzada

### 3.1. Variables de Entorno (Opcional)

Para seguridad adicional, puede almacenar credenciales en variables de entorno:

```bash
# En /etc/odoo/odoo.conf o .env
export CUCU_RENT_USERNAME="demo.largotek.alquiler"
export CUCU_RENT_PASSWORD="bd3f2919c865452aaf48f3c596507e2c"
```

**Modificar `res_company.py`:**
```python
import os

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    @api.model
    def _get_cucu_rent_credentials(self):
        return {
            'username': os.getenv('CUCU_RENT_USERNAME') or self.cucu_rent_username,
            'password': os.getenv('CUCU_RENT_PASSWORD') or self.cucu_rent_password,
        }
```

### 3.2. Configuración Multi-Compañía

Cada compañía puede tener sus propias credenciales CUCU:

```python
# Compañía A
cucu_rent_username = "empresa-a.alquiler"
cucu_rent_cafc_online = "CAFC123456789"

# Compañía B
cucu_rent_username = "empresa-b.alquiler"
cucu_rent_cafc_online = "CAFC987654321"
```

### 3.3. Timeout de Requests

Puede ajustar el timeout de las peticiones HTTP:

**En `cucu_rent_api.py`:**
```python
# Por defecto: 30s para auth, 60s para emisión
TIMEOUT_AUTH = 30
TIMEOUT_INVOICE = 60

response = requests.post(url, json=payload, timeout=TIMEOUT_INVOICE)
```

### 3.4. Proxy Configuration

Si usa proxy corporativo:

```python
proxies = {
    'http': 'http://proxy.empresa.com:8080',
    'https': 'https://proxy.empresa.com:8080',
}

response = requests.post(url, json=payload, proxies=proxies, timeout=60)
```

---

## 4. API CUCU - Especificaciones

### 4.1. Autenticación
**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "username": "demo.largotek.alquiler",
  "password": "bd3f2919c865452aaf48f3c596507e2c"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzUxMiJ9..."
  }
}
```

**Headers subsecuentes:**
```
Content-Type: application/json
cucukey: Token eyJhbGciOiJIUzUxMiJ9...
```

### 4.2. Emisión de Factura

**Endpoint:** `POST /api/v1/invoice/electronic/rent`

**Request:**
```json
{
  "posId": 1,
  "clientReasonSocial": "Juan Pérez",
  "clientDocumentType": "1",
  "clientNroDocument": "5678912",
  "clientCode": "CLI-001",
  "paramPaymentMethod": "1",
  "dateEmission": "2026-03-06T14:30:00",
  "userPos": "A4INC12ABCH",
  "paramDocumentSector": "1",
  "paramCurrency": "1",
  "clientComplement": "1A",
  "clientCity": "La Paz",
  "clientEmail": "cliente@email.com",
  "typeInvoice": 1,
  "typeOperation": 2,
  "billedPeriod": "Marzo 2026",
  "detailInvoice": [
    {
      "activityEconomic": "465000",
      "unitMeasure": 62,
      "codeProductSin": 99100,
      "codeProduct": "ALQ-001",
      "description": "Alquiler departamento",
      "qty": 1,
      "priceUnit": 3500.00
    }
  ]
}
```

**Response éxito:**
```json
{
  "success": true,
  "data": {
    "cuf": "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6",
    "invoiceNumber": 1234,
    "authorizationDate": "2026-03-06T14:30:15"
  }
}
```

**Response error:**
```json
{
  "success": false,
  "message": "Error en validación",
  "errors": {
    "billedPeriod": "Campo obligatorio"
  }
}
```

### 4.3. Anulación

**Endpoint:** `POST /api/v1/invoice/electronic/rent/anulation`

**Request:**
```json
{
  "cuf": "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6",
  "reasonCode": "1"
}
```

### 4.4. Códigos de Respuesta HTTP

| Código | Significado | Acción |
|--------|-------------|--------|
| 200 | OK | Procesar respuesta |
| 401 | No autorizado | Renovar token |
| 400 | Solicitud inválida | Revisar payload |
| 500 | Error servidor | Reintentar más tarde |
| 503 | Servicio no disponible | Verificar conectividad |

---

## 5. Estructura de Base de Datos

### 5.1. Tabla: `res_company`

**Campos añadidos:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `cucu_rent_username` | char(255) | Usuario CUCU |
| `cucu_rent_password` | char(255) | Contraseña CUCU |
| `cucu_rent_token` | text | Token JWT |
| `cucu_rent_token_expiry` | datetime | Expiración token |
| `cucu_rent_cafc_online` | char(100) | Código CAFC |
| `cucu_rent_endpoint` | char(255) | URL endpoint emisión |
| `cucu_rent_anulation_endpoint` | char(255) | URL endpoint anulación |
| `cucu_rent_revert_endpoint` | char(255) | URL endpoint reversión |
| `cucu_rent_auth_endpoint` | char(255) | URL endpoint auth |

### 5.2. Tabla: `account_move`

**Campos añadidos:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `is_rent_invoice` | boolean | Identificador sector |
| `rent_billed_period` | char(100) | Período facturado |
| `rent_property_address` | text | Dirección inmueble |
| `rent_type_operation` | char(10) | Tipo operación |
| `cucu_rent_cuf` | char(100) | CUF generado |
| `cucu_rent_response` | text | JSON respuesta |
| `cucu_rent_state` | char(20) | Estado CUCU |

### 5.3. Índices Recomendados

```sql
-- Índice para búsquedas de facturas de alquileres
CREATE INDEX idx_account_move_rent ON account_move(is_rent_invoice) 
WHERE is_rent_invoice = true;

-- Índice para búsqueda por CUF
CREATE INDEX idx_account_move_rent_cuf ON account_move(cucu_rent_cuf)
WHERE cucu_rent_cuf IS NOT NULL;

-- Índice para búsqueda por estado
CREATE INDEX idx_account_move_rent_state ON account_move(cucu_rent_state)
WHERE is_rent_invoice = true;
```

---

## 6. Logs y Debugging

### 6.1. Configuración de Logs

**Archivo:** `/etc/odoo/odoo.conf`

```ini
[options]
log_level = info
log_handler = :INFO,cucu_fact_rent:DEBUG
```

### 6.2. Logs del Módulo

**Ubicación:** `/var/log/odoo/odoo.log`

**Niveles de log:**

```python
_logger.debug('Mensaje de debug')    # Solo en desarrollo
_logger.info('Mensaje informativo')  # Operaciones normales
_logger.warning('Advertencia')       # Situaciones atípicas
_logger.error('Error')               # Errores recuperables
_logger.critical('Error crítico')   # Errores graves
```

### 6.3. Ejemplos de Logs

**Autenticación exitosa:**
```
2026-03-06 14:30:00,123 INFO cucu_fact_rent cucu_rent_api: === Solicitando token JWT para sector alquileres ===
2026-03-06 14:30:00,456 INFO cucu_fact_rent cucu_rent_api: ✅ Token JWT generado exitosamente (expira: 2026-05-05 14:30:00)
```

**Envío de factura:**
```
2026-03-06 14:35:00,789 INFO cucu_fact_rent cucu_rent_api: === Enviando factura INV/2026/0001 a CUCU (Alquileres) ===
2026-03-06 14:35:00,890 INFO cucu_fact_rent cucu_rent_api: Response Status: 200
2026-03-06 14:35:00,891 INFO cucu_fact_rent cucu_rent_api: ✅ Factura enviada exitosamente
2026-03-06 14:35:00,892 INFO cucu_fact_rent account_move: Factura INV/2026/0001 enviada exitosamente. CUF: A1B2C3...
```

**Error de validación:**
```
2026-03-06 14:40:00,123 ERROR cucu_fact_rent cucu_rent_api: ❌ Error CUCU: Campo billedPeriod es obligatorio
2026-03-06 14:40:00,124 ERROR cucu_fact_rent account_move: Error al enviar factura INV/2026/0002: Campo billedPeriod es obligatorio
```

### 6.4. Debugging con pdb

```python
# En cucu_rent_api.py
import pdb

def send_rent_invoice(self, invoice):
    pdb.set_trace()  # Breakpoint
    payload = invoice._prepare_cucu_rent_invoice_data()
    # ...
```

### 6.5. Monitoring con curl

**Probar autenticación:**
```bash
curl -X POST https://sandbox.cucu.ai/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo.largotek.alquiler",
    "password": "bd3f2919c865452aaf48f3c596507e2c"
  }'
```

**Probar emisión:**
```bash
curl -X POST https://sandbox.cucu.ai/api/v1/invoice/electronic/rent \
  -H "Content-Type: application/json" \
  -H "cucukey: Token YOUR_TOKEN_HERE" \
  -d @payload.json
```

---

## 7. Seguridad

### 7.1. Almacenamiento de Credenciales

⚠️ **Importante:** Las contraseñas se almacenan en texto plano en la base de datos.

**Recomendaciones:**
1. Usar variables de entorno (ver sección 3.1)
2. Encriptar base de datos
3. Limitar acceso a nivel de sistema operativo
4. Rotación periódica de credenciales

### 7.2. Permisos de Usuario

**Archivo:** `security/ir.model.access.csv`

```csv
access_cucu_rent_api_user,cucu.rent.api user,model_cucu_rent_api,base.group_user,1,0,0,0
access_cucu_rent_api_manager,cucu.rent.api manager,model_cucu_rent_api,account.group_account_manager,1,1,1,1
```

**Grupos:**
- `base.group_user`: Usuario normal (solo lectura)
- `account.group_account_manager`: Gerente contabilidad (lectura/escritura)

### 7.3. SSL/TLS

Todas las comunicaciones con CUCU API usan HTTPS:
- Certificado válido requerido
- TLS 1.2 o superior
- No deshabilitar verificación SSL en producción

```python
# NUNCA hacer esto en producción:
requests.post(url, json=payload, verify=False)  # ❌ Inseguro

# Correcto:
requests.post(url, json=payload)  # ✅ Verifica SSL
```

### 7.4. Rate Limiting

CUCU API puede tener límites de tasa:
- Máximo X peticiones por minuto
- Implementar retry con backoff exponencial

```python
import time
from requests.exceptions import HTTPError

max_retries = 3
for attempt in range(max_retries):
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        break
    except HTTPError as e:
        if e.response.status_code == 429:  # Too Many Requests
            wait_time = 2 ** attempt  # Backoff: 1s, 2s, 4s
            time.sleep(wait_time)
        else:
            raise
```

---

## 8. Optimización y Performance

### 8.1. Caché de Tokens

Los tokens se cachean automáticamente en `res.company`:
- Duración: 60 días
- Renovación automática al expirar
- Un token por compañía

### 8.2. Procesamiento Asíncrono (Futuro)

Para alto volumen de facturas:

```python
from odoo.addons.queue_job.job import job

@job
def send_rent_invoice_async(self, invoice_id):
    invoice = self.env['account.move'].browse(invoice_id)
    api_service = self.env['cucu.rent.api']
    return api_service.send_rent_invoice(invoice)
```

### 8.3. Batch Processing

Para emitir múltiples facturas:

```python
def action_send_multiple_rent_invoices(self):
    """Envía múltiples facturas en lote"""
    for invoice in self:
        try:
            invoice.action_send_rent_invoice_cucu()
            self.env.cr.commit()  # Commit individual
        except Exception as e:
            _logger.error(f'Error en {invoice.name}: {str(e)}')
            continue
```

### 8.4. Monitoreo de Performance

```python
import time

start_time = time.time()
result = api_service.send_rent_invoice(invoice)
end_time = time.time()

_logger.info(f'Factura enviada en {end_time - start_time:.2f} segundos')
```

---

## 9. Migración y Actualizaciones

### 9.1. Script de Migración
**Archivo:** `migrations/1.0.0/post-migration.py`

```python
def migrate(cr, version):
    """Migración post-instalación"""
    if not version:
        return
    
    # Inicializar configuración por defecto
    cr.execute("""
        UPDATE res_company
        SET cucu_rent_endpoint = 'https://sandbox.cucu.ai/api/v1/invoice/electronic/rent'
        WHERE cucu_rent_endpoint IS NULL
    """)
```

### 9.2. Actualización del Módulo

```bash
# 1. Pull de cambios
git pull origin feature/cucu-rent-invoicing

# 2. Actualizar módulo en Odoo
./odoo-bin -u cucu_fact_rent -d database_name

# O desde UI:
# Apps > CUCU rent > Actualizar
```

### 9.3. Backup Antes de Actualizar

```bash
# Backup base de datos
pg_dump -U odoo -F c database_name > backup_$(date +%Y%m%d).dump

# Backup filestore
tar -czf filestore_$(date +%Y%m%d).tar.gz /opt/odoo/.local/share/Odoo/filestore/
```

---

## 10. Personalización

### 10.1. Heredar el Módulo

**Crear módulo custom:**

```python
# custom_rent_invoice/__manifest__.py
{
    'name': 'Custom Rent Invoice',
    'depends': ['cucu_fact_rent'],
}

# custom_rent_invoice/models/account_move.py
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    # Añadir campos custom
    custom_field = fields.Char('Campo Custom')
    
    def _prepare_cucu_rent_invoice_data(self):
        """Extender payload"""
        payload = super()._prepare_cucu_rent_invoice_data()
        payload['customField'] = self.custom_field
        return payload
```

### 10.2. Webhooks (Futuro)

Notificar sistemas externos:

```python
def action_send_rent_invoice_cucu(self):
    result = super().action_send_rent_invoice_cucu()
    
    # Webhook post-envío
    webhook_url = self.company_id.custom_webhook_url
    if webhook_url:
        requests.post(webhook_url, json={
            'invoice_id': self.id,
            'cuf': self.cucu_rent_cuf,
            'event': 'invoice_sent'
        })
    
    return result
```

### 10.3. Reportes Custom

```python
from odoo import models, api

class RentInvoiceReport(models.AbstractModel):
    _name = 'report.cucu_fact_rent.rent_invoice_report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'docs': docs,
            'show_cuf': True,
        }
```

---

## 🔗 Referencias

- **Documentación CUCU API:** https://docs.cucu.bo
- **Normativa SIN Bolivia:** https://www.impuestos.gob.bo
- **Odoo Development:** https://www.odoo.com/documentation/
- **Python Requests:** https://docs.python-requests.org/

---

## 📞 Soporte Técnico

**Issues en GitHub:**  
https://github.com/wecodebolivia/gutvas/issues

**Email:**  
soporte@largotek.com

---

**Fin de la Guía Técnica**

*Última actualización: Marzo 2026*  
*Versión del módulo: 1.0.0*
