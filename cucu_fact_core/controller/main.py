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

        header_format = workbook.add_format({
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True,
        })

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

        worksheet.set_column(0, 0, len("Nro")*1.25)
        worksheet.set_column(1, 1, len("Nro. Factura")*1.25)
        worksheet.set_column(2, 2, 66)
        worksheet.set_column(3, 3, len("Tipo Documento")*1.25)
        worksheet.set_column(4, 4, len("NIT/CI/CEX")*1.25)
        worksheet.set_column(5, 5, 30)
        worksheet.set_column(6, 6, 21)
        worksheet.set_column(7, 7, len("Monto Total")*1.25)
        worksheet.set_column(8, 8, 27)
        worksheet.set_column(9, 9, len("Nombre Sucursal")*1.25)
        worksheet.set_column(10, 10, len("Id Sucursal")*1.25)
        worksheet.set_column(11, 11, len("Id Pos")*1.25)

        pos = config_obj.pos
        branch_office = config_obj.branch_office
        pos_configs = config_obj.pos_configs
        branch_configs = config_obj.branch_configs
        contingency = config_obj.contingency
        doc_id = config_obj.doc_id
        canceled_invoices = config_obj.canceled_invoices

        status = []
        if contingency:
            status = [695]
        elif canceled_invoices:
            status = [905]
        else:
            status = [908, 695, 905]

        invoice_domain = [
            ("sin_code_state", "in", status),
            ("date_emission", ">=", date_from),
            ("date_emission", "<=", date_to),
        ]

        if pos:
            invoice_domain += [
                ("pos_id", "in",
                 [config["cucu_pos_id"]["pos_id"] for config in pos_configs]),
                ("branch_id", "in",
                 [config["cucu_pos_id"]["branch_id"]["branch_id"] for config in pos_configs]),
            ]

        if branch_office:
            invoice_domain += [
                ("branch_id", "in",
                 [config["branch_id"] for config in branch_configs]),
            ]

        if len(doc_id) > 0:
            invoice_domain.append(
                ("partner_id.doc_id", "in",
                 [int(doc["code_type"]) for doc in doc_id])
            )

        invoices = request.env["cucu.invoice"].search(
            invoice_domain,
            order="invoice_number desc"
        )

        account_moves = invoices.mapped("account_move_id")
 
        row = 7
        count = 1
        basic_style = workbook.add_format({
            "align": "center",
            "valign": "center",
            "text_wrap": False
        })

        for inv in invoices:
            mov = inv.account_move_id

            worksheet.write(row, 0, count, basic_style)
            worksheet.write(row, 1, inv.invoice_number or "", basic_style)
            worksheet.write(row, 2, inv.cuf or "", basic_style)

            doc_type = inv.partner_id.doc_id.code_type if inv.partner_id.doc_id else 1
            worksheet.write(row, 3, DOC_NAMES[int(doc_type)], basic_style)

            worksheet.write(row, 4, inv.partner_id.nit_client or "", basic_style)
            worksheet.write(row, 5, inv.partner_id.reason_social or "", basic_style)
            worksheet.write(row, 6, convert_date(inv.date_emission), basic_style)
            worksheet.write(row, 7, inv.amount_subject_iva, basic_style)
            worksheet.write(row, 8, inv.sin_description_status, basic_style)
            worksheet.write(row, 9, inv.municipality or "", basic_style)
            worksheet.write(row, 10, inv.branch_id, basic_style)
            worksheet.write(row, 11, inv.pos_id, basic_style)

            row += 1
            count += 1

        workbook.close()

        fp = open(path + "/invoice_report.xlsx", "rb")
        data = fp.read()
        fp.close()

        if invoices:
            return request.make_response(
                data,
                headers=[
                    ("Content-Type", "application/vnd.ms-excel"),
                    ("Content-Disposition",
                     "attachment; filename=invoice_report.xls"),
                ],
            )
        else:
            _logger.info("NO SE ENCONTRARON REGISTROS")
            return _("NO SE ENCOTRARON REGISTROS EN EL RANGO DE FECHAS")
