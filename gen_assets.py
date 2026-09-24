"""Genera los SVG animados en pixel art del README de perfil (assets/*.svg).

Temática pirata/marina original (inspirada en One Piece, sin personajes ni
emblemas de la serie). Todo se dibuja con <rect> sobre una grilla y se anima
con CSS dentro del SVG, que GitHub respeta al mostrarlo como <img>.

    python3 gen_assets.py
"""
from pathlib import Path

OUT = Path(__file__).parent / "assets"

# ---------------------------------------------------------------- fuente 5x7
FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 10001 11001 10101 10011 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "00000 00000 00000 00000 00000 00000 00000", "·": "00000 00000 00000 00100 00000 00000 00000",
    ".": "00000 00000 00000 00000 00000 00000 00100", ",": "00000 00000 00000 00000 00000 00100 01000",
    "-": "00000 00000 00000 01110 00000 00000 00000", ":": "00000 00000 00100 00000 00000 00100 00000",
    "/": "00001 00001 00010 00100 01000 10000 10000", "!": "00100 00100 00100 00100 00100 00000 00100",
    ">": "01000 00100 00010 00001 00010 00100 01000", "+": "00000 00100 00100 11111 00100 00100 00000", "|": "00100 00100 00100 00100 00100 00100 00100",
    "(": "00010 00100 01000 01000 01000 00100 00010", ")": "01000 00100 00010 00010 00010 00100 01000",
}
ACCENT = {"Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U"}


def text_rects(s, x, y, scale, color, shadow=None):
    """Texto en fuente pixel 5x7 (mayúsculas), con sombra opcional."""
    out = []
    for dx, dy, col in ([(scale, scale, shadow)] if shadow else []) + [(0, 0, color)]:
        cx = x + dx
        for ch in s.upper():
            pix = []
            base = ACCENT.get(ch, "N" if ch == "Ñ" else ch)
            rows = FONT.get(base, FONT[" "]).split()
            for r, row in enumerate(rows):
                for c, bit in enumerate(row):
                    if bit == "1":
                        pix.append((c, r))
            if ch in ACCENT:
                pix += [(2, -2), (3, -3)]
            if ch == "Ñ":
                pix += [(1, -2), (2, -2), (3, -2)]
            out += merge(pix, cx, y + dy, scale, col)
            cx += 6 * scale
    return "".join(out)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def merge(pix, x0, y0, s, col):
    """Une píxeles contiguos de una fila en un solo <rect> (menos nodos)."""
    rows = {}
    for c, r in pix:
        rows.setdefault(r, []).append(c)
    out = []
    for r, cols in rows.items():
        cols.sort()
        start = prev = cols[0]
        for c in cols[1:] + [None]:
            if c is not None and c == prev + 1:
                prev = c
                continue
            out.append(f'<rect x="{x0 + start * s}" y="{y0 + r * s}" width="{(prev - start + 1) * s}" height="{s}" fill="{col}"/>')
            if c is not None:
                start = prev = c
    return out


def sprite(rows, palette, x, y, s):
    """Dibuja un sprite de caracteres ('.' = transparente)."""
    by_col = {}
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != ".":
                by_col.setdefault(palette[ch], []).append((c, r))
    return "".join("".join(merge(p, x, y, s, col)) for col, p in by_col.items())


def svg(w, h, body, style, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'shape-rendering="crispEdges" role="img" aria-label="{title}"><title>{title}</title>'
            f"<style>{style}</style>{body}</svg>\n")


# ------------------------------------------------------------------ sprites
SHIP = [
    ".................mrrrrr.............",
    ".................mrrrr..............",
    ".................m..................",
    ".........kkkkkkkkkkkkkkkkk..........",
    "........kwwwwwwwwwwwwwwwwwk.........",
    "........kwwwwwwwwwwwwwwwwwk.........",
    "........kwwwwwwwcccwwwwwwwk.........",
    "........kwwwwwwcccccwwwwwwk.........",
    "........kwwwwwcccccccwwwwwk.........",
    "........kwwwwwwwwwwwwwwwwwk.........",
    "........kwwwwcwwwcwwwcwwwwk.........",
    "........kwwwcwcwcwcwcwcwwwk.........",
    "........kwwwwwwwwwwwwwwwwWk.........",
    ".........kWWWWWWWWWWWWWWWk..........",
    ".........kkkkkkkkmkkkkkkkk..........",
    ".................m..................",
    ".kk..............m...............kk.",
    ".kbk.............m..............kbk.",
    ".kbbkkkkkkkkkkkkkkkkkkkkkkkkkkkkbbk.",
    "..kbyyyyyyyyyyyyyyyyyyyyyyyyyyyybk..",
    "..kbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbk..",
    "...kbbkBbbkBbbkBbbkBbbkBbbkBbbbbk...",
    "....kBBBBBBBBBBBBBBBBBBBBBBBBBBBk...",
    ".....kkkkkkkkkkkkkkkkkkkkkkkkkkk....",
]
SHIP_PAL = {"k": "#2b1a10", "b": "#9a6333", "B": "#6b4423", "y": "#f2c14e", "w": "#f6f1e3",
            "W": "#d9cfb6", "m": "#6b4423", "r": "#d64545", "c": "#3a86c8"}
FLAG2 = [".................mrrrr..............", ".................mrrrrr.............",
         ".................m.................."]

CLOUD = ["......wwww......", "...wwwwwwwwww...", "..wwwwwwwwwwwww.", "wwwwwwwwwwwwwwww", ".WWWWWWWWWWWWWW."]
GULL_UP = ["k.....k", ".k...k.", "..kkk.."]
GULL_FLAT = [".......", "kkk.kkk", "...k..."]
PALM = ["..gg.gg..", ".g.gGg.g.", "....t....", "....t....", "...t.....", "...t.....", ".sssssss.", "sssssssss"]
PALM_PAL = {"g": "#3f9a4a", "G": "#2d7a38", "t": "#7a4a22", "s": "#e8c77a"}


# ------------------------------------------------------------------- banner
def banner():
    W, H = 960, 300
    b = []
    sky = ["#1a1f4a", "#262b66", "#3a3a80", "#58458f", "#7d4f96", "#a85a8c", "#d06b78", "#ec8a62", "#f6ad62"]
    band = 196 // len(sky) + 1
    for i, col in enumerate(sky):
        b.append(f'<rect x="0" y="{i * band}" width="{W}" height="{band}" fill="{col}"/>')
    # estrellas titilantes arriba
    for i, (x, y) in enumerate([(520, 18), (610, 40), (700, 14), (760, 52), (880, 24), (930, 60), (450, 60), (40, 150)]):
        b.append(f'<rect class="tw" style="animation-delay:{i * 0.4:.1f}s" x="{x}" y="{y}" width="4" height="4" fill="#fff6d5"/>')
    # sol con halo pulsante
    sun = [(c, r) for r in range(-8, 9) for c in range(-8, 9) if c * c + r * r <= 64]
    halo = [(c, r) for r in range(-11, 12) for c in range(-11, 12) if 64 < c * c + r * r <= 121]
    b.append('<g class="halo">' + "".join(merge([(c + 11, r + 11) for c, r in halo], 700, 128, 4, "#f7c873")) + "</g>")
    b.append("".join(merge([(c + 8, r + 8) for c, r in sun], 712, 140, 4, "#ffd166")))
    # isla con palmera
    b.append(sprite(PALM, PALM_PAL, 60, 160, 4))
    # mar
    sea = ["#2f7fb5", "#23679a", "#1b5480", "#144266", "#0e324f"]
    for i, col in enumerate(sea):
        b.append(f'<rect x="0" y="{192 + i * 22}" width="{W}" height="{22}" fill="{col}"/>')
    # reflejo del sol
    for i in range(5):
        b.append(f'<rect class="glint" style="animation-delay:{i * 0.3:.1f}s" x="{724 - i * 4}" y="{200 + i * 12}" width="{40 + i * 8}" height="4" fill="#f7c873" opacity=".55"/>')
    # olas: dos capas que se desplazan en sentidos opuestos
    for cls, y, col, tile in (("wv1", 192, "#8fd3f4", [(0, 1), (1, 0), (2, 0), (3, 1)]),
                              ("wv2", 236, "#5fb0dc", [(0, 0), (1, 1), (2, 1), (3, 0)])):
        rects = []
        for t in range(0, W + 64, 32):
            rects += merge(tile, t, y, 4, col)
        b.append(f'<g class="{cls}">{"".join(rects)}</g>')
    # nubes que cruzan
    b.append(f'<g class="cl1">{sprite(CLOUD, {"w": "#fbe7e0", "W": "#e5b8b8"}, 0, 70, 5)}</g>')
    b.append(f'<g class="cl2">{sprite(CLOUD, {"w": "#f3d3d6", "W": "#c99aa9"}, 0, 30, 3)}</g>')
    # nube de lluvia con gotas
    b.append(sprite(CLOUD, {"w": "#6c6f8f", "W": "#4b4d6b"}, 560, 20, 4))
    for i, x in enumerate(range(572, 616, 8)):
        b.append(f'<rect class="rain" style="animation-delay:{(i * 0.23) % 1:.2f}s" x="{x}" y="44" width="3" height="8" fill="#a9d8ff"/>')
    # gaviotas
    for i, (x, y) in enumerate([(430, 120), (470, 104)]):
        b.append(f'<g class="gull" style="animation-delay:{i * 0.9}s"><g class="f1">{sprite(GULL_UP, {"k": "#2a2238"}, x, y, 3)}</g>'
                 f'<g class="f2">{sprite(GULL_FLAT, {"k": "#2a2238"}, x, y, 3)}</g></g>')
    # barco que se mece
    b.append('<g class="ship">'
             f'<g class="f1">{sprite(SHIP, SHIP_PAL, 780, 116, 4)}</g>'
             f'<g class="f2">{sprite(FLAG2 + ["." * 36] * 0, {"m": "#6b4423", "r": "#d64545"}, 780, 116, 4)}</g>'
             "</g>")
    # textos
    b.append(text_rects("BRUNO HERRERA", 40, 34, 6, "#fff6d5", "#2a1a3e"))
    b.append(text_rects("GEOFÍSICO | CIENTÍFICO DE DATOS", 40, 98, 3, "#ffd166", "#2a1a3e"))
    b.append(text_rects("PIPELINES DE DATOS EN PYTHON", 40, 130, 2, "#fbe7e0", "#2a1a3e"))
    b.append(f'<g class="blink">{text_rects("> CONCEPCIÓN, CHILE", 40, 272, 2, "#fff6d5", "#0e324f")}</g>')
    b.append(text_rects("COFUNDADOR METGEO SPA", W - 40 - text_width("COFUNDADOR METGEO SPA", 2), 272, 2, "#8fd3f4", "#0e324f"))
    style = """
.tw{animation:tw 2.4s steps(2) infinite}@keyframes tw{50%{opacity:.15}}
.halo{animation:halo 3s steps(3) infinite}@keyframes halo{50%{opacity:.35}}
.glint{animation:glint 1.6s steps(2) infinite}@keyframes glint{50%{opacity:.15}}
.wv1{animation:wv 2.4s steps(8) infinite}@keyframes wv{to{transform:translateX(-32px)}}
.wv2{animation:wv2 3.2s steps(8) infinite}@keyframes wv2{from{transform:translateX(-32px)}to{transform:translateX(0)}}
.cl1{animation:cl 38s linear infinite}@keyframes cl{from{transform:translateX(-120px)}to{transform:translateX(980px)}}
.cl2{animation:cl 55s linear infinite;animation-delay:-20s}
.rain{animation:rain 1s linear infinite}@keyframes rain{from{transform:translateY(0);opacity:1}to{transform:translateY(40px);opacity:0}}
.gull{animation:gull 14s linear infinite}@keyframes gull{from{transform:translate(-520px,10px)}50%{transform:translate(0,-6px)}to{transform:translate(560px,12px)}}
.f1{animation:fa .6s steps(1) infinite}.f2{animation:fb .6s steps(1) infinite}
@keyframes fa{50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}
.ship{animation:bob 2s steps(2) infinite}@keyframes bob{50%{transform:translateY(4px)}}
.ship .f1{animation:none}.ship .f2{animation:fb .8s steps(1) infinite}
.blink{animation:tw 1.2s steps(1) infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""
    return svg(W, H, "".join(b), style, "Bruno Herrera: geofísico y científico de datos")


# ------------------------------------------------------------------- skills
SKILLS = [  # (etiqueta, nivel 1-10, color), según el CV
    ("PYTHON", 9, "#f2c14e"), ("XARRAY / NETCDF", 9, "#f2c14e"), ("PIPELINES ETL + QC", 8, "#f2c14e"),
    ("STREAMLIT / PLOTLY", 8, "#f2c14e"), ("SQL", 5, "#f2c14e"), ("BASH", 6, "#f2c14e"),
    ("CROCO", 8, "#4fa3d9"), ("WRF", 6, "#4fa3d9"), ("LINUX / HPC", 8, "#4fa3d9"),
    ("MATLAB", 8, "#4fa3d9"), ("ML SCIKIT-LEARN", 6, "#7bc47f"), ("CLAUDE CODE / OPENCODE", 8, "#e07a5f"),
]


def frame(x, y, w, h, fill, border, dark):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{dark}"/>'
            f'<rect x="{x + 4}" y="{y + 4}" width="{w - 8}" height="{h - 8}" fill="{border}"/>'
            f'<rect x="{x + 8}" y="{y + 8}" width="{w - 16}" height="{h - 16}" fill="{fill}"/>')


def character(x, y, s):
    """Personaje (assets/personaje.png, 48x46) que respira y pestañea."""
    from PIL import Image
    im = Image.open(OUT / "personaje.png").convert("RGBA")
    by_col = {}
    for r in range(im.height):
        for c in range(im.width):
            px = im.getpixel((c, r))
            if px[3]:
                by_col.setdefault("#%02x%02x%02x" % px[:3], []).append((c, r))
    body = "".join("".join(merge(pix, x, y, s, col)) for col, pix in by_col.items())
    eyes = [17, 18, 19, 25, 26, 27, 28]  # columnas de los ojos (filas 20 y 21)
    blink = ("".join(merge([(c, 20) for c in eyes], x, y, s, "#f7b183"))
             + "".join(merge([(c, 21) for c in eyes], x, y, s, "#2c1c1c")))
    return f'<g class="breathe">{body}<g class="blinkeye">{blink}</g></g>'


def skills():
    W, H = 960, 380
    b = [f'<rect width="{W}" height="{H}" fill="#0e324f"/>']
    # cartel "SE BUSCA"
    px, py, pw, ph = 24, 20, 260, 340
    b.append(frame(px, py, pw, ph, "#f3e2b3", "#c9a66b", "#5e3b1c"))
    for x, y in [(px + 16, py + 16), (px + pw - 24, py + 16), (px + 16, py + ph - 24), (px + pw - 24, py + ph - 24)]:
        b.append(f'<rect x="{x}" y="{y}" width="8" height="8" fill="#8b5a2b"/>')
    b.append(text_rects("SE BUSCA", px + (pw - text_width("SE BUSCA", 4)) // 2, py + 34, 4, "#4a2c14"))
    b.append(frame(px + 50, py + 76, 160, 154, "#e6f2fb", "#8b5a2b", "#4a2c14"))
    ix, iy = px + 58, py + 84  # interior del marco: 144x138
    b.append(f'<rect x="{ix}" y="{iy}" width="144" height="92" fill="#4a9be8"/>'
             f'<rect x="{ix}" y="{iy + 92}" width="144" height="46" fill="#2b6cb0"/>'
             f'<rect x="{ix}" y="{iy + 92}" width="144" height="4" fill="#8fd3f4"/>')
    b.append(f'<clipPath id="marco"><rect x="{ix}" y="{iy}" width="144" height="138"/></clipPath>'
             f'<g clip-path="url(#marco)">{character(ix, iy, 3)}</g>')
    b.append(text_rects("BRUNO H.", px + (pw - text_width("BRUNO H.", 3)) // 2, py + 246, 3, "#4a2c14"))
    b.append(text_rects("RECOMPENSA", px + (pw - text_width("RECOMPENSA", 2)) // 2, py + 278, 2, "#8b5a2b"))
    b.append(text_rects("1.970.000", px + (pw - text_width("1.970.000", 3)) // 2, py + 298, 3, "#4a2c14"))
    b.append(text_rects("REGISTROS PROCESADOS", px + (pw - text_width("REGISTROS PROCESADOS", 1)) // 2, py + 324, 1, "#8b5a2b"))
    # panel de habilidades
    sx, sy = 310, 20
    b.append(frame(sx, sy, 626, 340, "#16304d", "#3a5f86", "#081a2b"))
    b.append(text_rects("HABILIDADES", sx + 28, sy + 26, 4, "#ffd166", "#081a2b"))
    b.append(f'<g class="blink">{text_rects(">", sx + 28 + text_width("HABILIDADES ", 4), sy + 26, 4, "#ffd166")}</g>')
    col_w = 296
    for i, (name, lvl, col) in enumerate(SKILLS):
        cx = sx + 28 + (i // 6) * col_w
        cy = sy + 76 + (i % 6) * 42
        b.append(text_rects(name, cx, cy, 2, "#e8eef5"))
        empty, full = [], []
        for s in range(10):
            x = cx + s * 26
            empty.append(f'<rect x="{x}" y="{cy + 18}" width="22" height="12" fill="#0b2238"/>')
            if s < lvl:
                full.append(f'<rect x="{x}" y="{cy + 18}" width="22" height="12" fill="{col}"/>'
                            f'<rect x="{x}" y="{cy + 18}" width="22" height="3" fill="#ffffff" opacity=".35"/>')
        b.append("".join(empty))
        # la barra llena es el estado final por defecto; la animación solo la "barre" desde la izquierda
        b.append(f'<g class="bar" style="animation-delay:{0.2 + i * 0.15:.2f}s;animation-timing-function:steps({lvl})">{"".join(full)}</g>')
    legend = [("LENGUAJES Y DATOS", "#f2c14e"), ("MODELACIÓN", "#4fa3d9"), ("MACHINE LEARNING", "#7bc47f"), ("DESARROLLO CON IA", "#e07a5f")]
    lx = sx + 28
    for name, col in legend:
        b.append(f'<rect x="{lx}" y="{sy + 326}" width="8" height="8" fill="{col}"/>')
        b.append(text_rects(name, lx + 14, sy + 326, 1, "#9fb6cc"))
        lx += 26 + text_width(name, 1) + 24
    style = """
.bar{transform-box:fill-box;transform-origin:0 50%;animation:bar .9s both}@keyframes bar{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}
.breathe{animation:breathe 1.6s steps(1) infinite}@keyframes breathe{50%{transform:translateY(3px)}}
.blinkeye{opacity:0;animation:blinkeye 3.6s steps(1) infinite}@keyframes blinkeye{0%,93%{opacity:0}94%,97%{opacity:1}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.blinkeye{opacity:0}}
"""
    return svg(W, H, "".join(b), style, "Cartel de se busca con mi personaje en pixel art y panel de habilidades")


# ---------------------------------------------------------------------- mapa
ISLANDS = [(600, 120, "MONITOR CONCEPCIÓN")]  # solo proyectos públicos


def island(cx, cy, rx, ry):
    land, sand = [], []
    for r in range(-ry, ry + 1):
        for c in range(-rx, rx + 1):
            d = (c / rx) ** 2 + (r / ry) ** 2
            if d <= 0.55:
                land.append((c + rx, r + ry))
            elif d <= 1:
                sand.append((c + rx, r + ry))
    x0, y0 = cx - rx * 4, cy - ry * 4
    return "".join(merge(sand, x0, y0, 4, "#e8c77a")) + "".join(merge(land, x0, y0, 4, "#4f9a4a"))


def treasure_map():
    W, H = 960, 300
    b = [frame(0, 0, W, H, "#2f7fb5", "#c9a66b", "#5e3b1c")]
    # textura de agua
    for i, (x, y) in enumerate([(60, 60), (250, 200), (470, 250), (700, 40), (520, 110), (900, 230), (180, 250), (780, 190)]):
        b.append(f'<g class="wave" style="animation-delay:{i * 0.35:.2f}s">'
                 + "".join(merge([(0, 1), (1, 0), (2, 0), (3, 1), (4, 1), (5, 0), (6, 0), (7, 1)], x, y, 3, "#8fd3f4")) + "</g>")
    route = "M70,230 C200,120 320,260 430,190 S540,90 590,112"
    b.append(f'<path d="{route}" fill="none" stroke="#5e3b1c" stroke-width="4" opacity=".35" shape-rendering="auto"/>')
    b.append(f'<path class="route" d="{route}" fill="none" stroke="#fff6d5" stroke-width="4" stroke-dasharray="10 10" shape-rendering="auto"/>')
    for x, y, name in ISLANDS:
        b.append(island(x, y, 12, 6))
        b.append(sprite(PALM, PALM_PAL, x - 18, y - 40, 4))
        tw = text_width(name, 2)
        b.append(f'<rect x="{x - tw // 2 - 6}" y="{y + 30}" width="{tw + 12}" height="26" fill="#f3e2b3"/>'
                 f'<rect x="{x - tw // 2 - 6}" y="{y + 52}" width="{tw + 12}" height="4" fill="#c9a66b"/>')
        b.append(text_rects(name, x - tw // 2, y + 36, 2, "#4a2c14"))
    # X del tesoro
    b.append(f'<g class="blink">{text_rects("X", 636, 100, 4, "#d64545", "#5e3b1c")}</g>')
    # rosa de los vientos
    b.append(text_rects("N", 896, 214, 2, "#fff6d5"))
    b.append('<rect x="900" y="232" width="4" height="36" fill="#fff6d5"/><rect x="884" y="248" width="36" height="4" fill="#fff6d5"/>'
             '<rect x="896" y="244" width="12" height="12" fill="#d64545"/>')
    b.append(text_rects("RUTA DE PROYECTOS", 24, 268, 2, "#fff6d5", "#0e324f"))
    # barquito que recorre la ruta
    small = sprite(SHIP, SHIP_PAL, -36, -44, 2)
    b.append(f'<g>{small}<animateMotion dur="16s" repeatCount="indefinite" path="{route}"/></g>')
    style = """
.route{animation:dash 1s linear infinite}@keyframes dash{to{stroke-dashoffset:-20}}
.wave{animation:wave 1.4s steps(2) infinite}@keyframes wave{50%{transform:translateX(6px)}}
.blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:.2}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""
    return svg(W, H, "".join(b), style, "Mapa de proyectos: Monitor meteorológico MetGeo Concepción")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in (("banner", banner), ("skills", skills), ("map", treasure_map)):
        data = fn()
        (OUT / f"{name}.svg").write_text(data, encoding="utf-8")
        print(f"assets/{name}.svg  {len(data) / 1024:.0f} KB")
