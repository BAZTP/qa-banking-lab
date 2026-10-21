import os
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e


def login(page):
    page.goto(os.getenv('LAB_BASE_URL', 'http://127.0.0.1:8001'))
    page.get_by_label('Usuario de demostración').fill('ana')
    page.get_by_label('Contraseña de demostración').fill('Demo123!')
    page.get_by_role('button', name='Entrar al laboratorio').click()
    expect(page.get_by_role('heading', name='Mis cuentas ficticias')).to_be_visible()


@pytest.mark.smoke
def test_login_and_logout(page):
    login(page)
    expect(page.locator('.account')).to_have_count(2)
    page.get_by_role('button', name='Cerrar sesión').click()
    expect(page.get_by_role('heading', name='Inicia una sesión de práctica')).to_be_visible()


def test_invalid_login(page):
    page.goto(os.getenv('LAB_BASE_URL', 'http://127.0.0.1:8001'))
    page.get_by_label('Usuario de demostración').fill('ana')
    page.get_by_label('Contraseña de demostración').fill('incorrecta')
    page.get_by_role('button', name='Entrar al laboratorio').click()
    expect(page.get_by_role('status')).to_have_text('Credenciales de demostración incorrectas')


def test_transfer_history_and_escaped_note(page):
    login(page)
    initial = page.locator('.balance').first.inner_text().split()[0]
    page.get_by_label('Cuenta de destino ficticia').fill('LAB-ANA-02')
    page.get_by_label('Importe (USD-DEMO)').fill('10.25')
    note = '<img src=x onerror=alert(1)>'
    page.get_by_label('Concepto (opcional)').fill(note)
    page.get_by_role('button', name='Simular transferencia').click()
    expect(page.get_by_role('status')).to_have_text('Transferencia simulada completada')
    expect(page.locator('.balance').first).to_have_text(f'{float(initial)-10.25:.2f} USD-DEMO')
    expect(page.locator('#history')).to_contain_text(note)
    expect(page.locator('#history img')).to_have_count(0)
    page.reload()
    expect(page.locator('#history')).to_contain_text(note)


def test_insufficient_balance(page):
    login(page)
    before = page.locator('.balance').first.inner_text()
    page.get_by_label('Cuenta de destino ficticia').fill('LAB-ANA-02')
    page.get_by_label('Importe (USD-DEMO)').fill('1000000')
    page.get_by_role('button', name='Simular transferencia').click()
    expect(page.get_by_role('status')).to_have_text('Saldo insuficiente')
    expect(page.locator('.balance').first).to_have_text(before)
