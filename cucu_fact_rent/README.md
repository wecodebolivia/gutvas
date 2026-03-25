# CUCU - Facturación Electrónica Sector Alquileres

## Descripción

Módulo de Odoo para emisión de facturas electrónicas del **sector alquileres** según normativa del Servicio de Impuestos Nacionales (SIN) de Bolivia, integrado con la API de CUCU.

## Características

✅ **Credenciales independientes** por sector (username/password específicos)  
✅ **Gestión automática de tokens JWT** con renovación al expirar  
✅ **Campo obligatorio**: `billedPeriod` (período facturado)  
✅ **Endpoints específicos**:
   - `/api/v1/invoice/electronic/rent` (emisión)
   - `/api/v1/invoice/electronic/rent/anulation` (anulación)
   - `/api/v1/invoice/electronic/rent/revert` (reversión)

✅ **CAFC configurables** (sandbox/producción)  
✅ **Manejo de errores 401** con reintento automático  
✅ **Logging detallado** para debugging  
✅ **Botón de prueba** de conexión en configuración  

## Instalación

1. Copiar el módulo `cucu_fact_rent` a la carpeta de addons de Odoo
2. Actualizar lista de aplicaciones
3. Buscar "CUCU - Facturación Electrónica Sector Alquileres"
4. Instalar

## Configuración
### 1. Credenciales CUCU

Navegar a: **Configuración > Compañías > Facturación Alquileres**

**Ambiente Sandbox (Pruebas):**
```
Usuario: demo.largotek.alquiler
Contraseña: bd3f2919c865452aaf48f3c596507e2c
CAFC: 10228BFCF149E (rango 1-1000)
Base URL: https://sandbox.cucu.ai
```

**Ambiente Producción:**
- Cambiar endpoints a `https://api.cucu.ai`
- Usar credenciales y CAFC de producción del SIN

### 2. Probar Conexión

Hacer clic en el botón **"🔌 Probar Conexión"** para validar las credenciales y obtener el token JWT.

## Uso

### Emitir Factura de Alquileres

1. Crear nueva factura de cliente
2. Activar el toggle **"Factura Alquileres"**
3. Completar campos obligatorios:
   - **Período Facturado**: Ej. "Mayo 2026"
   - **Tipo de Operación**: Alquiler o Venta
   - **Dirección Inmueble** (opcional)
4. Agregar líneas de factura (servicios de alquiler)
5. **Confirmar** la factura
6. Hacer clic en **"📤 Enviar a CUCU (Alquileres)"**
7. Si la emisión es exitosa, se generará un **CUF** (Código Único de Factura)

### Ver Respuesta CUCU

En la pestaña **"🏠 Datos Alquileres"** de la factura:
- **Estado CUCU**: draft / sent / validated / rejected / cancelled
- **CUF**: Código único generado por SIN
- **Respuesta API**: JSON completo de la respuesta CUCU

## Estructura Técnica

```
cucu_fact_rent/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── res_company.py       # Credenciales y configuración
│   ├── account_move.py       # Campos y lógica de factura
│   └── cucu_rent_api.py      # Servicio API
├── views/
│   ├── res_company_views.xml
│   └── account_move_views.xml
├── security/
│   └── ir.model.access.csv
└── README.md
```

## Dependencias

- `account` (Contabilidad Odoo)
- `l10n_bo` (Localización Bolivia)
- `cucu_fact_core` (Módulo base CUCU)
- Python: `requests`

## Soporte

**Desarrollado por:** LargoTek / WeCodeBolivia  
**Versión:** 1.0.0  
**Licencia:** LGPL-3  

## Notas Importantes

⚠️ **Token JWT**: Se renueva automáticamente cada 60 días  
⚠️ **CAFC**: Debe ser solicitado al SIN para cada punto de venta  
⚠️ **Ambiente Sandbox**: Usar solo para pruebas, no emite facturas válidas fiscalmente  
⚠️ **Header cucukey**: Formato obligatorio `Token {jwt}` (no `Bearer`)  

## Changelog

### v1.0.0 (2026-03-06)
- ✅ Versión inicial
- ✅ Integración con endpoints CUCU para alquileres
- ✅ Autenticación JWT con renovación automática
- ✅ Campos específicos del sector
- ✅ Validaciones de payload
- ✅ Logging detallado