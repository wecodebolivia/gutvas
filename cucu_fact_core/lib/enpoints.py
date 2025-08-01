import logging

_logger = logging.getLogger(__name__)

urls = {
    "login": "/auth/login",
    "branch": "/branchOffice",
    "pos": "/pos",
    "pos_regenerate": "/pos/regenerate/#value",
    "catalog": "/catalog",
    "email": "/email",
    "sale": "/sale",
    "debit": "/debit",
    "cancel_sale": "/sale/anulation",
    "cancel_debit": "/debit/anulation",
    "event_init": "/event/start",
    "event_end": "/event/end",
    "rate": "/rate",
    "cancel_rate": "/sale/anulation",
    "free_zone": "/freeZone",
    "cancel_free_zone": "/freeZone/anulation",
    "nit": "/codes/nit",
}

invalid_methods = [
    "login",
    "branch",
    "pos",
    "catalog",
    "email",
    "pos_regenerate",
    "nit",
    "event_init",
    "event_end",
]

version_api = "api/v1"


def _get_service(host: str, method: str, is_electronic: bool = True, replace: str = ""):
    method_value = urls[method] if method in urls else False
    if not method_value:
        return False
    method_value = method_value.replace("#value", str(replace))
    if method not in invalid_methods:
        type_url = "/invoice/electronic" if is_electronic else "/invoice/computarized"
        url = f"{host}/{version_api}{type_url}{method_value}"
    else:
        url = f"{host}/{version_api}{method_value}"
    _logger.info(f"REQUEST IN {url}")
    return url
