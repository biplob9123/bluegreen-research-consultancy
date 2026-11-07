(function () {
  "use strict";

  /* ---------- language: Bangla pages use Bangla messages and digits ---------- */
  var BN = document.documentElement.lang === "bn";
  function tr(en, bn) { return BN ? bn : en; }
  function num(n) { return BN ? String(n).replace(/[0-9]/g, function (d) { return "০১২৩৪৫৬৭৮৯"[d]; }) : String(n); }

  /* ---------- tidy address bar: /about.html -> /about, /index.html -> / ---------- */
  try {
    if (/^https?:$/.test(location.protocol) && /\.html$/.test(location.pathname) && !/\/404\.html$/.test(location.pathname)) {
      var clean = location.pathname.replace(/index\.html$/, "").replace(/\.html$/, "");
      history.replaceState(null, "", clean + location.search + location.hash);
    }
  } catch (e) {}

  /* ---------- mobile menu ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var menu = document.getElementById("menu");
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("open")) {
        menu.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }


  /* ---------- dropdown sub-menus (mobile accordion + keyboard) ---------- */
  var subToggles = document.querySelectorAll(".sub-toggle");
  Array.prototype.forEach.call(subToggles, function (b) {
    b.addEventListener("click", function () {
      var li = b.parentNode;
      var open = li.classList.toggle("open");
      b.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      Array.prototype.forEach.call(document.querySelectorAll(".has-sub.open"), function (li) {
        li.classList.remove("open");
        li.querySelector(".sub-toggle").setAttribute("aria-expanded", "false");
      });
    }
  });

  /* ---------- team profile pop-ups ---------- */
  var openers = document.querySelectorAll("[data-open]");
  Array.prototype.forEach.call(openers, function (el) {
    el.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest("a")) { return; }
      var d = document.getElementById(el.getAttribute("data-open"));
      if (d && d.showModal) { d.showModal(); document.body.classList.add("modal-open"); }
      e.stopPropagation();
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll("dialog.mdl"), function (d) {
    d.addEventListener("click", function (e) {
      if (e.target === d || (e.target.hasAttribute && e.target.hasAttribute("data-close"))) { d.close(); }
    });
    d.addEventListener("close", function () { document.body.classList.remove("modal-open"); });
  });

  /* ---------- scroll reveal, process line, number count-up ---------- */
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var targets = document.querySelectorAll(".sec-head, .svc-card, .four > div, .steps li, .strip, .linklist li, .mosaic figure, .ccard, .srow, .cl-card, .member, .cta-in, .three > div, .row, .proj, .form-card, .info-card, .stats > div, .soft .split > *");
  if ("IntersectionObserver" in window && !reduce) {
    var order = 0, lastParent = null;
    Array.prototype.forEach.call(targets, function (el) {
      if (el.parentNode !== lastParent) { order = 0; lastParent = el.parentNode; }
      el.classList.add("reveal");
      el.style.transitionDelay = Math.min(order, 8) * 70 + "ms";
      order++;
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) { return; }
        var el = en.target;
        el.classList.add("in");
        if (el.matches(".steps li")) { el.classList.add("lit"); }
        var num = el.querySelector && el.querySelector(".num");
        if (num) { countUp(num); }
        io.unobserve(el);
        if (!el.matches(".steps li")) {
          setTimeout(function () { el.classList.remove("reveal", "in"); el.style.transitionDelay = ""; }, 1400);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    Array.prototype.forEach.call(document.querySelectorAll(".reveal"), function (el) { io.observe(el); });
  } else {
    Array.prototype.forEach.call(document.querySelectorAll(".steps li"), function (el) { el.classList.add("lit"); });
  }
  function countUp(el) {
    var to = parseInt(el.getAttribute("data-to"), 10);
    if (!to || reduce) { return; }
    var start = null, dur = 1300;
    function step(t) {
      if (start === null) { start = t; }
      var p = Math.min((t - start) / dur, 1);
      el.textContent = num(Math.round(to * (1 - Math.pow(1 - p, 3))));
      if (p < 1) { requestAnimationFrame(step); } else { el.textContent = num(to); }
    }
    el.textContent = num(0);
    requestAnimationFrame(step);
  }

  /* ---------- contact form ---------- */
  var form = document.getElementById("contact-form");
  if (form) {
    var status = document.getElementById("form-status");
    var params = new URLSearchParams(window.location.search);
    var topic = params.get("topic");
    var select = form.querySelector("select[name=interest]");
    if (topic && select) {
      for (var i = 0; i < select.options.length; i++) {
        if (select.options[i].getAttribute("data-key") === topic.toLowerCase()) {
          select.selectedIndex = i;
          break;
        }
      }
    }
    var setStatus = function (msg, cls) {
      status.textContent = msg;
      status.className = "form-status " + (cls || "");
    };
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var data = new FormData(form);
      if (data.get("botcheck")) { return; }
      var key = form.getAttribute("data-key");
      var email = form.getAttribute("data-email");
      var btn = form.querySelector("button[type=submit]");

      var viaMailClient = function () {
        var body = "Name: " + data.get("name") + "\nEmail: " + data.get("email") +
          "\nPhone: " + (data.get("phone") || "-") + "\nOrganisation: " + (data.get("organisation") || "-") +
          "\nInterested in: " + data.get("interest") + "\n\n" + data.get("message");
        window.location.href = "mailto:" + email + "?subject=" +
          encodeURIComponent("Enquiry: " + data.get("interest")) + "&body=" + encodeURIComponent(body);
        setStatus(tr("Your email app should open with the message ready to send. If it does not, write to " + email + " or message us on WhatsApp.", "আপনার ইমেইল অ্যাপে বার্তাটি পাঠানোর জন্য তৈরি অবস্থায় খোলার কথা। না খুললে " + email + " ঠিকানায় লিখুন অথবা হোয়াটসঅ্যাপে বার্তা দিন।"), "ok");
      };

      if (!key || key.indexOf("YOUR_") === 0) { viaMailClient(); return; }

      btn.disabled = true;
      setStatus(tr("Sending…", "পাঠানো হচ্ছে…"));
      var payload = {
        access_key: key,
        subject: "Website enquiry: " + data.get("interest"),
        from_name: "BlueGreen website",
        name: data.get("name"), email: data.get("email"), phone: data.get("phone"),
        organisation: data.get("organisation"), interest: data.get("interest"), message: data.get("message")
      };
      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload)
      }).then(function (r) { return r.json(); }).then(function (j) {
        if (j.success) {
          form.reset();
          setStatus(tr("Thank you. We have your message and will reply within one working day.", "ধন্যবাদ। আপনার বার্তা আমরা পেয়েছি, এক কর্মদিবসের মধ্যে উত্তর দেব।"), "ok");
        } else { throw new Error(j.message || "failed"); }
      }).catch(function () {
        setStatus(tr("The message could not be sent. Please email " + email + " or message us on WhatsApp.", "বার্তাটি পাঠানো যায়নি। অনুগ্রহ করে " + email + " ঠিকানায় ইমেইল করুন অথবা হোয়াটসঅ্যাপে বার্তা দিন।"), "err");
      }).finally(function () { btn.disabled = false; });
    });
  }

  /* ---------- footer year ---------- */
  var y = document.getElementById("year");
  if (y) { y.textContent = num(new Date().getFullYear()); }

  /* ---------- gallery carousel ---------- */
  Array.prototype.forEach.call(document.querySelectorAll("[data-carousel]"), function (c) {
    var slides = c.querySelectorAll(".slide"), thumbs = c.querySelectorAll(".thumb"), cur = c.querySelector(".cur");
    var i = 0, timer = null, playing = true, btn = c.querySelector(".car-play");
    function go(n) {
      i = (n + slides.length) % slides.length;
      Array.prototype.forEach.call(slides, function (s, k) { s.classList.toggle("on", k === i); });
      Array.prototype.forEach.call(thumbs, function (t, k) { t.classList.toggle("on", k === i); });
      if (cur) { cur.textContent = num(i + 1); }
    }
    function start() { stop(); if (playing && !reduceMotion) { timer = setInterval(function () { go(i + 1); }, 5500); } }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var pv = c.querySelector(".prev"), nx = c.querySelector(".next");
    if (pv) { pv.addEventListener("click", function () { go(i - 1); start(); }); }
    if (nx) { nx.addEventListener("click", function () { go(i + 1); start(); }); }
    Array.prototype.forEach.call(thumbs, function (t, k) { t.addEventListener("click", function () { go(k); start(); }); });
    if (btn) { btn.addEventListener("click", function () { playing = !playing; btn.textContent = playing ? tr("Pause", "থামান") : tr("Play", "চালান"); playing ? start() : stop(); }); }
    c.addEventListener("mouseenter", stop); c.addEventListener("mouseleave", start);
    c.addEventListener("keydown", function (e) { if (e.key === "ArrowLeft") { go(i - 1); } if (e.key === "ArrowRight") { go(i + 1); } });
    var x0 = null;
    c.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    c.addEventListener("touchend", function (e) { if (x0 === null) { return; } var d = e.changedTouches[0].clientX - x0; if (Math.abs(d) > 40) { go(d < 0 ? i + 1 : i - 1); start(); } x0 = null; });
    if (btn) { btn.textContent = tr("Pause", "থামান"); }
    go(0); start();
  });

  /* ---------- course filter ---------- */
  var tabs = document.querySelectorAll(".tab[data-filter]");
  Array.prototype.forEach.call(tabs, function (t) {
    t.addEventListener("click", function () {
      var f = t.getAttribute("data-filter");
      Array.prototype.forEach.call(tabs, function (o) { o.setAttribute("aria-selected", o === t ? "true" : "false"); });
      Array.prototype.forEach.call(document.querySelectorAll(".ccard"), function (c) {
        var show = f === "all" || c.getAttribute("data-cat") === f;
        c.classList.toggle("hide", !show);
        if (show) { c.classList.remove("pop"); void c.offsetWidth; c.classList.add("pop"); }
      });
    });
  });

  /* ---------- ?course= prefill and team hash flash ---------- */
  try {
    var cq = new URLSearchParams(location.search).get("course"), ta = document.querySelector("#contact-form textarea, form textarea");
    if (cq && ta && !ta.value) { ta.value = tr("I would like to know about the course: " + cq + ".", "আমি এই কোর্সটি সম্পর্কে জানতে চাই: " + cq + "।"); }
  } catch (err) {}
  if (location.hash.indexOf("#p-") === 0) {
    var m = document.getElementById(location.hash.slice(1));
    if (m) { setTimeout(function () { m.scrollIntoView({ block: "center" }); m.classList.add("flash"); }, 400); }
  }

  /* ---------- open a pop-up straight from a link such as insights#etp ---------- */
  function openLinked() {
    if (location.hash.length < 2) { return; }
    var linked = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (linked && linked.tagName === "DIALOG" && linked.showModal && !linked.open) {
      linked.showModal();
      document.body.classList.add("modal-open");
    }
  }
  openLinked();
  window.addEventListener("hashchange", openLinked);
})();
