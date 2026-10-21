import os
import pytest
from fastapi.testclient import TestClient
from app.main import create_app


def pytest_collection_modifyitems(config, items):
    if os.getenv('RUN_E2E') != '1':
        for item in items:
            if 'e2e' in item.keywords:
                item.add_marker(pytest.mark.skip(reason='Opt-in: RUN_E2E=1 y servidor de prueba aislado'))


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / 'test.db')) as client:
        yield client


@pytest.fixture
def auth(client):
    response = client.post('/api/login', json={'username': 'ana', 'password': 'Demo123!'})
    assert response.status_code == 200
    client.headers['X-Lab-Request'] = '1'
    return client


@pytest.fixture(scope='session')
def browser_type_launch_args(browser_type_launch_args):
    executable = os.getenv('LAB_CHROMIUM_EXECUTABLE')
    if executable:
        return {**browser_type_launch_args, 'executable_path': executable}
    return browser_type_launch_args
