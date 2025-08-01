from odoo import fields, http, _
from odoo.http import request

import os
from odoo.addons.web.controllers.export import ExcelExport
from ..lib.date_utils import convert_date
from odoo.tools import config

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    xlsxwriter = None

import logging

_logger = logging.getLogger(__name__)

DOC_NAMES = ["", "CI", "CEX", "PAS", "OD", "NIT"]


class ExcelReport(ExcelExport):
    def _filestore(self):
        return config.filestore(request._cr.dbname)

    def _full_folder_path(self, path):
        # sanitize path
        return os.path.join(self._filestore(), path)

    @http.route("/cucu/report/sales", type="http", auth="public")
    def get_invoice_report(self, id):
        config_obj = request.env["invoice.report"].browse(int(id))
        date_from = fields.Datetime.to_string(config_obj.start_date)
        date_to = fields.Datetime.to_string(config_obj.end_date)
        path = self._full_folder_path("WK_export_update")
        if not os.path.isdir(path):
            os.mkdir(path)
        workbook = xlsxwriter.Workbook(path + "/invoice_report.xlsx")
        worksheet = workbook.add_worksheet()
        header_format = workbook.add_format(
            {
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
            }
        )

        worksheet.merge_range(4, 0, 5, 11, "REPORTE FACTURAS", header_format)

        worksheet.write(6, 0, "Nro")
        worksheet.write(6, 1, "Nro. Factura")
        worksheet.write(6, 2, "CUF")
        worksheet.write(6, 3, "Tipo Documento")
        worksheet.write(6, 4, "NIT/CI/CEX")
        worksheet.write(6, 5, "Razón Social")
        worksheet.write(6, 6, "Fecha Factura")
        worksheet.write(6, 7, "Monto Total")
        worksheet.write(6, 8, "Estado")
        worksheet.write(6, 9, "Nombre Sucursal")
        worksheet.write(6, 10, "Id Sucursal")
        worksheet.write(6, 11, "Id Pos")

        worksheet.set_column(0, 0, eval('len("Nro")*1.25'))
        worksheet.set_column(1, 1, eval('len("Nro. Factura")*1.25'))
        worksheet.set_column(2, 2, 66)
        worksheet.set_column(3, 3, eval('len("Tipo Documento")*1.25'))
        worksheet.set_column(4, 4, eval('len("NIT/CI/CEX")*1.25'))
        worksheet.set_column(5, 5, 30)
        worksheet.set_column(6, 6, 21)
        worksheet.set_column(7, 7, eval('len("Monto Total")*1.25'))
        worksheet.set_column(8, 8, 27)
        worksheet.set_column(9, 9, eval('len("Nombre Sucursal")*1.25'))
        worksheet.set_column(10, 10, eval('len("Id Sucursal")*1.25'))
        worksheet.set_column(11, 11, eval('len("Id Pos")*1.25'))

        pos = config_obj.pos
        branch_office = config_obj.branch_office
        pos_configs = config_obj.pos_configs
        branch_configs = config_obj.branch_configs
        contingency = config_obj.contingency
        doc_id = config_obj.doc_id
        canceled_invoices = config_obj.canceled_invoices
        is_valid = False
        status = []
        if contingency:
            status.append(695)
        elif canceled_invoices:
            status.append(905)
        else:
            # status.append(908)
            status = [908, 695, 905]
        pos_domain = []
        if pos:
            pos_domain = [
                ("date", ">=", date_from),
                ("siat_code_state", "in", status),
                ("date", "<=", date_to),
                (
                    "api_pos_id",
                    "in",
                    [config["cucu_pos_id"]["pos_id"] for config in pos_configs],
                ),
                (
                    "api_branch_id",
                    "in",
                    [
                        config["cucu_pos_id"]["branch_id"]["branch_id"]
                        for config in pos_configs
                    ],
                ),
            ]
            is_valid = True

        if branch_office:
            pos_domain = [
                ("date", ">=", date_from),
                ("siat_code_state", "in", status),
                ("date", "<=", date_to),
                (
                    "api_branch_id",
                    "in",
                    [config["branch_id"] for config in branch_configs],
                ),
            ]
            is_valid = True

        if len(doc_id) > 0:
            pos_domain.append(
                ("client_doc_id", "in", [int(doc["code_type"]) for doc in doc_id])
            )

        if is_valid:
            account = request.env["account.move"].search(
                pos_domain, order="api_invoice_number desc"
            )
            row = 7
            count = 1
            basic_style = workbook.add_format(
                {"align": "center", "valign": "center", "text_wrap": False}
            )
            for rec in account:
                worksheet.write(row, 0, count, basic_style)
                worksheet.write(row, 1, rec["api_invoice_number"], basic_style)
                worksheet.write(row, 2, rec["api_cuf"], basic_style)
                worksheet.write(
                    row,
                    3,
                    DOC_NAMES[int(rec["client_doc_id"]["code_type"]) or 1],
                    basic_style,
                )
                worksheet.write(row, 4, rec["client_nro_document"], basic_style)
                worksheet.write(row, 5, rec["client_reason_social"], basic_style)
                worksheet.write(
                    row, 6, convert_date(rec["api_date_emission"]), basic_style
                )
                worksheet.write(row, 7, rec["amount_subject_iva"], basic_style)
                worksheet.write(row, 8, rec["siat_description_status"], basic_style)
                worksheet.write(row, 9, rec["api_municipality"], basic_style)
                worksheet.write(row, 10, rec["api_branch_id"], basic_style)
                worksheet.write(row, 11, rec["api_pos_id"], basic_style)
                row += 1
                count += 1
        workbook.close()
        fp = open(path + "/invoice_report.xlsx", "rb")
        data = fp.read()
        fp.close()
        if len(account) > 0:
            return request.make_response(
                data,
                headers=[
                    ("Content-Type", "application/vnd.ms-excel"),
                    ("Content-Disposition", "attachment; filename=invoice_report.xls"),
                ],
            )

        else:
            _logger.info("NO SE ENCONTRARON REGISTROS")
            error = _("NO SE ENCOTRARON REGISTROS EN EL RANGO DE FECHAS")
            return error
