/*
 * CZU quiz engine – obecný "Moodle-like" trenažér, nezávislý na předmětu.
 *
 * Pipeline:  generator(seed) → render → (časovač, autosave) → grade → review → storage
 *
 * Formát otázky (vrací generátor):
 *   { id, title, points, prompt (HTML), kind: 'inline' | 'multi', explain (HTML),
 *     rows:    [[token…]…]  pro 'inline'; token = HTML string | {sel:[…], ans: idx} | {num:true, ans: n}
 *     options: [HTML…], answer: [bool…]  pro 'multi' }
 *
 * Hodnocení jako v Moodlu:
 *   inline: body × (správné rozbalovačky / všechny)
 *   multi:  body × max(0, (správně zaškrtnuté − špatně zaškrtnuté) / počet správných)
 *
 * Úložiště: localStorage (rozpracovaný pokus + historie). Pro budoucí přihlášení
 * stačí doplnit CONFIG.saveUrl – engine pak pokus po odeslání pošle i na server.
 */
(function () {
  'use strict';

  const root = document.getElementById('czu-app');
  if (!root) return;
  const CONFIG = {
    subject: root.dataset.subject,
    generator: root.dataset.generator,
    seed: parseInt(root.dataset.seed, 10),
    title: root.dataset.title,
    backUrl: root.dataset.backUrl,
    nextUrl: root.dataset.nextUrl,
    saveUrl: root.dataset.saveUrl || null, // budoucí: POST pokusu do Djanga (přihlášení studenti)
  };
  const test = window.CZU_GENERATORS[CONFIG.generator](CONFIG.seed);
  const QS = test.questions;
  const MAX = QS.reduce((s, q) => s + q.points, 0);
  const LIMIT_MS = test.timeLimitMin * 60 * 1000;

  // ---------- storage (vše v try/catch – privátní okno apod.) ----------
  const K_CUR = 'czu.' + CONFIG.subject + '.' + CONFIG.seed + '.current';
  const K_HIST = 'czu.' + CONFIG.subject + '.attempts';
  const load = (k, d) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } };
  const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* ignore */ } };
  const del = (k) => { try { localStorage.removeItem(k); } catch (e) { /* ignore */ } };

  const fmtNum = (x) => x.toFixed(2).replace('.', ',');
  const fmtDate = (ts) => new Date(ts).toLocaleString('cs-CZ', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  const fmtDur = (ms) => { const s = Math.round(ms / 1000); return Math.floor(s / 60) + ' min. ' + (s % 60) + ' sekund'; };

  let state = null;   // { start, answers: {qid: [...]}} během pokusu
  let timerId = null;

  // ---------- INTRO (jako stránka testu v Moodlu) ----------
  function renderIntro() {
    const hist = load(K_HIST, []).filter((a) => a.seed === CONFIG.seed);
    const best = hist.reduce((m, a) => Math.max(m, a.score), -1);
    const cur = load(K_CUR, null);
    const running = cur && Date.now() - cur.start < LIMIT_MS;
    root.innerHTML =
      '<div class="czu-intro">' +
      '<h1 class="czu-h1">' + CONFIG.title + '</h1>' +
      '<div class="czu-infobox"><p>Test sestavený podle cvičného testu z Moodlu: ' + QS.length + ' úloh, ' + MAX + ' bodů. Úlohy se generují podle čísla testu, takže tento test vyjde všem stejně.</p></div>' +
      '<button class="czu-btn" id="czu-start">' + (running ? 'Pokračovat v pokusu' : (hist.length ? 'Začít další pokus' : 'Začít pokus')) + '</button>' +
      '<p class="czu-meta">Časový limit: ' + test.timeLimitMin + ' min.</p>' +
      '<p class="czu-meta">Metoda hodnocení: Nejvyšší známka</p>' +
      (best >= 0 ? '<h2 class="czu-h2">Nejvyšší známka: ' + fmtNum(best) + ' / ' + fmtNum(MAX) + '.</h2>' : '') +
      (hist.length ? '<h2 class="czu-h2">Vaše pokusy</h2><div class="czu-attempts">' + hist.slice().reverse().map((a, i) => attemptCard(a, hist.length - i)).join('') + '</div>' : '') +
      '<p class="czu-small">Pokusy se ukládají jen ve vašem prohlížeči.</p>' +
      '</div>';
    document.getElementById('czu-start').onclick = () => startAttempt(running ? cur : null);
  }
  function attemptCard(a, n) {
    return '<div class="czu-card"><h3>Pokus ' + n + '</h3><table>' +
      '<tr><th>Stav</th><td>Dokončeno</td></tr>' +
      '<tr><th>Zahájení</th><td>' + fmtDate(a.start) + '</td></tr>' +
      '<tr><th>Dokončeno</th><td>' + fmtDate(a.end) + '</td></tr>' +
      '<tr><th>Trvání</th><td>' + fmtDur(a.end - a.start) + '</td></tr>' +
      '<tr><th>Známka</th><td><b>' + fmtNum(a.score) + '</b> z možných ' + fmtNum(MAX) + ' (' + fmtNum(100 * a.score / MAX) + '%)</td></tr>' +
      '</table></div>';
  }

  const allTokens = (q) => (q.table ? q.table.rows.flat() : []).concat(q.rows || []).flat().filter((t) => typeof t === 'object');

  // ---------- POKUS ----------
  function emptyAnswers() {
    const a = {};
    QS.forEach((q) => {
      a[q.id] = q.kind === 'multi' ? q.options.map(() => false) : allTokens(q).map(() => '');
    });
    return a;
  }
  function startAttempt(resume) {
    state = resume || { start: Date.now(), answers: emptyAnswers() };
    save(K_CUR, state);
    renderQuiz(false);
    tick();
    timerId = setInterval(tick, 1000);
    window.scrollTo(0, 0);
  }

  function renderQuiz(review, result) {
    const nav = QS.map((q, i) => {
      let cls = 'czu-navq';
      if (review) { const r = result.per[i]; cls += r >= q.points - 1e-9 ? ' ok' : r > 0 ? ' part' : ' bad'; }
      return '<a href="#' + q.id + '" class="' + cls + '" data-q="' + q.id + '">' + (i + 1) + '</a>';
    }).join('');
    let html = '';
    if (review) {
      html += '<div class="czu-summary"><table>' +
        '<tr><th>Zahájení</th><td>' + fmtDate(result.start) + '</td></tr>' +
        '<tr><th>Stav</th><td>Dokončeno' + (result.timeout ? ' (vypršel čas)' : '') + '</td></tr>' +
        '<tr><th>Dokončeno</th><td>' + fmtDate(result.end) + '</td></tr>' +
        '<tr><th>Trvání</th><td>' + fmtDur(result.end - result.start) + '</td></tr>' +
        '<tr><th>Známka</th><td><b>' + fmtNum(result.score) + '</b> z možných ' + fmtNum(MAX) + ' (<b>' + fmtNum(100 * result.score / MAX) + '%</b>)</td></tr>' +
        '</table><div class="czu-bar"><span style="width:' + (100 * result.score / MAX).toFixed(1) + '%"></span></div>' +
        '<div class="czu-actions"><button class="czu-btn" id="czu-again">Zkusit znovu</button>' +
        (CONFIG.nextUrl ? '<a class="czu-btn ghost" href="' + CONFIG.nextUrl + '">Další test →</a>' : '') +
        '<a class="czu-btn ghost" href="' + CONFIG.backUrl + '">Přehled testů</a></div></div>';
    }
    html += QS.map((q, i) => renderQuestion(q, i, review, review ? result.per[i] : null)).join('');
    if (!review) html += '<div class="czu-finish"><button class="czu-btn" id="czu-submit-bottom">Odeslat vše a ukončit</button></div>';

    root.innerHTML =
      '<div class="czu-layout">' +
      '<aside class="czu-side"><div class="czu-sidebox">' +
      '<div class="czu-sidetitle">Navigace v testu</div><div class="czu-navgrid">' + nav + '</div>' +
      (review ? '' : '<div id="czu-timer" class="czu-timer">--:--</div><button class="czu-btn small" id="czu-submit">Ukončit pokus…</button>') +
      '</div></aside>' +
      '<div class="czu-main"><h1 class="czu-h1">' + CONFIG.title + (review ? ' – náhled' : '') + '</h1>' + html + '</div></div>' +
      '<div id="czu-modal" class="czu-modal hidden"></div>';

    if (review) {
      document.getElementById('czu-again').onclick = () => { state = null; startAttempt(null); };
      root.querySelectorAll('input, select').forEach((el) => { el.disabled = true; });
    } else {
      root.querySelectorAll('select, input').forEach((el) => {
        el.addEventListener('change', onInput);
        if (el.type === 'number') el.addEventListener('input', onInput);
      });
      document.getElementById('czu-submit').onclick = confirmSubmit;
      document.getElementById('czu-submit-bottom').onclick = confirmSubmit;
      updateNav();
    }
  }

  function renderQuestion(q, i, review, got) {
    const ans = state.answers[q.id];
    let body = '';
    if (q.kind === 'multi') {
      body = '<div class="czu-opts">' + q.options.map((o, k) => {
        const checked = ans[k] ? ' checked' : '';
        let mark = '';
        if (review) {
          if (q.answer[k] && ans[k]) mark = '<span class="mk ok">✓</span>';
          else if (!q.answer[k] && ans[k]) mark = '<span class="mk bad">✗</span>';
          else if (q.answer[k] && !ans[k]) mark = '<span class="mk miss">← mělo být zaškrtnuto</span>';
        }
        const cls = review ? (q.answer[k] ? ' correct' : ans[k] ? ' wrong' : '') : '';
        return '<label class="czu-opt' + cls + '"><input type="checkbox" data-q="' + q.id + '" data-k="' + k + '"' + checked + '> <span class="lt">' + 'abcdefghijklmnop'[k] + '.</span> ' + o + mark + '</label>';
      }).join('') + '</div>';
    } else {
      let k = 0;
      const tok = (t) => {
        if (typeof t === 'string') return '<span class="tok">' + t + '</span>';
        const idx = k++;
        const v = ans[idx];
        if (t.sel) {
          const ok = review && String(v) === String(t.ans);
          const opts = '<option value="">' + (t.sel.length <= 2 && t.sel[0].length <= 1 ? '–' : 'Vyberte…') + '</option>' + t.sel.map((s, j) => '<option value="' + j + '"' + (String(v) === String(j) ? ' selected' : '') + '>' + s + '</option>').join('');
          return '<span class="selwrap' + (review ? (ok ? ' ok' : ' bad') : '') + '"><select data-q="' + q.id + '" data-k="' + idx + '">' + opts + '</select>' +
            (review ? (ok ? '<span class="mk ok">✓</span>' : '<span class="mk bad">✗ ' + t.sel[t.ans] + '</span>') : '') + '</span>';
        }
        const ok = review && v !== '' && Number(v) === t.ans;
        return '<span class="selwrap' + (review ? (ok ? ' ok' : ' bad') : '') + '"><input type="number" inputmode="numeric" data-q="' + q.id + '" data-k="' + idx + '" value="' + (v === '' ? '' : v) + '">' +
          (review ? (ok ? '<span class="mk ok">✓</span>' : '<span class="mk bad">✗ ' + t.ans + '</span>') : '') + '</span>';
      };
      if (q.table) {
        body += '<div class="czu-ttwrap"><table class="czu-tt"><thead><tr>' + q.table.head.map((h) => '<th>' + h + '</th>').join('') + '</tr></thead><tbody>' +
          q.table.rows.map((row) => '<tr>' + row.map((t) => '<td>' + tok(t) + '</td>').join('') + '</tr>').join('') + '</tbody></table></div>';
      }
      body += '<div class="czu-rows">' + (q.rows || []).map((row) => '<div class="czu-row">' + row.map(tok).join(' ') + '</div>').join('') + '</div>';
    }
    const info = review
      ? '<div class="czu-qstate ' + (got >= q.points - 1e-9 ? 'ok' : got > 0 ? 'part' : 'bad') + '">' + (got >= q.points - 1e-9 ? 'Správně' : got > 0 ? 'Částečně správně' : 'Nesprávně') + '</div><div>Počet bodů: ' + fmtNum(got) + ' z ' + fmtNum(q.points) + '</div>'
      : '<div class="czu-qstate" data-state="' + q.id + '">Dosud nezodpovězeno</div><div>Počet bodů z ' + fmtNum(q.points) + '</div>';
    return '<section class="czu-q" id="' + q.id + '">' +
      '<div class="czu-qinfo"><div class="czu-qno">Úloha <b>' + (i + 1) + '</b></div>' + info + '</div>' +
      '<div class="czu-qbody"><div class="czu-qtitle">' + q.title + '</div><div class="czu-prompt">' + q.prompt + '</div>' + body +
      (review ? '<details class="czu-explain" open><summary>Řešení a postup</summary>' + q.explain + '</details>' : '') +
      '</div></section>';
  }

  function onInput(e) {
    const el = e.target, q = el.dataset.q, k = +el.dataset.k;
    state.answers[q][k] = el.type === 'checkbox' ? el.checked : el.value;
    save(K_CUR, state);
    updateNav();
  }
  const answeredCount = (q) => state.answers[q.id].filter((v) => v !== '' && v !== false).length;
  function updateNav() {
    QS.forEach((q) => {
      const n = answeredCount(q), total = state.answers[q.id].length;
      const navEl = root.querySelector('.czu-navq[data-q="' + q.id + '"]');
      const st = root.querySelector('[data-state="' + q.id + '"]');
      const done = q.kind === 'multi' ? n > 0 : n === total;
      if (navEl) navEl.classList.toggle('answered', n > 0);
      if (st) st.textContent = done ? 'Zodpovězeno' : n > 0 ? 'Rozpracováno' : 'Dosud nezodpovězeno';
    });
  }

  function tick() {
    const left = LIMIT_MS - (Date.now() - state.start);
    const el = document.getElementById('czu-timer');
    if (left <= 0) { submit(true); return; }
    if (el) {
      const s = Math.ceil(left / 1000);
      el.textContent = 'Zbývající čas ' + Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
      el.classList.toggle('warn', s <= 300);
    }
  }

  function confirmSubmit() {
    const unanswered = QS.filter((q) => answeredCount(q) === 0).length;
    const m = document.getElementById('czu-modal');
    m.innerHTML = '<div class="czu-modalbox"><h3>Odeslat vše a ukončit?</h3>' +
      '<p>Jakmile test odešlete, nebudete už moci změnit své odpovědi.</p>' +
      (unanswered ? '<p class="warn">Nezodpovězené úlohy: ' + unanswered + '</p>' : '') +
      '<div class="czu-actions"><button class="czu-btn" id="czu-yes">Odeslat vše a ukončit</button><button class="czu-btn ghost" id="czu-no">Zpět k testu</button></div></div>';
    m.classList.remove('hidden');
    document.getElementById('czu-yes').onclick = () => submit(false);
    document.getElementById('czu-no').onclick = () => m.classList.add('hidden');
  }

  // ---------- HODNOCENÍ ----------
  function gradeQuestion(q, ans) {
    if (q.kind === 'multi') {
      const k = q.answer.filter(Boolean).length;
      let hit = 0, wrong = 0;
      q.answer.forEach((c, i) => { if (ans[i]) { if (c) hit++; else wrong++; } });
      return q.points * Math.max(0, (hit - wrong) / k);
    }
    const toks = allTokens(q);
    const good = toks.filter((t, i) => ans[i] !== '' && (t.sel ? String(ans[i]) === String(t.ans) : Number(ans[i]) === t.ans)).length;
    return q.points * good / toks.length;
  }

  function submit(timeout) {
    clearInterval(timerId);
    const end = Math.min(Date.now(), state.start + LIMIT_MS);
    const per = QS.map((q) => Math.round(gradeQuestion(q, state.answers[q.id]) * 100) / 100);
    const score = Math.round(per.reduce((a, b) => a + b, 0) * 100) / 100;
    const result = { seed: CONFIG.seed, start: state.start, end, score, max: MAX, per, timeout };
    const hist = load(K_HIST, []);
    hist.push({ seed: CONFIG.seed, start: state.start, end, score, max: MAX });
    save(K_HIST, hist.slice(-200));
    del(K_CUR);
    if (CONFIG.saveUrl) { // připraveno pro přihlášené studenty
      try {
        fetch(CONFIG.saveUrl, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '' }, body: JSON.stringify({ subject: CONFIG.subject, ...result, answers: state.answers }) });
      } catch (e) { /* offline – nevadí, zůstává lokálně */ }
    }
    renderQuiz(true, result);
    window.scrollTo(0, 0);
  }

  renderIntro();
})();
