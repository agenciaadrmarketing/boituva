(function () {
  "use strict";
  var GALERIA = __GALERIA__;
  var VALE = __VALE__;
  var FRASES = __FRASES__;
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (id) { return document.getElementById(id); };

  // UTM da visita (mantido do original)
  try {
    if (!sessionStorage.getItem("lead_utm")) {
      var q = new URLSearchParams(location.search), utm = {};
      ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid"].forEach(function (k) { utm[k] = q.get(k) || ""; });
      sessionStorage.setItem("lead_utm", JSON.stringify(utm));
    }
  } catch (e) {}

  var temIO = "IntersectionObserver" in window;

  // Animação de entrada: só esconde o que ainda não está na tela (sem forçar layout)
  if (!reduz && temIO) {
    var sel = ".h2, .sec > div > div > p, .sec > div > p, .grid3 > article, .grid3 > div, .sec details, .sec > div > div > div, footer > div";
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var el = en.target;
        if (en.isIntersecting) {
          if (el.classList.contains("reveal")) el.classList.add("in");
          io.unobserve(el);
        } else if (!el.classList.contains("reveal")) {
          el.classList.add("reveal");
        }
      });
    }, { rootMargin: "0px 0px 15% 0px" });
    document.querySelectorAll("section, footer").forEach(function (g) {
      if (g.classList.contains("hero-sec")) return;
      var i = 0;
      g.querySelectorAll(sel).forEach(function (el) {
        if (el.classList.contains("reveal")) return;
        el.style.transitionDelay = Math.min(i++, 4) * 45 + "ms";
        io.observe(el);
      });
    });
    document.querySelectorAll(".reveal").forEach(function (el) {
      var o = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { el.classList.add("in"); o.disconnect(); }
      }, { rootMargin: "0px 0px 15% 0px" });
      o.observe(el);
    });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("in"); });
  }

  // Animações contínuas (brilho dos botões, trilha dos passos, FAQ) só rodam quando visíveis
  if (temIO) {
    var aio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { en.target.classList.toggle("anim-off", !en.isIntersecting); });
    });
    document.querySelectorAll("a[data-msg], .passo-path, .faq-meter, .faq-tick").forEach(function (el) {
      if (!el.closest(".flutuante") && !el.closest("header")) { el.classList.add("anim-off"); aio.observe(el); }
    });
  }

  // Vale a pena saber (carrossel)
  var vi = 0, vAnim = false, vTimer, vBox = $("vale-conteudo");
  var dots = Array.prototype.slice.call(document.querySelectorAll("[data-vale-dot]"));
  function agendaVale() { clearTimeout(vTimer); vTimer = setTimeout(function () { irVale((vi + 1) % VALE.length); }, 6000); }
  function irVale(i) {
    if (vAnim || !vBox) return;
    vAnim = true; clearTimeout(vTimer);
    vBox.classList.add("saindo");
    setTimeout(function () {
      vi = i; var c = VALE[i];
      $("vale-num").textContent = c.n; $("vale-bg").textContent = c.n;
      $("vale-titulo").textContent = c.t; $("vale-texto").textContent = c.x;
      $("vale-progresso").style.height = ((i + 1) / VALE.length) * 100 + "%";
      dots.forEach(function (d, k) {
        var s = d.firstElementChild;
        s.style.width = k === i ? "28px" : "7px";
        s.style.background = k === i ? "#1EA94F" : "rgba(255,255,255,0.28)";
      });
      vBox.classList.remove("saindo");
      vAnim = false; agendaVale();
    }, 260);
  }
  dots.forEach(function (d) { d.addEventListener("click", function () { irVale(Number(d.getAttribute("data-idx"))); }); });
  document.querySelectorAll("[data-vale]").forEach(function (b) {
    b.addEventListener("click", function () { irVale((vi + Number(b.getAttribute("data-vale")) + VALE.length) % VALE.length); });
  });
  if (vBox) agendaVale();

  // Galeria / lightbox
  var lb = $("lb"), lbT;
  function abrirLb(i) {
    var g = GALERIA[i];
    $("lb-img").src = g.src; $("lb-img").alt = g.titulo;
    $("lb-titulo").textContent = g.titulo; $("lb-legenda").textContent = g.legenda;
    clearTimeout(lbT);
    lb.className = "lb"; lb.firstElementChild.className = "lb-card";
    lb.hidden = false;
  }
  function fecharLb() {
    if (lb.hidden) return;
    lb.className = "lb lb-out"; lb.firstElementChild.className = "lb-card lb-card-out";
    lbT = setTimeout(function () { lb.hidden = true; }, 240);
  }
  document.querySelectorAll("[data-lb]").forEach(function (el) {
    var abrir = function () { abrirLb(Number(el.getAttribute("data-lb"))); };
    el.addEventListener("click", abrir);
    el.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); abrir(); } });
  });
  if (lb) lb.addEventListener("click", fecharLb);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && lb) fecharLb(); });

  // Balão do WhatsApp com frases alternadas
  var balao = $("balao"), frase = 0, encerrado = false, t1, t2;
  var visivel = [7000, 9000, 6500, 8000], oculto = [5000, 11000, 7000, 14000];
  function ciclo() {
    if (encerrado) return;
    var i = frase;
    t1 = setTimeout(function () {
      balao.hidden = true;
      t2 = setTimeout(function () {
        if (encerrado) return;
        frase++;
        var f = FRASES[frase % FRASES.length];
        $("balao-titulo").textContent = f.t; $("balao-sub").textContent = f.s;
        balao.hidden = false;
        ciclo();
      }, oculto[i % oculto.length]);
    }, visivel[i % visivel.length]);
  }
  if (balao) {
    $("balao-fechar").addEventListener("click", function (e) {
      e.preventDefault(); e.stopPropagation();
      encerrado = true; clearTimeout(t1); clearTimeout(t2); balao.hidden = true;
    });
    ciclo();
  }
})();
