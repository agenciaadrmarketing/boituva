# Advogado em Boituva — Vieira & Marques

Landing page de `https://boituva.vieiraemarquesadvogados.com/`.

## Publicar (Hostinger)

Envie para a raiz do domínio (`public_html`):

- `index.html`
- `.htaccess` (compressão + cache)
- `assets/` (imagens otimizadas e fonte)
- `uploads/` (imagem de compartilhamento, logo e favicons)
- `favicon.ico`, `robots.txt`, `sitemap.xml`

As pastas `design/` e `tools/` **não** precisam ir para o servidor.

## Como a página é gerada

`index.html` é HTML estático, gerado a partir do fonte do Claude Design:

```
python3 tools/build_static.py
```

- Fonte: `design/publicar/index.html` (template do Claude Design)
- Interações (carrossel, galeria, balão, Trustindex): `tools/site.js`, embutido no HTML
- Imagens otimizadas (WebP, tamanhos responsivos): `assets/img/`
- Fonte Lexend Deca hospedada localmente: `assets/fonts/`

Para mudar textos ou layout, edite `design/publicar/index.html` e rode o script de novo.

## Desempenho (Lighthouse, mesmo teste do PageSpeed)

| | Antes | Depois |
|---|---|---|
| Performance mobile | 25 | 100 |
| LCP mobile | 42,7 s | 1,6 s |
| Peso total | 8,1 MB | ~145 KB (com gzip) |

## Arquivos do projeto (Claude Design)

`design/` guarda o projeto completo exportado do Claude Design (handoff):
`Advogado Boituva.dc.html` + `support.js` (fonte), `publicar/`, `export/` (versão antiga empacotada),
`boituva-hostinger.zip` (pacote antigo) e `uploads/` (imagens, logos, documentos de referência).
