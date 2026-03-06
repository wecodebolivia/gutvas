# 📘 Manual de Usuario - Facturación Electrónica Sector Alquileres

**Módulo:** CUCU - Facturación Electrónica Sector Alquileres  
**Versión:** 1.0.0  
**Fecha:** Marzo 2026  
**Desarrollado por:** LargoTek / WeCodeBolivia

---

## 📑 Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Instalación del Módulo](#2-instalación-del-módulo)
3. [Configuración Inicial](#3-configuración-inicial)
4. [Emisión de Facturas](#4-emisión-de-facturas)
5. [Consulta y Seguimiento](#5-consulta-y-seguimiento)
6. [Anulación de Facturas](#6-anulación-de-facturas)
7. [Solución de Problemas](#7-solución-de-problemas)
8. [Preguntas Frecuentes](#8-preguntas-frecuentes)

---

## 1. Introducción

### ¿Qué es este módulo?

Este módulo permite emitir **facturas electrónicas para el sector alquileres** según la normativa del Servicio de Impuestos Nacionales (SIN) de Bolivia, integrándose con la API de CUCU.

### ¿Qué necesito para usar este módulo?

- ✅ Odoo instalado (versión 15+)
- ✅ Módulo `cucu_fact_core` instalado
- ✅ Credenciales CUCU para sector alquileres
- ✅ Código CAFC asignado por el SIN

### Diferencias con facturación estándar

Las facturas de alquileres tienen campos adicionales obligatorios según normativa SIN:
- **Período facturado** (billedPeriod): Ejemplo "Mayo 2026"
- **Tipo de operación**: Alquiler o Venta
- **Dirección del inmueble** (opcional)

---

## 2. Instalación del Módulo

### Paso 1: Actualizar lista de aplicaciones

1. Ir a **Aplicaciones** en el menú principal
2. Hacer clic en el botón **Actualizar lista de aplicaciones**
3. Confirmar la actualización

![Actualizar Apps](https://via.placeholder.com/800x200/0066CC/FFFFFF?text=Actualizar+Lista+de+Aplicaciones)

### Paso 2: Buscar el módulo

1. En el buscador escribir: **"alquileres"** o **"CUCU rent"**
2. Encontrar el módulo: **"CUCU - Facturación Electrónica Sector Alquileres"**

### Paso 3: Instalar

1. Hacer clic en el botón **Instalar**
2. Esperar a que termine la instalación (1-2 minutos)
3. El sistema recargará automáticamente

✅ **Instalación completada**

---

## 3. Configuración Inicial

### 3.1. Acceder a la configuración

**Ruta:** Configuración → Compañías → [Tu Compañía] → Pestaña **🏠 Facturación Alquileres**

![Configuración](https://via.placeholder.com/800x400/00AA66/FFFFFF?text=Configuracion+Facturacion+Alquileres)

### 3.2. Credenciales CUCU

#### Ambiente Sandbox (Pruebas)

Use estas credenciales para realizar pruebas:

```
Usuario: demo.largotek.alquiler
Contraseña: bd3f2919c865452aaf48f3c596507e2c
```

#### Ambiente Producción

**⚠️ Importante:** Para facturación real, solicite sus credenciales de producción a CUCU.

**Pasos para configurar:**

1. **Usuario CUCU Alquileres**: Ingresar el usuario proporcionado por CUCU
2. **Password CUCU Alquileres**: Ingresar la contraseña (se oculta automáticamente)
3. Hacer clic en **💾 Guardar**

### 3.3. Probar la conexión

1. Hacer clic en el botón **🔌 Probar Conexión**
2. Si todo está correcto, verá el mensaje:

```
✅ Conexión Exitosa
Token JWT generado correctamente.
Expira: [fecha]
```

3. Si hay error, revisar usuario y contraseña

![Probar Conexión](https://via.placeholder.com/600x200/00AA66/FFFFFF?text=Conexion+Exitosa)

### 3.4. Configurar CAFC

**CAFC** = Código de Autorización de Facturas por Contingencia

#### Para ambiente Sandbox:
```
CAFC: 10228BFCF149E
Rango: 1 - 1000
```

#### Para ambiente Producción:
- Solicitar al SIN su CAFC específico
- Indicar el rango de numeración asignado

**Campo:** CAFC Alquileres (Electrónica en línea)

### 3.5. Verificar Endpoints

Los endpoints ya vienen preconfigurados:

**Sandbox:**
```
Autenticación: https://sandbox.cucu.ai/auth/login
Emisión: https://sandbox.cucu.ai/api/v1/invoice/electronic/rent
Anulación: https://sandbox.cucu.ai/api/v1/invoice/electronic/rent/anulation
Reversión: https://sandbox.cucu.ai/api/v1/invoice/electronic/rent/revert
```

**Producción:**
Cambiar `sandbox.cucu.ai` por `api.cucu.ai`

---

## 4. Emisión de Facturas

### 4.1. Crear nueva factura

**Ruta:** Facturación → Clientes → Facturas → **Crear**

![Nueva Factura](https://via.placeholder.com/800x500/0066CC/FFFFFF?text=Nueva+Factura+Cliente)

### 4.2. Activar modo "Factura Alquileres"

1. En la parte superior del formulario, activar el toggle **"Factura Alquileres"**
2. Aparecerán campos adicionales específicos del sector

![Toggle Alquileres](https://via.placeholder.com/400x100/FF6600/FFFFFF?text=Activar+Factura+Alquileres)

### 4.3. Completar datos del cliente

- **Cliente**: Seleccionar o crear
- **Fecha de factura**: Fecha de emisión
- **Período Facturado**: ⭐ **OBLIGATORIO** - Ejemplo: "Mayo 2026"
- **Tipo de Operación**: Seleccionar "Alquiler" o "Venta"

### 4.4. Agregar líneas de factura

1. En la pestaña **Líneas de factura**
2. Hacer clic en **Agregar una línea**
3. Seleccionar el servicio de alquiler
4. Indicar cantidad y precio unitario

**Ejemplo:**
```
Producto: Alquiler Departamento Zona Sur
Cantidad: 1
Precio Unit.: 3,500.00 BOB
```

### 4.5. Pestaña "Datos Alquileres" (opcional)

En esta pestaña puede ingresar información adicional:

- **Dirección Inmueble**: Dirección completa del inmueble alquilado
  - Ejemplo: "Calle 21 #456, Calacoto, La Paz"

### 4.6. Confirmar la factura

1. Revisar todos los datos
2. Hacer clic en **Confirmar**
3. La factura cambiará a estado **Publicado**

### 4.7. Enviar a CUCU

1. Hacer clic en el botón **📤 Enviar a CUCU (Alquileres)**
2. El sistema enviará la factura a CUCU API
3. Si es exitoso, recibirá:

```
✅ Factura Enviada a CUCU
CUF generado: [código CUF]
```

4. El **CUF** (Código Único de Factura) quedará guardado en la factura

![CUF Generado](https://via.placeholder.com/600x200/00AA66/FFFFFF?text=CUF+Generado+Exitosamente)

---

## 5. Consulta y Seguimiento

### 5.1. Ver estado de facturas de alquileres

**Ruta:** Facturación → Clientes → Facturas

**Aplicar filtro:**
1. Hacer clic en **Filtros**
2. Seleccionar **🏠 Facturas Alquileres**
3. Se mostrarán solo las facturas del sector alquileres

### 5.2. Estados CUCU

Cada factura tiene un estado que indica su situación:

| Estado | Descripción |
|--------|-------------|
| **📝 Borrador** | Factura no enviada aún |
| **📤 Enviada** | Enviada a CUCU, esperando respuesta |
| **✅ Validada** | Aprobada por SIN, CUF generado |
| **❌ Rechazada** | Rechazada por SIN o CUCU |
| **🚫 Anulada** | Factura anulada |

### 5.3. Ver detalles de respuesta CUCU

1. Abrir la factura
2. Ir a la pestaña **🏠 Datos Alquileres**
3. En la sección **Respuesta CUCU API** verá el JSON completo

**Información incluida:**
- CUF
- Fecha/hora de autorización
- Número de factura
- Mensajes de validación

### 5.4. Copiar CUF

El CUF tiene un botón de copiado rápido:
1. Hacer clic en el ícono 📋 junto al CUF
2. El código se copia al portapapeles

---

## 6. Anulación de Facturas

### 6.1. ¿Cuándo anular una factura?

Debe anular una factura de alquileres cuando:
- Se emitió por error
- Hay datos incorrectos que no se pueden corregir
- El cliente solicita la anulación

### 6.2. Proceso de anulación

⚠️ **Nota:** Esta funcionalidad se implementará en una versión futura.

**Proceso manual actual:**
1. Contactar a soporte CUCU
2. Proporcionar el CUF de la factura
3. Indicar el motivo de anulación (código según catálogo SIN)

**Motivos de anulación comunes:**
- Código 1: Error en datos
- Código 2: Factura duplicada
- Código 3: Solicitud del cliente

---

## 7. Solución de Problemas

### Problema 1: Error de autenticación (401)

**Síntoma:**
```
❌ Error de conexión CUCU:
401: {"message":"Not unauthorized"}
```

**Solución:**
1. Verificar usuario y contraseña en Configuración
2. Hacer clic en **🔌 Probar Conexión**
3. Si persiste, contactar a CUCU para verificar credenciales

### Problema 2: Campo "Período Facturado" vacío

**Síntoma:**
```
❌ Error: El campo "Período Facturado" es obligatorio
```

**Solución:**
1. Abrir la factura
2. Completar el campo **Período Facturado** (Ej: "Mayo 2026")
3. Guardar y reintentar envío

### Problema 3: Token expirado

**Síntoma:** El sistema demora mucho en enviar facturas

**Solución:**
- El sistema renueva automáticamente el token
- Si persiste, ir a Configuración y hacer clic en **🔌 Probar Conexión**

### Problema 4: Error de conexión

**Síntoma:**
```
❌ Error de conexión con CUCU API
```

**Solución:**
1. Verificar conexión a Internet
2. Verificar que los endpoints estén correctos
3. Si usa producción, verificar que cambió `sandbox` por `api`

### Problema 5: Factura rechazada

**Síntoma:** Estado = **❌ Rechazada**

**Solución:**
1. Ir a pestaña **🏠 Datos Alquileres**
2. Revisar **Respuesta CUCU API** para ver el motivo
3. Corregir el error indicado
4. Crear nueva factura con los datos correctos

---

## 8. Preguntas Frecuentes

### ¿Puedo usar el mismo usuario CUCU para todos los sectores?

**No.** Cada sector (alquileres, tasa cero, etc.) requiere credenciales específicas.

### ¿Cuánto dura el token JWT?

El token dura **60 días** y se renueva automáticamente cuando expira.

### ¿Puedo editar una factura después de enviarla a CUCU?

**No.** Una vez que tiene CUF asignado, la factura no se puede modificar. Debe anularla y crear una nueva.

### ¿Dónde veo el CUF de mis facturas?

En la lista de facturas, agregar la columna **CUF Alquileres** o abrir la factura y ver la pestaña **🏠 Datos Alquileres**.

### ¿Qué hago si el cliente necesita una factura urgente y CUCU no responde?

1. Verificar conexión a Internet
2. Revisar configuración de endpoints
3. Contactar a soporte CUCU: [correo/teléfono]

### ¿Las facturas de prueba (sandbox) son válidas fiscalmente?

**No.** Las facturas emitidas en ambiente sandbox son **solo para pruebas** y no tienen validez fiscal.

### ¿Cómo cambio de sandbox a producción?

1. Ir a Configuración → Compañías → 🏠 Facturación Alquileres
2. Cambiar todos los endpoints de `sandbox.cucu.ai` a `api.cucu.ai`
3. Ingresar credenciales de producción
4. Ingresar CAFC de producción
5. Hacer clic en **🔌 Probar Conexión**

### ¿Puedo facturar alquileres de diferentes inmuebles en una misma factura?

**Sí**, puede agregar múltiples líneas de factura. Sin embargo, el **Período Facturado** será el mismo para toda la factura.

### ¿Qué datos del cliente son obligatorios?

- Nombre o Razón Social
- Tipo de documento (CI/NIT)
- Número de documento
- Ciudad (opcional pero recomendado)
- Email (opcional pero recomendado)

### ¿Puedo reimprimir una factura después de enviarla a CUCU?

**Sí**, puede imprimir la factura cuantas veces necesite. El CUF quedará impreso en el documento.

---

## 📞 Soporte Técnico

### Desarrollador del Módulo
- **Empresa:** LargoTek / WeCodeBolivia
- **Email:** [soporte@largotek.com]
- **Teléfono:** [número]

### Soporte CUCU API
- **Website:** https://cucu.ai
- **Documentación:** https://docs.cucu.bo

### Servicio de Impuestos Nacionales (SIN)
- **Website:** https://www.impuestos.gob.bo
- **Mesa de ayuda:** [teléfono]

---

## 📋 Lista de Verificación Rápida

Antes de emitir su primera factura de alquileres, verifique:

- [ ] Módulo instalado correctamente
- [ ] Credenciales CUCU configuradas
- [ ] Botón "Probar Conexión" ejecutado exitosamente
- [ ] CAFC ingresado
- [ ] Endpoints configurados (sandbox o producción)
- [ ] Cliente creado con datos completos
- [ ] Productos/servicios de alquiler configurados

---

## 📄 Anexos

### Anexo A: Códigos de Actividad Económica

| Código | Descripción |
|--------|-------------|
| 465000 | Alquiler de inmuebles |

### Anexo B: Tipos de Documento

| Código | Descripción |
|--------|-------------|
| 1 | Cédula de Identidad (CI) |
| 5 | Número de Identificación Tributaria (NIT) |

### Anexo C: Métodos de Pago

| Código | Descripción |
|--------|-------------|
| 1 | Efectivo |
| 2 | Tarjeta |
| 3 | Cheque |
| 4 | Transferencia |

---

**Fin del Manual de Usuario**

*Última actualización: Marzo 2026*  
*Versión del módulo: 1.0.0*
