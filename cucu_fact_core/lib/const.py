CATALOGS_MAP = {
    "cucu.catalogs.product.service": "ProductService",
    "cucu.catalogs.activities": "Activities",
    "cucu.catalogs.event.significant": "ParamEventSignificant",
    "cucu.catalogs.payment.method": "ParamMethodPayment",
    "cucu.catalogs.currency": "ParamTypeCurrency",
    "cucu.catalogs.point.of.sale": "ParamPointOfSale",
    "cucu.catalogs.unit.measure": "ParamUnitMeasure",
    "cucu.catalogs.cancel": "ParamCauseAnnulation",
}

FONT_TYPE_SELECTION = [
    ("1", "OVERPASS"),
    ("2", "COURIER_STD"),
    ("3", "COURIER_PRIME"),
    ("4", "NOTO_SANS_MONO"),
]

CODE_EVENT_SELECTION = [
    ("1", "CORTE DEL SERVICIO DE INTERNET"),
    ("2", "INACCESIBILIDAD AL SERVICIO WEB DE LA ADMINISTRACIÓN TRIBUTARIA"),
    (
        "3",
        "INGRESO A ZONAS SIN INTERNET POR DESPLIEGUE DE PUNTO DE VENTA EN VEHICULOS AUTOMOTORES",
    ),
    ("4", "VENTA EN LUGARES SIN INTERNET"),
    ("5", "VIRUS INFORMÁTICO O FALLA DE SOFTWARE"),
    (
        "6",
        "CAMBIO DE INFRAESTRUCTURA DEL SISTEMA INFORMÁTICO DE FACTURACIÓN O FALLA DE HARDWARE",
    ),
    ("7", "CORTE DE SUMINISTRO DE ENERGIA ELECTRICA"),
]

TYPE_REPORT_MONTH = [
    ("1", "MONTH"),
    ("2", "DAY"),
]

CODE_TYPE_MOTIVE_SELECTION = [
    ("1", "FACTURA MAL EMITIDA"),
    ("2", "NOTA DE CREDITO-DEBITO MAL EMITIDA"),
    ("3", "DATOS DE EMISION INCORRECTOS"),
    ("4", "FACTURA O NOTA DE CREDITO-DEBITO DEVUELTA"),
]

CODE_DOC_SECTOR = [
    ("1", "FACTURA COMPRA-VENTA"),
    ("2", "FACTURA DE ALQUILER DE BIENES INMUEBLES"),
    ("3", "FACTURA COMERCIAL DE EXPORTACIÓN"),
    ("4", "FACTURA COMERCIAL DE EXPORTACIÓN EN LIBRE CONSIGNACIÓN"),
    ("5", "FACTURA DE ZONA FRANCA"),
    ("6", "FACTURA DE SERVICIO TURÍSTICO Y HOSPEDAJE"),
    ("7", "FACTURA DE COMERCIALIZACIÓN DE ALIMENTOS - SEGURIDAD"),
    (
        "8",
        "FACTURA DE TASA CERO POR VENTA DE LIBROS Y TRANSPORTE INTERNACIONAL DE CARGA",
    ),
    ("9", "FACTURA DE COMPRA Y VENTA DE MONEDA EXTRANJERA"),
    ("10", "FACTURA DUTTY FREE"),
    ("11", "FACTURA SECTORES EDUCATIVOS"),
    ("12", "FACTURA DE COMERCIALIZACIÓN DE HIDROCARBUROS"),
    ("13", "FACTURA DE SERVICIOS BÁSICOS"),
    ("14", "FACTURA PRODUCTOS ALCANZADOS POR EL ICE"),
    ("15", "FACTURA DE ENTIDADES FINANCIERAS"),
    ("16", "FACTURA DE HOTELES"),
    ("17", "FACTURA DE HOSPITALES/CLÍNICAS"),
    ("18", "FACTURA DE JUEGOS DE AZAR"),
    ("19", "FACTURA HIDROCARBUROS ALCANZADA IEHD"),
    ("20", "FACTURA COMERCIAL DE EXPORTACIÓN DE MINERALES"),
    ("21", "FACTURA VENTA INTERNA MINERALES"),
    ("22", "FACTURA TELECOMUNICACIONES"),
    ("23", "FACTURA PREVALORADA"),
    ("24", "NOTA DE CRÉDITO-DÉBITO"),
    ("28", "FACTURA COMERCIAL DE EXPORTACIÓN DE SERVICIOS"),
    ("29", "NOTA DE CONCILIACION"),
    ("30", "BOLETO AÉREO"),
    ("34", "FACTURA DE SEGUROS"),
    ("35", "FACTURA COMPRA VENTA BONIFICACIONES"),
    ("37", "FACTURA DE COMERCIALIZACIÓN DE GNV"),
    ("38", "FACTURA HIDROCARBUROS NO ALCANZADA IEHD"),
    ("41", "FACTURA COMPRA VENTA TASAS"),
    ("43", "FACTURA COMERCIAL DE EXPORTACIÓN HIDROCARBUROS"),
    ("44", "FACTURA IMPORTACION COMERCIALIZACION LUBRICANTES"),
    ("45", "FACTURA COMERCIAL DE EXPORTACION PRECIO VENTA"),
    ("47", "NOTA CRÉDITO DÉBITO DESCUENTO"),
    ("48", "NOTA CRÉDITO DÉBITO ICE"),
    ("51", "FACTURA ENGARRAFADORAS"),
]


def display_notification(type, title, message):
    return {
        "type": "ir.actions.client",
        "tag": "display_notification",
        "params": {
            "title": title,
            "message": message,
            "sticky": False,
            "type": type,
        },
    }


def tag_reload():
    return {
        "type": "ir.actions.client",
        "tag": "reload",
    }
