from decimal import Decimal, ROUND_HALF_UP


def halfup_convert(number):
    if number < 0:
        return 0
    return float(Decimal(number).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
