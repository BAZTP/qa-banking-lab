import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from app.main import create_app

PAYLOAD = {'source': 'LAB-ANA-01', 'destination': 'LAB-ANA-02', 'amount': '10.25', 'note': 'Práctica'}


@pytest.mark.smoke
def test_health_login_accounts_and_logout(client):
    assert client.get('/api/health').json() == {'status': 'ok', 'mode': 'educational'}
    assert client.get('/api/accounts').status_code == 401
    assert client.post('/api/login', json={'username': 'ana', 'password': 'Demo123!'}).status_code == 200
    assert len(client.get('/api/accounts').json()) == 2
    assert client.post('/api/logout', headers={'X-Lab-Request': '1'}).status_code == 200
    assert client.get('/api/accounts').status_code == 401


@pytest.mark.sanity
@pytest.mark.regression
def test_transfer_updates_both_balances_and_history(auth):
    response = auth.post('/api/transfers', json=PAYLOAD)
    assert response.status_code == 201
    assert [a['balance'] for a in auth.get('/api/accounts').json()] == ['989.75', '260.25']
    history = auth.get('/api/transfers').json()
    assert len(history) == 1
    assert history[0]['id'] == response.json()['id']
    assert history[0]['note'] == 'Práctica'
    assert history[0]['amount'] == '10.25'


CASES = json.loads((Path(__file__).parents[1] / 'data/transfers.json').read_text())


@pytest.mark.regression
@pytest.mark.parametrize('case', CASES, ids=[c['amount'] for c in CASES])
def test_data_driven_transfer(auth, case):
    response = auth.post('/api/transfers', json={**PAYLOAD, 'amount': case['amount']})
    assert response.status_code == case['status']
    assert auth.get('/api/accounts').json()[0]['balance'] == case['balance']
    assert len(auth.get('/api/transfers').json()) == (1 if case['status'] == 201 else 0)
    total = sum(round(float(a['balance']) * 100) for a in auth.get('/api/accounts').json())
    assert total == 125000


@pytest.mark.security
@pytest.mark.parametrize('username,password', [('ana', 'incorrecta'), ("' OR 1=1 --", 'Demo123!'), ('nadie', 'Demo123!')])
def test_reject_invalid_login(client, username, password):
    assert client.post('/api/login', json={'username': username, 'password': password}).status_code == 401
    assert client.get('/api/accounts').status_code == 401


@pytest.mark.security
def test_ownership_and_recipient_visibility(auth):
    assert auth.post('/api/transfers', json={**PAYLOAD, 'source': 'LAB-BRU-01'}).status_code == 404
    assert auth.get('/api/transfers').json() == []
    assert auth.post('/api/transfers', json=PAYLOAD).status_code == 201
    assert auth.post('/api/transfers', json={**PAYLOAD, 'destination': 'LAB-BRU-01'}).status_code == 201
    auth.post('/api/login', json={'username': 'bruno', 'password': 'Demo123!'})
    assert [a['id'] for a in auth.get('/api/accounts').json()] == ['LAB-BRU-01']
    assert auth.get('/api/accounts').json()[0]['balance'] == '760.25'
    assert len(auth.get('/api/transfers').json()) == 1


@pytest.mark.security
def test_csrf_cookie_and_headers(auth):
    auth.headers.pop('X-Lab-Request')
    assert auth.post('/api/transfers', json=PAYLOAD).status_code == 403
    response = auth.post('/api/login', json={'username': 'ana', 'password': 'Demo123!'})
    assert 'HttpOnly' in response.headers['set-cookie']
    assert 'SameSite=strict' in response.headers['set-cookie']
    assert response.headers['x-content-type-options'] == 'nosniff'


@pytest.mark.regression
@pytest.mark.parametrize('override,status', [({'destination': 'LAB-ANA-01'}, 422), ({'destination': 'LAB-NO-01'}, 404), ({'note': 'x'*141}, 422), ({'amount': 10}, 422)])
def test_invalid_transfers_are_atomic(auth, override, status):
    before = auth.get('/api/accounts').json()
    assert auth.post('/api/transfers', json={**PAYLOAD, **override}).status_code == status
    assert auth.get('/api/accounts').json() == before
    assert auth.get('/api/transfers').json() == []


@pytest.mark.regression
def test_concurrent_transfers_cannot_overdraw(auth):
    def send(_):
        return auth.post('/api/transfers', json={**PAYLOAD, 'amount': '600'}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(send, range(2))) == [201, 409]
    assert [a['balance'] for a in auth.get('/api/accounts').json()] == ['400.00', '850.00']
    assert len(auth.get('/api/transfers').json()) == 1


def test_restart_preserves_balances_and_does_not_reseed(tmp_path):
    path = tmp_path / 'persistent.db'
    for iteration in range(2):
        with TestClient(create_app(path)) as client:
            client.post('/api/login', json={'username': 'ana', 'password': 'Demo123!'})
            if iteration == 0:
                assert client.post('/api/transfers', json=PAYLOAD, headers={'X-Lab-Request': '1'}).status_code == 201
            assert client.get('/api/accounts').json()[0]['balance'] == '989.75'
            assert len(client.get('/api/transfers').json()) == 1


@pytest.mark.security
def test_unauthenticated_mutation_and_history(client):
    assert client.post('/api/transfers', json=PAYLOAD, headers={'X-Lab-Request': '1'}).status_code == 401
    assert client.get('/api/transfers').status_code == 401


def test_frontend_assets(client):
    assert 'QA Banking Lab' in client.get('/').text
    assert client.get('/static/app.js').status_code == 200
    assert client.get('/static/style.css').status_code == 200


@pytest.mark.security
def test_session_is_invalid_after_restart(tmp_path):
    path = tmp_path / 'sessions.db'
    with TestClient(create_app(path)) as client:
        client.post('/api/login', json={'username': 'ana', 'password': 'Demo123!'})
        cookie = client.cookies.get('lab_session')
    with TestClient(create_app(path)) as client:
        client.cookies.set('lab_session', cookie)
        assert client.get('/api/accounts').status_code == 401
