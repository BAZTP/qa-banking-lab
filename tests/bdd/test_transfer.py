import pytest
from pytest_bdd import scenarios, given, when, then

pytestmark = pytest.mark.bdd
scenarios('features/transfer.feature')


@given('Ana inició sesión con sus cuentas de práctica')
def logged_in(auth):
    assert auth.get('/api/accounts').json()[0]['balance'] == '1000.00'


@when('transfiere 10.25 entre sus cuentas', target_fixture='result')
def transfer(auth):
    return auth.post('/api/transfers', json={'source': 'LAB-ANA-01', 'destination': 'LAB-ANA-02', 'amount': '10.25'})


@when('intenta transferir 1000.01', target_fixture='result')
def overdraw(auth):
    return auth.post('/api/transfers', json={'source': 'LAB-ANA-01', 'destination': 'LAB-ANA-02', 'amount': '1000.01'})


@then('su cuenta de origen tiene 989.75 y existe una operación')
def success(auth, result):
    assert result.status_code == 201
    assert auth.get('/api/accounts').json()[0]['balance'] == '989.75'
    assert len(auth.get('/api/transfers').json()) == 1


@then('se rechaza sin cambiar el saldo ni el historial')
def rejected(auth, result):
    assert result.status_code == 409
    assert auth.get('/api/accounts').json()[0]['balance'] == '1000.00'
    assert auth.get('/api/transfers').json() == []
