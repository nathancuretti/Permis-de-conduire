/* Code de la route — appli de révision (sans framework). */
(function () {
  const REPO = "nathancuretti/permis-de-conduire";
  const EXAM_N = 40, EXAM_PASS = 35, EXAM_SECONDS = 20;
  const LETTERS = "ABCD";

  const $app = document.getElementById("app");
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

  function route() {
    stopTimer();
    const h = location.hash.slice(1);
    if (h === "choisir") return viewChoose();
    if (h === "reglages") return viewSettings();
    if (h === "quiz" && session) return viewQuestion();
    if (h === "resultat" && session) return viewResult();
    return viewHome();
  }
  const go = (h) => { if (location.hash === "#" + h) route(); else location.hash = h; };

  // ---------- accueil ----------
  function themeStats(code) {
    const qs = Q.filter((q) => q.theme === code);
    let master = 0, seen = 0;
    qs.forEach((q) => { const s = Store.status(q.id); if (s === "master") master++; else if (s !== "new") seen++; });
    return { n: qs.length, master, seen };
  }

  function viewHome() {
    setHeader("Code de la route");
    const errors = Q.filter((q) => Store.isError(q.id));
    const due = Q.filter((q) => Store.isDue(q.id) && !Store.isError(q.id));
    const seen = Q.filter((q) => !Store.isNew(q.id)).length;
    const master = Q.filter((q) => Store.status(q.id) === "master").length;
    const exams = Store.exams();
    const last = exams[exams.length - 1];

    let html = `
      <div class="card">
        <div class="stats">
          <div><b>${seen}<small style="font-size:14px;color:var(--muted)">/${Q.length}</small></b><span>questions vues</span></div>
          <div><b>${pct(master, Q.length)}%</b><span>maîtrisées</span></div>
          <div><b>${last ? last.score + "/" + last.n : "–"}</b><span>dernier examen</span></div>
        </div>
      </div>
      <button class="btn" id="bExam">Examen blanc <small>· ${Math.min(EXAM_N, Q.length)} questions · ${EXAM_SECONDS} s</small></button>
      <div class="row">
        <button class="btn secondary" id="bErr" ${errors.length ? "" : "disabled"}>Mes erreurs <small>(${errors.length})</small></button>
        <button class="btn secondary" id="bDue" ${due.length ? "" : "disabled"}>À revoir <small>(${due.length})</small></button>
      </div>
      <button class="btn ghost" id="bChoose">Réviser par thèmes et chapitres</button>
      <div class="card"><h2>Thèmes</h2>`;
    for (const t of META.themes) {
      const s = themeStats(t.code);
      html += `
        <div class="theme ${s.n ? "" : "empty"}" data-t="${t.code}">
          <div class="code">${t.code}</div>
          <div class="info">
            <div class="name">${esc(t.nom)}</div>
            <div class="meta">${s.n ? `${s.n} questions · ${pct(s.master, s.n)}% maîtrisées` : "bientôt"}</div>
            ${s.n ? `<div class="bar"><i style="width:${pct(s.master, s.n)}%"></i><i class="seen" style="width:${pct(s.seen, s.n)}%"></i></div>` : ""}
          </div>
        </div>`;
    }
    html += `</div>
      ${exams.length ? examHistory(exams) : ""}
      <button class="btn ghost" id="bSet">Réglages et sauvegarde</button>`;
    $app.innerHTML = html;
    document.getElementById("bExam").onclick = startExam;
    document.getElementById("bErr").onclick = () => start(shuffle(errors), "Mes erreurs", false);
    document.getElementById("bDue").onclick = () => start(shuffle(due), "À revoir", false);
    document.getElementById("bChoose").onclick = () => go("choisir");
    document.getElementById("bSet").onclick = () => go("reglages");
    $app.querySelectorAll(".theme[data-t]").forEach((el) => {
      el.onclick = () => {
        const t = el.dataset.t, qs = Q.filter((q) => q.theme === t);
        if (qs.length) start(pickTraining(qs, 20), META.themes.find((x) => x.code === t).nom, false);
      };
    });
  }

  function examHistory(exams) {
    const rows = exams.slice(-8).reverse().map((e) => {
      const d = new Date(e.ts);
      const ok = e.n === EXAM_N ? e.score >= EXAM_PASS : e.score >= Math.ceil(e.n * EXAM_PASS / EXAM_N);
      return `<div class="rev"><div class="dot ${ok ? "ok" : "ko"}">${ok ? "✓" : "✗"}</div>
        <div class="t"><b>${e.score}/${e.n}</b> <span class="muted">· ${d.toLocaleDateString("fr-FR")} ${d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}</span></div></div>`;
    }).join("");
    return `<div class="card"><h2>Examens blancs</h2>${rows}</div>`;
  }

  // Ordre de priorité en entraînement : erreurs, puis à revoir, puis jamais vues, puis le reste.
  function pickTraining(qs, n) {
    const rank = (q) => (Store.isError(q.id) ? 0 : Store.isDue(q.id) ? 1 : Store.isNew(q.id) ? 2 : 3);
    const sorted = shuffle(qs).sort((a, b) => rank(a) - rank(b));
    return n ? shuffle(sorted.slice(0, n)) : shuffle(sorted);
  }

  // ---------- choix des chapitres ----------
  const choice = { chaps: null, n: 20, filtre: "toutes" };

  function viewChoose() {
    setHeader("Réviser", () => go(""));
    if (!choice.chaps) choice.chaps = new Set();
    let html = `<div class="card"><h2>Chapitres</h2>`;
    for (const t of META.themes) {
      const tq = Q.filter((q) => q.theme === t.code).length;
      if (!tq) continue;
      html += `<details class="sel" open><summary>
          <input type="checkbox" data-theme="${t.code}">
          <span class="name">${t.code} · ${esc(t.nom)}</span><span class="chev">›</span></summary>`;
      for (const c of t.chapitres) {
        const cq = Q.filter((q) => q.chap === c.code).length;
        if (!cq) continue;
        html += `<label class="chk"><input type="checkbox" data-chap="${c.code}" ${choice.chaps.has(c.code) ? "checked" : ""}>
          ${esc(c.nom)}<span class="n">${cq}</span></label>`;
      }
      html += `</details>`;
    }
    html += `</div>
      <div class="card">
        <div class="label">Questions</div>
        <div class="seg" id="segF">
          ${[["toutes", "Toutes"], ["nouvelles", "Jamais vues"], ["erreurs", "Ratées"], ["revoir", "À revoir"]].map(([k, l]) => `<button data-v="${k}" class="${choice.filtre === k ? "on" : ""}">${l}</button>`).join("")}
        </div>
        <div class="label">Nombre</div>
        <div class="seg" id="segN">
          ${[[10, "10"], [20, "20"], [40, "40"], [0, "Toutes"]].map(([k, l]) => `<button data-v="${k}" class="${choice.n === k ? "on" : ""}">${l}</button>`).join("")}
        </div>
      </div>
      <div class="sticky-actions"><button class="btn" id="go"></button></div>`;
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
      btn.textContent = pool.length ? `Commencer · ${n} question${n > 1 ? "s" : ""}` : "Aucune question pour cette sélection";
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
    document.getElementById("go").onclick = () => start(pickTraining(poolFor(), choice.n), "Entraînement", false);
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
  function startExam() {
    // Répartition proportionnelle aux thèmes disponibles, priorité aux questions jamais vues.
    const pool = shuffle(Q);
    const rank = (q) => (Store.isNew(q.id) ? 0 : 1);
    const picked = pool.sort((a, b) => rank(a) - rank(b)).slice(0, EXAM_N);
    start(shuffle(picked), "Examen blanc", true);
  }

  function start(qs, label, exam) {
    if (!qs.length) return;
    session = {
      label, exam, i: 0,
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
      <div class="qhead">
        <span>${s.i + 1}/${s.items.length}</span>
        <div class="prog"><i style="width:${pct(s.i, s.items.length)}%"></i></div>
        <button class="flag" id="flag" title="Signaler un problème sur cette question">🚩</button>
      </div>
      ${q.img ? `<div class="media"><img src="${esc(q.img)}" alt="" class="${isSvg ? "svg" : ""} ${isSchema ? "schema" : ""}">${q.credit ? `<div class="credit">${esc(q.credit)}</div>` : ""}</div>` : ""}
      <div class="qtext">${esc(q.q)}</div>
      <div class="hint">Une ou plusieurs réponses possibles</div>
      <div id="choices">`;
    it.order.forEach((k, pos) => {
      html += `<button class="choice" data-k="${k}"><span class="letter">${LETTERS[pos]}</span><span>${esc(q.c[k])}</span></button>`;
    });
    html += `</div><div id="after"></div>
      <div class="sticky-actions"><button class="btn" id="valid" disabled>Valider</button></div>`;
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
      valid.disabled = false;
      valid.textContent = s.i + 1 < s.items.length ? "Question suivante" : "Voir le résultat";
      valid.onclick = next;
    }
    function next() {
      if (s.i + 1 < s.items.length) { s.i++; viewQuestion(); }
      else {
        if (s.exam) Store.addExam(s.items.filter((x) => x.ok).length, s.items.length);
        go("resultat");
      }
    }
  }

  function viewResult() {
    const s = session;
    setHeader("Résultat", () => { session = null; go(""); });
    const score = s.items.filter((x) => x.ok).length, n = s.items.length;
    const need = s.exam ? Math.ceil(n * EXAM_PASS / EXAM_N) : null;
    const pass = s.exam ? score >= need : score / n >= EXAM_PASS / EXAM_N;
    const wrong = s.items.filter((x) => !x.ok).map((x) => x.q);
    let html = `
      <div class="card score ${pass ? "pass" : "fail"}">
        <b>${score}/${n}</b>
        ${s.exam ? (pass ? "Examen réussi 🎉" : `Échec : il faut ${need} bonnes réponses`) : `${pct(score, n)}% de bonnes réponses`}
      </div>
      ${wrong.length ? `<button class="btn" id="redo">Rejouer mes ${wrong.length} erreur${wrong.length > 1 ? "s" : ""}</button>` : ""}
      <button class="btn ghost" id="home">Accueil</button>
      <div class="card"><h2>Correction</h2>`;
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
    html += `</div>`;
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
    $app.innerHTML = `
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
      </div>`;
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
