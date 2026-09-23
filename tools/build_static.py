#!/usr/bin/env python3
"""Gera o index.html estático (sem React/runtime) a partir do fonte do Claude Design.

Uso: python3 tools/build_static.py
Fonte: design/publicar/index.html  ->  Saída: index.html
"""
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "design" / "publicar" / "index.html"
OUT = ROOT / "index.html"

FONE = "551533470189"
MSG_PADRAO = "Oi, vim pelo site e quero agendar um atendimento no escritório em Boituva."


def wa(msg):
    return "https://wa.me/" + FONE + "?text=" + quote(msg, safe="")


AREAS = [
    ("Direito de Família", "Família", ["Divórcio com ou sem partilha de bens, com ou sem filhos menores", "Divórcio extrajudicial em cartório", "Pensão alimentícia: fixar, revisar ou exonerar", "União estável: formalizar ou dissolver", "Guarda de filhos"]),
    ("Direito Sucessório e Herança", "Herança", ["Inventário judicial e extrajudicial", "Herança: direitos, prazo para abrir inventário e multa por atraso", "Testamento", "Planejamento sucessório"]),
    ("Direito Trabalhista", "Trabalho", ["Rescisão indireta", "Reconhecimento de vínculo empregatício", "Desvio de função e assédio moral", "Verbas rescisórias, horas extras e insalubridade", "Estabilidade da gestante"]),
    ("Direito Criminal", "Direito Criminal", ["Defesa em inquérito policial, audiência de custódia e processo criminal", "Habeas corpus", "Prisão em flagrante", "Revisão criminal"]),
    ("Direito Médico e da Saúde", "Saúde", ["Defesa de médicos e dentistas: judicial, extrajudicial e ético-profissional", "Reajuste abusivo de plano de saúde", "Indenização por erro médico ou odontológico", "Cirurgia plástica pós-bariátrica", "Tratamento ou medicamento pelo SUS ou plano de saúde"]),
    ("Direito Bancário", "Direito Bancário", ["Juros abusivos em financiamento de veículo", "Busca e apreensão de veículo", "Golpe do Pix"]),
    ("Direito Imobiliário", "Imóveis", ["Locação: despejo, contrato e cobrança de aluguel", "Atraso na entrega de obra", "Usucapião"]),
    ("Direito Previdenciário", "INSS", ["BPC/LOAS", "Auxílio-doença (benefício por incapacidade temporária)", "Salário-maternidade"]),
]

VALE = [
    ("01", "Você recebeu uma carta, notificação ou intimação", "Documento oficial quase sempre vem com prazo curto para resposta. Quem procura orientação na mesma semana tem muito mais caminhos do que quem espera o prazo vencer."),
    ("02", "Alguém disse que \"não tem o que fazer\"", "Empresa, banco, INSS ou até um conhecido. Muita gente desiste de um direito real por causa de uma informação errada dada no balcão — vale ouvir quem analisa o caso por inteiro."),
    ("03", "O problema já se arrasta há meses", "Cobrança que não para, benefício negado, pensão atrasada, conflito de família sem solução. Quanto mais o tempo passa, mais provas se perdem e mais caro fica resolver."),
    ("04", "Vão te pedir para assinar alguma coisa", "Acordo, rescisão, confissão de dívida, partilha. Assinar sem entender é o erro mais comum e o mais difícil de desfazer depois. Uma leitura antes evita anos de processo."),
]

GALERIA = [
    ("assets/img/recepcao-1228.webp", "Recepção em Boituva/SP", "Rua Benedita Sanson Labronici, 180 — Chácara Labronici"),
    ("assets/img/equipe-600.webp", "A equipe", "Advogados e time de atendimento do escritório"),
    ("assets/img/sala-atendimento-1228.webp", "Sala de atendimento", "Atendimento presencial em Boituva ou reunião online"),
    ("assets/img/escritorio-boituva-1228.webp", "Como trabalhamos", "Cada caso é analisado em conjunto pela equipe"),
]

FRASES = [
    ("Precisa de um advogado em Boituva?", "Atendimento presencial com hora marcada, no centro da cidade."),
    ("Recebeu uma notificação?", "Documento oficial tem prazo. Marque um horário e traga para análise."),
    ("INSS negou seu benefício?", "Trazendo suas cartas e exames, a gente avalia o caso pessoalmente."),
    ("Vão te pedir para assinar algo?", "Antes de assinar, vale uma leitura com advogado. Agende um horário."),
]

# src original -> (src otimizado, srcset, sizes, width, height)
IMAGENS = {
    "uploads/16.jpg": ("assets/img/escritorio-boituva-1228.webp", "assets/img/escritorio-boituva-640.webp 640w, assets/img/escritorio-boituva-1228.webp 1228w", 1228, 819),
    "uploads/17-e1772128273241.jpg": ("assets/img/recepcao-1228.webp", "assets/img/recepcao-640.webp 640w, assets/img/recepcao-1228.webp 1228w", 1228, 570),
    "uploads/19.jpg": ("assets/img/sala-atendimento-1228.webp", "assets/img/sala-atendimento-640.webp 640w, assets/img/sala-atendimento-1228.webp 1228w", 1228, 819),
    "uploads/1-3.jpg": ("assets/img/cta-fundo-1228.webp", "assets/img/cta-fundo-640.webp 640w, assets/img/cta-fundo-1228.webp 1228w", 1228, 819),
    "uploads/equipe.jpg": ("assets/img/equipe-600.webp", None, 600, 400),
    "uploads/dscf5096_1_54227471182_o.webp": ("assets/img/dr-oscar-vieira-900.webp", "assets/img/dr-oscar-vieira-480.webp 480w, assets/img/dr-oscar-vieira-900.webp 900w", 900, 1350),
    "uploads/Gemini_Generated_Image_jcvy6ljcvy6ljcvy.jpeg": ("assets/img/textura-servicos.webp", None, 1400, 785),
    "uploads/Gemini_Generated_Image_4j0b2v4j0b2v4j0b.jpeg": ("assets/img/textura-passos.webp", None, 1400, 785),
    "uploads/logo-vm.png": ("assets/img/logo-vm-360.webp", "assets/img/logo-vm-360.webp 360w, assets/img/logo-vm-760.webp 760w", 360, 80),
}

FONT_FACE = """@font-face { font-family: 'Lexend Fallback'; src: local('Arial'), local('Helvetica'), local('Liberation Sans'), local('Roboto'); size-adjust: 110.2%; ascent-override: 90.7%; descent-override: 22.7%; line-gap-override: 0%; }
  @font-face { font-family: 'Lexend Deca'; font-style: normal; font-weight: 300 700; font-display: swap; src: url(assets/fonts/lexend-deca-latin.woff2) format('woff2'); unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }"""

EXTRA_CSS = """
  [hidden] { display: none !important; }
  .anim-off, .anim-off::before, .anim-off::after { animation-play-state: paused !important; }
  .lb-img { width: 100%; max-height: 76vh; object-fit: cover; display: block; }
  .vale-conteudo { transition: opacity .32s ease, transform .32s cubic-bezier(.22,.7,.2,1); }
  .vale-conteudo.saindo { opacity: 0; transform: translateY(8px); }
"""


def between(s, a, b):
    i = s.index(a) + len(a)
    return s[i:s.index(b, i)]


def cut_block(s, start_marker):
    """Remove um <sc-if ...>...</sc-if> (com aninhamento) que começa em start_marker."""
    i = s.index(start_marker)
    depth, j = 0, i
    tag = re.compile(r"<sc-if\b|</sc-if>")
    for m in tag.finditer(s, i):
        depth += 1 if m.group(0) != "</sc-if>" else -1
        if depth == 0:
            j = m.end()
            break
    return s[:i], s[i:j], s[j:]


def unwrap_if(s, value, replacement_open=""):
    a, block, b = cut_block(s, f'<sc-if value="{{{{ {value} }}}}"')
    inner = re.sub(r"^<sc-if[^>]*>", "", block)
    inner = inner[: inner.rindex("</sc-if>")]
    return a, inner, b


def converter_hover(body):
    """style-hover/focus/before/after -> classes CSS."""
    regras, classes = [], {}

    def imp(decls):
        out = []
        for d in decls.split(";"):
            d = d.strip()
            if d:
                out.append(d + " !important")
        return "; ".join(out)

    def tag_sub(m):
        t = m.group(0)
        attrs = dict(re.findall(r'\bstyle-(hover|focus|before|after)="([^"]*)"', t))
        if not attrs:
            return t
        key = json.dumps(attrs, sort_keys=True)
        if key not in classes:
            n = "x%d" % (len(classes) + 1)
            classes[key] = n
            for kind, decl in attrs.items():
                decl = html.unescape(decl)
                if kind == "hover":
                    regras.append(f".{n}:hover {{ {imp(decl)} }}")
                elif kind == "focus":
                    regras.append(f".{n}:focus {{ {imp(decl)} }}")
                else:
                    regras.append(f".{n}::{kind} {{ {decl} }}")
        n = classes[key]
        t = re.sub(r'\s+style-(hover|focus|before|after)="[^"]*"', "", t)
        if re.search(r'\sclass="', t):
            t = re.sub(r'\sclass="([^"]*)"', lambda mm: f' class="{mm.group(1)} {n}"', t, count=1)
        else:
            t = re.sub(r"^<([a-zA-Z0-9-]+)", lambda mm: f'<{mm.group(1)} class="{n}"', t)
        return t

    body = re.sub(r"<[a-zA-Z][^<>]*\bstyle-(?:hover|focus|before|after)=[^<>]*>", tag_sub, body)
    return body, "\n  ".join(regras)


def trocar_imagens(body):
    def img_sub(m):
        t = m.group(0)
        m_src = re.search(r'\ssrc="([^"]+)"', t)
        src = m_src.group(1) if m_src else None
        if src not in IMAGENS:
            return t
        novo, srcset, w, h = IMAGENS[src]
        t = t.replace(f'src="{src}"', f'src="{novo}"')
        t = re.sub(r'\s(width|height)="\d+"', "", t)
        extra = f' width="{w}" height="{h}"'
        if srcset:
            if "logo-vm" in novo:
                sizes = "380px" if "max-width: 380px" in t else "180px"
            elif "dr-oscar" in novo:
                sizes = "(max-width: 940px) 90vw, 448px"
            elif "transition: transform .6s" in t:
                sizes = "(max-width: 940px) 100vw, 780px"
            elif "height: 220px" in t:
                sizes = "(max-width: 500px) 100vw, 460px"
            else:
                sizes = "100vw"
            extra += f' srcset="{srcset}" sizes="{sizes}"'
        return t[:-1].rstrip("/").rstrip() + extra + ">"

    return re.sub(r"<img\b[^>]*>", img_sub, body)


def main():
    src = SRC.read_text(encoding="utf-8")
    head = between(src, "<helmet>", "</helmet>")
    body = between(src, "</helmet>", "</x-dc>")

    # ---------- HEAD ----------
    head = head.replace('<meta name="viewport" content="width=device-width, initial-scale=1">\n', "", 1)
    head = re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\n', "", head)
    head = re.sub(r'<link rel="preconnect" href="https://fonts\.gstatic\.com"[^>]*>\n', "", head)
    head = re.sub(r'<link href="https://fonts\.googleapis\.com/css2[^>]*>\n', "", head)
    head = re.sub(r'<link rel="preconnect" href="https://cdn\.trustindex\.io"[^>]*>\n', "", head)
    head = head.replace(
        '<link rel="preload" as="image" href="uploads/16.jpg" fetchpriority="high">',
        '<link rel="preload" as="font" type="font/woff2" href="assets/fonts/lexend-deca-latin.woff2" crossorigin>\n'
        '<link rel="preload" as="image" href="assets/img/escritorio-boituva-1228.webp" imagesrcset="assets/img/escritorio-boituva-640.webp 640w, assets/img/escritorio-boituva-1228.webp 1228w" imagesizes="100vw" fetchpriority="high">',
    )
    # CSS: fonte local, hero sem opacity 0 (não atrasa o LCP), contraste
    head = head.replace("<style>\n", "<style>\n  " + FONT_FACE + "\n", 1)
    head = head.replace(
        "@keyframes heroIn { from { opacity: 0; transform: translateY(22px); } to { opacity: 1; transform: none; } }",
        "@keyframes heroIn { from { transform: translateY(22px); } to { transform: none; } }",
    )
    # remove CSS do loader e do popup (não existem mais)
    head = re.sub(r"  @keyframes vmCardPulse[^\n]*\n  @keyframes vmGlow[^\n]*\n  @media \(prefers-reduced-motion: reduce\) \{ \.vm-loader-card[^\n]*\n", "", head)
    head = re.sub(r"  @keyframes tpModalVeil[^\n]*\n  @keyframes tpModalPop[^\n]*\n  @media \(prefers-reduced-motion: reduce\) \{ \.tp-veil[^\n]*\n", "", head)

    # ---------- BODY ----------
    # loader em tela cheia (atrasava LCP em ~1,4s) e popup de formulário (nunca era aberto)
    a, _, b = cut_block(body, '<sc-if value="{{ carregando }}"')
    body = a.rstrip() + "\n" + b
    a, _, b = cut_block(body, '<sc-if value="{{ formOpen }}"')
    body = a.rstrip() + "\n\n" + b.lstrip()

    # áreas de atuação
    a, block, b = cut_block_for(body, '<sc-for list="{{ areas }}"')
    card = re.sub(r"^<sc-for[^>]*>", "", block)[: -len("</sc-for>")]
    item_a, item_block, item_b = cut_block_for(card, '<sc-for list="{{ ar.itens }}"')
    item_tpl = re.sub(r"^<sc-for[^>]*>", "", item_block)[: -len("</sc-for>")].strip()
    cards = []
    for i, (titulo, curto, itens) in enumerate(AREAS):
        itens_html = "\n                ".join(item_tpl.replace("{{ it }}", html.escape(x)) for x in itens)
        c = item_a + itens_html + item_b
        msg = "Oi, vim pelo site e quero agendar um atendimento em Boituva sobre " + titulo + "."
        c = (c.replace("{{ ar.titulo }}", html.escape(titulo)).replace("{{ ar.num }}", "%02d" % (i + 1))
              .replace("{{ ar.curto }}", html.escape(curto)).replace("{{ ar.msg }}", html.escape(msg)))
        cards.append(c.strip())
    body = a + "\n          ".join(cards) + b

    # vale a pena saber: estado inicial + dots
    v = VALE[0]
    a, block, b = cut_block_for(body, '<sc-for list="{{ valeDots }}"')
    dot_tpl = re.sub(r"^<sc-for[^>]*>", "", block)[: -len("</sc-for>")].strip()
    dots = []
    for i, (n, _, _) in enumerate(VALE):
        d = (dot_tpl.replace("{{ d.idx }}", str(i)).replace("{{ d.n }}", n)
             .replace("{{ d.largura }}", "28px" if i == 0 else "7px")
             .replace("{{ d.cor }}", "#1EA94F" if i == 0 else "rgba(255,255,255,0.28)"))
        dots.append(d)
    body = a + "\n              ".join(dots) + b
    body = body.replace(
        '<div style="opacity: {{ valeOpacity }}; transform: {{ valeTransform }}; transition: opacity .32s ease, transform .32s cubic-bezier(.22,.7,.2,1);">',
        '<div class="vale-conteudo" id="vale-conteudo" aria-live="polite">',
    )
    body = body.replace('<div style="position: absolute; top: 0; left: 0; width: 100%; background: #1EA94F; height: {{ valeProgresso }}%;', '<div id="vale-progresso" style="position: absolute; top: 0; left: 0; width: 100%; background: #1EA94F; height: 25%;')
    body = body.replace(">{{ valeNumero }}</div>", ' id="vale-bg">01</div>', 1)
    body = body.replace("Item {{ valeNumero }} de 04", 'Item <span id="vale-num">01</span> de 04')
    body = body.replace(">{{ valeTitulo }}</h3>", f' id="vale-titulo">{html.escape(v[1])}</h3>')
    body = body.replace(">{{ valeTexto }}</p>", f' id="vale-texto">{html.escape(v[2])}</p>')
    body = body.replace('onClick="{{ valeIrDot }}"', "data-vale-dot")
    body = body.replace('onClick="{{ valeAnterior }}"', 'data-vale="-1"')
    body = body.replace('onClick="{{ valeProximo }}"', 'data-vale="1"')

    # galeria + lightbox
    for i in range(4):
        body = body.replace(f'onClick="{{{{ abrir{i} }}}}"', f'data-lb="{i}" role="button" tabindex="0" aria-label="Ampliar foto: {GALERIA[i][1]}"')
    body = body.replace('" loading="lazy">\n          <img', '">\n          <img')
    a, inner, b = unwrap_if(body, "temSelecao")
    inner = inner.replace('onClick="{{ fechar }}" class="{{ lbClass }}"', 'id="lb" class="lb" hidden role="dialog" aria-modal="true" aria-label="Foto ampliada"')
    inner = inner.replace('class="{{ lbCardClass }}"', 'class="lb-card"')
    inner = inner.replace("{{ lightboxImg }}", '<img id="lb-img" class="lb-img" alt="" decoding="async">')
    inner = inner.replace(">{{ selecionadaTitulo }}</p>", ' id="lb-titulo"></p>')
    inner = inner.replace(">{{ selecionadaLegenda }}</p>", ' id="lb-legenda"></p>')
    body = a + inner.strip() + b

    # Trustindex: carrega só quando a seção aparece
    body = body.replace('<div ref="{{ trustRef }}" style="min-height: {{ trustMinH }};"></div>', '<div id="trust" style="min-height: 320px;"></div>')
    a, inner, b = unwrap_if(body, "trustFalhou")
    inner = inner.replace("<div style=", '<div id="trust-fallback" hidden style=', 1)
    body = a + inner.strip() + b

    # balão flutuante
    a, inner, b = unwrap_if(body, "balaoAberto")
    inner = inner.replace('<div class="balao"', '<div class="balao" id="balao"', 1)
    inner = inner.replace('onClick="{{ fecharBalao }}"', 'id="balao-fechar" type="button"')
    inner = inner.replace(">{{ balaoTitulo }}</p>", f' id="balao-titulo">{html.escape(FRASES[0][0])}</p>')
    inner = inner.replace(">{{ balaoSubtitulo }}</p>", f' id="balao-sub">{html.escape(FRASES[0][1])}</p>')
    body = a + inner.strip() + b

    # links de WhatsApp: cada botão já leva a própria mensagem (sem JS)
    def wa_sub(m):
        t = m.group(0)
        msg = re.search(r'data-msg="([^"]*)"', t)
        url = wa(html.unescape(msg.group(1)) if msg else MSG_PADRAO)
        t = t.replace('href="{{ waLink }}"', f'href="{html.escape(url)}"')
        t = re.sub(r'\s+onClick="\{\{ abrirPopup \}\}"', "", t)
        if 'target="_blank"' not in t:
            t = t.replace("<a ", '<a target="_blank" rel="noopener" ', 1)
        return t

    body = re.sub(r'<a\b[^>]*href="\{\{ waLink \}\}"[^>]*>', wa_sub, body)

    body = body.replace("itemProp=", "itemprop=")
    body = body.replace("font-family: 'Lexend Deca', Helvetica, sans-serif;", "font-family: 'Lexend Deca', 'Lexend Fallback', Helvetica, sans-serif;")
    body, hover_css = converter_hover(body)
    body = trocar_imagens(body)

    # ajustes de desempenho/acessibilidade: só a imagem do hero tem prioridade alta
    body = re.sub(r'(<img src="assets/img/logo-vm-360\.webp") fetchpriority="high" decoding="async"(?=[^>]*max-width: 380px)', r'\1 loading="lazy" decoding="async"', body)
    body = re.sub(r'(<img src="assets/img/logo-vm-360\.webp") fetchpriority="high"', r'\1', body)

    leftover = re.findall(r"\{\{[^}]*\}\}|<sc-|style-hover|onClick=", body)
    if leftover:
        raise SystemExit("Sobras de template: %r" % leftover[:10])

    head = head.replace("</style>", "  " + hover_css + "\n" + EXTRA_CSS + "</style>", 1)

    js = (ROOT / "tools" / "site.js").read_text(encoding="utf-8")
    js = js.replace("__GALERIA__", json.dumps([{"src": s, "titulo": t, "legenda": l} for s, t, l in GALERIA], ensure_ascii=False))
    js = js.replace("__VALE__", json.dumps([{"n": n, "t": t, "x": x} for n, t, x in VALE], ensure_ascii=False))
    js = js.replace("__FRASES__", json.dumps([{"t": t, "s": s} for t, s in FRASES], ensure_ascii=False))

    out = (
        '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + head.strip() + "\n</head>\n<body>\n" + body.strip() + "\n<script>\n" + js.strip() + "\n</script>\n</body>\n</html>\n"
    )
    OUT.write_text(out, encoding="utf-8")
    print("ok:", OUT, len(out.encode()) // 1024, "KB")


def cut_block_for(s, start_marker):
    i = s.index(start_marker)
    depth = 0
    for m in re.finditer(r"<sc-for\b|</sc-for>", s[i:]):
        depth += 1 if m.group(0) != "</sc-for>" else -1
        if depth == 0:
            j = i + m.end()
            return s[:i], s[i:j], s[j:]
    raise ValueError(start_marker)


if __name__ == "__main__":
    main()
