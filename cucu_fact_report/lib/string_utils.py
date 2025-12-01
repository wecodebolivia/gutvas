import json
from datetime import datetime, timezone, timedelta


def string_to_json(string_json: str):
    parse = json.loads(string_json)
    return json.dumps(parse, indent=2, sort_keys=True)


def number_to_date(date_value):
    if not date_value:
        return ""

    if isinstance(date_value, datetime):
        return date_value.strftime("%Y/%m/%d %I:%M:%S")

    try:
        timestamp_s = int(date_value) / 1000
        zh = timezone(timedelta(hours=-4))
        dt = datetime.fromtimestamp(timestamp_s, tz=zh)
        return dt.strftime("%Y/%m/%d %I:%M:%S")
    except:
        pass

    try:
        dt = datetime.fromisoformat(date_value)
        return dt.strftime("%Y/%m/%d %I:%M:%S")
    except:
        pass

    return str(date_value)
