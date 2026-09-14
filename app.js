/* Becca's Closet — a tiny static shop with no backend.
   Saved list: localStorage + the URL hash (#saved=…), so a link IS the list. */
(() => {
  'use strict';

  // ---------- config ----------
  const HER_EMAIL = 'beccapruente@gmail.com';
  const BCC_EMAIL = '';   // optional: an address to quietly copy on every emailed list
  const STORAGE_KEY = 'beccas-closet-saved-v1';

  const OCC_LABEL = { teaching: 'For teaching', dance: 'For dancing', friend: 'With friends', hang: 'Hanging out', dressy: 'Dressy', outdoors: 'Outdoors' };
  const OCC_ORDER = ['teaching', 'dance', 'friend', 'hang', 'dressy', 'outdoors'];
  const COLOR_SWATCH = {
    'Black': '#2b2226', 'Grey': '#9a9598', 'White/Ivory': '#f6f1e6', 'Beige/Tan': '#d9c3a3', 'Brown': '#7a5238',
    'Denim': '#4f6a8f', 'Blue': '#5b7fc4', 'Green': '#6f8f6a', 'Red': '#b8404a', 'Pink': '#e9a3b6', 'Purple': '#8b6aa8',
    'Orange/Rust': '#c96f3e', 'Yellow/Gold': '#e0b84c', 'Multi/Print': 'linear-gradient(135deg,#e9a3b6,#e0b84c,#6f8f6a,#5b7fc4)'
  };
  const COLOR_ORDER = ['Black', 'Grey', 'White/Ivory', 'Beige/Tan', 'Brown', 'Denim', 'Blue', 'Green', 'Red', 'Pink', 'Purple', 'Orange/Rust', 'Yellow/Gold', 'Multi/Print'];
  const CATEGORY_ORDER = ['Dresses', 'Skirts', 'Pants', 'Jeans', 'Shirts & Blouses', 'Tops & Tees', 'Sweaters & Knitwear', 'Jumpsuits & Rompers', 'Jackets & Coats', 'Accessories'];
  const PRICE_BANDS = [
    { key: 'u100', label: 'Under $100', test: p => p < 100 },
    { key: '100-200', label: '$100 – $200', test: p => p >= 100 && p < 200 },
    { key: '200-350', label: '$200 – $350', test: p => p >= 200 && p < 350 },
    { key: '350+', label: '$350 and up', test: p => p >= 350 },
  ];

  const ITEMS = window.CLOSET;
  const byId = new Map(ITEMS.map(i => [i.id, i]));

  // ---------- state ----------
  const state = {
    q: '', sort: 'curated',
    category: new Set(), color: new Set(), brand: new Set(), occasion: new Set(), price: new Set(),
    saved: new Set(), shuffleOrder: null, view: [], modalIndex: -1,
  };

  // ---------- persistence ----------
  function loadSaved() {
    const ids = new Set();
    try { (JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')).forEach(n => byId.has(n) && ids.add(n)); } catch (e) { }
    const m = location.hash.match(/saved=([\d.,]+)/);
    if (m) m[1].split(/[.,]/).map(Number).forEach(n => byId.has(n) && ids.add(n));
    return ids;
  }
  function persist() {
    const ids = [...state.saved];
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(ids)); } catch (e) { }
    const hash = ids.length ? '#saved=' + ids.join('.') : '';
    history.replaceState(null, '', location.pathname + location.search + hash);
  }
  function shareLink() {
    const ids = [...state.saved];
    return location.origin + location.pathname + (ids.length ? '#saved=' + ids.join('.') : '');
  }

  // ---------- helpers ----------
  const $ = s => document.querySelector(s);
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const money = n => n == null ? 'Sold out' : '$' + (Number.isInteger(n) ? n.toLocaleString() : n.toFixed(2));
  const P = n => n == null ? Infinity : n;   // unpriced (sold-out) pieces sort last
  const heartSvg = '<svg><use href="#i-heart"/></svg>';
  let toastTimer;
  function toast(msg) {
    const t = $('#toast'); t.textContent = msg; t.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 1800);
  }
  function searchUrl(site, item) {
    const q = encodeURIComponent(`${item.brand} ${item.name}`);
    return site === 'ebay' ? `https://www.ebay.com/sch/i.html?_nkw=${q}&_sacat=15724`
      : `https://poshmark.com/search?query=${q}&department=Women`;
  }

  // ---------- filtering ----------
  function matches(item) {
    if (state.category.size && !state.category.has(item.category)) return false;
    if (state.color.size && !state.color.has(item.color)) return false;
    if (state.brand.size && !state.brand.has(item.brand)) return false;
    if (state.occasion.size && !item.occasions.some(o => state.occasion.has(o))) return false;
    if (state.price.size && (item.price == null || ![...state.price].some(k => PRICE_BANDS.find(b => b.key === k).test(item.price)))) return false;
    if (state.q) {
      const hay = `${item.brand} ${item.name} ${item.colorDetail || ''} ${item.categoryDetail || ''} ${item.retailer} ${item.color}`.toLowerCase();
      if (!state.q.split(/\s+/).every(w => hay.includes(w))) return false;
    }
    return true;
  }
  function sorted(list) {
    const l = list.slice();
    switch (state.sort) {
      case 'price-asc': l.sort((a, b) => P(a.price) - P(b.price) || a.id - b.id); break;
      case 'price-desc': l.sort((a, b) => P(b.price) - P(a.price) || a.id - b.id); break;
      case 'brand': l.sort((a, b) => a.brand.localeCompare(b.brand) || a.name.localeCompare(b.name)); break;
      case 'shuffle': {
        if (!state.shuffleOrder) reshuffle();
        const pos = state.shuffleOrder; l.sort((a, b) => pos.get(a.id) - pos.get(b.id)); break;
      }
      default: l.sort((a, b) => CATEGORY_ORDER.indexOf(a.category) - CATEGORY_ORDER.indexOf(b.category) || a.id - b.id); break; // curated: dresses first, spreadsheet order within each category
    }
    return l;
  }
  function reshuffle() {
    const ids = ITEMS.map(i => i.id);
    for (let i = ids.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1));[ids[i], ids[j]] = [ids[j], ids[i]]; }
    state.shuffleOrder = new Map(ids.map((id, k) => [id, k]));
  }
  function activeFilterCount() { return state.category.size + state.color.size + state.brand.size + state.occasion.size + state.price.size; }

  // ---------- facets ----------
  function countBy(key, values, getter) {
    // counts respect every OTHER active facet, so numbers stay honest as you refine
    const saved = new Set(state[key]); state[key].clear();
    const pool = ITEMS.filter(matches); state[key] = saved;
    const c = new Map(values.map(v => [v, 0]));
    pool.forEach(it => getter(it).forEach(v => c.has(v) && c.set(v, c.get(v) + 1)));
    return c;
  }
  function renderFacets() {
    const brands = [...new Set(ITEMS.map(i => i.brand))].sort((a, b) => a.localeCompare(b));
    const cCat = countBy('category', CATEGORY_ORDER, i => [i.category]);
    const cCol = countBy('color', COLOR_ORDER, i => [i.color]);
    const cOcc = countBy('occasion', OCC_ORDER, i => i.occasions);
    const cBrand = countBy('brand', brands, i => [i.brand]);
    const cPrice = countBy('price', PRICE_BANDS.map(b => b.key), i => i.price == null ? [] : PRICE_BANDS.filter(b => b.test(i.price)).map(b => b.key));

    const opt = (key, v, label, cnt, extra = '') =>
      `<label class="opt"><input type="checkbox" data-facet="${key}" value="${esc(v)}" ${state[key].has(v) ? 'checked' : ''}><span class="box"></span>${extra}<span class="lbl">${esc(label)}</span><span class="cnt">${cnt}</span></label>`;
    const pill = (key, v, label) =>
      `<label class="pill"><input type="checkbox" data-facet="${key}" value="${esc(v)}" ${state[key].has(v) ? 'checked' : ''}>${esc(label)}</label>`;
    const facet = (title, key, body, open = true) =>
      `<details class="facet" ${open ? 'open' : ''}><summary>${title}${state[key].size ? `<span class="n">${state[key].size}</span>` : ''}</summary><div class="facet-body ${key === 'occasion' || key === 'price' ? 'wrap' : ''}">${body}</div></details>`;

    $('#facets').innerHTML =
      facet('Occasion', 'occasion', OCC_ORDER.map(o => pill('occasion', o, OCC_LABEL[o])).join('')) +
      facet('Category', 'category', CATEGORY_ORDER.map(c => opt('category', c, c, cCat.get(c))).join('')) +
      facet('Color', 'color', COLOR_ORDER.map(c => opt('color', c, c, cCol.get(c), `<span class="sw" style="background:${COLOR_SWATCH[c]}"></span>`)).join('')) +
      facet('Price', 'price', PRICE_BANDS.map(b => pill('price', b.key, b.label)).join('')) +
      facet('Brand', 'brand', `<input class="facet-search" id="brand-q" type="search" placeholder="Find a brand…" autocomplete="off"><div class="brand-list" id="brand-list">${brands.map(b => opt('brand', b, b, cBrand.get(b))).join('')}</div>`, state.brand.size > 0);
  }

  // ---------- grid ----------
  function cardHtml(it) {
    const on = state.saved.has(it.id);
    return `<article class="card" data-id="${it.id}">
      <button class="heart ${on ? 'on' : ''}" type="button" aria-label="${on ? 'Remove from saved' : 'Save'}" aria-pressed="${on}">${heartSvg}</button>
      <div class="frame" data-open="${it.id}"><img loading="lazy" src="${it.img}" alt="${esc(it.name)}" ${it.hi ? '' : 'class="soft"'}></div>
      <div class="meta" data-open="${it.id}">
        <p class="brand">${esc(it.brand)}</p>
        <h3 class="name">${esc(it.name)}</h3>
        <div class="price ${it.price == null ? 'soldout' : ''}">${it.price == null ? 'Sold out · hunt secondhand' : money(it.price)}</div>
      </div></article>`;
  }
  function render() {
    state.view = sorted(ITEMS.filter(matches));
    const n = state.view.length;
    $('#grid').innerHTML = state.view.map(cardHtml).join('');
    $('#empty').hidden = n > 0;
    $('#results-count').innerHTML = n === ITEMS.length ? `All <b>${n}</b> pieces` : `<b>${n}</b> of ${ITEMS.length} pieces`;
    $('#apply-count').textContent = `${n} piece${n === 1 ? '' : 's'}`;
    const fc = activeFilterCount();
    $('#mb-filter-count').textContent = fc ? `· ${fc}` : '';
    renderChips();
    renderFacets();
  }
  function renderChips() {
    const chips = [];
    const add = (key, v, label) => chips.push(`<button class="chip" type="button" data-chip="${key}" data-value="${esc(v)}">${esc(label)} <svg><use href="#i-x"/></svg></button>`);
    state.occasion.forEach(v => add('occasion', v, OCC_LABEL[v]));
    state.category.forEach(v => add('category', v, v));
    state.color.forEach(v => add('color', v, v));
    state.price.forEach(v => add('price', v, PRICE_BANDS.find(b => b.key === v).label));
    state.brand.forEach(v => add('brand', v, v));
    if (state.q) add('q', state.q, `“${state.q}”`);
    $('#chips').innerHTML = chips.join('') + (chips.length > 1 ? `<button class="link" type="button" data-chip="all">Clear all</button>` : '');
  }

  // ---------- saved ----------
  function toggleSaved(id, sourceBtn) {
    const was = state.saved.has(id);
    was ? state.saved.delete(id) : state.saved.add(id);
    persist(); updateSavedUi();
    document.querySelectorAll(`.card[data-id="${id}"] .heart, .modal-heart[data-id="${id}"]`).forEach(b => {
      b.classList.toggle('on', !was); b.setAttribute('aria-pressed', String(!was)); b.setAttribute('aria-label', !was ? 'Remove from saved' : 'Save');
      if (!was) { b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop'); }
    });
    toast(was ? 'Taken out of your saved pieces' : 'Tucked away ♥');
    if ($('#drawer').classList.contains('open')) renderDrawer();
  }
  function updateSavedUi() {
    const n = state.saved.size;
    $('#saved-count').textContent = n; $('#mb-saved-count').textContent = n;
  }
  function savedItems() { return [...state.saved].map(id => byId.get(id)).filter(Boolean); }
  function renderDrawer() {
    const items = savedItems();
    const body = $('#drawer-body'), foot = $('#drawer-foot');
    if (!items.length) {
      body.innerHTML = `<div class="drawer-empty">${heartSvg}<p class="big">Nothing tucked away yet.</p><p>Tap the heart on anything that catches your eye and it will wait for you here.</p></div>`;
      foot.innerHTML = '';
      return;
    }
    body.innerHTML = items.map(it => `<div class="saved-item" data-id="${it.id}">
        <img src="${it.img}" alt="" data-open="${it.id}">
        <div><p class="brand">${esc(it.brand)}</p><div class="nm" data-open="${it.id}">${esc(it.name)}</div><div class="pr">${it.price == null ? 'Sold out' : money(it.price)} · ${esc(it.color)}</div></div>
        <button class="icon-btn rm" type="button" data-remove="${it.id}" aria-label="Remove"><svg width="18" height="18"><use href="#i-x"/></svg></button>
      </div>`).join('');
    const total = items.reduce((s, i) => s + (i.price || 0), 0);
    const unpriced = items.filter(i => i.price == null).length;
    foot.innerHTML = `<div class="total"><span>${items.length} piece${items.length === 1 ? '' : 's'}${unpriced ? ` <small>(${unpriced} unpriced)</small>` : ''}</span><b>${money(total)}</b></div>
      <div class="drawer-actions">
        <a class="btn rose full" id="mail-list" href="${mailtoHref(items, total)}">Email me my list</a>
        <button class="btn" id="copy-link" type="button">Copy share link</button>
        <button class="btn ghost" id="clear-saved" type="button">Clear list</button>
      </div>
      <p class="tiny">Your list is saved in this browser and inside the share link.</p>`;
  }
  function mailtoHref(items, total) {
    const link = shareLink();
    let lines = items.map(i => `♥ ${i.brand} — ${i.name} (${i.color}) — ${money(i.price)}\n   ${i.url}`);
    let body;
    for (; ;) {
      body = `My saved pieces from Becca's Closet:\n\n${lines.join('\n\n')}\n\nTotal: ${money(total)}\n\nOpen the list anytime: ${link}\n`;
      if (encodeURIComponent(body).length < 1800 || lines.length <= 1) break;   // keep the mailto short enough for every mail app
      lines = items.slice(0, Math.max(1, lines.length - 1)).map(i => `♥ ${i.brand} — ${i.name} — ${money(i.price)}`);
      if (lines.length < items.length) lines.push(`…and ${items.length - lines.length} more, all in the link below.`);
    }
    const params = new URLSearchParams({ subject: 'My picks from Becca’s Closet', body });
    if (BCC_EMAIL) params.set('bcc', BCC_EMAIL);
    return `mailto:${HER_EMAIL}?${params.toString().replace(/\+/g, '%20')}`;
  }
  async function copyShareLink() {
    const link = shareLink();
    try { await navigator.clipboard.writeText(link); toast('Link copied'); }
    catch (e) { prompt('Copy this link:', link); }
  }

  // ---------- modal ----------
  function openModal(id) {
    const idx = state.view.findIndex(i => i.id === id);
    state.modalIndex = idx >= 0 ? idx : -1;
    const it = byId.get(id);
    const on = state.saved.has(id);
    $('#modal-inner').innerHTML = `
      <div class="modal-media">
        <img src="${it.img}" alt="${esc(it.name)}">
        <div class="arch"></div>
        <button class="heart modal-heart ${on ? 'on' : ''}" type="button" data-id="${it.id}" aria-pressed="${on}" aria-label="${on ? 'Remove from saved' : 'Save'}">${heartSvg}</button>
        ${state.modalIndex >= 0 && state.view.length > 1 ? `<div class="modal-nav"><button type="button" data-nav="-1" aria-label="Previous"><svg><use href="#i-arrow"/></svg></button><button type="button" data-nav="1" aria-label="Next"><svg><use href="#i-arrow"/></svg></button></div>` : ''}
      </div>
      <div class="modal-body">
        <button class="icon-btn modal-close" type="button" data-close aria-label="Close"><svg width="20" height="20"><use href="#i-x"/></svg></button>
        <p class="brand">${esc(it.brand)}${it.retailer !== it.brand ? ` · at ${esc(it.retailer)}` : ''}</p>
        <h2>${esc(it.name)}</h2>
        <div class="price">${it.price == null ? 'Sold out at ' + esc(it.retailer) + ' · worth a secondhand hunt' : money(it.price)}</div>
        <div class="tags">
          <span class="tag">${esc(it.category)}</span>
          <span class="tag col">${esc(it.colorDetail || it.color)}</span>
          ${it.occasions.map(o => `<span class="tag occ">${OCC_LABEL[o] || o}</span>`).join('')}
        </div>
        ${it.fabric ? `<p class="fabric-line">${esc(it.fabric)}</p>` : ''}
        ${it.desc ? `<div class="about"><h3>About this piece</h3><p>${esc(it.desc)}</p></div>` : ''}
        ${it.details && it.details.length ? `<div class="about"><h3>Cut, fabric &amp; care</h3><ul class="details">${it.details.map(d => `<li>${esc(d)}</li>`).join('')}</ul></div>` : ''}
        ${!it.desc && !(it.details && it.details.length) ? `<p class="lowres-note">${esc(it.retailer)} keeps its details behind a login wall, so the full description lives on their site.</p>` : ''}
        ${it.why ? `<p class="why"><span>Why these occasions</span> ${esc(it.why)}</p>` : ''}
        ${it.categoryDetail && it.categoryDetail !== it.category ? `<p class="detail-row">Listed as <b>${esc(it.categoryDetail)}</b></p>` : ''}
        <div class="links">
          <a href="${esc(it.url)}" target="_blank" rel="noopener"><span>See it at ${esc(it.retailer)} <small>· original listing</small></span><svg><use href="#i-arrow"/></svg></a>
          <a href="${searchUrl('ebay', it)}" target="_blank" rel="noopener"><span>Find it on eBay <small>· search</small></span><svg><use href="#i-arrow"/></svg></a>
          <a href="${searchUrl('posh', it)}" target="_blank" rel="noopener"><span>Find it on Poshmark <small>· search</small></span><svg><use href="#i-arrow"/></svg></a>
        </div>
      </div>`;
    const m = $('#modal');
    if (!m.open) m.showModal();
    m.querySelector('.modal-body').scrollTop = 0;
  }
  function navModal(dir) {
    if (state.modalIndex < 0) return;
    const n = state.view.length;
    const next = state.view[(state.modalIndex + dir + n) % n];
    openModal(next.id);
  }

  // ---------- panels ----------
  function openPanel(which) {
    closePanels();
    $('#scrim').hidden = false;
    $(which).classList.add('open'); $(which).setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    if (which === '#drawer') renderDrawer();
  }
  function closePanels() {
    $('#scrim').hidden = true;
    ['#drawer', '#filters'].forEach(s => { $(s).classList.remove('open'); $(s).setAttribute('aria-hidden', $(s).id === 'filters' ? 'false' : 'true'); });
    document.body.style.overflow = '';
  }

  // ---------- events ----------
  document.addEventListener('click', e => {
    const t = e.target.closest('button, a, .frame, .meta, [data-open]');
    if (!t) return;
    if (t.classList.contains('heart')) { e.preventDefault(); toggleSaved(Number(t.dataset.id || t.closest('.card').dataset.id), t); return; }
    if (t.dataset.open) { openModal(Number(t.dataset.open)); return; }
    if (t.dataset.remove) { toggleSaved(Number(t.dataset.remove)); return; }
    if (t.dataset.nav) { navModal(Number(t.dataset.nav)); return; }
    if (t.hasAttribute('data-close')) { $('#modal').close(); return; }
    if (t.dataset.chip) {
      if (t.dataset.chip === 'all') clearAll();
      else if (t.dataset.chip === 'q') { state.q = ''; $('#q').value = ''; }
      else state[t.dataset.chip].delete(t.dataset.value);
      render(); return;
    }
    switch (t.id) {
      case 'open-saved': case 'mb-saved': openPanel('#drawer'); break;
      case 'mb-filters': openPanel('#filters'); break;
      case 'close-drawer': case 'close-filters': case 'apply-filters': closePanels(); break;
      case 'surprise': case 'mb-surprise': reshuffle(); state.sort = 'shuffle'; $('#sort').value = 'shuffle'; render(); window.scrollTo({ top: $('#topbar').offsetTop, behavior: 'smooth' }); toast('Shuffled ✨'); break;
      case 'clear-all': case 'empty-clear': clearAll(); render(); break;
      case 'copy-link': copyShareLink(); break;
      case 'clear-saved': if (confirm('Clear your whole saved list?')) { state.saved.clear(); persist(); updateSavedUi(); render(); renderDrawer(); } break;
      case 'mail-list': setTimeout(() => toast('Opening your mail app…'), 50); break;
    }
  });
  $('#scrim').addEventListener('click', closePanels);
  $('#facets').addEventListener('change', e => {
    const cb = e.target; if (!cb.dataset.facet) return;
    cb.checked ? state[cb.dataset.facet].add(cb.value) : state[cb.dataset.facet].delete(cb.value);
    const bq = $('#brand-q') ? $('#brand-q').value : '';
    render();
    if (bq) { $('#brand-q').value = bq; filterBrandList(bq); }
  });
  $('#facets').addEventListener('input', e => { if (e.target.id === 'brand-q') filterBrandList(e.target.value); });
  function filterBrandList(q) {
    q = q.trim().toLowerCase();
    $('#brand-list').querySelectorAll('.opt').forEach(o => { o.style.display = !q || o.textContent.toLowerCase().includes(q) ? '' : 'none'; });
  }
  let qTimer;
  $('#q').addEventListener('input', e => { clearTimeout(qTimer); qTimer = setTimeout(() => { state.q = e.target.value.trim().toLowerCase(); render(); }, 120); });
  $('#sort').addEventListener('change', e => { state.sort = e.target.value; if (state.sort === 'shuffle') reshuffle(); render(); });
  document.addEventListener('keydown', e => {
    if ($('#modal').open) { if (e.key === 'ArrowRight') navModal(1); if (e.key === 'ArrowLeft') navModal(-1); return; }
    if (e.key === 'Escape') closePanels();
  });
  $('#modal').addEventListener('click', e => { if (e.target === e.currentTarget) e.currentTarget.close(); });
  window.addEventListener('hashchange', () => { loadSaved().forEach(id => state.saved.add(id)); persist(); updateSavedUi(); render(); });
  function clearAll() { ['category', 'color', 'brand', 'occasion', 'price'].forEach(k => state[k].clear()); state.q = ''; $('#q').value = ''; }

  // ---------- go ----------
  state.saved = loadSaved(); persist();
  $('#hero-count').textContent = ITEMS.length;
  updateSavedUi();
  render();
})();
