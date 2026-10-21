"""Reglas monetarias puras: nunca usar float para almacenar dinero."""
from decimal import Decimal, InvalidOperation


def to_cents(value: str) -> int:
    try:
        amount = Decimal(value)
        if not amount.is_finite() or amount <= 0 or amount > Decimal('1000000'):
            raise ValueError('Importe fuera de rango (0, 1000000]')
        if amount != amount.quantize(Decimal('0.01')):
            raise ValueError('El importe admite como máximo dos decimales')
        return int(amount * 100)
    except (InvalidOperation, TypeError):
        raise ValueError('Importe inválido') from None


def money(cents: int) -> str:
    return f'{Decimal(cents) / 100:.2f}'
