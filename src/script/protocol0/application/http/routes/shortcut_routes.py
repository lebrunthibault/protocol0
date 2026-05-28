"""Routes du gestionnaire de raccourcis (catalogue + config des bindings + UI).

- GET /actions       : catalogue des actions assignables (M2, cf. ActionCatalog).
- GET /shortcuts     : page HTML/JS de config (M3).
- GET /shortcuts/list: bindings courants en JSON (M3).
- GET /shortcuts/add : ajoute/remplace un binding (M3).

Tout est GET-only (le Router ne fait que do_GET) : la mutation de /shortcuts/add
passe par les query params, dont `params` est un blob JSON url-encodé. Acceptable
car le serveur n'écoute que sur 127.0.0.1 (cf. risques §4, POST = suivi différé).
"""
import json
from typing import Any, Dict, List

from protocol0.application.http.ActionCatalog import get_catalog
from protocol0.application.http.HttpServer import get_container
from protocol0.application.http.Router import route
from protocol0.domain.shortcut.Binding import Binding
from protocol0.domain.shortcut.ShortcutConfigService import ShortcutConfigService


@route("GET", "/shortcuts")
def shortcuts_page() -> str:
    """Render the HTML page to view and configure keyboard shortcuts."""
    return _PAGE


@route("GET", "/actions")
def actions() -> List[Dict[str, Any]]:
    """List the actions assignable to a keyboard shortcut, with their params."""
    return get_catalog()


@route("GET", "/shortcuts/list")
def shortcuts_list() -> List[Dict[str, Any]]:
    """List the configured shortcut bindings as JSON."""
    return [b.to_dict() for b in get_container().get(ShortcutConfigService).list()]


@route("GET", "/shortcuts/add")
def shortcuts_add(combo: str, action: str, params: str = "{}") -> Dict[str, Any]:
    """Add or replace the binding for a combo. `params` is a URL-encoded JSON blob."""
    try:
        parsed = json.loads(params)
    except ValueError as e:
        raise ValueError("params is not valid JSON: %s" % e)
    if not isinstance(parsed, dict):
        raise ValueError("params must be a JSON object")
    binding = Binding(combo=combo, action=action, params=parsed)
    get_container().get(ShortcutConfigService).upsert(binding)
    return binding.to_dict()


# Page HTML/JS inline (zéro build, fetch vanilla — cf. décision §6). Le JS
# canonicalise la combo à partir de `e.code` (position physique) pour produire
# EXACTEMENT la même chaîne que le détecteur (qui lit le `vk`) : modificateurs
# dans l'ordre ctrl, alt, shift, win, puis la touche, minuscules, joints par '+'.
# Namespace : a-z, 0-9, f1-f12 (idem detector._key_name). Attention : ne pas
# passer cette string dans str.format / % — le JS contient des { } littéraux.
_PAGE = """<!doctype html><html><head><meta charset='utf-8'>
<title>Protocol 0 — Shortcuts</title>
<style>
body{font-family:sans-serif;max-width:720px;margin:2em auto;padding:0 1em}
table{border-collapse:collapse;width:100%;margin-top:1em}
th,td{border-bottom:1px solid #ddd;padding:.4em .6em;text-align:left}
th{background:#f4f4f4}
code,kbd{font-family:monospace}
#capture{border:1px solid #aaa;border-radius:4px;padding:.5em .8em;min-width:8em;
  display:inline-block;background:#fafafa;cursor:text}
#capture:focus{outline:2px solid #4a90d9;background:#fff}
label{display:block;margin:.6em 0 .2em}
#msg{margin-top:.6em;min-height:1.2em}
.err{color:#b00}
.ok{color:#070}
button{padding:.4em 1em}
</style></head><body>
<h1>Keyboard shortcuts</h1>

<h2>Add a shortcut</h2>
<label for='action'>Action</label>
<select id='action'></select>

<div id='params'></div>

<label>Combo (focus the box, then press the keys)</label>
<span id='capture' tabindex='0'>click & press…</span>
<button id='clear' type='button'>clear</button>

<p><button id='add' type='button'>Add binding</button></p>
<div id='msg'></div>

<h2>Current bindings</h2>
<table><thead><tr><th>Combo</th><th>Action</th><th>Params</th></tr></thead>
<tbody id='bindings'></tbody></table>

<script>
const MOD_ORDER = ['ctrl','alt','shift','win'];
let actions = [];
let combo = '';

// e.code (physical position) -> canonical key, matching the detector's vk map.
function keyName(code){
  let m;
  if((m = code.match(/^Key([A-Z])$/))) return m[1].toLowerCase();
  if((m = code.match(/^Digit([0-9])$/))) return m[1];
  if((m = code.match(/^Numpad([0-9])$/))) return m[1];
  if((m = code.match(/^F([0-9]{1,2})$/))){ const n = +m[1]; if(n>=1 && n<=12) return 'f'+n; }
  return null;
}

function isModifier(code){
  return /^(Control|Alt|Shift|Meta|OS)/.test(code);
}

function buildCombo(e){
  const mods = [];
  if(e.ctrlKey) mods.push('ctrl');
  if(e.altKey) mods.push('alt');
  if(e.shiftKey) mods.push('shift');
  if(e.metaKey) mods.push('win');
  const key = keyName(e.code);
  if(key === null) return null;
  const ordered = MOD_ORDER.filter(m => mods.includes(m));
  return ordered.concat([key]).join('+');
}

const captureEl = document.getElementById('capture');
captureEl.addEventListener('keydown', e => {
  e.preventDefault();
  e.stopPropagation();
  if(isModifier(e.code)){ captureEl.textContent = 'press a key…'; return; }
  const c = buildCombo(e);
  if(c === null){ captureEl.textContent = 'unsupported key'; return; }
  combo = c;
  captureEl.textContent = c;
});
document.getElementById('clear').addEventListener('click', () => {
  combo = ''; captureEl.textContent = 'click & press…';
});

function renderParams(){
  const sel = document.getElementById('action').value;
  const action = actions.find(a => a.name === sel);
  const box = document.getElementById('params');
  box.innerHTML = '';
  if(!action) return;
  for(const p of action.params){
    const label = document.createElement('label');
    label.textContent = p.name + (p.required ? '' : ' (optional)');
    const input = document.createElement('input');
    input.dataset.param = p.name;
    input.id = 'param-' + p.name;
    box.appendChild(label);
    box.appendChild(input);
  }
}

function collectParams(){
  const out = {};
  for(const input of document.querySelectorAll('#params input')){
    const v = input.value.trim();
    if(v !== '') out[input.dataset.param] = v;
  }
  return out;
}

function msg(text, cls){
  const el = document.getElementById('msg');
  el.textContent = text;
  el.className = cls || '';
}

async function loadActions(){
  actions = await (await fetch('/actions')).json();
  const sel = document.getElementById('action');
  sel.innerHTML = '';
  for(const a of actions){
    const opt = document.createElement('option');
    opt.value = a.name;
    opt.textContent = a.label + ' (' + a.name + ')';
    sel.appendChild(opt);
  }
  renderParams();
}

async function loadBindings(){
  const list = await (await fetch('/shortcuts/list')).json();
  const tbody = document.getElementById('bindings');
  tbody.innerHTML = '';
  for(const b of list){
    const tr = document.createElement('tr');
    const cells = [b.combo, b.action, JSON.stringify(b.params)];
    for(const c of cells){
      const td = document.createElement('td');
      td.textContent = c;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
}

async function addBinding(){
  if(!combo){ msg('Capture a combo first.', 'err'); return; }
  const action = document.getElementById('action').value;
  const params = collectParams();
  const qs = new URLSearchParams({combo, action, params: JSON.stringify(params)});
  const r = await fetch('/shortcuts/add?' + qs.toString());
  if(!r.ok){ msg('Error: ' + (await r.text()), 'err'); return; }
  msg('Added ' + combo + ' \\u2192 ' + action, 'ok');
  await loadBindings();
}

document.getElementById('action').addEventListener('change', renderParams);
document.getElementById('add').addEventListener('click', addBinding);
loadActions();
loadBindings();
</script>
</body></html>"""
