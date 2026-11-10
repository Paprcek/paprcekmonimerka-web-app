/*
 * Generátor cvičných testů – Matematická logika a grafy (TAE75E / TAE41E), ČZU.
 *
 * Princip: test je deterministický podle čísla (seed). "Cvičný test 3" je tak
 * pro všechny stejný a dá se o něm mluvit. Správná řešení se POČÍTAJÍ
 * (pravdivostní tabulky, definice vlastností relací, uzávěry…), nikde nejsou
 * ručně opsaná, takže v nich nemůže být překlep.
 *
 * Výstup: { title, timeLimitMin, questions: [...] } – formát popsaný v engine.js.
 * Typy úloh vychází z cvičného testu v Moodlu a ze sbírek Logika_1, Logika_2, Množiny.
 */
(function () {
  'use strict';

  // ---------- RNG (mulberry32) ----------
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
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const num = (x) => (x < 0 ? '−' + (-x) : String(x));

  // ---------- Výroková logika ----------
  const V = (n) => ({ t: 'v', n });
  const N = (a) => ({ t: 'n', a });
  const mk = (t, a, b) => ({ t, a, b });
  const SYM = { and: '∧', or: '∨', imp: '⇒', eq: '⇔' };

  function ev(f, env) {
    switch (f.t) {
      case 'v': return env[f.n];
      case 'n': return !ev(f.a, env);
      case 'and': return ev(f.a, env) && ev(f.b, env);
      case 'or': return ev(f.a, env) || ev(f.b, env);
      case 'imp': return !ev(f.a, env) || ev(f.b, env);
      case 'eq': return ev(f.a, env) === ev(f.b, env);
    }
  }
  function show(f) {
    if (f.t === 'v') return f.n;
    if (f.t === 'n') return (f.a.t === 'v' || f.a.t === 'n') ? show(f.a) + '′' : '(' + show(f.a) + ')′';
    const side = (c) => {
      const bin = c.t !== 'v' && c.t !== 'n';
      const flat = c.t === f.t && (f.t === 'and' || f.t === 'or');
      return bin && !flat ? '(' + show(c) + ')' : show(c);
    };
    return side(f.a) + ' ' + SYM[f.t] + ' ' + side(f.b);
  }
  const size = (f) => (f.t === 'v' ? 1 : f.t === 'n' ? 1 + size(f.a) : 1 + size(f.a) + size(f.b));
  function varsOf(f, s = new Set()) {
    if (f.t === 'v') s.add(f.n); else if (f.t === 'n') varsOf(f.a, s); else { varsOf(f.a, s); varsOf(f.b, s); }
    return s;
  }
  // řádky v pořadí jako ve sbírce: 1 1 1, 1 1 0, …, 0 0 0
  function rows(vars) {
    const n = vars.length, out = [];
    for (let i = 0; i < (1 << n); i++) {
      const env = {};
      vars.forEach((v, k) => { env[v] = !((i >> (n - 1 - k)) & 1); });
      out.push(env);
    }
    return out;
  }
  const tv = (f, vars) => rows(vars).map((e) => (ev(f, e) ? 1 : 0));
  function classify(f, vars) {
    const t = tv(f, vars), s = t.reduce((a, b) => a + b, 0);
    return s === t.length ? 'taut' : s === 0 ? 'contra' : 'sat';
  }
  function rf(r, vars, d) {
    if (d <= 0 || r() < 0.2) { const v = V(pick(r, vars)); return r() < 0.4 ? N(v) : v; }
    const op = pick(r, ['and', 'or', 'imp', 'eq', 'and', 'or', 'imp']);
    let f = mk(op, rf(r, vars, d - 1), rf(r, vars, d - 1));
    if (r() < 0.15) f = N(f);
    return f;
  }
  // "hloupé" podformule typu A ⇔ A, B ∧ B, A ∧ A′ – v reálném testu by nebyly
  const litVar = (x) => (x.t === 'v' ? x.n : x.t === 'n' && x.a.t === 'v' ? x.a.n : null);
  function trivial(f) {
    if (f.t === 'v') return false;
    if (f.t === 'n') return f.a.t === 'n' || trivial(f.a);
    const va = litVar(f.a), vb = litVar(f.b);
    if (va && va === vb) return true;
    return trivial(f.a) || trivial(f.b);
  }
  function dn(f) { // odstraní dvojité negace
    if (f.t === 'v') return f;
    if (f.t === 'n') return f.a.t === 'n' ? dn(f.a.a) : N(dn(f.a));
    return mk(f.t, dn(f.a), dn(f.b));
  }
  function nodes(f, out = []) {
    out.push(f);
    if (f.t === 'n') nodes(f.a, out); else if (f.t !== 'v') { nodes(f.a, out); nodes(f.b, out); }
    return out;
  }
  function replace(f, target, repl) {
    if (f === target) return repl;
    if (f.t === 'v') return f;
    if (f.t === 'n') return N(replace(f.a, target, repl));
    return mk(f.t, replace(f.a, target, repl), replace(f.b, target, repl));
  }
  function applyRandom(r, f, rules) {
    const cands = [];
    nodes(f).forEach((n) => rules.forEach((rule) => { const res = rule(n); if (res) cands.push([n, res]); }));
    if (!cands.length) return null;
    const [n, res] = pick(r, cands);
    return dn(replace(f, n, res));
  }
  const EQUIV_RULES = [
    (n) => n.t === 'imp' ? mk('or', N(n.a), n.b) : null,
    (n) => n.t === 'imp' ? mk('imp', N(n.b), N(n.a)) : null,
    (n) => n.t === 'n' && n.a.t === 'and' ? mk('or', N(n.a.a), N(n.a.b)) : null,
    (n) => n.t === 'n' && n.a.t === 'or' ? mk('and', N(n.a.a), N(n.a.b)) : null,
    (n) => n.t === 'n' && n.a.t === 'imp' ? mk('and', n.a.a, N(n.a.b)) : null,
    (n) => n.t === 'eq' ? mk('and', mk('imp', n.a, n.b), mk('imp', n.b, n.a)) : null,
    (n) => n.t === 'or' ? mk('imp', N(n.a), n.b) : null,
    (n) => n.t === 'and' ? N(mk('or', N(n.a), N(n.b))) : null,
    (n) => n.t === 'eq' ? mk('eq', N(n.a), N(n.b)) : null,
    (n) => (n.t === 'and' || n.t === 'or') ? mk(n.t, n.b, n.a) : null,
  ];
  const MUTATIONS = [
    (n) => n.t === 'imp' ? mk('imp', n.b, n.a) : null,
    (n) => n.t === 'and' ? mk('or', n.a, n.b) : null,
    (n) => n.t === 'or' ? mk('and', n.a, n.b) : null,
    (n) => n.t === 'eq' ? mk('imp', n.a, n.b) : null,
    (n) => n.t === 'v' ? N(n) : null,
    (n) => n.t === 'n' ? n.a : null,
  ];

  const fm = (f) => '<span class="fm">' + esc(typeof f === 'string' ? f : show(f)) + '</span>';
  function ttHTML(vars, cols) {
    const rs = rows(vars);
    let h = '<table class="tt"><thead><tr>' + vars.map((v) => '<th>' + v + '</th>').join('') +
      cols.map((c) => '<th class="sep">' + esc(c.name) + '</th>').join('') + '</tr></thead><tbody>';
    rs.forEach((env) => {
      h += '<tr>' + vars.map((v) => '<td>' + (env[v] ? 1 : 0) + '</td>').join('') +
        cols.map((c) => { const x = ev(c.f, env) ? 1 : 0; return '<td class="sep ' + (x ? 'one' : 'zero') + '">' + x + '</td>'; }).join('') + '</tr>';
    });
    return h + '</tbody></table>';
  }

  // ---------- Q: tautologie / kontradikce ----------
  function qFormulaType(r) {
    const LABEL = { taut: 'tautologie', contra: 'kontradikce', sat: 'splnitelná, ale ne tautologie' };
    const ORDER = ['taut', 'contra', 'sat'];
    const targets = shuffle(r, ['taut', 'contra', 'sat', pick(r, ['taut', 'sat', 'contra', 'sat'])]);
    const seen = new Set(), items = [];
    targets.forEach((target) => {
      let found = null;
      for (let i = 0; i < 8000 && !found; i++) {
        const vars = r() < 0.5 ? ['A', 'B'] : ['A', 'B', 'C'];
        const f = rf(r, vars, ri(r, 2, 3)), s = size(f), str = show(f);
        if (s < 5 || s > 12 || varsOf(f).size !== vars.length || seen.has(str) || trivial(f)) continue;
        if (classify(f, vars) === target) found = { f, vars };
      }
      if (!found) { // pojistka – nemělo by nastat
        const A = V('A'), B = V('B');
        const f = target === 'taut' ? mk('imp', A, mk('imp', B, A)) : target === 'contra' ? mk('and', mk('or', A, B), mk('and', N(A), N(B))) : mk('imp', A, B);
        found = { f, vars: ['A', 'B'] };
      }
      seen.add(show(found.f));
      items.push({ ...found, cls: classify(found.f, found.vars) });
    });
    const letters = 'abcd';
    return {
      title: 'Tautologie, kontradikce, splnitelnost', points: 4, kind: 'inline',
      prompt: 'Pro každou formuli rozhodněte, zda je tautologie, kontradikce, nebo splnitelná formule, která není tautologií.',
      rows: items.map((it, i) => ['(' + letters[i] + ')', fm(it.f), 'je', { sel: ORDER.map((k) => LABEL[k]), ans: ORDER.indexOf(it.cls) }]),
      explain: items.map((it, i) => '<div class="ex-item"><p><b>(' + letters[i] + ')</b> ' + fm(it.f) + ' → <b>' + LABEL[it.cls] + '</b></p>' +
        ttHTML(it.vars, [{ name: 'φ', f: it.f }]) + '</div>').join('') +
        '<p class="note">Tautologie má ve sloupci samé 1, kontradikce samé 0, splnitelná formule aspoň jednu 1.</p>',
    };
  }

  // ---------- Q: ekvivalence formulí ----------
  function qEquivalence(r) {
    const targets = shuffle(r, [true, true, false, false]);
    const letters = 'abcd', items = [];
    targets.forEach((target) => {
      let item = null;
      for (let i = 0; i < 3000 && !item; i++) {
        const vars = r() < 0.4 ? ['A', 'B'] : ['A', 'B', 'C'];
        const phi = dn(rf(r, vars, ri(r, 2, 3)));
        const s = size(phi);
        if (s < 4 || s > 9 || varsOf(phi).size < 2 || trivial(phi)) continue;
        let psi = applyRandom(r, phi, EQUIV_RULES);
        if (!psi) continue;
        if (r() < 0.5) psi = applyRandom(r, psi, EQUIV_RULES) || psi;
        if (!target) psi = applyRandom(r, psi, MUTATIONS);
        if (!psi || show(psi) === show(phi) || size(psi) > 14 || trivial(psi)) continue;
        const allVars = ['A', 'B', 'C'].filter((v) => varsOf(phi).has(v) || varsOf(psi).has(v));
        const same = tv(phi, allVars).join('') === tv(psi, allVars).join('');
        if (same !== target) continue;
        item = { phi, psi, vars: allVars, same };
      }
      items.push(item);
    });
    return {
      title: 'Ekvivalence formulí', points: 4, kind: 'inline',
      prompt: 'Rozhodněte, zda jsou dvojice formulí navzájem ekvivalentní (mají stejnou pravdivostní tabulku).',
      rows: items.map((it, i) => ['(' + letters[i] + ')', fm(it.phi), '<span class="muted">a</span>', fm(it.psi), { sel: ['jsou ekvivalentní', 'nejsou ekvivalentní'], ans: it.same ? 0 : 1 }]),
      explain: items.map((it, i) => '<div class="ex-item"><p><b>(' + letters[i] + ')</b> ' + (it.same ? 'jsou ekvivalentní – sloupce φ a ψ se shodují.' : 'nejsou ekvivalentní – sloupce se liší (zvýrazněno).') + '</p>' +
        ttHTML(it.vars, [{ name: 'φ = ' + show(it.phi), f: it.phi }, { name: 'ψ = ' + show(it.psi), f: it.psi }]) + '</div>').join(''),
    };
  }

  // ---------- Q: minimální DNF (jako ve cvičném testu) ----------
  const DV = ['A', 'B', 'C'];
  const termStr = (t) => t.map((x, k) => (x === null ? null : DV[k] + (x ? '' : '′'))).filter(Boolean).join(' ∧ ');
  const minIdxBits = (i) => [!((i >> 2) & 1), !((i >> 1) & 1), !(i & 1)];
  const covers = (t, i) => minIdxBits(i).every((b, k) => t[k] === null || t[k] === (b ? 1 : 0));
  const coverSet = (t) => [0, 1, 2, 3, 4, 5, 6, 7].filter((i) => covers(t, i));
  const lits = (t) => t.filter((x) => x !== null).length;
  const ALL_TERMS = (() => {
    const out = [];
    for (const a of [1, 0, null]) for (const b of [1, 0, null]) for (const c of [1, 0, null]) if (!(a === null && b === null && c === null)) out.push([a, b, c]);
    return out;
  })();

  function minimalDNF(F) {
    const Fs = new Set(F);
    const impl = ALL_TERMS.filter((t) => coverSet(t).every((i) => Fs.has(i)));
    const primes = impl.filter((p) => {
      const cp = coverSet(p);
      return !impl.some((q) => q !== p && coverSet(q).length > cp.length && cp.every((i) => covers(q, i)));
    });
    let best = null, bestCount = 0;
    for (let mask = 1; mask < (1 << primes.length); mask++) {
      const chosen = primes.filter((_, k) => (mask >> k) & 1);
      const cov = new Set(); chosen.forEach((t) => coverSet(t).forEach((i) => cov.add(i)));
      if (![...Fs].every((i) => cov.has(i))) continue;
      const cost = chosen.reduce((s, t) => s + lits(t), 0) * 10 + chosen.length;
      if (!best || cost < best.cost) { best = { cost, chosen }; bestCount = 1; } else if (cost === best.cost) bestCount++;
    }
    return { primes, best: best.chosen, unique: bestCount === 1 };
  }

  function qMinDNF(r) {
    for (let attempt = 0; attempt < 2000; attempt++) {
      const F = shuffle(r, [0, 1, 2, 3, 4, 5, 6, 7]).slice(0, ri(r, 3, 6)).sort((a, b) => a - b);
      const { primes, best, unique } = minimalDNF(F);
      if (!unique || best.length < 2 || best.length > 3) continue;
      const key = (t) => t.join(',');
      const bestKeys = new Set(best.map(key));
      const minterms = F.map((i) => minIdxBits(i).map((b) => (b ? 1 : 0)));
      // distraktory: nepoužité prosté implikanty, mintermy, náhodné termy
      const pool = [];
      const add = (t) => { if (!bestKeys.has(key(t)) && !pool.some((p) => key(p) === key(t))) pool.push(t); };
      shuffle(r, primes).forEach(add);
      shuffle(r, minterms).forEach(add);
      shuffle(r, ALL_TERMS.filter((t) => lits(t) >= 2)).forEach(add);
      const distract = pool.slice(0, 6 - best.length);
      const opts = shuffle(r, best.map((t) => ({ t, ok: true })).concat(distract.map((t) => ({ t, ok: false }))));
      // zobrazení formule: disjunkce mintermů, někdy s opakováním (jako v Moodlu)
      let shown = shuffle(r, minterms);
      if (r() < 0.6) shown.splice(ri(r, 0, shown.length), 0, pick(r, minterms));
      const formula = shown.map((t) => '(' + termStr(t) + ')').join(' ∨ ');
      const bits = (i) => minIdxBits(i).map((b) => (b ? 1 : 0)).join('');
      return {
        title: 'Minimální disjunktivní tvar', points: 5, kind: 'multi',
        prompt: 'Je zadána formule<div class="fm-block">' + esc(formula) + '</div>Vyberte konjunkce, jejichž disjunkcí je minimální disjunktivní tvar zadané formule.',
        options: opts.map((o) => fm(termStr(o.t))),
        answer: opts.map((o) => o.ok),
        explain: '<p>Formule je pravdivá v řádcích (A B C): <b>' + F.map(bits).join(', ') + '</b>.</p>' +
          '<p>Prosté implikanty (nedají se už zjednodušit): ' + primes.map((t) => fm(termStr(t))).join(', ') + '.</p>' +
          '<p>Nejmenší pokrytí všech řádků: <b>' + fm(best.map((t) => '(' + termStr(t) + ')').join(' ∨ ')) + '</b></p>' +
          '<p class="note">Postup (Quine–McCluskey / Karnaughova mapa): sloučíte mintermy lišící se v jedné proměnné, dokud to jde, a pak vyberete co nejméně implikantů tak, aby pokryly všechny jedničky.</p>',
      };
    }
  }

  // ---------- Q: logický důsledek ----------
  function qConsequence(r) {
    const vars = ['A', 'B', 'C'];
    for (let attempt = 0; attempt < 3000; attempt++) {
      const phi = dn(rf(r, vars, ri(r, 2, 3)));
      const tphi = tv(phi, vars), cnt = tphi.reduce((a, b) => a + b, 0);
      if (cnt < 2 || cnt > 5 || size(phi) < 5 || size(phi) > 11 || varsOf(phi).size < 3 || trivial(phi)) continue;
      const pool = new Map();
      for (let i = 0; i < 400; i++) {
        const psi = dn(rf(r, vars, ri(r, 1, 2)));
        if (size(psi) > 6 || trivial(psi)) continue;
        pool.set(show(psi), psi);
      }
      pool.delete(show(phi));
      const isCons = (psi) => tv(psi, vars).every((x, k) => !tphi[k] || x);
      const all = [...pool.values()];
      const cons = shuffle(r, all.filter(isCons));
      const consNT = cons.filter((p) => classify(p, vars) !== 'taut');
      const non = shuffle(r, all.filter((p) => !isCons(p)));
      if (!consNT.length || non.length < 3) continue;
      const nCons = Math.min(ri(r, 1, 3), cons.length);
      const chosenCons = consNT.slice(0, nCons);
      if (chosenCons.length < nCons) { const t = cons.find((p) => classify(p, vars) === 'taut'); if (t) chosenCons.push(t); }
      const chosen = shuffle(r, chosenCons.concat(non.slice(0, 4 - chosenCons.length)));
      return {
        title: 'Logický důsledek', points: 4, kind: 'multi',
        prompt: 'Které z následujících formulí jsou logickým důsledkem formule <span class="fm">φ = ' + esc(show(phi)) + '</span>?',
        options: chosen.map((p) => fm(p)),
        answer: chosen.map(isCons),
        explain: '<p>ψ je důsledkem φ, právě když v každém řádku, kde je φ pravdivá, je pravdivá i ψ.</p>' +
          ttHTML(vars, [{ name: 'φ', f: phi }].concat(chosen.map((p, k) => ({ name: 'ψ' + (k + 1) + ' = ' + show(p), f: p })))) +
          '<p>Důsledky: <b>' + (chosen.filter(isCons).map((p) => fm(p)).join(', ') || 'žádná') + '</b></p>',
      };
    }
  }

  // ---------- Q: množiny na reálné ose (jako ve cvičném testu) ----------
  function genSet(r) {
    const pattern = pick(r, ['L', 'R', 'I', 'I+S', 'S+I', 'L+I', 'I+R', 'L+R', 'S+R', 'L+S', 'I+I']);
    const parts = pattern.split('+');
    const need = parts.reduce((s, p) => s + (p === 'I' ? 2 : 1), 0);
    const pts = shuffle(r, [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]).slice(0, need).sort((a, b) => a - b);
    let k = 0;
    return parts.map((p) => {
      if (p === 'L') return { lo: -Infinity, hi: pts[k++], lc: false, hc: r() < 0.5 };
      if (p === 'R') return { lo: pts[k++], hi: Infinity, lc: r() < 0.5, hc: false };
      if (p === 'S') { const x = pts[k++]; return { lo: x, hi: x, lc: true, hc: true }; }
      const lo = pts[k++], hi = pts[k++];
      return { lo, hi, lc: r() < 0.5, hc: r() < 0.5 };
    });
  }
  const inSet = (S, x) => S.some((c) => (x > c.lo || (x === c.lo && c.lc)) && (x < c.hi || (x === c.hi && c.hc)));
  const setStr = (S) => S.map((c) => {
    if (c.lo === c.hi) return '{' + num(c.lo) + '}';
    const br = (ch) => '<span class="br">' + ch + '</span>';
    const lo = c.lo === -Infinity ? br('(') + '−∞' : br(c.lc ? '⟨' : '(') + num(c.lo);
    const hi = c.hi === Infinity ? '∞' + br(')') : num(c.hi) + br(c.hc ? '⟩' : ')');
    return lo + ', ' + hi;
  }).join(' ∪ ');

  function qSets(r) {
    for (let attempt = 0; attempt < 500; attempt++) {
      const A = genSet(r), B = genSet(r);
      const ends = new Set();
      A.concat(B).forEach((c) => { if (isFinite(c.lo)) ends.add(c.lo); if (isFinite(c.hi)) ends.add(c.hi); });
      let cand = shuffle(r, [...ends]).slice(0, 4);
      shuffle(r, [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7]).forEach((x) => { if (cand.length < 5 && !cand.includes(x)) cand.push(x); });
      cand.sort((a, b) => a - b);
      const ops = [
        { name: 'A ∪ B', f: (x) => inSet(A, x) || inSet(B, x) },
        { name: 'A ∩ B', f: (x) => inSet(A, x) && inSet(B, x) },
        { name: 'A ∖ B', f: (x) => inSet(A, x) && !inSet(B, x) },
        { name: 'B ∖ A', f: (x) => inSet(B, x) && !inSet(A, x) },
      ];
      let yes = 0; cand.forEach((x) => ops.forEach((o) => { if (o.f(x)) yes++; }));
      if (yes < 6 || yes > 13) continue;
      if (!ops.every((o) => cand.some((x) => o.f(x)))) continue; // každá operace aspoň jednou "náleží"
      const yn = (b) => (b ? '<b class="ok">ano</b>' : '<b class="bad">ne</b>');
      return {
        title: 'Množinové operace na reálné ose', points: 5, kind: 'inline',
        prompt: 'Mějme množiny <span class="fm">A = ' + setStr(A) + '</span>, <span class="fm">B = ' + setStr(B) + '</span>.<br>Určete A ∪ B, A ∩ B, A ∖ B, B ∖ A. Pro každý bod vyberte všechna pravdivá tvrzení:',
        rows: cand.map((x) => {
          const row = ['Bod <b>' + num(x) + '</b>'];
          ops.forEach((o) => { row.push({ sel: ['náleží', 'nenáleží'], ans: o.f(x) ? 0 : 1 }); row.push(fm(o.name) + ','); });
          row[row.length - 1] = row[row.length - 1].replace(/,$/, '.');
          return row;
        }),
        explain: '<table class="tt"><thead><tr><th>bod</th><th>∈ A</th><th>∈ B</th>' + ops.map((o) => '<th class="sep">' + o.name + '</th>').join('') + '</tr></thead><tbody>' +
          cand.map((x) => '<tr><td>' + num(x) + '</td><td>' + yn(inSet(A, x)) + '</td><td>' + yn(inSet(B, x)) + '</td>' +
            ops.map((o) => '<td class="sep">' + yn(o.f(x)) + '</td>').join('') + '</tr>').join('') + '</tbody></table>' +
          '<p class="note">Pozor na krajní body: kulatá závorka ( ) bod nezahrnuje, lomená ⟨ ⟩ ano. A ∖ B = body z A, které nejsou v B.</p>',
      };
    }
  }

  // ---------- Relace ----------
  const SETS = [['1', '2', '3', '4'], ['a', 'b', 'c', 'd'], ['♥', '♠', '♦', '♣']];
  const pkey = (p) => p[0] + '|' + p[1];
  const pairStr = (p) => '(' + p[0] + ',' + p[1] + ')';
  function props(S, R) {
    const has = new Set(R.map(pkey)), h = (x, y) => has.has(x + '|' + y);
    const why = {};
    const nr = S.find((x) => !h(x, x)); if (nr) why.refl = 'chybí (' + nr + ',' + nr + ')';
    const ns = R.find(([x, y]) => !h(y, x)); if (ns) why.sym = pairStr(ns) + ' ∈ R, ale (' + ns[1] + ',' + ns[0] + ') ∉ R';
    const na = R.find(([x, y]) => x !== y && h(y, x)); if (na) why.anti = pairStr(na) + ' i (' + na[1] + ',' + na[0] + ') ∈ R';
    let nt = null;
    for (const [x, y] of R) { for (const [y2, z] of R) { if (y === y2 && !h(x, z)) { nt = [x, y, z]; break; } } if (nt) break; }
    if (nt) why.trans = '(' + nt[0] + ',' + nt[1] + '), (' + nt[1] + ',' + nt[2] + ') ∈ R, ale (' + nt[0] + ',' + nt[2] + ') ∉ R';
    const nf = S.find((x) => R.filter((p) => p[0] === x).length > 1);
    if (nf) why.func = 'prvek ' + nf + ' má více obrazů: ' + R.filter((p) => p[0] === nf).map(pairStr).join(', ');
    const p = { refl: !why.refl, sym: !why.sym, anti: !why.anti, trans: !why.trans, func: !why.func };
    p.equiv = p.refl && p.sym && p.trans; p.order = p.refl && p.anti && p.trans;
    return { p, why };
  }
  function transClosure(S, R) {
    const has = new Set(R.map(pkey));
    for (const k of S) for (const i of S) for (const j of S) if (has.has(i + '|' + k) && has.has(k + '|' + j)) has.add(i + '|' + j);
    return has;
  }
  const keysToPairs = (keys) => [...keys].map((k) => k.split('|'));
  const sortPairs = (S, P) => P.slice().sort((a, b) => S.indexOf(a[0]) - S.indexOf(b[0]) || S.indexOf(a[1]) - S.indexOf(b[1]));
  const relStr = (P) => '{ ' + P.map(pairStr).join(', ') + ' }';

  function qRelationProps(r) {
    const S = pick(r, SETS);
    const all = []; S.forEach((x) => S.forEach((y) => all.push([x, y])));
    let R;
    const mode = pick(r, ['equiv', 'order', 'func', 'random', 'equiv', 'order']);
    if (mode === 'equiv') {
      const cls = S.map(() => ri(r, 0, 2));
      R = all.filter(([x, y]) => cls[S.indexOf(x)] === cls[S.indexOf(y)]);
    } else if (mode === 'order') {
      const perm = shuffle(r, S);
      const base = all.filter(([x, y]) => perm.indexOf(x) < perm.indexOf(y) && r() < 0.45);
      R = keysToPairs(transClosure(S, base.concat(S.map((x) => [x, x]))));
    } else if (mode === 'func') {
      R = S.filter(() => r() > 0.2).map((x) => [x, pick(r, S)]);
    } else {
      R = shuffle(r, all).slice(0, ri(r, 4, 8));
    }
    if (r() < 0.55) { // drobná porucha, aby to nebylo "učebnicové"
      if (r() < 0.5 && R.length > 3) R.splice(ri(r, 0, R.length - 1), 1);
      else { const add = pick(r, all.filter((p) => !R.some((q) => pkey(q) === pkey(p)))); if (add) R.push(add); }
    }
    if (!R.length) R = [[S[0], S[1]]];
    R = shuffle(r, R);
    const { p, why } = props(S, R);
    const LIST = [
      ['refl', 'reflexivní'], ['sym', 'symetrická'], ['anti', 'antisymetrická'], ['trans', 'tranzitivní'],
      ['equiv', 'ekvivalence'], ['order', 'uspořádání'], ['func', 'zobrazení'],
    ];
    const reason = {
      equiv: p.equiv ? 'je reflexivní, symetrická a tranzitivní' : 'ekvivalence = reflexivní + symetrická + tranzitivní, něco chybí',
      order: p.order ? 'je reflexivní, antisymetrická a tranzitivní' : 'uspořádání = reflexivní + antisymetrická + tranzitivní, něco chybí',
    };
    return {
      title: 'Vlastnosti relace', points: 5, kind: 'inline',
      prompt: 'Je zadána relace R na množině {' + S.join(',') + '}. Rozhodněte, jaké má vlastnosti.<div class="fm-block">R = ' + relStr(R) + '</div>',
      rows: LIST.map(([k, name]) => ['Relace R', { sel: ['je', 'není'], ans: p[k] ? 0 : 1 }, name + '.']),
      explain: '<ul class="ex-list">' + LIST.map(([k, name]) => '<li><b>' + (p[k] ? 'je' : 'není') + ' ' + name + '</b> – ' +
        (why[k] || reason[k] || (k === 'func' ? 'každý prvek má nejvýše jeden obraz' : 'podmínka platí pro všechny dvojice')) + '</li>').join('') + '</ul>' +
        '<p class="note">Zobrazení zde (stejně jako ve výsledcích sbírky) znamená: každý prvek má <i>nejvýše jeden</i> obraz – prvek bez obrazu nevadí.</p>',
    };
  }

  function qRelationComplete(r) {
    const S = ['a', 'b', 'c', 'd'];
    const all = []; S.forEach((x) => S.forEach((y) => all.push([x, y])));
    const type = pick(r, ['equiv', 'equiv', 'trans', 'order']);
    for (let attempt = 0; attempt < 2000; attempt++) {
      let R, closure;
      if (type === 'order') {
        const perm = shuffle(r, S);
        R = shuffle(r, all.filter(([x, y]) => perm.indexOf(x) < perm.indexOf(y))).slice(0, ri(r, 3, 4));
        if (r() < 0.5) { const x = pick(r, S); R.push([x, x]); }
        closure = transClosure(S, R.concat(S.map((x) => [x, x])));
      } else {
        R = shuffle(r, all).slice(0, ri(r, 4, 6));
        if (type === 'equiv') {
          const sym = R.concat(R.map(([x, y]) => [y, x])).concat(S.map((x) => [x, x]));
          closure = transClosure(S, sym);
        } else closure = transClosure(S, R);
      }
      const Rk = new Set(R.map(pkey));
      if (Rk.size !== R.length) continue;
      const added = [...closure].filter((k) => !Rk.has(k));
      const lo = type === 'trans' ? 2 : 3;
      if (added.length < lo || added.length > 9) continue;
      if (type === 'equiv' && closure.size === 16) continue; // jedna třída = nuda
      const options = sortPairs(S, all.filter((p) => !Rk.has(pkey(p))));
      const addedSet = new Set(added);
      const TYPE_TXT = { equiv: 'jednalo o ekvivalenci', trans: 'byla výsledná relace tranzitivní', order: 'jednalo o uspořádání' };
      let extra = '';
      if (type === 'equiv') {
        const cls = []; const seen = new Set();
        S.forEach((x) => { if (seen.has(x)) return; const c = S.filter((y) => closure.has(x + '|' + y)); c.forEach((y) => seen.add(y)); cls.push('{' + c.join(',') + '}'); });
        extra = '<p>Třídy ekvivalence: <b>' + cls.join(', ') + '</b></p>';
      }
      const how = {
        equiv: 'Přidáme všechny smyčky (x,x), ke každé dvojici její obrácenou a pak doplňujeme tranzitivitu, dokud něco přibývá.',
        trans: 'Opakovaně hledáme (x,y), (y,z) ∈ R bez (x,z) a přidáme ji – i dvojice, které vzniknou až z přidaných (tranzitivní uzávěr).',
        order: 'Přidáme smyčky (x,x) pro všechny prvky a doplníme tranzitivitu. Antisymetrie už platí, takže jde o uspořádání.',
      };
      return {
        title: 'Doplnění relace', points: 5, kind: 'multi',
        prompt: 'Doplňte relaci R na množině {a,b,c,d} nejmenším počtem dvojic tak, aby se ' + TYPE_TXT[type] + '.<div class="fm-block">R = ' + relStr(sortPairs(S, R).length === R.length ? shuffle(r, R) : R) + '</div>Vyberte jednu nebo více možností:',
        options: options.map((p) => '<span class="fm">' + pairStr(p) + '</span>'),
        answer: options.map((p) => addedSet.has(pkey(p))),
        explain: '<p>' + how[type] + '</p><p>Je nutné přidat: <b>' + sortPairs(S, keysToPairs(added)).map(pairStr).join(', ') + '</b></p>' + extra,
      };
    }
  }

  // ---------- Q: slovní úloha (Vennův diagram) ----------
  const THEMES = [
    { intro: 'Na sportovním soustředění je {N} studentů. Každý si mohl zapsat fotbal, plavání a posilovnu (nebo nic).', items: ['fotbal', 'plavání', 'posilovna'], who: 'studentů', what: 'sport' , none: 'si nezapsalo nic', one: 'si zapsalo právě jeden sport', two: 'si zapsalo právě dva sporty' },
    { intro: 'Ve frontě u pokladen stojí {N} zákazníků. Sledujeme, kdo má ve vozíku pivo, jogurty a rohlíky.', items: ['pivo', 'jogurty', 'rohlíky'], who: 'zákazníků', none: 'nemá nic z toho', one: 'má právě jednu z těchto potravin', two: 'má právě dvě z těchto potravin' },
    { intro: 'V restauraci obědvá {N} turistů. Mohli si objednat polévku, hlavní jídlo a zákusek.', items: ['polévka', 'hlavní jídlo', 'zákusek'], who: 'turistů', none: 'si neobjednalo nic', one: 'si objednalo právě jednu věc', two: 'si objednalo právě dvě věci' },
    { intro: 'Ve skupině {N} studentů jsme zjišťovali, které jazyky ovládají: angličtinu, němčinu a španělštinu.', items: ['angličtina', 'němčina', 'španělština'], who: 'studentů', none: 'neovládá žádný z jazyků', one: 'ovládá právě jeden jazyk', two: 'ovládá právě dva jazyky' },
    { intro: 'Průzkumu se zúčastnilo {N} domácností. Ptali jsme se, které služby předplácí: Netflix, HBO Max a Disney+.', items: ['Netflix', 'HBO Max', 'Disney+'], who: 'domácností', none: 'nepředplácí nic', one: 'předplácí právě jednu službu', two: 'předplácí právě dvě služby' },
  ];
  function qVenn(r) {
    const th = pick(r, THEMES);
    const g = { a: ri(r, 2, 9), b: ri(r, 2, 9), c: ri(r, 1, 8), ab: ri(r, 0, 6), ac: ri(r, 0, 5), bc: ri(r, 1, 6), abc: ri(r, 1, 4), none: ri(r, 0, 6) };
    const total = Object.values(g).reduce((s, x) => s + x, 0);
    const [X, Y, Z] = th.items;
    const nA = g.a + g.ab + g.ac + g.abc, nB = g.b + g.ab + g.bc + g.abc, nC = g.c + g.ac + g.bc + g.abc;
    const pairs = [[X, Y, Z, g.ab], [X, Z, Y, g.ac], [Y, Z, X, g.bc]];
    const clues = [X + ': <b>' + nA + '</b>', Y + ': <b>' + nB + '</b>', Z + ': <b>' + nC + '</b>'];
    pairs.forEach(([p, q, o, only]) => {
      if (r() < 0.5) clues.push(p + ' i ' + q + ' (případně i ' + o + '): <b>' + (only + g.abc) + '</b>');
      else clues.push(p + ' i ' + q + ', ale ne ' + o + ': <b>' + only + '</b>');
    });
    clues.push('všechny tři: <b>' + g.abc + '</b>');
    const one = g.a + g.b + g.c, two = g.ab + g.ac + g.bc;
    return {
      title: 'Slovní úloha s množinami', points: 6, kind: 'inline',
      prompt: th.intro.replace('{N}', '<b>' + total + '</b>') + ' Víme:<ul class="clues">' + clues.map((c) => '<li>' + c + '</li>').join('') + '</ul>',
      rows: [
        ['Kolik ' + th.who + ' ' + th.none + '?', { num: true, ans: g.none }],
        ['Kolik ' + th.who + ' ' + th.one + '?', { num: true, ans: one }],
        ['Kolik ' + th.who + ' ' + th.two + '?', { num: true, ans: two }],
      ],
      explain: '<p>Nakreslíme Vennův diagram a plníme ho od středu ven:</p><ul class="ex-list">' +
        '<li>všechny tři: <b>' + g.abc + '</b></li>' +
        '<li>jen ' + X + ' a ' + Y + ': <b>' + g.ab + '</b>, jen ' + X + ' a ' + Z + ': <b>' + g.ac + '</b>, jen ' + Y + ' a ' + Z + ': <b>' + g.bc + '</b></li>' +
        '<li>jen ' + X + ': ' + nA + ' − ' + g.ab + ' − ' + g.ac + ' − ' + g.abc + ' = <b>' + g.a + '</b>; jen ' + Y + ': <b>' + g.b + '</b>; jen ' + Z + ': <b>' + g.c + '</b></li>' +
        '<li>nic: ' + total + ' − ' + (total - g.none) + ' = <b>' + g.none + '</b></li></ul>' +
        '<p>Právě jedna: ' + g.a + ' + ' + g.b + ' + ' + g.c + ' = <b>' + one + '</b>; právě dvě: ' + g.ab + ' + ' + g.ac + ' + ' + g.bc + ' = <b>' + two + '</b>.</p>' +
        '<p class="note">Pozor na rozdíl „X i Y“ (zahrnuje i ty, co mají všechny tři) vs. „X i Y, ale ne Z“.</p>',
    };
  }

  // ---------- Sestavení testu ----------
  const BUILDERS = [qFormulaType, qMinDNF, qSets, qRelationProps, qRelationComplete, qEquivalence, qConsequence, qVenn];

  function generate(seed) {
    const questions = BUILDERS.map((b, i) => {
      const q = b(mulberry32(seed * 7919 + i * 104729 + 17));
      q.id = 'q' + (i + 1);
      return q;
    });
    return { timeLimitMin: 50, questions };
  }

  window.CZU_GENERATORS = window.CZU_GENERATORS || {};
  window.CZU_GENERATORS.mlg = generate;
  if (typeof module !== 'undefined') module.exports = { generate, _internal: { minimalDNF, props, transClosure, inSet, show, tv } };
})();
