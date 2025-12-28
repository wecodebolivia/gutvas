import json
from datetime import datetime, timezone, timedelta


def string_to_json(string_json: str):
    parse = json.loads(string_json)
    return json.dumps(parse, indent=2, sort_keys=True)


def number_to_date(date_unix):
    timestamp_s = date_unix / 1000
    zh = timezone(timedelta(hours=-4))
    date = datetime.fromtimestamp(timestamp_s, tz=zh)
    return date.strftime("%Y/%m/%d %I:%M:%S")
