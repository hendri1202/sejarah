/* KRONIK — perilaku halaman. Tanpa dependensi. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function smoothTo(y, dur) {
    if (reduce) { window.scrollTo(0, y); return; }
    var start = window.scrollY, t0 = null;
    var d = dur || 420;
    function ease(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }
    function step() {
      if (t0 === null) t0 = Date.now();
      var p = Math.min(1, (Date.now() - t0) / d);
      window.scrollTo(0, Math.round(start + (y - start) * ease(p)));
      if (p < 1) window.setTimeout(step, 16);
    }
    window.setTimeout(step, 0);
    window.setTimeout(function () {
      if (Math.abs(window.scrollY - y) > 4) window.scrollTo(0, y);
    }, d + 140);
  }
  var $ = function (s, el) { return (el || doc).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || doc).querySelectorAll(s)); };

  /* ——— tema ——— */
  try {
    var saved = localStorage.getItem("kronik-theme");
    if (saved) root.setAttribute("data-theme", saved);
    else if (window.matchMedia("(prefers-color-scheme: dark)").matches) root.setAttribute("data-theme", "malam");
  } catch (e) {}
  var themeBtn = $("[data-theme-toggle]");
  if (themeBtn) {
    var paint = function () {
      var dark = root.getAttribute("data-theme") === "malam";
      themeBtn.setAttribute("aria-pressed", dark ? "true" : "false");
      themeBtn.setAttribute("title", dark ? "Mode terang" : "Mode malam");
      themeBtn.textContent = dark ? "Terang" : "Malam";
    };
    paint();
    themeBtn.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") === "malam";
      root.setAttribute("data-theme", dark ? "siang" : "malam");
      try { localStorage.setItem("kronik-theme", dark ? "siang" : "malam"); } catch (e) {}
      paint();
    });
  }

  /* ——— laci daftar isi ——— */
  var drawer = $(".drawer"), scrim = $(".scrim");
  var setDrawer = function (open) {
    if (!drawer) return;
    drawer.setAttribute("data-open", open ? "true" : "false");
    if (scrim) scrim.setAttribute("data-open", open ? "true" : "false");
    if (open) {
      drawer.removeAttribute("aria-hidden");
      var first = drawer.querySelector("a");
      if (first) first.focus({ preventScroll: true });
    } else {
      drawer.setAttribute("aria-hidden", "true");
    }
  };
  $$("[data-drawer-open]").forEach(function (b) {
    b.addEventListener("click", function () { setDrawer(true); });
  });
  $$("[data-drawer-close]").forEach(function (b) {
    b.addEventListener("click", function () { setDrawer(false); });
  });
  $$("[data-search-close]").forEach(function (b) {
    b.addEventListener("click", closeSearch);
  });
  if (scrim) scrim.addEventListener("click", function () { setDrawer(false); });

  /* ——— kepala menyusut saat menggulir ——— */
  var head = $(".masthead"), lastY = window.scrollY;
  var onScroll = function () {
    var y = window.scrollY;
    if (head) {
      if (y > 140 && y > lastY + 6) head.setAttribute("data-hidden", "true");
      else if (y < lastY - 6) head.removeAttribute("data-hidden");
    }
    lastY = y;
    var bar = $(".progress");
    if (bar) {
      var h = doc.body.scrollHeight - window.innerHeight;
      bar.style.setProperty("--p", h > 0 ? Math.min(1, y / h).toFixed(4) : 0);
    }
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ——— pencarian ——— */
  var data = window.KRONIK_INDEX || [];
  var search = $(".search"), input = search ? search.querySelector("input") : null;
  var list = search ? search.querySelector(".search__results") : null;
  var cursor = -1;

  function renderSearch(q) {
    if (!list) return;
    var norm = function (s) { return (s || "").toLowerCase(); };
    var terms = norm(q).split(/\s+/).filter(Boolean);
    var hits = data
      .map(function (it) {
        var title = norm(it.t), lead = norm((it.d || "") + " " + (it.k || "")), body = norm(it.x || "");
        var hay = title + " " + lead + " " + body;
        if (!terms.every(function (t) { return hay.indexOf(t) !== -1; })) return null;
        var score = 0;
        terms.forEach(function (t) {
          if (title.indexOf(t) !== -1) score += 8;
          if (lead.indexOf(t) !== -1) score += 3;
          score += Math.min(4, (body.split(t).length - 1));
        });
        return { it: it, score: score };
      })
      .filter(Boolean)
      .sort(function (a, b) { return b.score - a.score; })
      .slice(0, 14)
      .map(function (r) { return r.it; });

    if (!q.trim()) {
      list.innerHTML =
        data.slice(0, 6).map(function (it) {
          return item(it);
        }).join("") || '<li class="search__hint">Belum ada indeks.</li>';
      cursor = -1;
      return;
    }
    list.innerHTML = hits.length
      ? hits.map(item).join("")
      : '<li class="search__hint">Tidak ada yang cocok. Coba kata lain, misalnya “VOC”, “Sangiran”, atau “1945”.</li>';
    cursor = -1;
  }
  function item(it) {
    return (
      '<li><a href="' + it.u + '"><span class="r-k">' + it.k + '</span>' +
      '<span class="r-t">' + it.t + '</span>' +
      '<span class="r-d">' + (it.d || "") + '</span></a></li>'
    );
  }
  function openSearch() {
    if (!search) return;
    search.setAttribute("open", "");
    document.body.style.overflow = "hidden";
    renderSearch("");
    setTimeout(function () { if (input) input.focus(); }, 40);
  }
  function closeSearch() {
    if (!search) return;
    search.removeAttribute("open");
    document.body.style.overflow = "";
  }
  $$("[data-search-open]").forEach(function (b) {
    b.addEventListener("click", openSearch);
  });
  if (search) {
    search.addEventListener("click", function (e) { if (e.target === search) closeSearch(); });
  }
  if (input) {
    input.addEventListener("input", function () { renderSearch(input.value); });
    input.addEventListener("keydown", function (e) {
      var links = $$(".search__results a");
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!links.length) return;
        cursor = (cursor + (e.key === "ArrowDown" ? 1 : -1) + links.length) % links.length;
        links.forEach(function (a, i) { a.setAttribute("aria-selected", i === cursor ? "true" : "false"); });
        links[cursor].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter" && links.length) {
        e.preventDefault();
        (links[cursor < 0 ? 0 : cursor]).click();
      }
    });
  }
  doc.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { closeSearch(); setDrawer(false); }
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(doc.activeElement.tagName);
    if (!typing && (e.key === "/" || (e.key === "k" && (e.metaKey || e.ctrlKey)))) {
      e.preventDefault(); openSearch();
    }
  });

  /* ——— saringan kronologi ——— */
  var chips = $$("[data-filter]");
  if (chips.length) {
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        var f = chip.getAttribute("data-filter");
        chips.forEach(function (c) {
          c.setAttribute("aria-pressed", c === chip ? "true" : "false");
        });
        $$(".tl").forEach(function (row) {
          row.hidden = !(f === "semua" || row.getAttribute("data-cat") === f);
        });
        var visible = $$(".tl").filter(function (r) { return !r.hidden; }).length;
        var count = $("[data-tl-count]");
        if (count) count.textContent = visible + " peristiwa";
      });
    });
  }

  /* ——— navigasi kibor antar bab ——— */
  var art = $(".chapter");
  if (art) {
    var prevUrl = art.getAttribute("data-prev"), nextUrl = art.getAttribute("data-next");
    doc.addEventListener("keydown", function (e) {
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(doc.activeElement.tagName)) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      var target = e.key === "ArrowLeft" ? prevUrl : e.key === "ArrowRight" ? nextUrl : null;
      if (target) window.location.href = target;
    });
  }

  /* ——— kembali ke atas ——— */
  var top = doc.createElement("button");
  top.className = "to-top";
  top.type = "button";
  top.setAttribute("aria-label", "Kembali ke atas");
  top.textContent = "↑ Atas";
  doc.body.appendChild(top);
  top.addEventListener("click", function () { smoothTo(0); });
  var showTop = function () {
    top.setAttribute("data-show", window.scrollY > 900 ? "true" : "false");
  };
  window.addEventListener("scroll", showTop, { passive: true });
  showTop();

  /* ——— tautan daftar isi bab ——— */
  $$('.chapter-toc a, .prose a[href^="#"]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      var id = (a.getAttribute("href") || "").slice(1);
      var target = id ? doc.getElementById(id) : null;
      if (!target) return;
      e.preventDefault();
      var y = target.getBoundingClientRect().top + window.scrollY - 78;
      smoothTo(y);
      if (history.replaceState) history.replaceState(null, "", "#" + id);
    });
  });

  /* ——— arsip artikel ——— */
  var arcList = $("[data-arc-list]");
  if (arcList && window.KRONIK_ENTRIES) {
    var all = window.KRONIK_ENTRIES.slice();
    var state = { era: "semua", q: "", tag: "", shown: 0 };
    var PAGE = 60;
    var tagSel = $("[data-arc-tag]");
    var counter = $("[data-arc-count]");
    var moreBtn = $("[data-arc-more]");
    var tags = {};
    all.forEach(function (e) { (e.g || []).forEach(function (t) { tags[t] = (tags[t] || 0) + 1; }); });
    if (tagSel) {
      Object.keys(tags).sort().forEach(function (t) {
        var o = doc.createElement("option");
        o.value = t; o.textContent = t + " (" + tags[t] + ")";
        tagSel.appendChild(o);
      });
      tagSel.addEventListener("change", function () { state.tag = tagSel.value; state.shown = 0; paint(); });
    }
    function match(e) {
      if (state.era !== "semua" && e.e !== state.era) return false;
      if (state.tag && (e.g || []).indexOf(state.tag) === -1) return false;
      if (state.q) {
        var hay = (e.t + " " + e.y + " " + e.d + " " + (e.g || []).join(" ")).toLowerCase();
        if (hay.indexOf(state.q) === -1) return false;
      }
      return true;
    }
    function paint() {
      var hits = all.filter(match);
      if (state.shown === 0) state.shown = PAGE;
      var slice = hits.slice(0, state.shown);
      arcList.innerHTML = slice.map(function (e) {
        var part = e.e;
        return '<li><a href="artikel/' + e.i + '.html"><span class="y">' + e.y +
          '</span><span class="t">' + e.t + '</span><span class="e">' + part + '</span></a></li>';
      }).join("") || '<li style="padding:18px 0;color:var(--muted)">Tidak ada artikel yang cocok.</li>';
      if (counter) counter.textContent = hits.length + " artikel";
      if (moreBtn) moreBtn.parentNode.style.display = hits.length > state.shown ? "" : "none";
    }
    var q = $("[data-arc-q]");
    if (q) {
      q.addEventListener("input", function () {
        state.q = q.value.trim().toLowerCase(); state.shown = 0; paint();
      });
    }
    $$("[data-era]").forEach(function (b) {
      b.addEventListener("click", function () {
        $$("[data-era]").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        state.era = b.getAttribute("data-era"); state.shown = 0; paint();
      });
    });
    if (moreBtn) moreBtn.addEventListener("click", function () { state.shown += PAGE; paint(); });
    paint();
  }

  /* ——— sorot bab aktif di laci ——— */
  var here = location.pathname.split("/").pop();
  $$(".drawer a").forEach(function (a) {
    var href = a.getAttribute("href") || "";
    if (href.split("/").pop() === here) a.setAttribute("aria-current", "page");
  });
})();
