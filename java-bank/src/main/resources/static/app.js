const $ = id => document.getElementById(id);
const message = text => { $('message').textContent = text; };
function loginView() { $('dashboard').hidden = true; $('login-panel').hidden = false; }
async function api(path, options = {}) {
  const response = await fetch(`/api/${path}`, {...options, headers: {'Content-Type': 'application/json', 'X-Lab-Request': '1'}});
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401) loginView();
    throw new Error(data.detail || 'No se pudo completar la operación');
  }
  return data;
}
function cell(row, text) { const td = document.createElement('td'); td.textContent = text; row.append(td); }
async function refresh() {
  const [accounts, history] = await Promise.all([api('accounts'), api('history')]);
  $('accounts').replaceChildren();
  for (const id of ['source', 'withdraw-source']) $(id).replaceChildren();
  for (const account of accounts) {
    const card = document.createElement('article'); card.className = 'account';
    for (const text of [account.label, account.id]) { const p = document.createElement('p'); p.textContent = text; card.append(p); }
    const balance = document.createElement('span'); balance.className = 'balance'; balance.textContent = `${account.balance} USD-DEMO`; card.append(balance); $('accounts').append(card);
    for (const id of ['source', 'withdraw-source']) { const option = document.createElement('option'); option.value = account.id; option.textContent = account.id; $(id).append(option); }
  }
  $('history').replaceChildren();
  for (const item of history) {
    const row = document.createElement('tr'); cell(row, item.kind === 'WITHDRAWAL' ? 'Retiro' : 'Transferencia');
    cell(row, `${item.source} → ${item.destination || 'Retiro ficticio'}`); cell(row, `${item.amount} USD-DEMO`); cell(row, `${item.note} · ${item.createdAt}`); $('history').append(row);
  }
  if (!history.length) { const row = document.createElement('tr'); cell(row, 'Sin operaciones todavía'); $('history').append(row); }
  $('login-panel').hidden = true; $('dashboard').hidden = false;
}
function form(id, action) {
  $(id).addEventListener('submit', async event => {
    event.preventDefault(); const button = event.submitter; button.disabled = true;
    try { await action(); } catch (error) { message(error.message); } finally { button.disabled = false; }
  });
}
form('login-form', async () => {
  await api('login', {method: 'POST', body: JSON.stringify({username: $('username').value, password: $('password').value})});
  $('password').value = ''; await refresh(); message('Sesión iniciada');
});
form('transfer-form', async () => {
  const body = Object.fromEntries(['source','destination','amount','note'].map(id => [id,$(id).value]));
  await api('transfers', {method: 'POST', body: JSON.stringify(body)}); $('amount').value = ''; $('note').value = '';
  await refresh(); message('Transferencia simulada completada');
});
form('withdraw-form', async () => {
  await api('withdrawals', {method: 'POST', body: JSON.stringify({source: $('withdraw-source').value, amount: $('withdraw-amount').value})});
  $('withdraw-amount').value = ''; await refresh(); message('Retiro simulado completado');
});
$('logout').addEventListener('click', async () => {
  try { await api('logout', {method: 'POST'}); loginView(); message('Sesión cerrada'); } catch (error) { message(error.message); }
});
api('health').then(health => { if (health.trainingBugs) { $('mode').textContent = 'ENTRENAMIENTO · BUGS INTENCIONALES ACTIVOS'; $('mode').classList.add('training'); } }).catch(error => message(error.message));
refresh().catch(error => { loginView(); if (!error.message.includes('Inicia sesión')) message(error.message); });
