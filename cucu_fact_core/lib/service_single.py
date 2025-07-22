import requests
import logging

from odoo.exceptions import ValidationError
from .enpoints import _get_service

_logger = logging.getLogger(__name__)

service_cancel_url = {
    "1": "cancel_sale",
    "5": "cancel_free_zone",
    "8": "cancel_rate",
    "24": "cancel_debit",
}

service_invoice_url = {
    "1": "sale",
    "5": "free_zone",
    "8": "rate",
    "24": "debit",
}


def create_header(token):
    return {
        "content-type": "application/json",
        "cucukey": f"Token {token}",
    }


valid_status_code = [200, 201]


def api_service(url, params_json, error_message, token="", method="POST"):
    try:
        _logger.info("....... PARAMS %s", params_json)
        if method == "POST":
            res = requests.post(url=url, json=params_json, headers=create_header(token))
        else:
            res = requests.get(url=url, json=params_json, headers=create_header(token))
        response = res.json()
        if response["success"] or response["message"] == "TOKEN CREADED":
            _logger.info("....... PARAMS %s", response["data"])
            return response
        elif error_message == "":
            return False
        else:
            _logger.error(response)
            raise ValidationError(response["message"])
    except requests.exceptions.HTTPError as errh:
        _logger.error(errh.args[0])
        raise ValidationError(errh.args[0])
    except requests.exceptions.ReadTimeout as errrt:  # noqa: F841
        _logger.error("TIME OUT ERROR SERVER")
        raise ValidationError("TIME OUT ERROR SERVER")
    except requests.exceptions.ConnectionError as conerr:  # noqa: F841
        _logger.error("API CUCU NOT CONNECT")
        raise ValidationError("API CUCU NOT CONNECT")
    finally:
        _logger.info(f"URL -> {url}")


def service_login(**params):
    params_json = {
        "username": params["username"],
        "password": params["password"],
    }
    url = _get_service(params["host"], "login")
    return api_service(url, params_json, "LOGIN SERVICE ERROR")


def get_service_catalogs(**params):
    params_json = {
        "posId": params["posId"],
        "branchId": params["branchId"],
    }
    url = _get_service(params["host"], "catalog")
    return api_service(
        url, params_json, "ERROR IN SYNC CATALOGS", params["token"], "GET"
    )


def create_service_catalogs(**params):
    params_json = {
        "posId": params["pos_id"],
        "branchId": params["branch_id"],
    }
    url = _get_service(params["host"], "catalog")
    return api_service(
        url, params_json, "ERROR IN CREATE SYNC CATALOGS", params["token"]
    )


def create_pos(**params):
    params_json = {
        "branchId": params["branch_id"],
        "siatTypePos": params["siat_type_pos"],
        "siatDescription": params["siat_description"],
        "posName": params["pos_name"],
        "name": params["name"],
    }
    url = _get_service(params["host"], "pos")
    return api_service(url, params_json, "ERROR CREATE POS", params["token"])


def get_service_branchs(**params):
    url = _get_service(params["host"], "branch")
    return api_service(url, {}, "SYNC ERROR BRANCH", params["token"], "GET")


def get_service_pos_regenerate(**params):
    url = _get_service(params["host"], "pos_regenerate", True, params["branchId"])
    return api_service(url, {}, "SYNC ERROR POS REGENERATE", params["token"], "GET")


def valid_service_nit(**params):
    params_json = {"nit": params["nit"], "posId": 1}
    url = _get_service(params["host"], "nit")
    res = api_service(url, params_json, "", params["token"], "QUERY")
    return res


def send_invoice(**params):
    method = service_invoice_url[params["docSector"]]
    url = _get_service(params["host"], method, params["isElectronic"])
    res = api_service(url, params, "ERROR IN SEND INVOICE", params["token"])
    return res


def send_cancel_invoice(**params):
    method = service_cancel_url[params["docSector"]]
    url = _get_service(params["host"], method, params["isElectronic"])
    res = api_service(url, params, "ERROR IN SEND INVOICE", params["token"])
    return res


def send_revert_invoice(**params):
    method = service_invoice_url[params["docSector"]]
    url = _get_service(params["host"], method, params["isElectronic"])
    res = api_service(f"{url}/revert", params, "ERROR IN SEND INVOICE", params["token"])
    return res


def send_status_invoice(**params):
    method = service_invoice_url[params["docSector"]]
    url = _get_service(params["host"], method, params["isElectronic"])
    res = api_service(
        f"{url}/status", params, "ERROR IN SEND INVOICE", params["token"], "GET"
    )
    return res


def create_event_start(**params):
    url = _get_service(params["host"], "event_init")
    res = api_service(url, params, "ERROR IN CREATE EVENT", params["token"])
    return res


def create_event_end(**params):
    url = _get_service(params["host"], "event_end")
    res = api_service(url, params, "ERROR IN CREATE END EVENT", params["token"])
    return res


def send_email(**params):
    url = _get_service(params["host"], "email")
    res = api_service(url, params, "ERROR SEND EMAIL", params["token"])
    return res
