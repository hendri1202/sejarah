/* KRONIK — perilaku halaman. Tanpa dependensi. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
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

  /* ——— sorot bab aktif di laci ——— */
  var here = location.pathname.split("/").pop();
  $$(".drawer a").forEach(function (a) {
    var href = a.getAttribute("href") || "";
    if (href.split("/").pop() === here) a.setAttribute("aria-current", "page");
  });
})();
