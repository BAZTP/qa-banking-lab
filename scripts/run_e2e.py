"""Ejecuta navegador contra un servidor temporal aislado, en Windows o Linux."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='qa-banking-e2e-') as directory:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        base = f'http://127.0.0.1:{port}'
        environment = {**os.environ, 'QA_BANK_DB': str(Path(directory) / 'e2e.db'),
                       'RUN_E2E': '1', 'LAB_BASE_URL': base}
        with (Path(directory) / 'server.log').open('w+') as log:
            server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app',
                                       '--host', '127.0.0.1', '--port', str(port)],
                                      cwd=ROOT, env=environment, stdout=log, stderr=log)
            try:
                for _ in range(100):
                    if server.poll() is not None:
                        break
                    try:
                        with urlopen(f'{base}/api/health', timeout=1) as response:
                            if response.status == 200:
                                return subprocess.call([sys.executable, '-m', 'pytest', 'tests/e2e',
                                                        *sys.argv[1:]], cwd=ROOT, env=environment)
                    except (URLError, TimeoutError):
                        time.sleep(0.1)
                log.seek(0)
                print(log.read(), file=sys.stderr)
                return 1
            finally:
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()


if __name__ == '__main__':
    sys.exit(main())
