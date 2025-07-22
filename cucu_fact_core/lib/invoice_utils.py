import xmltodict
import json
import re
from .date_utils import convert_date


def key_invoice(doc_sector, is_electronic):
    type_invoice = ""
    if doc_sector == 1:
        type_invoice = (
            "facturaElectronicaCompraVenta"
            if is_electronic
            else "facturaComputarizadaCompraVenta"
        )
    if doc_sector == 24:
        type_invoice = (
            "notaFiscalElectronicaCreditoDebito"
            if is_electronic
            else "notaFiscalComputarizadaCreditoDebito"
        )
    return type_invoice


def nro_document(header):
    document_type = int(header["codigoTipoDocumentoIdentidad"])
    if document_type == 1:
        return (
            f'{header["numeroDocumento"]}-{header["complemento"]}'
            if header["complemento"]
            else header["numeroDocumento"]
        )
    return header["numeroDocumento"]


def get_json(xml_invoice, is_electronic, doc_sector):
    regex_delete = (
        'xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    )
    string_regex = re.sub(regex_delete, "", xml_invoice)
    string_regex = string_regex.replace(
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"', ""
    )
    obj = xmltodict.parse(string_regex, encoding="utf-8", force_list="detalle")
    string_json = json.dumps(obj)
    json_data = json.loads(string_json)
    return json_data[key_invoice(doc_sector, is_electronic)]


def get_details(detail_invoice, doc_sector):
    detail = []
    index = 1
    for line in detail_invoice:
        detail.append(
            {
                "name_product": line["codigoProducto"] + " " + line["descripcion"],
                "code_product": line["codigoProducto"],
                "name": line["descripcion"],
                "qty": "%.2f" % float(line["cantidad"]),
                "line_price": "%.2f" % float(line["precioUnitario"]),
                "sub_total": "%.2f" % float(line["subTotal"]),
                "discount": "%.2f" % float(line["montoDescuento"]),
                "is_return": (
                    int(line["codigoDetalleTransaccion"]) == 2
                    if doc_sector == 24
                    else False
                ),
                "unit_measure": str(line["unidadMedida"]),
                "id": index,
            }
        )
        index = index + 1
    return detail


def convert_xml_to_object_sale(xml, is_electronic):
    json_data = get_json(xml, is_electronic, 1)
    head = json_data["cabecera"]
    header = {
        "nit_emissor": str(head["nitEmisor"]),
        "branch_id_api": head["codigoSucursal"],
        "pos_id_api": head["codigoPuntoVenta"],
        "cuf": head["cuf"],
        "invoice_number": head["numeroFactura"],
        "amount_total": "%.2f" % float(head["montoTotal"]),
        "amount_total_currency": "%.2f" % float(head["montoTotalMoneda"]),
        "amount_subject_iva": "%.2f" % float(head["montoTotalSujetoIva"]),
        "amount_gift_card": "%.2f" % float(head["montoGiftCard"]),
        "additional_discount": "%.2f" % float(head["descuentoAdicional"]),
        "legend": head["leyenda"],
        "reason_social_emissor": head["razonSocialEmisor"],
        "municipality": head["municipio"],
        "address": head["direccion"],
        "nit": nro_document(head),
        "reason_social": head["nombreRazonSocial"],
        "doc_sector": int(head["codigoDocumentoSector"]),
        "code_client": head["codigoCliente"],
        "user_pos": head["usuario"],
        "pos_phone": head["telefono"],
        "pos_name": f'No. Punto de Venta {head["codigoPuntoVenta"]}',
        "date_emission": convert_date(head["fechaEmision"]),
    }
    return {"header": header, "detail": get_details(json_data["detalle"], 1)}


def convert_xml_to_object_note(xml, is_electronic):
    json_data = get_json(xml, is_electronic, 24)

    head = json_data["cabecera"]
    header = {
        "nit_emissor": str(head["nitEmisor"]),
        "reason_social_emissor": head["razonSocialEmisor"],
        "municipality": head["municipio"],
        "pos_phone": head["telefono"],
        "invoice_number": head["numeroNotaCreditoDebito"],
        "nro_invoice_old": head["numeroFactura"],
        "cuf": head["cuf"],
        "cuf_old": head["numeroAutorizacionCuf"],
        "amount_original": "%.2f" % float(head["montoTotalOriginal"]),
        "amount_return": "%.2f" % float(head["montoTotalDevuelto"]),
        "amount_debit_credit": "%.2f" % float(head["montoEfectivoCreditoDebito"]),
        "legend": head["leyenda"],
        "address": head["direccion"],
        "nit": nro_document(head),
        "reason_social": head["nombreRazonSocial"],
        "doc_sector": int(head["codigoDocumentoSector"]),
        "code_client": head["codigoCliente"],
        "user_pos": head["usuario"],
        "pos_name": f'No. Punto de Venta {head["codigoPuntoVenta"]}',
        "date_emission": convert_date(head["fechaEmisionFactura"]),
        "date_emission_note": convert_date(head["fechaEmision"]),
    }
    return {"header": header, "detail": get_details(json_data["detalle"], 24)}
