/* Tanya Kronik — pencarian arsip (BM25) + fallback Wikipedia + mode LLM opsional */
(function () {
  "use strict";
  var BM = window.KRONIK_BM25;
  var root = document.documentElement;
  var $ = function (s, el) { return (el || document).querySelector(s); };

  var STOP = new Set(("yang dan di ke dari untuk pada dengan dalam ini itu adalah atau juga akan sudah telah " +
    "tidak ada oleh sebagai karena jika maka saat setelah sebelum bisa lebih paling para kami kita mereka dia " +
    "ia nya pun lah kah ketika hingga sampai antara bagi secara serta tetapi namun belum masih hanya saja sangat " +
    "banyak sedikit seorang sebuah suatu tiap setiap apa apakah bagaimana kenapa mengapa siapa kapan dimana di mana " +
    "berapa bagaimanakah adakah").split(" "));

  function tok(text) {
    return (text || "").toLowerCase().replace(/[^a-z0-9\s-]/g, " ").split(/\s+/)
      .filter(function (w) { return w.length > 2 && !STOP.has(w); });
  }

  function bm25(query, limit) {
    if (!BM) return [];
    var terms = Array.from(new Set(tok(query)));
    if (!terms.length) return [];
    var scores = new Map(), matched = new Map(), matchedIdf = new Map();
    var totalIdf = 0;
    terms.forEach(function (t) {
      var post = BM.post[t];
      var df0 = post ? post.split(",").length : 1;
      totalIdf += Math.log(1 + (BM.n - df0 + 0.5) / (df0 + 0.5));
    });
    terms.forEach(function (t) {
      var post = BM.post[t];
      if (!post) return;
      var pairs = post.split(",");
      var df = pairs.length;
      var idf = Math.log(1 + (BM.n - df + 0.5) / (df + 0.5));
      pairs.forEach(function (pair) {
        var bits = pair.split(":");
        var d = +bits[0], tf = +bits[1];
        var dl = BM.lens[d] || 400;
        var s = idf * (tf * 2.2) / (tf + 1.2 * (0.25 + 0.75 * dl / BM.avg));
        scores.set(d, (scores.get(d) || 0) + s);
        if (!matched.has(d)) matched.set(d, new Set());
        matched.get(d).add(t);
        if (!matchedIdf.has(d)) matchedIdf.set(d, new Set());
        matchedIdf.get(d).add(t);
        var doc0 = BM.docs[d];
        var anchor0 = (doc0[1] + " " + (doc0[5] || "")).toLowerCase();
        if (anchor0.indexOf(t) > -1) {
          var boost = doc0[1].toLowerCase().indexOf(t) > -1 ? 2.2 : 1.1;
          scores.set(d, (scores.get(d) || 0) + idf * boost);
        }
      });
    });
    return Array.from(scores.entries())
      .sort(function (a, b) { return b[1] - a[1]; })
      .slice(0, limit || 5)
      .map(function (e) {
        var doc = BM.docs[e[0]];
        var m = matched.get(e[0]) || new Set();
        return {
          score: e[1], url: doc[0], title: doc[1], kind: doc[2], era: doc[3], years: doc[4],
          tags: doc[5] || "",
          coverage: m.size / terms.length,
          weighted: Array.from(matchedIdf.get(e[0]) || []).reduce(function (acc, tt) {
            var pp = BM.post[tt];
            var dfx = pp ? pp.split(",").length : 1;
            return acc + Math.log(1 + (BM.n - dfx + 0.5) / (dfx + 0.5));
          }, 0) / (totalIdf || 1)
        };
      });
  }

  function sentences(text) {
    return text.replace(/\s+/g, " ").split(/(?<=[.!?])\s+(?=[A-Z“"«])/).filter(function (s) {
      return s.length > 40;
    });
  }

  function idfOf(term) {
    var post = BM && BM.post[term];
    if (!post) return 0;
    var df = post.split(",").length;
    return Math.log(1 + (BM.n - df + 0.5) / (df + 0.5));
  }

  async function passages(hit, terms) {
    try {
      var res = await fetch(hit.url, { credentials: "same-origin" });
      if (!res.ok) return [];
      var html = await res.text();
      var doc = new DOMParser().parseFromString(html, "text/html");
      var nodes = Array.from(doc.querySelectorAll(".prose p, .prose li"));
      var weights = {};
      terms.forEach(function (t) { weights[t] = idfOf(t) || 1; });
      var scored = [];
      nodes.forEach(function (n, i) {
        var t = (n.textContent || "").trim();
        if (t.length < 60) return;
        var low = t.toLowerCase();
        var w = 0, hit = 0;
        terms.forEach(function (term) {
          if (low.indexOf(term) > -1) { w += weights[term]; hit++; }
        });
        if (!hit) return;
        scored.push({ t: t, w: w, hit: hit, pos: i });
      });
      scored.sort(function (a, b) { return b.w - a.w || b.hit - a.hit || a.pos - b.pos; });
      return scored.slice(0, 2).map(function (s) {
        var ss = sentences(s.t);
        if (!ss.length) return s.t.slice(0, 400);
        ss.sort(function (a, b) {
          var la = a.toLowerCase(), lb = b.toLowerCase(), wa = 0, wb = 0;
          terms.forEach(function (t) {
            if (la.indexOf(t) > -1) wa += weights[t];
            if (lb.indexOf(t) > -1) wb += weights[t];
          });
          return wb - wa;
        });
        var pick = ss.slice(0, 2).join(" ");
        return pick.length > 420 ? pick.slice(0, 400).replace(/\s+\S*$/, "") + "…" : pick;
      });
    } catch (e) {
      return [];
    }
  }

  function esc(s) {
    return (s || "").replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  async function wikiSearch(query, limit) {
    var api = "https://id.wikipedia.org/w/api.php?action=query&format=json&origin=*" +
      "&generator=search&gsrsearch=" + encodeURIComponent(query) +
      "&gsrlimit=" + (limit || 3) + "&prop=extracts|info&exintro=1&explaintext=1&inprop=url";
    try {
      var res = await fetch(api);
      var data = await res.json();
      if (!data.query || !data.query.pages) return [];
      return Object.values(data.query.pages).map(function (p) {
        return { title: p.title, extract: (p.extract || "").slice(0, 600), url: p.fullurl };
      });
    } catch (e) {
      return [];
    }
  }

  function llmConfig() {
    try { return JSON.parse(localStorage.getItem("kronik-llm") || "null"); } catch (e) { return null; }
  }

  async function askLLM(question, context, history) {
    var cfg = llmConfig();
    if (!cfg || !cfg.key || !cfg.url || !cfg.model) return null;
    var sys = "Kamu asisten sejarah situs Kronik. Jawab dalam bahasa Indonesia, ringkas, 3-6 kalimat. " +
      "Gunakan HANYA konteks yang diberikan untuk fakta; kalau konteks tidak memuat jawabannya, katakan " +
      "bahwa arsip tidak memuatnya dan sarankan sumber lain. Jangan mengarang angka, tanggal, atau kutipan.";
    var msgs = [{ role: "system", content: sys }].concat(history.slice(-4)).concat([
      { role: "user", content: "KONTEKS:\n" + context + "\n\nPERTANYAAN: " + question }
    ]);
    var res = await fetch(cfg.url.replace(/\/$/, "") + "/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + cfg.key },
      body: JSON.stringify({ model: cfg.model, messages: msgs, temperature: 0.3, max_tokens: 500 })
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    var data = await res.json();
    return (data.choices && data.choices[0] && data.choices[0].message.content) || null;
  }

  /* ————— UI ————— */
  var log = $("[data-chat-log]");
  var form = $("[data-chat-form]");
  var input = $("[data-chat-input]");
  var history = [];

  function bubble(role, html) {
    var el = document.createElement("div");
    el.className = "msg msg--" + role;
    el.innerHTML = html;
    log.appendChild(el);
    el.scrollIntoView({ block: "end", behavior: "smooth" });
    return el;
  }

  function sourceList(hits) {
    if (!hits.length) return "";
    return '<ul class="msg__src">' + hits.map(function (h) {
      return '<li><a href="' + h.url + '">' + esc(h.title) + '</a>' +
        '<span>' + (h.kind === "bab" ? "Bab" : "Arsip") + ' · ' + esc(h.years) + '</span></li>';
    }).join("") + "</ul>";
  }

  async function answer(question) {
    var terms = tok(question);
    var hits = bm25(question, 5);
    var top = hits[0] ? hits[0].score : 0;
    var cov = hits[0] ? hits[0].coverage : 0;
    var anchor = hits[0] ? (hits[0].title + " " + hits[0].tags).toLowerCase() : "";
    var titleHit = hits[0] ? terms.some(function (t) { return anchor.indexOf(t) > -1; }) : false;
    var strong = terms.length > 0 && top > 2.6 && cov >= 0.5 && titleHit && (hits[0].weighted || 0) >= 0.55;

    if (strong) {
      var blocks = [];
      for (var i = 0; i < Math.min(3, hits.length); i++) {
        var ps = await passages(hits[i], terms);
        if (!ps.length) continue;
        blocks.push('<div class="msg__quote"><p>“' + esc(ps[0]) + '”</p>' +
          '<a href="' + hits[i].url + '">' + esc(hits[i].title) + " →</a></div>");
      }
      if (blocks.length) {
        return '<p class="msg__lead">Ini yang tercatat di arsip:</p>' + blocks.join("") +
          sourceList(hits.slice(0, 3));
      }
    }

    // tidak yakin: cari di luar arsip lebih dulu
    var wiki = await wikiSearch(question, 3);
    if (wiki.length) {
      var hint = "";
      if (titleHit && hits.length) {
        var ps2 = await passages(hits[0], terms);
        if (ps2.length) {
          hint = '<div class="msg__quote msg__quote--weak"><p>“' + esc(ps2[0]) + '”</p>' +
            '<a href="' + hits[0].url + '">' + esc(hits[0].title) + " →</a></div>";
        }
      }
      return '<p class="msg__lead">Arsip Kronik tidak memuat jawaban langsung. Dari Wikipedia bahasa Indonesia:</p>' +
        wiki.map(function (w) {
          return '<div class="msg__quote"><p><strong>' + esc(w.title) + '</strong> — ' +
            esc(w.extract.slice(0, 320).replace(/\s+\S*$/, "")) + '…</p>' +
            '<a href="' + w.url + '" target="_blank" rel="noopener">Buka Wikipedia →</a></div>';
        }).join("") + hint;
    }

    if (hits.length && titleHit) {
      var ps3 = await passages(hits[0], terms);
      if (ps3.length) {
        return '<p class="msg__lead">Tidak ada jawaban pasti, tetapi bagian ini menyebut topiknya:</p>' +
          '<div class="msg__quote"><p>“' + esc(ps3[0]) + '”</p>' +
          '<a href="' + hits[0].url + '">' + esc(hits[0].title) + " →</a></div>" + sourceList(hits.slice(0, 2));
      }
    }

    return '<p class="msg__lead">Saya tidak menemukan ini di arsip maupun Wikipedia. Coba kata kunci lain, ' +
      'misalnya nama peristiwa, tokoh, atau tempat.</p>';
  }

  async function send(text) {
    if (!text.trim()) return;
    bubble("user", esc(text));
    history.push({ role: "user", content: text });
    var pending = bubble("bot", '<p class="msg__lead">Mencari di arsip…</p>');
    var html;
    var cfg = llmConfig();
    if (cfg && cfg.key) {
      try {
        var hits = bm25(text, 4);
        var ctx = [];
        for (var i = 0; i < hits.length; i++) {
          var ps = await passages(hits[i], tok(text));
          ctx.push("[" + hits[i].title + "] " + (ps.join(" ") || ""));
        }
        var wiki = await wikiSearch(text, 2);
        wiki.forEach(function (w) { ctx.push("[Wikipedia: " + w.title + "] " + w.extract.slice(0, 300)); });
        var out = await askLLM(text, ctx.join("\n\n").slice(0, 6000), history);
        if (out) {
          html = "<p>" + esc(out).replace(/\n+/g, "</p><p>") + "</p>" + sourceList(hits.slice(0, 3));
        }
      } catch (e) {
        html = null;
      }
    }
    if (!html) html = await answer(text);
    pending.innerHTML = html;
    history.push({ role: "assistant", content: pending.textContent });
    pending.scrollIntoView({ block: "end", behavior: "smooth" });
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = input.value;
      input.value = "";
      send(v);
    });
  }
  document.querySelectorAll("[data-ask]").forEach(function (b) {
    b.addEventListener("click", function () { send(b.getAttribute("data-ask")); });
  });

  var settings = $("[data-llm-settings]");
  if (settings) {
    settings.addEventListener("click", function () {
      document.querySelector(".llm").setAttribute("data-open", "true");
      var cfg = llmConfig() || {};
      $("[data-llm-url]").value = cfg.url || "https://openrouter.ai/api/v1";
      $("[data-llm-model]").value = cfg.model || "openai/gpt-4o-mini";
      $("[data-llm-key]").value = cfg.key || "";
    });
  }
  var saveBtn = $("[data-llm-save]");
  if (saveBtn) {
    saveBtn.addEventListener("click", function () {
      var cfg = {
        url: $("[data-llm-url]").value.trim(),
        model: $("[data-llm-model]").value.trim(),
        key: $("[data-llm-key]").value.trim()
      };
      localStorage.setItem("kronik-llm", JSON.stringify(cfg));
      document.querySelector(".llm").setAttribute("data-open", "false");
      bubble("bot", '<p class="msg__lead">Mode LLM aktif. Jawaban akan disusun dari potongan arsip + Wikipedia ' +
        'memakai kunci API di peramban kamu.</p>');
    });
  }
  var offBtn = $("[data-llm-off]");
  if (offBtn) {
    offBtn.addEventListener("click", function () {
      localStorage.removeItem("kronik-llm");
      document.querySelector(".llm").setAttribute("data-open", "false");
    });
  }

  if (input) input.focus();
})();
