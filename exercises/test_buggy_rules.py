"""Opt-in: pytest exercises -v. XFAIL estricto documenta los defectos conocidos."""
import pytest
from exercises.buggy_rules import accepts_amount, can_transfer


@pytest.mark.xfail(strict=True, reason='BUG-01: se acepta cero')
def test_zero_is_rejected():
    assert not accepts_amount(0)


@pytest.mark.xfail(strict=True, reason='BUG-02: saldo exacto rechazado')
def test_exact_balance_is_allowed():
    assert can_transfer(100, 100)
