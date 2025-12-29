import json
from datetime import datetime, timezone, timedelta


def string_to_json(string_json: str):
    parse = json.loads(string_json)
    return json.dumps(parse, indent=2, sort_keys=True)


def number_to_date(date_unix):
    """
    Convierte timestamps a string de fecha.

    Soporta:
    - int/float en milisegundos
    - int/float en segundos
    - strings numéricos (ms o s)
    - strings ISO datetime (con o sin 'Z')
    - si no puede parsear, devuelve el valor original como string
    """
    if date_unix is None:
        return ""

    zh = timezone(timedelta(hours=-4))  # Bolivia (-04:00)

    # Si viene como string, intentar normalizar
    if isinstance(date_unix, str):
        s = date_unix.strip()
        if not s:
            return ""

        # 1) ¿Es número?
        try:
            date_unix = float(s)
        except Exception:
            # 2) ¿Es ISO datetime?
            try:
                iso = s.replace("Z", "+00:00")
                dt = datetime.fromisoformat(iso)
                if dt.tzinfo:
                    dt = dt.astimezone(zh)
                else:
                    dt = dt.replace(tzinfo=zh)
                return dt.strftime("%Y/%m/%d %H:%M:%S")
            except Exception:
                # 3) No lo entiendo → lo devuelvo tal cual
                return s

    # A esta altura, intentamos convertir a número
    try:
        ts = float(date_unix)
    except Exception:
        return str(date_unix)

    # Heurística: si es enorme, casi seguro viene en ms
    # 2025 en ms ~ 1.7e12, en s ~ 1.7e9
    if ts > 10_000_000_000:  # > 1e10 => milisegundos
        timestamp_s = ts / 1000.0
    else:
        timestamp_s = ts  # segundos

    dt = datetime.fromtimestamp(timestamp_s, tz=zh)
    return dt.strftime("%Y/%m/%d %H:%M:%S")
