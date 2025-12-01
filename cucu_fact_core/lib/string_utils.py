# from jwt import JWT
from datetime import datetime, timezone
import xmltodict
import json
import re
from .date_utils import convert_date
import jwt
import logging

_logger = logging.getLogger(__name__)


def valid_token(token: str) -> bool:
    """
    Returns True if the token is expired or invalid.
    Also logs how much time is left until expiration.
    """
    if not token:
        _logger.warning("Token no existe.")
        return True

    try:
        # jwt = JWT()
        decode = jwt.decode(token, options={"verify_signature": False})
        exp = decode.get("exp")
        if not exp:
            _logger.warning("Token sin 'exp', considerado inválido.")
            return True

        # Current UTC time
        now_ts = datetime.now(tz=timezone.utc).timestamp()
        remaining_seconds = exp - now_ts

        if remaining_seconds < 0:
            _logger.info(f"Token expirado hace {-remaining_seconds:.0f} segundos.")
            return True

        _logger.info(
            f"Token válido. Tiempo restante: {remaining_seconds:.0f} segundos."
        )
        return False

    except Exception as e:
        _logger.warning(f"Error al validar token: {e}")
        return True


def string_to_json(string_json: str):
    parse = json.loads(string_json)
    return json.dumps(parse, indent=2, sort_keys=True)


def map_header(header):
    doc_sector = int(header["codigoDocumentoSector"])
    if doc_sector == 1:
        return {
            "fechaEmision": convert_date(header["fechaEmision"]),
            "montoTotal": float(header["montoTotal"]),
            "montoTotalSujetoIva": float(header["montoTotalSujetoIva"]),
            "montoTotalMoneda": float(header["montoTotalMoneda"]),
            "montoGiftCard": float(header["montoGiftCard"]),
            "descuentoAdicional": float(header["descuentoAdicional"]),
            "leyenda": header["leyenda"],
            "municipio": header["municipio"],
        }
    return {
        "fechaEmision": convert_date(header["fechaEmisionFactura"]),
        "montoTotal": float(header["montoTotalDevuelto"]),
        "montoTotalSujetoIva": float(header["montoTotalDevuelto"]),
        "montoTotalMoneda": 0,
        "montoGiftCard": 0,
        "descuentoAdicional": float(header["montoDescuentoCreditoDebito"]),
        "leyenda": header["leyenda"],
        "municipio": header["municipio"],
    }


def convert_xml_to_object(invoice, is_electronic):
    # remove null fields
    xml_invoice = invoice["invoiceXml"]
    regex_delete = (
        'xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    )
    string_regex = re.sub(regex_delete, "", xml_invoice)
    obj = xmltodict.parse(string_regex, encoding="utf-8", force_list="detalle")
    string_json = json.dumps(obj)
    json_data = json.loads(string_json)
    key_invoice = ""
    doc_sector = int(invoice["docSector"])
    if doc_sector == 1:
        key_invoice = (
            "facturaElectronicaCompraVenta"
            if is_electronic
            else "facturaComputarizadaCompraVenta"
        )
    if doc_sector == 24:
        key_invoice = (
            "notaFiscalElectronicaCreditoDebito"
            if is_electronic
            else "notaFiscalComputarizadaCreditoDebito"
        )
    header = json_data[key_invoice]["cabecera"]
    return {
        "doc_sector": int(header["codigoDocumentoSector"]),
        "nombreRazonSocial": header["nombreRazonSocial"],
        **map_header(header),
    }
