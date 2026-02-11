import json
import re
import logging

from ..lib.qr_image import generate_qr
from odoo import models
from ..lib.string_utils import number_to_date

_logger = logging.getLogger(__name__)


def _get_number_document(header):
    document_type = int(header["codigoTipoDocumentoIdentidad"])
    if document_type == 1:
        return (
            f'{header["numeroDocumento"]}-{header["complemento"]}'
            if header["complemento"]
            else header["numeroDocumento"]
        )
    return header["numeroDocumento"]


class AccountMove(models.Model):
    _inherit = "account.move"

    def _search_unit_measure(self, code_type):
        return self.env["cucu.catalogs.unit.measure"].search(
            [("code_type", "=", code_type)], limit=1
        )

    def _render_invoice_details(self, details):
        detail = []
        for line in details:
            unit_measure = self._search_unit_measure(line["unidadMedida"])
            for key in ["cantidad", "precioUnitario", "montoDescuento", "subTotal"]:
                if isinstance(line[key], (int, float)):
                    line[key] = f"{float(line[key]):.2f}"

            # ------------------------------------------------------------
            # Limpieza de descripción:
            # En muchos casos SIN/Factura trae la descripción como "[REF] Nombre"
            # o "REF - Nombre". Aquí dejamos solo el nombre del producto.
            # (El código de producto ya se muestra en su propia columna)
            # ------------------------------------------------------------
            desc = (line.get("descripcion") or "").strip()
            code = str(line.get("codigoProducto") or "").strip()
            if desc:
                cleaned = desc

                if code:
                    # Casos: "[CODE] Nombre", "(CODE) Nombre", "CODE - Nombre", "CODE Nombre"
                    cleaned = re.sub(r"^\[\s*%s\s*\]\s*" % re.escape(code), "", cleaned)
                    cleaned = re.sub(r"^\(\s*%s\s*\)\s*" % re.escape(code), "", cleaned)
                    cleaned = re.sub(r"^%s\s*[-–—]\s*" % re.escape(code), "", cleaned)
                    cleaned = re.sub(r"^%s\s+" % re.escape(code), "", cleaned)

                # Caso genérico: "[ALGO] Nombre"
                cleaned = re.sub(r"^\[[A-Za-z0-9._\-]+\]\s*", "", cleaned)

                line["descripcion"] = cleaned.strip()

            detail.append({**line, "unit_description": unit_measure.description})
        return detail

    def _format_header_amounts(self, header):
        """
        Formatea todos los valores monetarios del header con 2 decimales.
        Esto asegura que todos los montos se muestren consistentemente
        con 2 posiciones decimales en los reportes.
        """
        # Lista de campos monetarios que deben formatearse
        monetary_fields = [
            'montoTotal',
            'montoTotalSujetoIva',
            'descuentoAdicional',
            'montoTotalMoneda',
            'montoGiftCard',
            'montoTotalArrendamientoFinanciero',
            'montoTotal2',
            'importeBaseCredFiscalComputable',
        ]
        
        for field in monetary_fields:
            if field in header and isinstance(header[field], (int, float)):
                header[field] = f"{float(header[field]):.2f}"
        
        return header

    def render_invoice(self):
        header = {}
        if not self.invoice_id:
            return
        invoice = self.invoice_id[-1]
        params_invoice = {
            "qr_code": invoice.qr_code,
            "observations": invoice.observations,
            "qr": "data:image/png;base64," + generate_qr(invoice.qr_code),
            "branch_name": self.pos_id.cucu_pos_id.branch_id.name,
            "invoice_url": invoice.url_cucu,
            "payment_key": "ok" if self.is_sin else "no",
        }
        invoice_json = json.loads(invoice.invoice_json)
        doc_sector = int(invoice_json["cabecera"]["codigoDocumentoSector"])
        if doc_sector == 1:
            header = {**invoice_json["cabecera"], **params_invoice}
        if doc_sector == 24:
            header = {**invoice_json["cabecera"], **params_invoice}
            header["fechaEmisionFactura"] = number_to_date(
                header["fechaEmisionFactura"]
            )

        detail = self._render_invoice_details(invoice_json["detalle"])
        header["numeroDocumento"] = _get_number_document(header)
        header["fechaEmision"] = number_to_date(header["fechaEmision"])
        header["montoLiteral"] = invoice.amount_literal
        header["codigoPuntoVenta"] = f'No. Punto de Venta {header["codigoPuntoVenta"]}'
        header["doc_sector"] = invoice.doc_sector
        
        # Formatear todos los valores monetarios del header con 2 decimales
        header = self._format_header_amounts(header)
        
        return {"header": header, "detail": detail}
