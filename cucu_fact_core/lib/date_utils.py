from datetime import datetime
import pytz


def convert_date(str_date):
    if not str_date:
        return None
    date = datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S.%f")
    return date.strftime("%d/%m/%Y %H:%M%p")


def convert_date_str(str_date):
    if not str_date:
        return None
    return datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S.%f")


def convert_date_event(date, utc):
    if not date:
        return None
    timezone = pytz.timezone(utc)
    return date.astimezone(timezone).strftime("%Y-%m-%dT%H:%M:%S.%f")
