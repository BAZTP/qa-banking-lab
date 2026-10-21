import pytest
from app.domain import money, to_cents


@pytest.mark.parametrize('amount,expected', [('0.01', 1), ('10.25', 1025), ('1000000', 100000000), ('1.00', 100)])
def test_amount_in_cents(amount, expected):
    assert to_cents(amount) == expected
    assert to_cents(money(expected)) == expected


@pytest.mark.parametrize('amount', ['0', '-1', '1.001', 'NaN', 'Infinity', 'abc', '', '1000000.01'])
def test_invalid_amount(amount):
    with pytest.raises(ValueError):
        to_cents(amount)
