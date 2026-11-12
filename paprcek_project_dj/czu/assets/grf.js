/*
 * Generátor cvičných testů – Matematická logika a grafy, 2. zápočet (grafy), ČZU.
 *
 * Struktura 1:1 podle cvičného testu v Moodlu: 6 úloh, 2 + 6 + 4 + 6 + 10 + 10 = 38 bodů.
 *   1. Skóre grafu (Havel–Hakimi)            2 b
 *   2. Izomorfismus orientovaných grafů      6 b
 *   3. Eulerovský graf (tah jedním tahem)    4 b
 *   4. Prefixová notace → hodnota, postfix   6 b
 *   5. Maximální tok a minimální řezy       10 b
 *   6. Minimální kostra                     10 b
 *
 * Test je deterministický podle čísla (seed) a všechna řešení se POČÍTAJÍ.
 * Generátor bere jen zadání, která mají jednoznačnou odpověď
 * (jediný maximální tok, jediná minimální kostra).
 */
(function () {
  'use strict';

  // ---------- RNG a pomocníci ----------
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const ri = (r, a, b) => a + Math.floor(r() * (b - a + 1));
  const pick = (r, arr) => arr[Math.floor(r() * arr.length)];
  function shuffle(r, arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  }
  const num = (x) => (x < 0 ? '−' + (-x) : String(x));
  const vi = (s) => '<i>' + s + '</i>';
  const tuple = (arr) => '<span class="fm">(' + arr.join(', ') + ')</span>';

  // ---------- SVG kreslení grafů ----------
  let SVGID = 0;
  /*
   * nodes: [{x, y, label}], edges: [{u, v, w, dir, t, side, hl}]
   * w = popisek hrany, t = poloha popisku podél hrany (0..1), side = ±1 strana popisku
   */
  function svgGraph(o) {
    const id = 'czug' + (++SVGID) + '-' + Math.floor(Math.random() * 1e6);
    const R = o.r || 14, pad = R + 8;
    const xs = o.nodes.map((n) => n.x), ys = o.nodes.map((n) => n.y);
    const x0 = Math.min(...xs) - pad, y0 = Math.min(...ys) - pad;
    const W = Math.max(...xs) - x0 + pad, H = Math.max(...ys) - y0 + pad;
    const scale = o.scale || 1;
    let s = '<svg class="czu-svg' + (o.cls ? ' ' + o.cls : '') + '" viewBox="' + x0 + ' ' + y0 + ' ' + W + ' ' + H + '" width="' + Math.round(W * scale) + '" height="' + Math.round(H * scale) + '" role="img">' +
      '<defs><marker id="' + id + '" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 L3,5 z" fill="currentColor"/></marker></defs>';
    o.edges.forEach((e) => {
      const a = o.nodes[e.u], b = o.nodes[e.v];
      const dx = b.x - a.x, dy = b.y - a.y, L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L;
      const x1 = a.x + ux * R, y1 = a.y + uy * R, x2 = b.x - ux * (R + 1), y2 = b.y - uy * (R + 1);
      s += '<line x1="' + x1.toFixed(1) + '" y1="' + y1.toFixed(1) + '" x2="' + x2.toFixed(1) + '" y2="' + y2.toFixed(1) + '"' +
        (e.hl ? ' class="hl"' : e.dim ? ' class="dim"' : '') + (e.dir ? ' marker-end="url(#' + id + ')"' : '') + '/>';
      if (e.w !== undefined && e.w !== null) {
        const t = e.t === undefined ? 0.5 : e.t, side = e.side || 1, off = o.off || 10;
        const mx = a.x + dx * t + uy * off * side, my = a.y + dy * t - ux * off * side;
        s += '<text class="w' + (e.hl ? ' hl' : '') + '" x="' + mx.toFixed(1) + '" y="' + my.toFixed(1) + '">' + e.w + '</text>';
      }
    });
    o.nodes.forEach((n) => {
      s += '<circle cx="' + n.x + '" cy="' + n.y + '" r="' + R + '"' + (n.hl ? ' class="hl"' : '') + '/>' +
        (n.label !== undefined ? '<text class="n" x="' + n.x + '" y="' + n.y + '">' + n.label + '</text>' : '');
    });
    return s + '</svg>';
  }

  // =====================================================================
  // 1. SKÓRE GRAFU (2 b)
  // =====================================================================
  function havelHakimi(seq) {
    const steps = [];
    let s = seq.slice().sort((a, b) => b - a);
    steps.push(s.slice());
    for (;;) {
      if (s.every((x) => x === 0)) return { ok: true, steps };
      const d = s.shift();
      if (d > s.length) return { ok: false, steps, why: 'první číslo ' + d + ' je větší než počet zbývajících vrcholů (' + s.length + '), takže nelze odebrat ' + d + ' hran' };
      for (let i = 0; i < d; i++) s[i]--;
      if (s.some((x) => x < 0)) { steps.push(s.slice()); return { ok: false, steps, why: 'vyšlo záporné číslo' }; }
      s.sort((a, b) => b - a);
      steps.push(s.slice());
    }
  }
  function randomDegrees(r, n) {
    const deg = Array(n).fill(0);
    const p = 0.3 + r() * 0.45;
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (r() < p) { deg[i]++; deg[j]++; }
    return deg;
  }
  function qScore(r) {
    const want = r() < 0.5; // rozhodnuto předem, ať jsou Pravda/Nepravda vyrovnané
    for (let attempt = 0; attempt < 2000; attempt++) {
      const n = ri(r, 5, 8);
      let seq = randomDegrees(r, n);
      if (seq.some((d) => d === 0)) continue;
      if (!want) {
        const mode = r();
        if (mode < 0.2) { // lichý součet
          const i = ri(r, 0, n - 1);
          seq[i] += seq[i] < n - 1 ? 1 : -1;
        } else { // přesun jedné hrany mezi vrcholy (součet zůstává sudý)
          const i = ri(r, 0, n - 1), j = ri(r, 0, n - 1);
          if (i === j) continue;
          seq[i] += 1; seq[j] -= 1;
          if (mode > 0.8) { const k = ri(r, 0, n - 1); if (k !== i && k !== j) { seq[k] += 1; seq[j] -= 1; } }
        }
        if (seq.some((d) => d < 1)) continue;
      }
      const sum = seq.reduce((a, b) => a + b, 0);
      const hh = sum % 2 === 0 ? havelHakimi(seq) : null;
      const ok = !!(hh && hh.ok);
      if (ok !== want) continue;
      const shown = r() < 0.7 ? seq.slice().sort((a, b) => a - b) : seq.slice().sort((a, b) => b - a);
      let explain = '<p>Součet stupňů = ' + shown.join(' + ') + ' = <b>' + sum + '</b>' +
        (sum % 2 ? ', <b class="bad">je lichý</b>. Podle principu sudosti (každá hrana přispívá ke dvěma vrcholům) musí být součet stupňů sudý, takže takový graf <b>neexistuje</b>.</p>' : ', je sudý, takže to rozhodne Havel–Hakimi.</p>');
      if (hh) {
        explain += '<p>Havel–Hakimi: posloupnost seřadíme sestupně, odebereme největší číslo <i>d</i> a od dalších <i>d</i> čísel odečteme 1. Opakujeme.</p><ol class="ex-list">' +
          hh.steps.map((s) => '<li>' + tuple(s) + '</li>').join('') + '</ol>' +
          (hh.ok ? '<p>Došli jsme k samým nulám, takže prostý graf se skóre ' + tuple(shown) + ' <b class="ok">existuje</b>.</p>'
            : '<p>Postup se zastavil: ' + hh.why + '. Prostý graf proto <b class="bad">neexistuje</b>.</p>');
      }
      return {
        title: 'Skóre grafu', points: 2, kind: 'inline',
        prompt: 'Rozhodněte, zda existuje prostý graf se skóre ' + tuple(shown) + '.',
        rows: [[{ radio: ['Pravda', 'Nepravda'], ans: ok ? 0 : 1, vertical: true }]],
        explain,
      };
    }
  }

  // =====================================================================
  // 2. IZOMORFISMUS ORIENTOVANÝCH GRAFŮ (6 b)
  // =====================================================================
  const POS5 = [{ x: 55, y: 0 }, { x: 165, y: 0 }, { x: 215, y: 98 }, { x: 110, y: 172 }, { x: 0, y: 98 }];
  const PERMS5 = (() => {
    const out = [];
    const rec = (p, rest) => { if (!rest.length) { out.push(p); return; } rest.forEach((x, i) => rec(p.concat(x), rest.slice(0, i).concat(rest.slice(i + 1)))); };
    rec([], [0, 1, 2, 3, 4]);
    return out;
  })();
  const adj = (edges, n) => { const A = Array.from({ length: n }, () => Array(n).fill(0)); edges.forEach(([u, v]) => { A[u][v] = 1; }); return A; };
  function isoPerm(E1, E2) {
    if (E1.length !== E2.length) return null;
    const B = adj(E2, 5);
    for (const p of PERMS5) if (E1.every(([u, v]) => B[p[u]][p[v]])) return p;
    return null;
  }
  const degs = (E) => { const out = Array(5).fill(0), inn = Array(5).fill(0); E.forEach(([u, v]) => { out[u]++; inn[v]++; }); return { out, inn }; };
  const degSig = (E) => { const d = degs(E); return d.out.map((o, i) => o + '/' + d.inn[i]).sort().join(' '); };
  const tri = (E) => { const A = adj(E, 5); let c = 0; for (let a = 0; a < 5; a++) for (let b = 0; b < 5; b++) for (let d = 0; d < 5; d++) if (a < b && a < d && A[a][b] && A[b][d] && A[d][a]) c++; return c; };
  function connected(n, pairs) {
    const seen = new Set([0]), st = [0];
    while (st.length) { const x = st.pop(); pairs.forEach(([u, v]) => { const y = u === x ? v : v === x ? u : -1; if (y >= 0 && !seen.has(y)) { seen.add(y); st.push(y); } }); }
    return seen.size === n;
  }
  const drawDi = (E, labels, scale) => svgGraph({
    nodes: POS5.map((p, i) => ({ ...p, label: labels ? labels[i] : undefined })), r: 13, scale: scale || 1,
    edges: E.map(([u, v]) => ({ u, v, dir: true })),
  });

  function qIso(r) {
    const PAIRS = []; for (let i = 0; i < 5; i++) for (let j = i + 1; j < 5; j++) PAIRS.push([i, j]);
    for (let attempt = 0; attempt < 400; attempt++) {
      const sk = shuffle(r, PAIRS).slice(0, ri(r, 6, 7));
      if (!connected(5, sk)) continue;
      const orient = (mask) => sk.map(([u, v], i) => ((mask >> i) & 1 ? [v, u] : [u, v]));
      const mainMask = ri(r, 0, (1 << sk.length) - 1);
      const main = orient(mainMask);
      const iso = [], non = [];
      for (let m = 0; m < (1 << sk.length); m++) {
        if (m === mainMask) continue;
        const E = orient(m), p = isoPerm(main, E);
        (p ? iso : non).push({ E, p });
      }
      if (iso.length < 1) continue;
      const k = ri(r, 1, Math.min(3, iso.length));
      const sig = degSig(main);
      const hard = shuffle(r, non.filter((o) => degSig(o.E) === sig));
      const easy = shuffle(r, non.filter((o) => degSig(o.E) !== sig));
      const wrong = hard.slice(0, ri(r, 1, 3)).concat(easy).slice(0, 6 - k);
      if (wrong.length < 6 - k) continue;
      const opts = shuffle(r, shuffle(r, iso).slice(0, k).map((o) => ({ ...o, ok: true })).concat(wrong.map((o) => ({ ...o, ok: false }))));
      const L = ['1', '2', '3', '4', '5'];
      const mainD = degs(main);
      const explain = '<p>Nejdřív porovnejte <b>stupně</b>: každý vrchol má výstupní/vstupní stupeň. Zadaný graf má dvojice ' +
        '<b>' + sig.split(' ').join(', ') + '</b>. Kde se liší, izomorfní být nemůže. Kde sedí, hledejte přiřazení vrcholů, které zachová všechny šipky.</p>' +
        '<div class="czu-figs"><figure>' + drawDi(main, L, 1) + '<figcaption>zadaný graf (očíslovaný)</figcaption></figure></div><ul class="ex-list">' +
        opts.map((o, i) => {
          const lt = 'abcdef'[i] + ') ';
          if (o.ok) {
            const lab = Array(5); o.p.forEach((t, src) => { lab[t] = L[src]; });
            return '<li class="ex-item">' + lt + '<b class="ok">izomorfní</b>: vrcholy očíslované podle zadaného grafu, všechny šipky sedí.<div class="czu-figs"><figure>' + drawDi(o.E, lab, 0.9) + '</figure></div></li>';
          }
          const s2 = degSig(o.E);
          let why;
          if (s2 !== sig) why = 'jiné stupně (' + s2.split(' ').join(', ') + ')';
          else if (tri(o.E) !== tri(main)) why = 'stupně sedí, ale liší se počet orientovaných cyklů délky 3 (' + tri(o.E) + ' vs. ' + tri(main) + ')';
          else why = 'stupně sedí, ale žádné přiřazení vrcholů nezachová všechny šipky (vrcholy se stejnými stupni jsou spojené jinak)';
          return '<li class="ex-item">' + lt + '<b class="bad">není izomorfní</b>: ' + why + '.</li>';
        }).join('') + '</ul>';
      void mainD;
      return {
        title: 'Izomorfismus orientovaných grafů', points: 6, kind: 'multi',
        prompt: 'Vyberte, které grafy jsou izomorfní s grafem<div class="czu-figs">' + drawDi(main, null, 1) + '</div>',
        options: opts.map((o) => '<span class="czu-figs">' + drawDi(o.E, null, 0.85) + '</span>'),
        answer: opts.map((o) => o.ok),
        explain,
      };
    }
  }

  // =====================================================================
  // 3. EULEROVSKÝ GRAF (4 b)
  // =====================================================================
  const EV = ['a', 'b', 'c', 'd', 'e', 'f', 'g'];
  const EPOS = [{ x: 0, y: 62 }, { x: 95, y: 0 }, { x: 95, y: 124 }, { x: 190, y: 62 }, { x: 285, y: 0 }, { x: 285, y: 124 }, { x: 375, y: 62 }];
  const ECAND = [[0, 1], [0, 2], [1, 2], [1, 3], [2, 3], [1, 4], [2, 5], [3, 4], [3, 5], [4, 5], [4, 6], [5, 6]];
  function eulerTrail(n, E, start) {
    const adjL = Array.from({ length: n }, () => []);
    E.forEach(([u, v], i) => { adjL[u].push([v, i]); adjL[v].push([u, i]); });
    const used = Array(E.length).fill(false), st = [start], path = [];
    while (st.length) {
      const x = st[st.length - 1];
      while (adjL[x].length && used[adjL[x][adjL[x].length - 1][1]]) adjL[x].pop();
      if (!adjL[x].length) { path.push(st.pop()); continue; }
      const [y, i] = adjL[x].pop(); used[i] = true; st.push(y);
    }
    return path.reverse();
  }
  const normList = (v) => String(v).toLowerCase().replace(/[\s{}()[\]]/g, '').split(/[,;]+/).filter(Boolean);
  function qEuler(r) {
    const target = pick(r, ['closed', 'open', 'open', 'none', 'none']);
    for (let attempt = 0; attempt < 2000; attempt++) {
      const E = shuffle(r, ECAND).slice(0, ri(r, 9, 12));
      const deg = Array(7).fill(0); E.forEach(([u, v]) => { deg[u]++; deg[v]++; });
      if (deg.some((d) => d < 2) || !connected(7, E)) continue;
      const odd = deg.map((d, i) => (d % 2 ? i : -1)).filter((i) => i >= 0);
      const kind = odd.length === 0 ? 'closed' : odd.length === 2 ? 'open' : 'none';
      if (kind !== target) continue;
      const oddL = odd.map((i) => EV[i]);
      const isE = kind !== 'none';
      let check, show;
      if (kind === 'closed') {
        check = (v) => { const a = normList(v); return a.length === 2 && a[0] === a[1] && EV.includes(a[0]); };
        show = 'libovolný vrchol dvakrát, např. a,a';
      } else if (kind === 'open') {
        check = (v) => { const a = normList(v); return a.length === 2 && a.slice().sort().join() === oddL.join(); };
        show = oddL.join(',') + ' (nebo ' + oddL.slice().reverse().join(',') + ')';
      } else {
        check = (v) => normList(v).join() === oddL.join();
        show = oddL.join(',');
      }
      const trail = isE ? eulerTrail(7, E, kind === 'open' ? odd[0] : 0).map((i) => EV[i]).join(' – ') : '';
      const svg = svgGraph({ nodes: EPOS.map((p, i) => ({ ...p, label: EV[i] })), edges: E.map(([u, v]) => ({ u, v })), r: 15 });
      const explain = '<p>Graf je souvislý. Rozhodují <b>stupně vrcholů</b>: ' +
        EV.map((v, i) => vi(v) + ' = ' + deg[i]).join(', ') + '.</p>' +
        (kind === 'closed' ? '<p>Všechny stupně jsou sudé, takže existuje <b>uzavřený</b> eulerovský tah. Začíná a končí ve stejném vrcholu, a to v kterémkoli. Odpověď je tedy např. <b>a,a</b>.</p>'
          : kind === 'open' ? '<p>Přesně dva vrcholy mají lichý stupeň (' + oddL.map(vi).join(', ') + '), takže existuje <b>otevřený</b> eulerovský tah. Musí začít v jednom z nich a skončit ve druhém, odpověď je <b>' + oddL.join(',') + '</b>.</p>'
            : '<p>Lichý stupeň má ' + odd.length + ' vrcholů (' + oddL.map(vi).join(', ') + '). Eulerovský tah existuje jen při 0 nebo 2 vrcholech lichého stupně, takže graf <b>není eulerovský</b>. Do políčka patří <b>' + oddL.join(',') + '</b>.</p>') +
        (isE ? '<p>Příklad tahu: ' + trail + '</p>' : '');
      return {
        title: 'Eulerovský graf', points: 4, kind: 'inline',
        prompt: 'Je tento graf eulerovský (lze ho nakreslit jedním tahem)?<div class="czu-figs">' + svg + '</div>',
        rows: [
          [{ radio: ['Ano, je', 'Ne, není'], ans: isE ? 0 : 1 }],
          ['V případě, že je eulerovský, napište první a poslední vrchol nějakého eulerovského tahu, oddělené čárkou:', { text: true, check, show, w: 120 }],
          ['<span class="note">V případě, že není eulerovský, vypište do políčka výše všechny vrcholy lichého stupně, abecedně a oddělené čárkou.</span>'],
        ],
        explain,
      };
    }
  }

  // =====================================================================
  // 4. PREFIXOVÁ NOTACE (6 b)
  // =====================================================================
  const OPS = ['+', '−', '×', '/'];
  function genExpr(r, ops) {
    if (ops === 0) return { n: ri(r, 1, 9) };
    const l = ri(r, 0, ops - 1);
    return { op: pick(r, OPS), a: genExpr(r, l), b: genExpr(r, ops - 1 - l) };
  }
  function evalE(e) {
    if (e.n !== undefined) return e.n;
    const a = evalE(e.a), b = evalE(e.b);
    if (!Number.isFinite(a) || !Number.isFinite(b)) return NaN;
    let v;
    if (e.op === '+') v = a + b; else if (e.op === '−') v = a - b; else if (e.op === '×') v = a * b;
    else { if (b === 0 || a % b !== 0) return NaN; v = a / b; }
    return Math.abs(v) > 99 ? NaN : v;
  }
  const pre = (e) => (e.n !== undefined ? String(e.n) : e.op + pre(e.a) + pre(e.b));
  const post = (e) => (e.n !== undefined ? String(e.n) : post(e.a) + post(e.b) + e.op);
  const inf = (e, top) => (e.n !== undefined ? String(e.n) : (top ? '' : '(') + inf(e.a) + ' ' + e.op + ' ' + inf(e.b) + (top ? '' : ')'));
  function steps(e, out) {
    if (e.n !== undefined) return e.n;
    const a = steps(e.a, out), b = steps(e.b, out), v = evalE(e);
    out.push(num(a) + ' ' + e.op + ' ' + num(b) + ' = <b>' + num(v) + '</b>');
    return v;
  }
  const normPost = (v) => String(v).replace(/\s+/g, '').replace(/[*xX·⋅]/g, '×').replace(/[:÷]/g, '/').replace(/[-–]/g, '−');
  function qPrefix(r) {
    for (let attempt = 0; attempt < 5000; attempt++) {
      const e = genExpr(r, ri(r, 4, 6));
      const v = evalE(e);
      if (!Number.isFinite(v)) continue;
      const p = pre(e), ops = new Set(p.replace(/\d/g, ''));
      if (ops.size < 3 || !ops.has('/')) continue;
      if (e.a.n !== undefined && e.b.n !== undefined) continue;
      const pf = post(e), st = [];
      steps(e, st);
      return {
        title: 'Prefixová a postfixová notace', points: 6, kind: 'inline',
        prompt: 'Výraz v prefixové notaci<div class="fm-block" style="font-style:normal;letter-spacing:.06em">' + p + '</div>vypočítejte, pokud víte, že každé číslo ve výrazu je kladné a jednociferné. Následně tento výraz převeďte do postfixové notace.',
        rows: [
          ['Hodnota výrazu:', { text: true, w: 90, check: (x) => { const t = String(x).trim().replace(/[−–]/g, '-'); return /^-?\d+$/.test(t) && Number(t) === v; }, show: num(v) }],
          ['Postfixová notace:', { text: true, w: 220, check: (x) => normPost(x) === pf, show: pf }, '<span class="note">místo × můžete psát *</span>'],
        ],
        explain: '<p>Prefix čteme zleva: operátor patří ke dvěma výrazům, které za ním následují. Uzávorkovaný (infixový) zápis je</p>' +
          '<div class="fm-block" style="font-style:normal">' + inf(e, true) + '</div>' +
          '<p>Výpočet od nejvnitřnějších závorek:</p><ol class="ex-list">' + st.map((s) => '<li>' + s + '</li>').join('') + '</ol>' +
          '<p>Postfix (operátor až za oběma operandy): <b style="letter-spacing:.06em">' + pf + '</b></p>' +
          '<p class="note">Kontrola postfixu: čtěte zleva, čísla dávejte na zásobník, a když přijde operátor, vezměte dvě horní čísla a vraťte výsledek.</p>',
      };
    }
  }

  // =====================================================================
  // 5. MAXIMÁLNÍ TOK A MINIMÁLNÍ ŘEZY (10 b)
  // =====================================================================
  const FN = ['s', 'p', 'q', 'r', 'u', 't'];
  const FPOS = [{ x: 0, y: 92 }, { x: 80, y: 0 }, { x: 225, y: 0 }, { x: 80, y: 184 }, { x: 225, y: 184 }, { x: 305, y: 92 }];
  const FE = [[0, 1], [0, 3], [1, 2], [1, 4], [3, 2], [3, 4], [2, 5], [4, 5]]; // sp sr pq pu rq ru qt ut
  const FLAB = { '0,1': { t: 0.5, side: 1 }, '0,3': { t: 0.5, side: -1 }, '1,2': { t: 0.5, side: 1 }, '1,4': { t: 0.32, side: 1 }, '3,2': { t: 0.32, side: -1 }, '3,4': { t: 0.5, side: 1 }, '2,5': { t: 0.5, side: 1 }, '4,5': { t: 0.5, side: -1 } };
  const ename = ([u, v]) => FN[u] + FN[v];
  function maxFlow(cap) {
    const f = FE.map(() => 0), paths = [];
    for (;;) {
      // BFS v reziduální síti
      const prev = Array(6).fill(null); prev[0] = { from: -1 };
      const q = [0];
      while (q.length && !prev[5]) {
        const x = q.shift();
        FE.forEach(([u, v], i) => {
          if (u === x && !prev[v] && cap[i] - f[i] > 0) { prev[v] = { from: x, i, dir: 1 }; q.push(v); }
          if (v === x && !prev[u] && f[i] > 0) { prev[u] = { from: x, i, dir: -1 }; q.push(u); }
        });
      }
      if (!prev[5]) break;
      let b = Infinity, x = 5; const seq = [];
      while (x !== 0) { const p = prev[x]; b = Math.min(b, p.dir > 0 ? cap[p.i] - f[p.i] : f[p.i]); seq.push(p); x = p.from; }
      seq.forEach((p) => { f[p.i] += p.dir * b; });
      const nodes = [FN[0]].concat(seq.slice().reverse().map((p) => (p.dir > 0 ? '' : '←') + FN[FE[p.i][p.dir > 0 ? 1 : 0]]));
      paths.push({ text: seq.slice().reverse().reduce((acc, p) => acc + (p.dir > 0 ? ' → ' : ' ⇠ ') + FN[p.dir > 0 ? FE[p.i][1] : FE[p.i][0]], 's'), b });
      void nodes;
    }
    return { f, value: f[0] + f[1], paths };
  }
  function uniqueFlow(cap, f) {
    // tok je jediný ⇔ reziduální síť nemá orientovaný cyklus délky ≥ 3
    const out = Array.from({ length: 6 }, () => []);
    FE.forEach(([u, v], i) => { if (cap[i] - f[i] > 0) out[u].push(v); if (f[i] > 0) out[v].push(u); });
    let found = false;
    const dfs = (start, x, seen, len) => {
      if (found) return;
      out[x].forEach((y) => {
        if (y === start && len >= 3) found = true;
        else if (!seen.has(y) && y > start) { seen.add(y); dfs(start, y, seen, len + 1); seen.delete(y); }
      });
    };
    for (let s = 0; s < 6 && !found; s++) dfs(s, s, new Set([s]), 1);
    return !found;
  }
  const cutCap = (S, cap) => FE.reduce((sum, [u, v], i) => sum + (S.has(u) && !S.has(v) ? cap[i] : 0), 0);
  const cutStr = (S) => '{' + [0, 1, 2, 3, 4].filter((i) => S.has(i)).map((i) => FN[i]).join(',') + '}';
  const drawFlow = (cap, f, hlS) => svgGraph({
    nodes: FPOS.map((p, i) => ({ ...p, label: FN[i], hl: hlS && hlS.has(i) })), r: 14, off: 9,
    edges: FE.map(([u, v], i) => ({ u, v, dir: true, w: f ? f[i] + '/' + cap[i] : cap[i], ...FLAB[u + ',' + v], hl: f && hlS && hlS.has(u) && !hlS.has(v) })),
  });
  function qFlow(r) {
    for (let attempt = 0; attempt < 3000; attempt++) {
      const cap = FE.map(() => ri(r, 1, 9));
      const { f, value, paths } = maxFlow(cap);
      if (value < 5 || !uniqueFlow(cap, f)) continue;
      const cuts = [];
      for (let m = 0; m < 16; m++) { const S = new Set([0]); [1, 2, 3, 4].forEach((v, k) => { if ((m >> k) & 1) S.add(v); }); cuts.push({ S, c: cutCap(S, cap) }); }
      const mins = cuts.filter((c) => c.c === value);
      if (mins.length > 4) continue;
      const others = shuffle(r, cuts.filter((c) => c.c !== value)).slice(0, 9 - mins.length);
      const opts = shuffle(r, mins.map((c) => ({ ...c, ok: true })).concat(others.map((c) => ({ ...c, ok: false }))));
      const capStr = (S) => FE.map((e, i) => (S.has(e[0]) && !S.has(e[1]) ? vi(ename(e)) + ' ' + cap[i] : null)).filter(Boolean).join(' + ');
      return {
        title: 'Maximální tok a minimální řezy', points: 10, kind: 'inline', multiPoints: 4,
        prompt: 'Nalezněte maximální tok a minimální řezy dané sítě:<div class="czu-figs">' + drawFlow(cap) + '</div>',
        rows: FE.map((e, i) => ['Maximální tok podél hrany ' + vi(ename(e)) + ' je:', { num: true, ans: f[i] }]),
        optionsPrompt: 'Z níže uvedených řezů vyberte ty, které jsou minimální.',
        optionsInline: true,
        options: opts.map((o) => cutStr(o.S)),
        answer: opts.map((o) => o.ok),
        explain: '<p>Fordův–Fulkersonův algoritmus: hledáme cesty ze <i>s</i> do <i>t</i>, po kterých jde ještě něco poslat (⇠ znamená hranu použitou proti směru, tedy vrácení toku), a pošleme po nich minimum volných kapacit.</p><ol class="ex-list">' +
          paths.map((p) => '<li>' + p.text + ': pošleme <b>' + p.b + '</b></li>').join('') + '</ol>' +
          '<p>Další cesta neexistuje, maximální tok má velikost <b>' + value + '</b>. Toky po hranách (tok/kapacita):</p>' +
          '<div class="czu-figs">' + drawFlow(cap, f) + '</div>' +
          '<p>' + FE.map((e, i) => vi(ename(e)) + ' = <b>' + f[i] + '</b>').join(', ') + '</p>' +
          '<p><b>Řez</b> je množina vrcholů obsahující <i>s</i> (a ne <i>t</i>). Jeho kapacita je součet kapacit hran, které z ní <b>vedou ven</b>. Minimální řezy mají kapacitu rovnou maximálnímu toku, tedy ' + value + ':</p><ul class="ex-list">' +
          opts.map((o) => '<li>' + cutStr(o.S) + ': ' + capStr(o.S) + ' = <b class="' + (o.ok ? 'ok' : '') + '">' + o.c + '</b>' + (o.ok ? ' ✓ minimální' : '') + '</li>').join('') + '</ul>',
      };
    }
  }

  // =====================================================================
  // 6. MINIMÁLNÍ KOSTRA (10 b)
  // =====================================================================
  const KN = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
  const KPOS = [{ x: 0, y: 0 }, { x: 125, y: 0 }, { x: 250, y: 0 }, { x: 375, y: 0 }, { x: 0, y: 125 }, { x: 125, y: 125 }, { x: 250, y: 125 }, { x: 375, y: 125 }];
  const KBASE = [[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7], [0, 4], [1, 5], [2, 6], [3, 7]];
  const KDIAG = [[[1, 4], [0, 5]], [[1, 6], [2, 5]], [[3, 6], [2, 7]]]; // be/af, bg/cf, dg/ch
  function find(p, x) { while (p[x] !== x) { p[x] = p[p[x]]; x = p[x]; } return x; }
  function qMST(r) {
    for (let attempt = 0; attempt < 3000; attempt++) {
      const E = KBASE.slice();
      KDIAG.forEach((pair) => { if (r() < 0.85) E.push(pick(r, pair)); });
      const w = E.map(() => ri(r, 1, 9));
      const order = E.map((_, i) => i).sort((a, b) => w[a] - w[b] || a - b);
      const par = KN.map((_, i) => i), inT = E.map(() => false), log = [];
      order.forEach((i) => {
        const [u, v] = E[i], a = find(par, u), b = find(par, v);
        if (a !== b) { par[a] = b; inT[i] = true; log.push({ i, add: true }); } else log.push({ i, add: false });
      });
      // jednoznačnost: žádná hrana mimo kostru se stejnou vahou nesmí nahradit hranu kostry
      let unique = true;
      E.forEach((te, ti) => {
        if (!inT[ti] || !unique) return;
        const p2 = KN.map((_, i) => i);
        E.forEach(([u, v], j) => { if (inT[j] && j !== ti) p2[find(p2, u)] = find(p2, v); });
        E.forEach(([u, v], j) => { if (!inT[j] && w[j] === w[ti] && find(p2, u) !== find(p2, v)) unique = false; });
      });
      if (!unique) continue;
      const total = E.reduce((s, _, i) => s + (inT[i] ? w[i] : 0), 0);
      const nm = ([u, v]) => KN[u] + KN[v];
      const lab = (e, i) => {
        const [u, v] = e;
        if (u + 4 === v) return { side: 1 };          // svislé: popisek vlevo
        if (v === u + 1) return { side: 1 };          // vodorovné: nad hranou
        return { t: 0.35, side: (KPOS[v].x > KPOS[u].x ? 1 : -1) };
      };
      const draw = (hl) => svgGraph({
        nodes: KPOS.map((p, i) => ({ ...p, label: KN[i] })), r: 15, off: 11,
        edges: E.map((e, i) => ({ u: e[0], v: e[1], w: w[i], ...lab(e, i), hl: hl && inT[i], dim: hl && !inT[i] })),
      });
      const rows = [];
      for (let i = 0; i < E.length; i += 3) {
        const row = [];
        E.slice(i, i + 3).forEach((e, k) => { row.push('<span class="lbl">Hrana ' + vi(nm(e)) + '</span>'); row.push({ sel: ['ano', 'ne'], ans: inT[i + k] ? 0 : 1, ph: '–' }); });
        rows.push(row);
      }
      return {
        title: 'Minimální kostra', points: 10, kind: 'inline',
        prompt: 'Určete, které hrany jsou součástí minimální kostry grafu.<div class="czu-figs">' + draw(false) + '</div>',
        rows,
        explain: '<p>Kruskalův algoritmus: hrany seřadíme podle váhy a postupně přidáváme. Hranu vynecháme, pokud by vytvořila kružnici. Kostra má 8 − 1 = 7 hran.</p>' +
          '<ol class="ex-list">' + log.map((l) => '<li>' + vi(nm(E[l.i])) + ' (' + w[l.i] + '): ' + (l.add ? '<b class="ok">přidáme</b>' : '<span class="muted">vynecháme, vznikla by kružnice</span>') + '</li>').join('') + '</ol>' +
          '<div class="czu-figs">' + draw(true) + '</div>' +
          '<p>Minimální kostra: ' + E.map((e, i) => (inT[i] ? vi(nm(e)) : null)).filter(Boolean).join(', ') + ', celková váha <b>' + total + '</b>.</p>',
      };
    }
  }

  const BUILDERS = [qScore, qIso, qEuler, qPrefix, qFlow, qMST];

  function generate(seed) {
    const questions = BUILDERS.map((b, i) => {
      const q = b(mulberry32(seed * 7919 + i * 104729 + 31));
      q.id = 'q' + (i + 1);
      return q;
    });
    return { timeLimitMin: 50, questions };
  }

  if (typeof window !== 'undefined') {
    window.CZU_GENERATORS = window.CZU_GENERATORS || {};
    window.CZU_GENERATORS.grf = generate;
  }
  if (typeof module !== 'undefined') module.exports = { generate, _internal: { havelHakimi, isoPerm, maxFlow, uniqueFlow, eulerTrail, evalE, pre, post, normPost, cutCap } };
})();
