const $ = id => document.getElementById(id);
function message(text) { $('message').textContent = text; }
async function api(path, options = {}) {
  const response = await fetch(`/api/${path}`, {
    ...options, headers: {'Content-Type': 'application/json', 'X-Lab-Request': '1'}
  });
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401 && path !== 'login') showLogin();
    throw new Error(typeof data.detail === 'string' ? data.detail : 'Revisa los datos introducidos');
  }
  return data;
}
function showLogin() { $('dashboard').hidden = true; $('login-panel').hidden = false; }
function cell(row, text) { const td = document.createElement('td'); td.textContent = text; row.append(td); }
async function refresh() {
  const [accounts, history] = await Promise.all([api('accounts'), api('transfers')]);
  $('accounts').replaceChildren(); $('source').replaceChildren();
  for (const account of accounts) {
    const card = document.createElement('article'); card.className = 'account';
    for (const text of [account.label, account.id]) { const p = document.createElement('p'); p.textContent = text; card.append(p); }
    const balance = document.createElement('span'); balance.className = 'balance';
    balance.textContent = `${account.balance} ${account.currency}`; card.append(balance); $('accounts').append(card);
    const option = document.createElement('option'); option.value = account.id; option.textContent = account.id; $('source').append(option);
  }
  $('history').replaceChildren();
  for (const item of history) {
    const row = document.createElement('tr'); cell(row, `${item.source} → ${item.destination}`);
    cell(row, `${item.amount} USD-DEMO`); cell(row, `${item.note} · ${item.created_at}`); $('history').append(row);
  }
  if (!history.length) { const row = document.createElement('tr'); cell(row, 'Aún no hay transferencias'); $('history').append(row); }
  $('login-panel').hidden = true; $('dashboard').hidden = false;
}
$('login-form').addEventListener('submit', async event => {
  event.preventDefault(); const button = event.submitter; button.disabled = true;
  try { await api('login', {method: 'POST', body: JSON.stringify({username: $('username').value, password: $('password').value})}); $('password').value = ''; await refresh(); message('Sesión de práctica iniciada'); }
  catch (error) { message(error.message); } finally { button.disabled = false; }
});
$('transfer-form').addEventListener('submit', async event => {
  event.preventDefault(); $('transfer-button').disabled = true;
  try {
    const body = Object.fromEntries(['source', 'destination', 'amount', 'note'].map(key => [key, $(key).value]));
    await api('transfers', {method: 'POST', body: JSON.stringify(body)});
    $('amount').value = ''; $('note').value = ''; await refresh(); message('Transferencia simulada completada');
  } catch (error) { message(error.message); } finally { $('transfer-button').disabled = false; }
});
$('logout').addEventListener('click', async () => {
  try { await api('logout', {method:'POST'}); showLogin(); message('Sesión cerrada'); }
  catch (error) { message(error.message); }
});
refresh().catch(error => { showLogin(); if (!error.message.includes('Inicia sesión')) message(error.message); });
