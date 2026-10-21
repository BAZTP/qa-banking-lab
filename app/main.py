"""API educativa. No apta para banca ni uso en producción."""
import hmac
import os
import secrets
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from app.db import connect, initialize, password_hash
from app.domain import money, to_cents

STATIC = Path(__file__).parent / 'static'


class Login(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class Transfer(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source: str = Field(min_length=1, max_length=40)
    destination: str = Field(min_length=1, max_length=40)
    amount: str = Field(min_length=1, max_length=30)
    note: str = Field(default='', max_length=140)


def create_app(db_path=None):
    path = str(db_path or os.getenv('QA_BANK_DB', 'data/lab.db'))
    sessions = {}  # Proceso único; sesiones efímeras con vencimiento.

    @asynccontextmanager
    async def lifespan(app):
        initialize(path)
        yield
        sessions.clear()

    api = FastAPI(title='QA Banking Lab', version='0.1.0', lifespan=lifespan)

    @api.middleware('http')
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'"
        if request.url.path in ('/docs', '/redoc'):
            # Swagger/ReDoc generados por FastAPI usan CDN y un bootstrap inline.
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; img-src 'self' data: https://fastapi.tiangolo.com; frame-ancestors 'none'"
        response.headers['Cache-Control'] = 'no-store'
        return response

    def user(request: Request):
        # JSON + cabecera propia impiden envíos CSRF de formularios de otro origen.
        if request.method not in ('GET', 'HEAD') and request.headers.get('X-Lab-Request') != '1':
            raise HTTPException(403, 'Falta cabecera X-Lab-Request')
        token = request.cookies.get('lab_session', '')
        session = sessions.get(token)
        if not session or session[1] <= time.monotonic():
            sessions.pop(token, None)
            raise HTTPException(401, 'Inicia sesión para continuar')
        return session[0]

    @api.get('/api/health')
    def health():
        with connect(path) as db:
            db.execute('SELECT 1').fetchone()
        return {'status': 'ok', 'mode': 'educational'}

    @api.post('/api/login')
    def login(payload: Login, request: Request, response: Response):
        with connect(path) as db:
            row = db.execute('SELECT * FROM users WHERE username = ?', (payload.username,)).fetchone()
        # Ejecutar derivación también para usuarios inexistentes.
        salt = row['salt'] if row else '00' * 16
        candidate = password_hash(payload.password, salt)
        if not row or not hmac.compare_digest(candidate, row['password_hash']):
            raise HTTPException(401, 'Credenciales de demostración incorrectas')
        sessions.pop(request.cookies.get('lab_session', ''), None)
        token = secrets.token_urlsafe(32)
        sessions[token] = (row['id'], time.monotonic() + 3600)
        response.set_cookie('lab_session', token, httponly=True, samesite='strict',
                            secure=request.url.scheme == 'https', max_age=3600)
        return {'username': row['username']}

    @api.post('/api/logout')
    def logout(request: Request, response: Response, uid=Depends(user)):
        sessions.pop(request.cookies.get('lab_session', ''), None)
        response.delete_cookie('lab_session')
        return {'message': 'Sesión cerrada'}

    @api.get('/api/accounts')
    def accounts(uid=Depends(user)):
        with connect(path) as db:
            rows = db.execute('SELECT * FROM accounts WHERE user_id = ? ORDER BY id', (uid,)).fetchall()
        return [{'id': r['id'], 'label': r['label'], 'balance': money(r['balance']), 'currency': 'USD-DEMO'} for r in rows]

    @api.get('/api/transfers')
    def history(uid=Depends(user)):
        with connect(path) as db:
            rows = db.execute('''SELECT t.* FROM transfers t
                JOIN accounts a ON a.id = t.destination
                WHERE t.user_id = ? OR a.user_id = ? ORDER BY t.id DESC''', (uid, uid)).fetchall()
        return [{'id': r['id'], 'source': r['source'], 'destination': r['destination'],
                 'amount': money(r['amount']), 'note': r['note'], 'created_at': r['created_at']} for r in rows]

    @api.post('/api/transfers', status_code=201)
    def transfer(payload: Transfer, uid=Depends(user)):
        try:
            cents = to_cents(payload.amount)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        if payload.source == payload.destination:
            raise HTTPException(422, 'Las cuentas deben ser distintas')
        with connect(path) as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                source = db.execute('SELECT * FROM accounts WHERE id = ? AND user_id = ?', (payload.source, uid)).fetchone()
                if not source:
                    raise HTTPException(404, 'Cuenta de origen no disponible')
                dest = db.execute('SELECT id FROM accounts WHERE id = ?', (payload.destination,)).fetchone()
                if not dest:
                    raise HTTPException(404, 'Cuenta de destino no disponible')
                if source['balance'] < cents:
                    raise HTTPException(409, 'Saldo insuficiente')
                db.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (cents, payload.source))
                db.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (cents, payload.destination))
                cur = db.execute('INSERT INTO transfers(user_id, source, destination, amount, note) VALUES (?, ?, ?, ?, ?)',
                                 (uid, payload.source, payload.destination, cents, payload.note))
                db.commit()
            except Exception:
                db.rollback()
                raise
        return {'id': cur.lastrowid, 'amount': money(cents), 'message': 'Transferencia simulada completada'}

    api.mount('/static', StaticFiles(directory=STATIC), name='static')

    @api.get('/', include_in_schema=False)
    def index():
        return FileResponse(STATIC / 'index.html')

    return api


app = create_app()
