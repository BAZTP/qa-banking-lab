"""Recorrido de navegador contra JAR y base temporal. Requiere Python + Playwright.

Ejecutar desde java-bank/: python qa/browser_check.py [--training]
"""
import argparse
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
from urllib.request import urlopen
from urllib.error import URLError

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--training', action='store_true')
    args = parser.parse_args()
    jar = ROOT / 'target/java-banking-lab-0.1.0.jar'
    if not jar.exists():
        raise SystemExit('Primero compila el JAR con mvnw clean verify')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    command = ['java', '-jar', str(jar), f'--server.port={port}', '--spring.datasource.url=jdbc:h2:mem:browser;DB_CLOSE_DELAY=-1']
    if args.training:
        command += ['--spring.profiles.active=training', '--lab.training-bugs=true']
    with tempfile.TemporaryDirectory(prefix='java-bank-browser-') as directory:
        with (Path(directory) / 'server.log').open('w+') as log:
            server = subprocess.Popen(command, cwd=directory, stdout=log, stderr=log)
            try:
                for _ in range(300):
                    if server.poll() is not None:
                        break
                    try:
                        with urlopen(base + '/api/health', timeout=1) as response:
                            if response.status == 200:
                                break
                    except (URLError, TimeoutError):
                        time.sleep(.2)
                else:
                    raise AssertionError('El servidor no respondió en el plazo esperado')
                if server.poll() is not None:
                    log.seek(0)
                    raise AssertionError(log.read())
                with sync_playwright() as playwright:
                    launch = {}
                    if os.getenv('LAB_CHROMIUM_EXECUTABLE'):
                        launch['executable_path'] = os.environ['LAB_CHROMIUM_EXECUTABLE']
                    browser = playwright.chromium.launch(**launch)
                    try:
                        page = browser.new_page(viewport={'width': 1280, 'height': 900})
                        errors = []
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.goto(base)
                        page.get_by_label('Usuario', exact=True).fill('ana')
                        page.get_by_label('Contraseña', exact=True).fill('incorrecta')
                        page.get_by_role('button', name='Iniciar sesión', exact=True).click()
                        expect(page.get_by_role('status')).to_contain_text('incorrectas')
                        page.get_by_label('Contraseña', exact=True).fill('Demo123!')
                        page.get_by_role('button', name='Iniciar sesión', exact=True).click()
                        expect(page.locator('.balance').first).to_have_text('1000.00 USD-DEMO')
                        if args.training:
                            expect(page.locator('#mode')).to_contain_text('BUGS INTENCIONALES ACTIVOS')
                            page.get_by_label('Importe a retirar').fill('1000.00')
                            page.get_by_role('button', name='Simular retiro', exact=True).click()
                            expect(page.get_by_role('status')).to_have_text('Saldo insuficiente')
                            page.get_by_label('Cuenta de destino', exact=True).fill('LAB-ANA-01')
                            page.get_by_label('Importe a transferir').fill('10.00')
                            page.get_by_role('button', name='Simular transferencia', exact=True).click()
                            expect(page.get_by_role('status')).to_have_text('Transferencia simulada completada')
                            expect(page.locator('#history tr')).to_have_count(1)
                            expect(page.locator('.balance').first).to_have_text('1000.00 USD-DEMO')
                        else:
                            page.get_by_label('Importe a retirar').fill('50.00')
                            page.get_by_role('button', name='Simular retiro', exact=True).click()
                            expect(page.locator('.balance').first).to_have_text('950.00 USD-DEMO')
                            page.get_by_label('Cuenta de destino', exact=True).fill('LAB-ANA-02')
                            page.get_by_label('Importe a transferir').fill('10.25')
                            page.get_by_label('Concepto', exact=True).fill('<img src=x onerror=alert(1)>')
                            page.get_by_role('button', name='Simular transferencia', exact=True).click()
                            expect(page.locator('.balance').first).to_have_text('939.75 USD-DEMO')
                            expect(page.locator('.balance').nth(1)).to_have_text('260.25 USD-DEMO')
                            expect(page.locator('#history tr')).to_have_count(2)
                            expect(page.locator('#history img')).to_have_count(0)
                            expect(page.locator('#history')).to_contain_text('<img src=x onerror=alert(1)>')
                            page.get_by_label('Importe a retirar').fill('1000000')
                            page.get_by_role('button', name='Simular retiro', exact=True).click()
                            expect(page.get_by_role('status')).to_have_text('Saldo insuficiente')
                            expect(page.locator('.balance').first).to_have_text('939.75 USD-DEMO')
                            page.reload()
                            expect(page.locator('#history tr')).to_have_count(2)
                        artifacts = ROOT.parent / 'test-results/java-browser'
                        artifacts.mkdir(parents=True, exist_ok=True)
                        label = 'training' if args.training else 'normal'
                        page.screenshot(path=str(artifacts / f'{label}.png'), full_page=True)
                        page.set_viewport_size({'width':390,'height':844})
                        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                        page.get_by_role('button', name='Cerrar sesión', exact=True).click()
                        expect(page.get_by_role('heading', name='Entra al laboratorio')).to_be_visible()
                        assert page.request.get(base+'/api/accounts').status == 401
                        assert not errors, errors
                        print(f'OK navegador {label}: login, operaciones, historial, vista móvil y logout')
                    finally:
                        browser.close()
            finally:
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()


if __name__ == '__main__':
    main()
