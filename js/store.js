/* Suivi de progression, stocké dans le navigateur (localStorage).
 *
 * Par question : historique des réponses, « boîte » de répétition espacée (Leitner),
 * date de prochaine révision, statut « erreur » (sort après 2 bonnes réponses de suite).
 */
(function () {
  const KEY = "permis.v1";
  const DAY = 86400000;
  const INTERVALS = [0, 1, 3, 7, 14, 30]; // jours, par boîte
  const MASTER_BOX = 2; // maîtrisée à partir de la boîte 2 (2 bonnes réponses d'affilée au moins)

  function empty() { return { q: {}, exams: [], v: 1 }; }

  let data;
  try { data = JSON.parse(localStorage.getItem(KEY)) || empty(); } catch (e) { data = empty(); }
  if (!data.q) data.q = {};
  if (!data.exams) data.exams = [];

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) { /* stockage indisponible */ }
  }

  const Store = {
    get(id) { return data.q[id]; },

    record(id, ok) {
      const now = Date.now();
      const s = data.q[id] || { h: [], box: 0, due: now, err: false, streak: 0 };
      s.h.push([now, ok ? 1 : 0]);
      if (s.h.length > 30) s.h = s.h.slice(-30);
      if (ok) {
        s.box = Math.min(s.box + 1, INTERVALS.length - 1);
        s.streak = (s.streak || 0) + 1;
        if (s.streak >= 2) s.err = false;
      } else {
        s.box = 0;
        s.streak = 0;
        s.err = true;
      }
      s.due = now + INTERVALS[s.box] * DAY;
      data.q[id] = s;
      save();
    },

    status(id) {
      const s = data.q[id];
      if (!s || !s.h.length) return "new";
      if (s.err) return "err";
      if (s.box >= MASTER_BOX) return "master";
      return "seen";
    },
    isError(id) { const s = data.q[id]; return !!(s && s.err); },
    isDue(id) { const s = data.q[id]; return !!(s && s.h.length && s.due <= Date.now()); },
    isNew(id) { const s = data.q[id]; return !s || !s.h.length; },

    addExam(score, n) { data.exams.push({ ts: Date.now(), score, n }); save(); },
    exams() { return data.exams; },

    export() { return JSON.stringify(data); },
    import(json) {
      const d = JSON.parse(json);
      if (!d || typeof d.q !== "object") throw new Error("Fichier invalide");
      data = d; if (!data.exams) data.exams = []; save();
    },
    reset() { data = empty(); save(); },
  };
  window.Store = Store;
})();
