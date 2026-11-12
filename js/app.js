/* Code de la route — appli de révision (sans framework). */
(function () {
  const REPO = "nathancuretti/permis-de-conduire";
  const EXAM_N = 40, EXAM_PASS = 35, EXAM_SECONDS = 20;
  const LETTERS = "ABCD";

  const $main = document.getElementById("app");
  let $app = $main;          // conteneur de la vue en cours (page ou fenêtre)
  let modal = null;          // fenêtre ouverte : { el, title }
  const $title = document.getElementById("title");
  const $back = document.getElementById("back");
  const $topRight = document.getElementById("topRight");

  let META = null;           // data/themes.json
  let Q = [];                // toutes les questions
  let BYID = {};
  let CHAP_OF = {};          // notion -> chapitre
  let THEME_OF = {};         // notion -> thème
  let session = null;        // série en cours
  let timer = null;

  // ---------- utilitaires ----------
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const shuffle = (a) => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);
  function toast(msg) {
    const t = document.createElement("div"); t.className = "toast"; t.textContent = msg;
    document.body.appendChild(t); setTimeout(() => t.remove(), 2200);
  }
  function setHeader(title, back) {
    if (modal) { modal.el.querySelector(".m-title").textContent = title; return; }
    $title.textContent = title;
    $back.hidden = !back;
    $back.onclick = back || null;
    $topRight.textContent = "";
  }
  function stopTimer() { if (timer) { clearInterval(timer); timer = null; } }

  // ---------- chargement ----------
  async function load() {
    META = await (await fetch("data/themes.json", { cache: "no-cache" })).json();
    const lists = await Promise.all(META.fichiers.map((f) => fetch(f, { cache: "no-cache" }).then((r) => r.json())));
    Q = lists.flat();
    for (const t of META.themes) for (const c of t.chapitres) for (const n of c.notions) { CHAP_OF[n.id] = c.code; THEME_OF[n.id] = t.code; }
    Q.forEach((q) => { BYID[q.id] = q; q.chap = CHAP_OF[q.n]; q.theme = THEME_OF[q.n]; });
    window.addEventListener("hashchange", route);
    route();
  }

  // Pages intermédiaires affichées en fenêtre par-dessus l'accueil.
  const MODALS = [["choisir", () => viewChoose()], ["erreurs", () => viewErrors()], ["examens", () => viewExams()],
    ["reglages", () => viewSettings()], ["theme/", (h) => viewTheme(h.slice(6))]];

  function closeModal() {
    if (!modal) return;
    modal.el.remove(); modal = null; $app = $main;
    document.body.classList.remove("modal-open");
  }
  function openModal(render, h) {
    const keepScroll = window.scrollY;
    viewHome();
    window.scrollTo(0, keepScroll);
    const el = document.createElement("div");
    el.className = "overlay";
    el.innerHTML = `<div class="sheet" role="dialog" aria-modal="true">
        <div class="m-head"><span class="m-title"></span><button class="m-close" aria-label="Fermer">✕</button></div>
        <div class="m-body"></div></div>`;
    document.body.appendChild(el);
    document.body.classList.add("modal-open");
    modal = { el };
    $app = el.querySelector(".m-body");
    el.onclick = (e) => { if (e.target === el) go(""); };
    el.querySelector(".m-close").onclick = () => go("");
    document.onkeydown = (e) => { if (e.key === "Escape") go(""); };
    render(h);
  }

  function route() {
    stopTimer();
    document.onkeydown = null;
    closeModal();
    const h = location.hash.slice(1);
    const m = MODALS.find(([k]) => (k.endsWith("/") ? h.startsWith(k) : h === k));
    if (m) return openModal(m[1], h);
    if (h === "quiz" && session) return viewQuestion();
    if (h === "resultat" && session) return viewResult();
    return viewHome();
  }
  const go = (h) => { if (location.hash === "#" + h) route(); else location.hash = h; };

  // ---------- accueil ----------
  function counts(qs) {
    const c = { n: qs.length, master: 0, ok: 0, err: 0, new: 0 };
    qs.forEach((q) => c[Store.status(q.id)]++);
    return c;
  }
  const bar = (c) => `<div class="bar">${["master", "ok", "err"].map((k) => `<i class="c-${k}" style="width:${(100 * c[k]) / (c.n || 1)}%"></i>`).join("")}</div>`;

  function viewHome() {
    setHeader("Code de la route");
    const errors = Q.filter((q) => Store.isError(q.id));
    const due = Q.filter((q) => Store.isDue(q.id) && !Store.isError(q.id));
    const all = counts(Q);
    const exams = Store.exams();
    const last = exams[exams.length - 1];

    let themes = "";
    for (const t of META.themes) {
      const qs = Q.filter((q) => q.theme === t.code), c = counts(qs);
      const chaps = t.chapitres.map((ch) => {
        const cq = qs.filter((q) => q.chap === ch.code);
        return cq.length ? `<div><span>${esc(ch.nom)}</span><span>${counts(cq).master}/${cq.length}</span></div>` : "";
      }).join("");
      themes += `
        <div class="theme ${c.n ? "" : "empty"}" data-t="${t.code}" role="button" tabindex="0">
          <div class="code">${t.num}</div>
          <div class="info">
            <div class="name">${esc(t.nom)}</div>
            <div class="meta">${c.n ? `${c.n} questions · ${c.master} maîtrisées · ${c.ok} réussies · ${c.err} ratées` : "Bientôt disponible"}</div>
            ${c.n ? bar(c) : ""}
            ${t.chapitres.filter((ch) => qs.some((q) => q.chap === ch.code)).length > 1 ? `<div class="chaps">${chaps}</div>` : ""}
          </div>
        </div>`;
    }

    $app.innerHTML = `
      <div class="layout home">
        <div class="a">
          <div class="card">
            <div class="stats">
              <div><b>${all.n - all.new}<small>/${all.n}</small></b><span>vues</span></div>
              <div><b>${pct(all.master, all.n)}%</b><span>maîtrisées</span></div>
              <div class="click" id="bLast" role="button" tabindex="0"><b class="${last ? (passed(last) ? "t-ok" : "t-ko") : ""}">${last ? last.score + "<small>/" + last.n + "</small>" : "–"}</b><span>dernier examen ›</span></div>
            </div>
            ${bar(all)}
            <div class="legend">
              <span><i class="c-master"></i>maîtrisées (2 bonnes d'affilée)</span>
              <span><i class="c-ok"></i>réussies</span>
              <span><i class="c-err"></i>ratées</span>
            </div>
          </div>
          <button class="btn" id="bExam">Examen blanc <small>· ${Math.min(EXAM_N, Q.length)} questions · ${EXAM_SECONDS} s</small></button>
          <div class="row">
            <button class="btn secondary" id="bErr" ${errors.length ? "" : "disabled"}>Mes erreurs <small>(${errors.length})</small></button>
            <button class="btn secondary" id="bDue" ${due.length ? "" : "disabled"}>À revoir <small>(${due.length})</small></button>
          </div>
          <button class="btn ghost" id="bChoose">Réviser par chapitres</button>
        </div>
        <div class="s">
          <h2 class="page-title">Thèmes<small>Clique sur un thème pour voir tes statistiques et le réviser</small></h2>
          <div class="themes">${themes}</div>
        </div>
        <div class="b">
          <div style="height:14px"></div>
          ${exams.length ? examHistory(exams.slice(-3), true) : ""}
          <button class="btn ghost" id="bSet">Réglages et sauvegarde</button>
        </div>
      </div>`;
    document.getElementById("bExam").onclick = () => startExam();
    document.getElementById("bErr").onclick = () => go("erreurs");
    document.getElementById("bLast").onclick = () => go("examens");
    document.getElementById("bDue").onclick = () => start(shuffle(due), "À revoir", false);
    document.getElementById("bChoose").onclick = () => go("choisir");
    document.getElementById("bSet").onclick = () => go("reglages");
    $app.querySelectorAll(".theme[data-t]").forEach((el) => {
      el.onclick = () => { if (!el.classList.contains("empty")) go("theme/" + el.dataset.t); };
    });
  }

  const needFor = (n) => Math.ceil((n * EXAM_PASS) / EXAM_N);
  const passed = (e) => e.score >= needFor(e.n);
  const scopeName = (e) => (!e.scope || e.scope === "all") ? "Examen blanc complet" : "Examen · " + e.scope.map((c) => (META.themes.find((t) => t.code === c) || { nom: "ancien thème " + c }).nom).join(", ");
  const fmtDate = (ts) => { const d = new Date(ts); return `${d.toLocaleDateString("fr-FR")} ${d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}`; };

  function examRows(list) {
    return list.slice().reverse().map((e) => `<div class="rev">
        <div class="dot ${passed(e) ? "ok" : "ko"}">${passed(e) ? "✓" : "✗"}</div>
        <div class="t"><b>${e.score}/${e.n}</b> <span class="muted">· ${esc(scopeName(e))}</span><div class="muted">${fmtDate(e.ts)}</div></div></div>`).join("");
  }
  function examHistory(list, link) {
    return `<div class="card"><h2>Derniers examens</h2>${examRows(list)}
      ${link ? `<button class="btn ghost" style="margin:10px 0 0" onclick="location.hash='examens'">Voir les 20 dernières notes</button>` : ""}</div>`;
  }

  // ---------- historique des examens ----------
  function viewExams() {
    setHeader("Mes examens", () => go(""));
    const list = Store.exams().slice(-20);
    if (!list.length) {
      $app.innerHTML = `<div class="narrow"><div class="card"><p class="muted">Aucun examen pour l'instant.</p>
        <button class="btn" id="bE">Lancer un examen blanc</button></div></div>`;
      document.getElementById("bE").onclick = () => startExam();
      return;
    }
    const pcts = list.map((e) => e.score / e.n);
    const avg = Math.round((100 * pcts.reduce((a, b) => a + b, 0)) / pcts.length);
    const nPass = list.filter(passed).length;
    const W = 600, H = 180, pad = 24, bw = (W - pad) / 20;
    const yPass = H - (H - 20) * (EXAM_PASS / EXAM_N);
    const bars = list.map((e, i) => {
      const h = (H - 20) * (e.score / e.n);
      return `<rect x="${pad + i * bw + 3}" y="${H - h}" width="${bw - 6}" height="${h}" rx="3" class="${passed(e) ? "b-ok" : "b-ko"}"><title>${e.score}/${e.n} · ${fmtDate(e.ts)}</title></rect>`;
    }).join("");
    $app.innerHTML = `<div class="narrow">
      <h2 class="page-title">Mes 20 dernières notes</h2>
      <div class="card">
        <div class="stats">
          <div><b>${list.length}</b><span>examens</span></div>
          <div><b>${avg}%</b><span>moyenne</span></div>
          <div><b>${nPass}<small>/${list.length}</small></b><span>réussis</span></div>
        </div>
        <svg class="chart" viewBox="0 0 ${W} ${H + 4}" preserveAspectRatio="none" role="img" aria-label="Notes des derniers examens">
          ${bars}
          <line x1="${pad}" x2="${W}" y1="${yPass}" y2="${yPass}" class="pass-line"/>
          <text x="0" y="${yPass + 4}" class="pass-txt">35</text>
        </svg>
        <div class="legend"><span><i class="c-master"></i>réussi</span><span><i class="c-err"></i>échoué</span><span>— seuil 35/40</span></div>
      </div>
      <div class="card"><h2>Détail</h2>${examRows(list)}</div>
      <button class="btn" id="bE">Nouvel examen blanc</button></div>`;
    document.getElementById("bE").onclick = () => startExam();
  }

  // ---------- page d'un thème ----------
  function viewTheme(code) {
    const t = META.themes.find((x) => x.code === code);
    if (!t) return go("");
    setHeader(t.nom, () => go(""));
    const qs = Q.filter((q) => q.theme === code), c = counts(qs);
    const errs = qs.filter((q) => Store.isError(q.id));
    const ex = Store.exams().filter((e) => Array.isArray(e.scope) && e.scope.length === 1 && e.scope[0] === code).slice(-5);
    const chaps = t.chapitres.map((ch) => {
      const cq = qs.filter((q) => q.chap === ch.code);
      if (!cq.length) return "";
      const cc = counts(cq);
      return `<div class="chap-row">
        <div class="t"><div>${esc(ch.nom)}</div>
          <div class="muted">${cc.n} questions · ${cc.master} maîtrisées · ${cc.ok} réussies · ${cc.err} ratées · ${cc.new} jamais vues</div>${bar(cc)}</div>
        <button class="mini" data-chap="${ch.code}">Réviser</button></div>`;
    }).join("");
    $app.innerHTML = `<div class="narrow">
      <h2 class="page-title">${esc(t.nom)}</h2>
      <div class="card">
        <div class="stats four">
          <div><b>${pct(c.master, c.n)}%</b><span>maîtrisées</span></div>
          <div><b>${c.ok}</b><span>réussies</span></div>
          <div><b class="${c.err ? "t-ko" : ""}">${c.err}</b><span>ratées</span></div>
          <div><b>${c.new}</b><span>jamais vues</span></div>
        </div>
        ${bar(c)}
        <div class="legend"><span><i class="c-master"></i>maîtrisées</span><span><i class="c-ok"></i>réussies</span><span><i class="c-err"></i>ratées</span><span><i class="c-new"></i>jamais vues</span></div>
      </div>
      <div class="card"><h2>Chapitres</h2>${chaps}</div>
      ${ex.length ? `<div class="card"><h2>Examens sur ce thème</h2>${examRows(ex)}</div>` : ""}
      <div class="sticky-actions">
        <div class="row">
          <button class="btn" id="bRev">Réviser <small>· 20 q</small></button>
          <button class="btn secondary" id="bTx">Examen <small>· ${Math.min(EXAM_N, qs.length)} q · 20 s</small></button>
        </div>
        ${errs.length ? `<button class="btn ghost" id="bTe">Revoir mes ${errs.length} erreur${errs.length > 1 ? "s" : ""} de ce thème</button>` : ""}
      </div></div>`;
    document.getElementById("bRev").onclick = () => start(pickTraining(qs, 20), t.nom, false);
    document.getElementById("bTx").onclick = () => startExam([code]);
    const bTe = document.getElementById("bTe");
    if (bTe) bTe.onclick = () => start(shuffle(errs), "Erreurs · " + t.nom, false);
    $app.querySelectorAll("button[data-chap]").forEach((b) => b.onclick = () => {
      const ch = t.chapitres.find((x) => x.code === b.dataset.chap);
      start(pickTraining(qs.filter((q) => q.chap === ch.code), 20), ch.nom, false);
    });
  }

  // ---------- mes erreurs ----------
  function viewErrors() {
    setHeader("Mes erreurs", () => go(""));
    const errs = Q.filter((q) => Store.isError(q.id));
    const sel = new Set(META.themes.map((t) => t.code).filter((c) => errs.some((q) => q.theme === c)));
    let rows = "";
    for (const t of META.themes) {
      const te = errs.filter((q) => q.theme === t.code);
      if (!te.length) continue;
      const detail = t.chapitres.map((ch) => { const n = te.filter((q) => q.chap === ch.code).length; return n ? `${esc(ch.nom)} : ${n}` : ""; }).filter(Boolean).join(" · ");
      rows += `<label class="err-row"><input type="checkbox" data-t="${t.code}" checked>
        <div class="t"><div><b>${esc(t.nom)}</b></div><div class="muted">${detail}</div></div>
        <span class="count">${te.length}</span></label>`;
    }
    $app.innerHTML = `<div class="narrow">
      <h2 class="page-title">Mes erreurs<small>Une question sort de cette liste après 2 bonnes réponses d'affilée</small></h2>
      <div class="card"><h2>Erreurs par thème</h2>${rows || `<p class="muted">Aucune erreur en cours. 👏</p>`}</div>
      <div class="sticky-actions"><button class="btn" id="go"></button></div></div>`;
    const btn = document.getElementById("go");
    const sync = () => {
      const n = errs.filter((q) => sel.has(q.theme)).length;
      btn.disabled = !n;
      btn.textContent = n ? `Revoir ${n} erreur${n > 1 ? "s" : ""}` : "Choisis au moins un thème";
    };
    $app.querySelectorAll("input[data-t]").forEach((b) => b.onchange = () => { b.checked ? sel.add(b.dataset.t) : sel.delete(b.dataset.t); sync(); });
    btn.onclick = () => start(shuffle(errs.filter((q) => sel.has(q.theme))), "Mes erreurs", false);
    sync();
  }

  // Ordre de priorité en entraînement : erreurs, puis à revoir, puis jamais vues, puis le reste.
  function pickTraining(qs, n) {
    const rank = (q) => (Store.isError(q.id) ? 0 : Store.isDue(q.id) ? 1 : Store.isNew(q.id) ? 2 : 3);
    const sorted = shuffle(qs).sort((a, b) => rank(a) - rank(b));
    return n ? shuffle(sorted.slice(0, n)) : shuffle(sorted);
  }

  // ---------- choix des chapitres ----------
  const choice = { chaps: null, n: 20, filtre: "toutes", mode: "train" };

  function viewChoose() {
    setHeader("Réviser", () => go(""));
    if (!choice.chaps) choice.chaps = new Set();
    let html = `<div class="layout choose"><div><h2 class="page-title">Réviser par chapitres</h2><div class="card"><h2>Chapitres</h2>`;
    for (const t of META.themes) {
      const tq = Q.filter((q) => q.theme === t.code).length;
      if (!tq) continue;
      html += `<details class="sel"><summary>
          <input type="checkbox" data-theme="${t.code}">
          <span class="name">${t.num} · ${esc(t.nom)}</span><span class="n">${tq}</span><span class="chev">›</span></summary>`;
      for (const c of t.chapitres) {
        const cq = Q.filter((q) => q.chap === c.code).length;
        if (!cq) continue;
        html += `<label class="chk"><input type="checkbox" data-chap="${c.code}" ${choice.chaps.has(c.code) ? "checked" : ""}>
          ${esc(c.nom)}<span class="n">${cq}</span></label>`;
      }
      html += `</details>`;
    }
    html += `</div></div>
      <div class="opts"><div class="card">
        <div class="label">Mode</div>
        <div class="seg" id="segM">
          ${[["train", "Entraînement"], ["exam", "Examen chronométré"]].map(([k, l]) => `<button data-v="${k}" class="${choice.mode === k ? "on" : ""}">${l}</button>`).join("")}
        </div>
        <div class="label">Questions</div>
        <div class="seg" id="segF">
          ${[["toutes", "Toutes"], ["nouvelles", "Jamais vues"], ["erreurs", "Ratées"], ["revoir", "À revoir"]].map(([k, l]) => `<button data-v="${k}" class="${choice.filtre === k ? "on" : ""}">${l}</button>`).join("")}
        </div>
        <div class="label">Nombre</div>
        <div class="seg" id="segN">
          ${[[10, "10"], [20, "20"], [40, "40"], [0, "Toutes"]].map(([k, l]) => `<button data-v="${k}" class="${choice.n === k ? "on" : ""}">${l}</button>`).join("")}
        </div>
      </div>
      <div class="sticky-actions"><button class="btn" id="go"></button></div></div></div>`;
    $app.innerHTML = html;

    const syncThemes = () => {
      $app.querySelectorAll("input[data-theme]").forEach((tb) => {
        const boxes = [...tb.closest("details").querySelectorAll("input[data-chap]")];
        const on = boxes.filter((b) => b.checked).length;
        tb.checked = on === boxes.length && on > 0;
        tb.indeterminate = on > 0 && on < boxes.length;
      });
      const pool = poolFor();
      const n = choice.n ? Math.min(choice.n, pool.length) : pool.length;
      const btn = document.getElementById("go");
      btn.disabled = !pool.length;
      btn.textContent = pool.length ? `${choice.mode === "exam" ? "Lancer l'examen" : "Commencer"} · ${n} question${n > 1 ? "s" : ""}` : "Aucune question pour cette sélection";
    };
    $app.querySelectorAll("input[data-chap]").forEach((b) => {
      b.onchange = () => { b.checked ? choice.chaps.add(b.dataset.chap) : choice.chaps.delete(b.dataset.chap); syncThemes(); };
    });
    $app.querySelectorAll("input[data-theme]").forEach((tb) => {
      tb.onclick = (e) => e.stopPropagation();
      tb.onchange = () => {
        tb.closest("details").querySelectorAll("input[data-chap]").forEach((b) => {
          b.checked = tb.checked; tb.checked ? choice.chaps.add(b.dataset.chap) : choice.chaps.delete(b.dataset.chap);
        });
        syncThemes();
      };
    });
    const seg = (id, key, conv) => document.querySelectorAll(`#${id} button`).forEach((b) => {
      b.onclick = () => { choice[key] = conv(b.dataset.v); document.querySelectorAll(`#${id} button`).forEach((x) => x.classList.toggle("on", x === b)); syncThemes(); };
    });
    seg("segF", "filtre", (v) => v);
    seg("segN", "n", (v) => +v);
    seg("segM", "mode", (v) => v);
    document.getElementById("go").onclick = () => {
      const pool = poolFor();
      if (choice.mode === "exam") {
        const scope = [...new Set(pool.map((q) => q.theme))];
        start(shuffle(pool).slice(0, choice.n || pool.length), "Examen", true, scope);
      } else start(pickTraining(pool, choice.n), "Entraînement", false);
    };
    syncThemes();
  }

  function poolFor() {
    let qs = Q.filter((q) => choice.chaps.has(q.chap));
    if (choice.filtre === "nouvelles") qs = qs.filter((q) => Store.isNew(q.id));
    if (choice.filtre === "erreurs") qs = qs.filter((q) => Store.isError(q.id));
    if (choice.filtre === "revoir") qs = qs.filter((q) => Store.isDue(q.id));
    return qs;
  }

  // ---------- session de questions ----------
  function startExam(themes) {
    // Examen complet (tous thèmes) ou limité à des thèmes ; priorité aux questions jamais vues.
    const pool = shuffle(themes ? Q.filter((q) => themes.includes(q.theme)) : Q);
    const rank = (q) => (Store.isNew(q.id) ? 0 : 1);
    const picked = pool.sort((a, b) => rank(a) - rank(b)).slice(0, EXAM_N);
    start(shuffle(picked), themes ? "Examen · " + themes.map((c) => META.themes.find((t) => t.code === c).nom).join(", ") : "Examen blanc", true, themes || "all");
  }

  function start(qs, label, exam, scope) {
    if (!qs.length) return;
    session = {
      label, exam, scope, i: 0,
      items: qs.map((q) => ({ q, order: shuffle(q.c.map((_, k) => k)), picked: new Set(), done: false, ok: null })),
    };
    go("quiz");
  }

  function viewQuestion() {
    const s = session, it = s.items[s.i], q = it.q;
    setHeader(s.label, () => { if (confirm("Quitter la série en cours ?")) { session = null; go(""); } });
    const isSvg = q.img && q.img.endsWith(".svg");
    const isSchema = q.img && q.img.includes("/schemas/");
    let html = `
      <div class="layout quiz ${q.img ? "" : "no-img"}">
      ${q.img ? `<div class="q-media"><div class="media ${isSvg && !isSchema ? "signe" : ""}"><img src="${esc(q.img)}" alt="" class="${isSvg ? "svg" : ""} ${isSchema ? "schema" : ""}">${q.credit ? `<div class="credit">${esc(q.credit)}</div>` : ""}</div></div>` : ""}
      <div class="q-body">
      <div class="qhead">
        <span>${s.i + 1}/${s.items.length}</span>
        <div class="prog"><i style="width:${pct(s.i, s.items.length)}%"></i></div>
        <button class="flag" id="flag" title="Signaler un problème sur cette question">🚩</button>
      </div>
      <div class="qtext">${esc(q.q)}</div>
      <div class="hint">Une ou plusieurs réponses possibles</div>
      <div id="choices">`;
    it.order.forEach((k, pos) => {
      html += `<button class="choice" data-k="${k}"><span class="letter">${LETTERS[pos]}</span><span>${esc(q.c[k])}</span></button>`;
    });
    html += `</div><div id="after"></div>
      <div class="sticky-actions"><button class="btn" id="valid" disabled>Valider</button></div>
      <div class="kbd">Clavier : A B C D pour répondre · Entrée pour valider</div>
      </div></div>`;
    $app.innerHTML = html;
    window.scrollTo(0, 0);

    const btns = [...$app.querySelectorAll(".choice")];
    const valid = document.getElementById("valid");
    const refresh = () => {
      btns.forEach((b) => b.classList.toggle("on", it.picked.has(+b.dataset.k)));
      valid.disabled = !it.picked.size;
    };
    btns.forEach((b) => b.onclick = () => {
      if (it.done) return;
      const k = +b.dataset.k;
      it.picked.has(k) ? it.picked.delete(k) : it.picked.add(k);
      refresh();
    });
    refresh();
    document.getElementById("flag").onclick = () => flag(q, it);
    document.onkeydown = (e) => {
      if (location.hash !== "#quiz" || e.metaKey || e.ctrlKey || e.altKey) return;
      const pos = LETTERS.indexOf(e.key.toUpperCase());
      if (pos >= 0 && pos < btns.length) { btns[pos].click(); e.preventDefault(); }
      else if (e.key === "Enter" && !valid.disabled) { valid.click(); e.preventDefault(); }
    };
    valid.onclick = () => submit();

    if (s.exam) {
      let left = EXAM_SECONDS;
      const tick = () => { $topRight.textContent = `${left}s`; $topRight.className = "top-right timer" + (left <= 5 ? " low" : ""); };
      tick();
      timer = setInterval(() => { left--; tick(); if (left <= 0) { stopTimer(); submit(); } }, 1000);
    }

    function submit() {
      if (it.done) return;
      stopTimer();
      it.done = true;
      const good = new Set(q.ok);
      it.ok = it.picked.size === good.size && [...it.picked].every((k) => good.has(k));
      Store.record(q.id, it.ok);
      if (s.exam) return next();
      // correction immédiate
      btns.forEach((b) => {
        const k = +b.dataset.k, sel = it.picked.has(k), g = good.has(k);
        b.classList.remove("on");
        if (g && sel) b.classList.add("good");
        else if (g) b.classList.add("good", "missed");
        else if (sel) b.classList.add("bad");
        b.disabled = true;
      });
      document.getElementById("after").innerHTML = `
        <div class="verdict ${it.ok ? "ok" : "ko"}">${it.ok ? "✓ Bonne réponse" : "✗ Mauvaise réponse"}</div>
        <div class="expl">${esc(q.ex)}${q.src ? `<span class="src">Source : ${esc(q.src)}</span>` : ""}</div>`;
      document.getElementById("after").scrollIntoView({ behavior: "smooth", block: "nearest" });
      valid.disabled = false;
      valid.textContent = s.i + 1 < s.items.length ? "Question suivante" : "Voir le résultat";
      valid.onclick = next;
    }
    function next() {
      if (s.i + 1 < s.items.length) { s.i++; viewQuestion(); }
      else {
        if (s.exam) Store.addExam(s.items.filter((x) => x.ok).length, s.items.length, s.scope);
        go("resultat");
      }
    }
  }

  function viewResult() {
    const s = session;
    setHeader("Résultat", () => { session = null; go(""); });
    const score = s.items.filter((x) => x.ok).length, n = s.items.length;
    const need = s.exam ? needFor(n) : null;
    const pass = s.exam ? score >= need : score / n >= EXAM_PASS / EXAM_N;
    const wrong = s.items.filter((x) => !x.ok).map((x) => x.q);
    let html = `
      <div class="layout result"><div class="a">
      <div class="card score ${pass ? "pass" : "fail"}">
        <b>${score}/${n}</b>
        ${s.exam ? (pass ? "Examen réussi 🎉" : `Échec : il faut ${need} bonnes réponses`) : `${pct(score, n)}% de bonnes réponses`}
      </div>
      ${wrong.length ? `<button class="btn" id="redo">Rejouer mes ${wrong.length} erreur${wrong.length > 1 ? "s" : ""}</button>` : ""}
      <button class="btn ghost" id="home">Accueil</button>
      </div><div><div class="card"><h2>Correction</h2>`;
    s.items.forEach((x, i) => {
      const q = x.q;
      const mine = x.order.filter((k) => x.picked.has(k)).map((k) => LETTERS[x.order.indexOf(k)]).join(", ") || "aucune";
      const right = x.order.filter((k) => q.ok.includes(k)).map((k) => LETTERS[x.order.indexOf(k)]).join(", ");
      html += `<div class="rev" data-i="${i}">
        <div class="dot ${x.ok ? "ok" : "ko"}">${x.ok ? "✓" : "✗"}</div>
        <div class="t"><div>${esc(q.q)}</div>
          <div class="muted">Votre réponse : ${mine} · Bonne réponse : ${right}</div>
          <div class="more" hidden>
            ${q.img ? `<div class="media" style="margin-top:8px"><img src="${esc(q.img)}" alt="" class="${q.img.endsWith(".svg") ? "svg" : ""}" style="height:auto;max-height:22vh"></div>` : ""}
            ${x.order.map((k, pos) => `<div class="muted">${LETTERS[pos]}. ${esc(q.c[k])}${q.ok.includes(k) ? " ✓" : ""}</div>`).join("")}
            <div class="expl">${esc(q.ex)}${q.src ? `<span class="src">Source : ${esc(q.src)}</span>` : ""}</div>
          </div></div></div>`;
    });
    html += `</div></div></div>`;
    $app.innerHTML = html;
    window.scrollTo(0, 0);
    const redo = document.getElementById("redo");
    if (redo) redo.onclick = () => start(shuffle(wrong), "Mes erreurs", false);
    document.getElementById("home").onclick = () => { session = null; go(""); };
    $app.querySelectorAll(".rev").forEach((r) => r.onclick = () => { const m = r.querySelector(".more"); m.hidden = !m.hidden; });
  }

  // ---------- signalement ----------
  function flag(q, it) {
    const lines = [
      `**Question** \`${q.id}\` (notion \`${q.n}\`)`, "",
      `> ${q.q}`, "",
      ...q.c.map((c, k) => `- ${q.ok.includes(k) ? "✅" : "▫️"} ${c}`), "",
      q.img ? `Image : \`${q.img}\`` : "",
      it && it.picked.size ? `Ma réponse : ${[...it.picked].map((k) => q.c[k]).join(" / ")}` : "",
      "", "**Problème :** ",
    ].filter((l, i, a) => l !== "" || a[i - 1] !== "");
    const url = `https://github.com/${REPO}/issues/new?title=${encodeURIComponent("[Question] " + q.id)}&body=${encodeURIComponent(lines.join("\n"))}`;
    window.open(url, "_blank", "noopener");
  }

  // ---------- réglages ----------
  function viewSettings() {
    setHeader("Réglages", () => go(""));
    let theme = "auto";
    try { theme = localStorage.getItem("permis.theme") || "auto"; } catch (e) {}
    $app.innerHTML = `<div class="narrow">
      <div class="card"><h2>Apparence</h2>
        <div class="seg" id="segT" style="margin:0">
          ${[["auto", "Automatique"], ["light", "Clair"], ["dark", "Sombre"]].map(([k, l]) => `<button data-v="${k}" class="${theme === k ? "on" : ""}">${l}</button>`).join("")}
        </div>
      </div>
      <div class="card"><h2>Sauvegarde</h2>
        <p class="muted">Ta progression est enregistrée dans ce navigateur. Exporte-la de temps en temps (ou pour changer d'appareil).</p>
        <button class="btn secondary" id="exp">Exporter ma progression</button>
        <button class="btn secondary" id="imp">Importer une sauvegarde</button>
        <input type="file" id="file" accept="application/json,.json" hidden>
      </div>
      <div class="card"><h2>Contenu</h2>
        <p class="muted">${Q.length} questions · ${META.themes.reduce((a, t) => a + t.chapitres.reduce((b, c) => b + c.notions.filter((n) => n.q).length, 0), 0)} notions couvertes sur ${META.themes.reduce((a, t) => a + t.chapitres.reduce((b, c) => b + c.notions.length, 0), 0)}.</p>
        <p class="muted">Le 🚩 en haut de chaque question ouvre un ticket GitHub pour signaler une erreur.</p>
        <p class="muted">Photos : Panoramax (licences indiquées sous chaque photo). Panneaux et schémas dessinés pour l'appli.</p>
      </div>
      <div class="card"><h2>Zone sensible</h2>
        <button class="btn ghost" id="reset" style="color:var(--ko)">Effacer toute ma progression</button>
      </div></div>`;
    document.querySelectorAll("#segT button").forEach((b) => b.onclick = () => {
      const v = b.dataset.v;
      try { v === "auto" ? localStorage.removeItem("permis.theme") : localStorage.setItem("permis.theme", v); } catch (e) {}
      if (v === "auto") delete document.documentElement.dataset.theme; else document.documentElement.dataset.theme = v;
      document.querySelectorAll("#segT button").forEach((x) => x.classList.toggle("on", x === b));
    });
    document.getElementById("exp").onclick = () => {
      const blob = new Blob([Store.export()], { type: "application/json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `permis-progression-${new Date().toISOString().slice(0, 10)}.json`;
      a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    };
    const file = document.getElementById("file");
    document.getElementById("imp").onclick = () => file.click();
    file.onchange = async () => {
      try { Store.import(await file.files[0].text()); toast("Progression importée"); }
      catch (e) { toast("Fichier invalide"); }
    };
    document.getElementById("reset").onclick = () => {
      if (confirm("Effacer toute la progression ? Cette action est définitive.")) { Store.reset(); toast("Progression effacée"); }
    };
  }

  // ---------- démarrage ----------
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
  }
  load().catch((e) => { $app.innerHTML = `<p class="loading">Impossible de charger les questions.<br>${esc(e.message)}</p>`; });
})();
