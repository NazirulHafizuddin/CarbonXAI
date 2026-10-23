"""
landing.py
Scroll-based landing page for CarbonXAI. It is shown before the dashboard (see app.py).

How it works
- Every screen is a st.container(key="lpsec_...") that CSS turns into a full-height panel.
  Text and cards inside are plain HTML written with st.markdown(unsafe_allow_html=True).
- Buttons that must do something in Python (go to the dashboard) are real Streamlit buttons.
  Buttons that only scroll (Start exploring, menu links) are plain HTML anchors.
- Horizontal storytelling is a CSS scroll-snap row (no JavaScript).
- Scroll reveal uses CSS scroll-driven animation. Browsers without it simply show everything.

Where to customise (search for the TODO markers below)
- FEEDBACK_URL : paste your user acceptance test form link.
- IMAGES       : paste your own photos for the dark screens. Without them, built-in vector art is used.

Maintainer notes (same rules as ui.py)
- Markdown ends an HTML block at a blank line, and indents of 4 spaces become code. Every HTML
  string goes through _h(), which removes line breaks and indents.
- Avoid the dollar sign in text: Streamlit would try to render it as LaTeX.
"""

import base64
import math
import os
import random
from html import escape

import streamlit as st

import ui

# ═════════════════════════════ CONFIGURE HERE ═════════════════════════════
# TODO (feedback form): paste the link of your User Acceptance Test form between the quotes.
# While it is empty, the feedback buttons show as a clearly marked placeholder.
FEEDBACK_URL = "https://forms.cloud.microsoft/r/0DiMxG1xhK"

# TODO (images): put your files in the assets/ folder and write the file name here, for example
#   "hero": "assets/hero.jpg"
# Use landscape photos, about 1600 px wide and under 400 KB each (the file is sent to the browser
# inside the page). A dark gradient is added on top so the white text stays readable.
#   hero     -> screen 1, Earth / sustainability / clean future
#   why      -> screen 3, city pollution, transport, industry, renewable energy
#   action   -> screen 5 (optional), left empty keeps the soft green panel
#   feedback -> screen 6, anything calm and clean
IMAGES = {"hero": None, "why": None, "action": None, "feedback": None}

DASHBOARD_PAGE = "dashboard.py"
INTRO_PAGE = "landing_page.py"
PROJECT_TITLE = ("An Explainable Machine Learning Framework for Carbon Emission Prediction "
                 "and Contributing Factor Analysis Using SHAP")


def _h(s):
    """Collapse an HTML string to one line (see maintainer notes)."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


# ═════════════════════════════ ICONS ═════════════════════════════
_ICONS = {
    "co2": "<circle cx='12' cy='12' r='9'/><path d='M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18'/>",
    "heat": "<path d='M10 14V5a2 2 0 0 1 4 0v9a4 4 0 1 1-4 0z'/><path d='M12 9v7'/>",
    "foot": "<path d='M7 20c-2 0-3-2-3-4 0-3 2-5 4-5s3 2 3 5c0 2-1 4-4 4z'/><path d='M15 13c-2 0-3-2-3-4 0-3 2-5 4-5s3 2 3 5c0 2-1 4-4 4z' transform='translate(1 3)'/>",
    "car": "<path d='M5 13l1.6-4.2A2 2 0 0 1 8.5 7.5h7a2 2 0 0 1 1.9 1.3L19 13'/><rect x='3' y='13' width='18' height='5' rx='2'/><circle cx='7.5' cy='18' r='1.4'/><circle cx='16.5' cy='18' r='1.4'/>",
    "plane": "<path d='M21 3L3 10.5l6.5 2.5L12 20z'/><path d='M9.5 13L21 3'/>",
    "bolt": "<path d='M13 2L4 14h6l-1 8 9-12h-6z'/>",
    "food": "<path d='M12 21c-5 0-8-4-8-8 0-3 2-5 5-5 1.2 0 2 .5 3 .5s1.8-.5 3-.5c3 0 5 2 5 5 0 4-3 8-8 8z'/><path d='M12 8c0-2 1-4 3-5'/>",
    "bag": "<path d='M5 8h14l-1 12H6z'/><path d='M9 8V6a3 3 0 0 1 6 0v2'/>",
    "bin": "<path d='M5 7h14M10 7V4h4v3M7 7l1 13h8l1-13'/><path d='M10 11v6M14 11v6'/>",
    "sliders": "<path d='M4 7h10M18 7h2M4 17h2M10 17h10'/><circle cx='16' cy='7' r='2'/><circle cx='8' cy='17' r='2'/>",
    "bars": "<path d='M5 20V10M12 20V4M19 20v-7'/>",
    "spark": "<path d='M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z'/><path d='M19 16l.7 1.8L21.5 18.5l-1.8.7L19 21l-.7-1.8-1.8-.7 1.8-.7z'/>",
    "leaf": "<path d='M5 19c0-9 5-14 14-14 0 9-5 14-14 14z'/><path d='M5 19L13 11'/>",
    "route": "<circle cx='6' cy='18' r='2'/><circle cx='18' cy='6' r='2'/><path d='M8 18h6a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h6'/>",
    "plug": "<path d='M9 3v5M15 3v5M7 8h10v3a5 5 0 0 1-10 0z'/><path d='M12 16v5'/>",
}


def icon(name, size=26, stroke=1.8):
    return (f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='currentColor' "
            f"stroke-width='{stroke}' stroke-linecap='round' stroke-linejoin='round'>{_ICONS[name]}</svg>")


# ═════════════════════════════ BUILT-IN ARTWORK ═════════════════════════════
def _svg_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


@st.cache_data(show_spinner=False)
def earth_art():
    """A dotted globe, lit from the upper left, with an orbit and two accent glows."""
    cx = cy = 450
    R = 330
    tilt, spin = math.radians(-20), math.radians(-30)
    light = (-0.45, 0.55, 0.70)
    dots = []
    for lat in range(-84, 85, 6):
        phi = math.radians(lat)
        n = max(1, int(round(2 * math.pi * math.cos(phi) / math.radians(6))))
        for k in range(n):
            lam = 2 * math.pi * k / n + spin
            x, y, z = math.cos(phi) * math.sin(lam), math.sin(phi), math.cos(phi) * math.cos(lam)
            y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
            if z < 0.04:
                continue
            lit = max(0.0, x * light[0] + y * light[1] + z * light[2])
            shade = 0.10 + 0.90 * lit
            r = 1.3 + 3.3 * z
            red, green, blue = (int(a + (b - a) * shade) for a, b in ((34, 212), (66, 238), (22, 94)))
            dots.append(f"<circle cx='{cx + R * x:.1f}' cy='{cy - R * y:.1f}' r='{r:.1f}' "
                        f"fill='rgb({red},{green},{blue})' opacity='{0.28 + 0.72 * shade:.2f}'/>")
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 900'>"
        "<defs><radialGradient id='g' cx='38%' cy='36%' r='62%'><stop offset='0' stop-color='#C5E04F' stop-opacity='.38'/>"
        "<stop offset='1' stop-color='#C5E04F' stop-opacity='0'/></radialGradient>"
        "<radialGradient id='p' cx='50%' cy='50%' r='50%'><stop offset='0' stop-color='#FF7DA6' stop-opacity='.55'/>"
        "<stop offset='1' stop-color='#FF7DA6' stop-opacity='0'/></radialGradient></defs>"
        "<circle cx='450' cy='450' r='440' fill='url(#g)'/>"
        "<circle cx='770' cy='730' r='150' fill='url(#p)'/>"
        + "".join(dots) +
        "<ellipse cx='450' cy='450' rx='430' ry='120' fill='none' stroke='#fff' stroke-opacity='.16' "
        "stroke-width='1.4' transform='rotate(-24 450 450)'/>"
        "<circle r='7' fill='#FF7DA6'><animateMotion dur='26s' repeatCount='indefinite' rotate='auto' "
        "path='M 20 450 a 430 120 0 1 1 860 0 a 430 120 0 1 1 -860 0' /></circle>"
        "</svg>")
    return _svg_uri(svg)


@st.cache_data(show_spinner=False)
def city_art():
    """Skyline, chimneys with smoke, and wind turbines on a ridge. Flat and dark on purpose."""
    rnd = random.Random(7)
    parts = ["<defs><linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#0B0F0C' stop-opacity='0'/>"
             "<stop offset='1' stop-color='#E2487A' stop-opacity='.28'/></linearGradient>"
             "<filter id='bl'><feGaussianBlur stdDeviation='14'/></filter></defs>",
             "<rect width='1600' height='700' fill='url(#sky)'/>",
             "<circle cx='1180' cy='470' r='150' fill='#FF7DA6' opacity='.22' filter='url(#bl)'/>"]
    # distant ridge with wind turbines
    parts.append("<path d='M700 700 L700 560 Q900 500 1100 540 T1600 520 L1600 700z' fill='#141A15'/>")
    for tx, ty, s in ((980, 528, 1.0), (1160, 520, 1.25), (1340, 506, 1.0), (1500, 500, 0.8)):
        parts.append(f"<g transform='translate({tx} {ty}) scale({s})'><path d='M-2 0h4l-1 110h-2z' fill='#2A3326'/>"
                     "<g><path d='M0 0 L-4 -46 L4 -46z' fill='#C5E04F' opacity='.85'/>"
                     "<path d='M0 0 L-4 -46 L4 -46z' fill='#C5E04F' opacity='.85' transform='rotate(120)'/>"
                     "<path d='M0 0 L-4 -46 L4 -46z' fill='#C5E04F' opacity='.85' transform='rotate(240)'/>"
                     f"<animateTransform attributeName='transform' type='rotate' from='0' to='360' dur='{9 + s * 4:.0f}s' repeatCount='indefinite'/></g>"
                     "<circle r='4' fill='#C5E04F'/></g>")
    # smoke
    for sx, sy, n in ((290, 330, 5), (352, 360, 4), (415, 340, 5)):
        for i in range(n):
            parts.append(f"<circle cx='{sx + i * 26 + rnd.randint(-8, 8)}' cy='{sy - i * 46}' r='{26 + i * 12}' fill='#9AA09A' opacity='{0.22 - i * 0.03:.2f}' filter='url(#bl)'/>")
    # skyline
    x = 0
    while x < 880:
        w = rnd.randint(46, 96)
        h = rnd.randint(150, 400) if x > 420 else rnd.randint(90, 230)
        parts.append(f"<rect x='{x}' y='{700 - h}' width='{w}' height='{h}' fill='#161B17'/>")
        for wy in range(700 - h + 18, 690, 26):
            for wx in range(x + 10, x + w - 10, 16):
                if rnd.random() < 0.22:
                    parts.append(f"<rect x='{wx}' y='{wy}' width='6' height='9' rx='1' fill='#C5E04F' opacity='.35'/>")
        x += w + rnd.randint(4, 14)
    # factory with chimneys
    parts.append("<rect x='250' y='540' width='240' height='160' fill='#1D241E'/>"
                 "<rect x='270' y='350' width='34' height='190' fill='#1D241E'/><rect x='334' y='380' width='34' height='160' fill='#1D241E'/>"
                 "<rect x='398' y='360' width='34' height='180' fill='#1D241E'/>"
                 "<path d='M250 540 L330 500 L330 540 L410 500 L410 540 L490 500 L490 540z' fill='#1D241E'/>")
    parts.append("<rect x='0' y='680' width='1600' height='20' fill='#0B0F0C'/>")
    return _svg_uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1600 700' preserveAspectRatio='xMidYMax slice'>"
                    + "".join(parts) + "</svg>")


@st.cache_data(show_spinner=False)
def _photo_uri(path, mtime):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "jpeg")
    with open(path, "rb") as f:
        return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()


def _photo(key):
    path = IMAGES.get(key)
    if path and os.path.exists(path):
        return _photo_uri(path, os.path.getmtime(path))
    return None


def _card_img(filename):
    """Base64 data URI for a file in assets/, used as a lp-card background photo.
    Returns None (plain colour card) if the file is missing, same fallback rule
    as know_your_carbon.py's _img()."""
    path = os.path.join("assets", filename)
    if os.path.exists(path):
        return _photo_uri(path, os.path.getmtime(path))
    return None


# ═════════════════════════════ STYLE ═════════════════════════════
LANDING_CSS = """
<style>
/* ---------- shell: full width, smooth scrolling with gentle snap ---------- */
[data-testid="stMain"] { scroll-behavior: smooth; scroll-snap-type: y proximity; }
[data-testid="stMainBlockContainer"], .block-container { max-width: 100% !important; padding: 0 !important; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap: 0 !important; }
.lp-anchor { display:block; height:0; }

/* ---------- screens ---------- */
[class*="st-key-lpsec_"] { --lp-pad: max(24px, calc((100vw - 28px - 1180px) / 2));
  position:relative; scroll-snap-align:start; min-height:100vh; box-sizing:border-box;
  padding: 118px var(--lp-pad) 84px; display:flex; flex-direction:column; justify-content:center; gap: 1.15rem; }
.st-key-lpsec_hero, .st-key-lpsec_why, .st-key-lpsec_feedback, .st-key-lpsec_action {
  width: calc(100% - 28px); margin: 14px; border-radius: 40px; overflow: hidden; }
.st-key-lpsec_hero, .st-key-lpsec_why, .st-key-lpsec_feedback { color:#fff; background-color:#0B0F0C; }
.st-key-lpsec_action { background: linear-gradient(160deg, #EEF6C9 0%, #DCEB9B 55%, #C5E04F 130%); }
[class*="st-key-lpsec_"] [data-testid="stElementContainer"] { width:100%; }

/* ---------- type ---------- */
.lp-eyebrow { font-size:13px; letter-spacing:.16em; text-transform:uppercase; font-weight:700; color:#6F9A12; }
.dark .lp-eyebrow, .lp-eyebrow.on-dark { color:#C5E04F; }
.lp-h1 { font-size: clamp(38px, 5vw, 68px); font-weight:700 !important; line-height:1.0; letter-spacing:-.045em; text-wrap:balance; margin:14px 0 18px 0; color:#fff; }
.lp-h1 b { font-weight:600; color:#C5E04F; }
.lp-h2 { font-size: clamp(32px, 4.2vw, 58px); font-weight:700 !important; line-height:1.06; letter-spacing:-.035em; text-wrap:balance; margin:10px 0 10px 0; color:var(--cx-ink); max-width: 20ch; }
.lp-h2.wide { max-width: 24ch; }
.lp-h2.on-dark { color:#fff; }
.lp-lead { font-size: clamp(16px, 1.45vw, 20px); line-height:1.55; max-width:56ch; color:var(--cx-muted); margin:0; text-wrap:pretty; font-weight:400; }
.lp-lead.on-dark { color: rgba(255,255,255,.74); }
.lp-hint { font-size:13.5px; color:var(--cx-muted-2); display:flex; align-items:center; gap:8px; margin:6px 0 10px 0; }
.lp-fine { margin-top:18px; font-size:12.5px; color:var(--cx-muted); line-height:1.5; max-width:70ch; }

/* ---------- hero extras ---------- */
.lp-stats { display:flex; gap:10px; flex-wrap:wrap; margin-top:22px; }
.lp-stat { padding:9px 16px; border-radius:999px; font-size:13.5px; font-weight:600; background:rgba(255,255,255,.10);
  border:1px solid rgba(255,255,255,.18); color:#EAF0EA; backdrop-filter: blur(10px); }
.st-key-lpsec_hero::after { content:"Scroll to continue"; position:absolute; left:50%; bottom:26px; transform:translateX(-50%); white-space:nowrap;
  font-size:12.5px; letter-spacing:.14em; text-transform:uppercase; color:rgba(255,255,255,.6); pointer-events:none; }
.st-key-lpsec_hero::before { content:""; position:absolute; left:50%; bottom:58px; width:1px; height:34px; pointer-events:none;
  background:linear-gradient(180deg, rgba(197,224,79,.9), rgba(197,224,79,0)); animation: lp-cue 2.2s ease-in-out infinite; transform-origin: top; }
@keyframes lp-cue { 0% { transform:scaleY(0); } 50% { transform:scaleY(1); } 100% { transform:scaleY(1); opacity:0; } }

/* ---------- fixed top menu ---------- */
.st-key-lp_nav { position:fixed; top:14px; left:50%; transform:translateX(-50%); width:min(1180px, calc(100vw - 28px)); z-index:999;
  padding:6px 8px 6px 18px; border-radius:999px; background:var(--cx-nav-bg); border:1px solid var(--cx-nav-border);
  backdrop-filter: blur(18px) saturate(1.5); -webkit-backdrop-filter: blur(18px) saturate(1.5); box-shadow:0 16px 40px -22px rgba(0,0,0,.45); }
.st-key-lp_nav [data-testid="stHorizontalBlock"] { align-items:center; gap:8px; }
.lp-links { display:flex; justify-content:center; gap:4px; flex-wrap:wrap; }
.lp-links a { padding:8px 14px; border-radius:999px; font-size:14px; font-weight:600; color:var(--cx-ink) !important; text-decoration:none !important; transition:background .2s; }
.lp-links a:hover { background:rgba(127,130,127,.16); }

/* ---------- pills and buttons ---------- */
.lp-pill { display:inline-flex; align-items:center; gap:10px; padding:14px 26px; border-radius:999px; font-weight:700; font-size:16px;
  text-decoration:none !important; transition: transform .25s ease, background .25s ease, box-shadow .25s ease; white-space:nowrap; }
.lp-pill.lime { background:#C5E04F; color:#0F1110 !important; box-shadow:0 14px 30px -14px rgba(197,224,79,.9); }
.lp-pill.lime:hover { transform:translateY(-2px); background:#D3EC6A; }
[class*="st-key-lpb_"] button, [class*="st-key-lpb_"] a[data-testid*="LinkButton"] { border-radius:999px !important; padding:13px 26px !important; min-height:0 !important;
  font-weight:700 !important; font-size:16px !important; transition: transform .25s ease, background .25s ease !important; box-shadow:none !important; }
[class*="st-key-lpb_"] button *, [class*="st-key-lpb_"] a * { color:inherit !important; font-weight:700 !important; font-size:16px !important; margin:0; }
[class*="st-key-lpb_"] button:hover:not(:disabled) { transform:translateY(-2px); }
[class*="st-key-lpb_ghost"] button, [class*="st-key-lpb_ghost"] a { background:rgba(255,255,255,.10) !important; color:#fff !important; border:1px solid rgba(255,255,255,.42) !important; backdrop-filter: blur(10px); }
[class*="st-key-lpb_ghost"] button:hover:not(:disabled) { background:rgba(255,255,255,.2) !important; }
[class*="st-key-lpb_dark"] button, [class*="st-key-lpb_dark"] a { background:#0F1110 !important; color:#fff !important; border:1px solid #0F1110 !important; }
[class*="st-key-lpb_line"] button, [class*="st-key-lpb_line"] a { background:var(--cx-chip-bg) !important; color:var(--cx-ink) !important; border:1px solid var(--cx-chip-border) !important; }
[class*="st-key-lpb_line"] button:hover:not(:disabled) { background:#0F1110 !important; color:#fff !important; }
[class*="st-key-lpb_lime"] button, [class*="st-key-lpb_lime"] a { background:#C5E04F !important; color:#0F1110 !important; border:1px solid #C5E04F !important; }
[class*="st-key-lpb_"] button:disabled { opacity:.55; cursor:not-allowed; }
.st-key-lpb_skip { display:flex; justify-content:flex-end; width:100% !important; }
.st-key-lpb_skip [data-testid="stButton"] { width:auto !important; }
.st-key-lp_nav [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; }
.st-key-lp_nav [data-testid="stColumn"] { min-width:0 !important; min-height:44px; justify-content:center; }
.st-key-lp_nav .cx-brand { height:44px; }
.st-key-lpb_skip button { padding:9px 20px !important; font-size:14px !important; background:#0F1110 !important; color:#fff !important; border:1px solid #0F1110 !important; }
.st-key-lpb_skip button * { font-size:14px !important; }

/* ---------- horizontal rail ---------- */
.lp-rail { display:flex; gap:16px; overflow-x:auto; scroll-snap-type:x mandatory; scroll-padding-inline: var(--lp-pad);
  padding:16px var(--lp-pad) 46px var(--lp-pad); margin:-16px calc(-1 * var(--lp-pad)) -22px calc(-1 * var(--lp-pad)); scrollbar-width:thin;
  scrollbar-color: rgba(15,17,16,.55) rgba(15,17,16,.08); -webkit-overflow-scrolling:touch; overscroll-behavior-x: contain; }
.lp-rail::-webkit-scrollbar { height:6px; } .lp-rail::-webkit-scrollbar-track { background:rgba(15,17,16,.08); border-radius:6px; }
.lp-rail::-webkit-scrollbar-thumb { background:rgba(15,17,16,.5); border-radius:6px; }
.lp-card { flex:0 0 min(80vw, 330px); min-height:310px; scroll-snap-align:start; border-radius:30px; padding:26px; background:var(--cx-card-bg); color:var(--cx-ink); position:relative;
  box-shadow: 0 1px 0 var(--cx-card-shadow-inset) inset, 0 24px 44px -28px rgba(20,22,20,.35); transition: transform .35s ease, box-shadow .35s ease; display:flex; flex-direction:column; }
.lp-card:hover { transform:translateY(-6px); box-shadow: 0 1px 0 var(--cx-card-shadow-inset) inset, 0 34px 54px -26px rgba(20,22,20,.42); }
.lp-card.dark { background:linear-gradient(180deg,#171A17,#0C0E0C); color:#fff; }
.lp-card.lime { background:linear-gradient(160deg,#DCEF86,#B4D13C); }
.lp-card.pink { background:linear-gradient(165deg,#FFB6CD,#FF5088); color:#fff; }
.lp-card.green { background:linear-gradient(165deg,#8FE3A1,#1E8A47); color:#fff; }
.lp-card.blue { background:linear-gradient(165deg,#8FD3F4,#1C6FA8); color:#fff; }
.lp-card.teal { background:linear-gradient(165deg,#7FE8D0,#15876E); color:#fff; }
.lp-card.violet { background:linear-gradient(165deg,#C7C3FF,#5B4BC4); color:#fff; }
.lp-card.wide { flex-basis:min(86vw, 400px); }
.lp-card .ic { width:54px; height:54px; border-radius:17px; display:grid; place-items:center; background:var(--cx-icon-bg); color:var(--cx-ink); }
.lp-card.dark .ic, .lp-card.pink .ic, .lp-card.green .ic, .lp-card.blue .ic, .lp-card.teal .ic, .lp-card.violet .ic { background:rgba(255,255,255,.16); color:#fff; }
.lp-card.lime .ic { background:rgba(15,17,16,.10); }
.lp-card .tag { margin-top:auto; font-size:12.5px; letter-spacing:.12em; text-transform:uppercase; font-weight:700; opacity:.55; }
.lp-card h3 { font-size:24px; font-weight:600 !important; letter-spacing:-.03em; text-wrap:balance; margin:22px 0 8px 0; color:inherit; line-height:1.12; }
.lp-card p { font-size:15.5px; line-height:1.55; margin:0 0 18px 0; color:inherit; opacity:.82; }
.lp-card.dark h3, .lp-card.pink h3, .lp-card.green h3, .lp-card.blue h3, .lp-card.teal h3, .lp-card.violet h3 { color:#fff; }

.lp-card.photo { color:#fff; background-size:cover; background-position:center; background-color:#0C0E0C; overflow:hidden; }
.lp-card.photo::before { content:""; position:absolute; inset:0; border-radius:inherit;
  background:linear-gradient(180deg, rgba(8,11,9,.90) 0%, rgba(8,11,9,.42) 46%, rgba(8,11,9,.06) 76%); }
.lp-card.photo > * { position:relative; z-index:1; }
.lp-card.photo .ic { background:rgba(255,255,255,.22); color:#fff; backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); }
.lp-card.photo h3, .lp-card.photo p, .lp-card.photo .tag { color:#fff; }


/* ---------- rail arrows (Apple-style round buttons) ---------- */
.lp-arrows { display:flex; justify-content:flex-end; gap:12px; margin-top:4px; }
.lp-arrow { width:44px; height:44px; border-radius:50%; border:0; display:grid; place-items:center; cursor:pointer; padding:0;
  background:var(--cx-pill-bg); color:var(--cx-pill-text); transition: background .2s, transform .2s, opacity .2s; }
.lp-arrow:hover:not(:disabled) { background:#0F1110; color:#fff; transform:scale(1.06); }
:root[data-theme="dark"] .lp-arrow:hover:not(:disabled) { background:#C5E04F; color:#0F1110; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .lp-arrow:hover:not(:disabled) { background:#C5E04F; color:#0F1110; } }
.lp-arrow:focus-visible { outline:2px solid #6F9A12; outline-offset:2px; }
.lp-arrow:disabled { opacity:.35; cursor:default; }
.lp-arrow svg { width:20px; height:20px; }
@media (hover:none) and (max-width:760px) { .lp-arrows { display:none; } }

/* ---------- glass cards on dark screens ---------- */
.lp-trio { display:grid; grid-template-columns:repeat(3, 1fr); gap:16px; margin-top:18px; }
.lp-glass { background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.16); border-radius:28px; padding:26px;
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); transition: transform .35s ease, background .35s ease; }
.lp-glass:hover { transform:translateY(-5px); background:rgba(255,255,255,.12); }
.lp-glass .num { font-size:clamp(38px, 4.2vw, 58px); font-weight:600; letter-spacing:-.045em; line-height:1; color:#C5E04F; }
.lp-glass h3 { font-size:21px; font-weight:600 !important; margin:14px 0 8px 0; color:#fff; letter-spacing:-.01em; }
.lp-glass p { font-size:15px; line-height:1.55; margin:0; color:rgba(255,255,255,.76); }
.lp-glass .src { display:inline-block; margin-top:14px; font-size:12px; color:rgba(255,255,255,.55); }
.lp-chip { display:inline-flex; align-items:center; gap:8px; padding:8px 16px; border-radius:999px; font-size:13.5px; font-weight:600; width:fit-content;
  background:rgba(197,224,79,.14); border:1px solid rgba(197,224,79,.45); color:#DDF08A; }

/* ---------- module cards and flow ---------- */
.lp-mod { margin-bottom:12px; background:#fff; border-radius:30px; padding:24px; min-height:318px; position:relative; overflow:hidden;
  box-shadow: 0 1px 0 rgba(255,255,255,.9) inset, 0 24px 44px -28px rgba(20,22,20,.35); transition: transform .35s ease; }
.lp-mod:hover { transform:translateY(-6px); }
.lp-mod .n { position:absolute; right:22px; top:16px; font-size:54px; font-weight:600; letter-spacing:-.05em; color:rgba(15,17,16,.07); }
.lp-mod .ic { width:54px; height:54px; border-radius:17px; display:grid; place-items:center; background:#0F1110; color:#C5E04F; }
.lp-mod.pink .ic { background:linear-gradient(165deg,#FF9DBD,#FF5088); color:#fff; }
.lp-mod.lime .ic { background:#C5E04F; color:#0F1110; }
.lp-mod h3 { font-size:21px; font-weight:600 !important; letter-spacing:-.02em; line-height:1.25; min-height:52.5px;
  margin:20px 0 8px 0; color:#0F1110; }
.lp-mod p { font-size:15px; line-height:1.55; margin:0; color:#5A5F63; }
.lp-flow { display:flex; align-items:center; gap:9px; flex-wrap:wrap; margin-top:22px; }
.lp-flow .st { display:flex; align-items:center; gap:10px; padding:11px 16px 11px 11px; border-radius:999px; background:rgba(255,255,255,.75);
  border:1px solid rgba(15,17,16,.08); font-weight:600; font-size:14.5px; backdrop-filter: blur(10px); white-space:nowrap; }
.lp-flow .st b { width:30px; height:30px; border-radius:50%; background:#0F1110; color:#C5E04F; display:grid; place-items:center; font-size:14px; }
.lp-flow .ar { color:#9AA09A; font-size:20px; }

/* ---------- action cards ---------- */
.lp-acts { display:grid; grid-template-columns:repeat(5, 1fr); gap:14px; margin-top:20px; }
.lp-act { background:rgba(255,255,255,.78); border:1px solid rgba(255,255,255,.9); border-radius:28px; padding:22px 20px; min-height:236px;
  backdrop-filter: blur(14px); transition: transform .35s ease, background .35s ease; box-shadow:0 20px 40px -28px rgba(60,80,10,.5); }
.lp-act:hover { transform:translateY(-6px); background:#fff; }
.lp-act .ic { width:48px; height:48px; border-radius:15px; display:grid; place-items:center; background:#0F1110; color:#C5E04F; }
.lp-act h3 { font-size:19px; font-weight:600 !important; letter-spacing:-.01em; margin:18px 0 8px 0; color:#0F1110; line-height:1.15; }
.lp-act p { font-size:14px; line-height:1.5; margin:0; color:#4D5348; }

/* ---------- feedback ---------- */
.lp-form { background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.18); border-radius:30px; padding:28px; max-width:620px; margin-top:22px;
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); }
.lp-form .lab { font-size:13px; letter-spacing:.14em; text-transform:uppercase; font-weight:700; color:#C5E04F; }
.lp-form h3 { font-size:28px; font-weight:600 !important; letter-spacing:-.02em; margin:10px 0 8px 0; color:#fff; }
.lp-form .ph { margin-top:14px; padding:14px 16px; border-radius:16px; border:1.5px dashed rgba(255,255,255,.4); color:rgba(255,255,255,.82); font-size:15px; }
.lp-form .ph code { background:rgba(197,224,79,.16); color:#DDF08A; padding:2px 8px; border-radius:8px; font-size:13px; }
.lp-foot { margin-top:34px; font-size:12.5px; color:rgba(255,255,255,.5); max-width:70ch; line-height:1.5; }

/* ---------- reveal on scroll (only where the browser supports it) ---------- */
@keyframes lp-rise { from { opacity:0; transform: translateY(34px); } to { opacity:1; transform:none; } }
@supports (animation-timeline: view()) {
  .lp-rise { animation: lp-rise linear both; animation-timeline: view(); animation-range: entry 4% entry 62%; }
  .lp-trio .lp-glass:nth-child(2), .lp-acts .lp-act:nth-child(2) { animation-range: entry 10% entry 68%; }
  .lp-trio .lp-glass:nth-child(3), .lp-acts .lp-act:nth-child(3) { animation-range: entry 16% entry 74%; }
  .lp-acts .lp-act:nth-child(4) { animation-range: entry 20% entry 78%; }
  .lp-acts .lp-act:nth-child(5) { animation-range: entry 24% entry 82%; }
}
@keyframes lp-drift { 0%, 100% { background-position: var(--lp-x) 49%; } 50% { background-position: var(--lp-x) 53%; } }

/* ---------- smaller screens ---------- */
@media (max-width: 1000px) {
  .lp-trio { grid-template-columns: 1fr; } .lp-acts { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 760px) {
  .lp-links { display:none; }
  [class*="st-key-lpsec_"] { padding: 104px 22px 64px 22px; min-height: 92vh; }
  .st-key-lpsec_hero, .st-key-lpsec_why, .st-key-lpsec_feedback, .st-key-lpsec_action { border-radius:30px; margin:8px; width: calc(100% - 16px); }
  .lp-acts { grid-template-columns: 1fr; } .lp-cue { display:none; }
  .st-key-lp_nav { padding:6px 8px 6px 14px; }
  .st-key-lp_nav [data-testid="stColumn"]:nth-child(2) { display:none; }
  .st-key-lp_nav [data-testid="stColumn"]:nth-child(1) { flex:1 1 auto !important; width:auto !important; }
  .st-key-lp_nav [data-testid="stColumn"]:nth-child(3) { flex:0 0 auto !important; width:auto !important; }
}
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}
</style>
"""


def _section_css():
    """Backgrounds are built here so that photos from IMAGES can replace the built-in art."""
    veil = "linear-gradient(90deg, rgba(8,11,9,.92) 0%, rgba(8,11,9,.62) 48%, rgba(8,11,9,.25) 100%)"
    css = []
    hero = _photo("hero")
    if hero:
        css.append(f".st-key-lpsec_hero {{ background: {veil}, url('{hero}') center / cover no-repeat; }}")
    else:
        css.append(".st-key-lpsec_hero { --lp-x: 99%; animation: lp-drift 14s ease-in-out infinite; background-color:#0B0F0C; "
                   "background-image: radial-gradient(760px 560px at 78% 48%, rgba(197,224,79,.13), rgba(197,224,79,0) 70%), "
                   f"url('{earth_art()}'); background-repeat:no-repeat; background-size: auto, min(50vw, 700px) auto; "
                   "background-position: 0 0, var(--lp-x) 49%; }")
    why = _photo("why")
    if why:
        css.append(f".st-key-lpsec_why {{ background: linear-gradient(180deg, rgba(8,11,9,.78), rgba(8,11,9,.55)), url('{why}') center / cover no-repeat; }}")
    else:
        css.append(f".st-key-lpsec_why {{ background-image: linear-gradient(180deg, rgba(11,15,12,.15) 0%, rgba(11,15,12,.0) 55%), url('{city_art()}'); "
                   "background-repeat:no-repeat; background-size: auto, cover; background-position: 0 0, center bottom; }")
    act = _photo("action")
    if act:
        css.append(f".st-key-lpsec_action {{ background: linear-gradient(160deg, rgba(238,246,201,.9), rgba(197,224,79,.82)), url('{act}') center / cover no-repeat; }}")
    fb = _photo("feedback")
    if fb:
        css.append(f".st-key-lpsec_feedback {{ background: linear-gradient(180deg, rgba(8,11,9,.82), rgba(8,11,9,.7)), url('{fb}') center / cover no-repeat; }}")
    else:
        css.append(".st-key-lpsec_feedback { background-image: radial-gradient(800px 520px at 12% 0%, rgba(197,224,79,.16), rgba(197,224,79,0) 65%), "
                   "radial-gradient(700px 520px at 100% 100%, rgba(255,125,166,.22), rgba(255,125,166,0) 65%); }")
    return "<style>" + "\n".join(css) + "</style>"


# ═════════════════════════════ NAVIGATION HELPERS ═════════════════════════════
def go_dashboard(page=None):
    """Open the dashboard, optionally on one of its four pages."""
    if page:
        st.session_state["_goto"] = page
    st.switch_page(DASHBOARD_PAGE)


# ═════════════════════════════ SCREENS ═════════════════════════════
def _nav():
    with st.container(key="lp_nav"):
        c1, c2, c3 = st.columns([1.2, 3.4, 1.2], vertical_alignment="center")
        with c1:
            st.markdown(ui.brand(), unsafe_allow_html=True)
        with c2:
            st.markdown(_h("""<div class='lp-links'>
                <a href='#lp-about'>The basics</a><a href='#lp-why'>Why it matters</a><a href='#lp-help'>How it works</a>
                <a href='#lp-action'>Findings</a><a href='#lp-feedback'>Feedback</a></div>"""), unsafe_allow_html=True)
        with c3:
            # SKIP INTRO: goes straight to the dashboard
            if st.button("Skip intro", key="lpb_skip"):
                go_dashboard()


def _hero():
    with st.container(key="lpsec_hero"):
        st.markdown(_h("""<span id='lp-top' class='lp-anchor'></span>
            <div class='lp-eyebrow on-dark'>Explainable machine learning for sustainability</div>
            <h1 class='lp-h1'>See what <b>drives</b><br>a carbon footprint,<br>not just the number.</h1>
            <p class='lp-lead on-dark'>CarbonXAI trains and compares three machine learning models on individual carbon footprint data,
            then uses SHAP to show which lifestyle factors drive each prediction. Built for students and sustainability researchers.</p>"""), unsafe_allow_html=True)
        b1, b2, _ = st.columns([1.15, 1.25, 4], gap="small", vertical_alignment="center")
        with b1:
            # START EXPLORING: plain anchor, scrolls to the next screen
            st.markdown("<a class='lp-pill lime' href='#lp-about'>Start exploring &darr;</a>", unsafe_allow_html=True)
        with b2:
            # GO TO DASHBOARD: skips the story
            if st.button("Go to dashboard", key="lpb_ghost_hero"):
                go_dashboard()
        st.markdown(_h("""<div class='lp-stats'><span class='lp-stat'>19 lifestyle inputs</span>
            <span class='lp-stat'>3 models compared</span><span class='lp-stat'>SHAP explanations</span></div>"""), unsafe_allow_html=True)


_CHEV_L = "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'><path d='M15 5l-7 7 7 7'/></svg>"
_CHEV_R = "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'><path d='M9 5l7 7-7 7'/></svg>"

# Makes the round arrow buttons scroll the card row by one card. Installed once per browser tab.
# Swiping, the scrollbar and the keyboard keep working without it.
_ARROW_JS = """<script>
(function () {
  if (window.__lpArrows) return; window.__lpArrows = true;
  function railOf(btn) { var sec = btn.closest('[class*="st-key-lpsec_"]'); return sec && sec.querySelector('.lp-rail'); }
  function sync() {
    document.querySelectorAll('.lp-arrows').forEach(function (box) {
      var sec = box.closest('[class*="st-key-lpsec_"]'), rail = sec && sec.querySelector('.lp-rail'); if (!rail) return;
      var max = rail.scrollWidth - rail.clientWidth - 2;
      box.querySelectorAll('.lp-arrow').forEach(function (b) {
        b.disabled = b.dataset.dir === '-1' ? rail.scrollLeft <= 2 : rail.scrollLeft >= max;
      });
    });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.lp-arrow'); if (!b) return;
    var rail = railOf(b); if (!rail) return;
    var card = rail.querySelector('.lp-card'), step = card ? card.getBoundingClientRect().width + 16 : 340;
    rail.scrollBy({ left: Number(b.dataset.dir) * step, behavior: 'smooth' });
  });
  document.addEventListener('scroll', sync, true);
  window.addEventListener('resize', sync);
  setInterval(sync, 500);
})();
</script>"""


def _card(kind, ic, title, text, tag="", photo=None):
    tag_html = f"<span class='tag'>{escape(tag)}</span>" if tag else ""
    if photo:
        img = _card_img(photo)
        if img:
            kind = (kind + " photo").strip()
            return (f"<article class='lp-card {kind}' style=\"background-image:url('{img}')\">"
                    f"<span class='ic'>{icon(ic)}</span><h3>{escape(title)}</h3>"
                    f"<p>{escape(text)}</p>{tag_html}</article>")
    return (f"<article class='lp-card {kind}'><span class='ic'>{icon(ic)}</span><h3>{escape(title)}</h3>"
            f"<p>{escape(text)}</p>{tag_html}</article>")


def _about():
    with st.container(key="lpsec_about"):
        cards = [
            _card("dark wide", "co2", "Carbon emissions",
                  "Carbon dioxide (CO₂) released into the air, mostly when we burn fuels such as petrol, diesel, coal and gas.", "The basics",
                  photo="lp_emission.jpg"),
            _card("lime wide", "heat", "Greenhouse gases",
                  "CO₂, methane and nitrous oxide trap heat in the atmosphere. The more of them, the warmer the planet.", "The basics",
                  photo="lp_greenhouse.jpg"),
            _card("pink wide", "foot", "Carbon footprint",
                  "All the greenhouse gases linked to what one person does, counted in kg of CO₂e. CO₂e puts every gas on the same scale.", "The basics",
                  photo="lp_footprint.jpg"),
            _card("green", "car", "Transport", "Petrol and diesel vehicles release CO₂ from the tailpipe. Public transport, walking and cycling usually release less.", "Everyday source",
                  photo="kyc_traffic_card.jpg"),
            _card("blue", "plane", "Air travel", "Flights burn large amounts of jet fuel, so even a few trips can add a lot to a footprint.", "Everyday source",
                  photo="kyc_airtravel_card.jpg"),
            _card("teal", "bolt", "Home energy", "Electricity and heating release CO₂ when they come from fossil fuels.", "Everyday source",
                  photo="kyc_pylons_card.jpg"),
            _card("violet", "food", "Food", "Growing, moving and cooking food all release greenhouse gases, and some diets release more than others.", "Everyday source",
                  photo="kyc_food_card.jpg"),
            _card("pink", "bag", "Shopping", "Making and shipping clothes and goods uses energy, so what and how often we buy matters.", "Everyday source",
                  photo="kyc_shopping_card.jpg"),
            _card("green", "bin", "Waste", "Landfills release methane, and recycling can cut the energy needed to make new materials.", "Everyday source",
                  photo="kyc_landfill_card.jpg"),
        ]
        st.markdown(_h(f"""<span id='lp-about' class='lp-anchor'></span>
            <div class='lp-rise'><div class='lp-eyebrow'>01 &middot; The basics</div>
            <h2 class='lp-h2'>What is carbon emission?</h2>
            <p class='lp-lead'>Everyday life releases greenhouse gases. Here is the short version.</p></div>
            <div class='lp-hint'>Swipe or scroll sideways &rarr;</div>
            <div class='lp-rail' id='lp-rail-basics'>{''.join(cards)}</div>
            <div class='lp-arrows'>
              <button type='button' class='lp-arrow' data-dir='-1' aria-label='Previous card'>{_CHEV_L}</button>
              <button type='button' class='lp-arrow' data-dir='1' aria-label='Next card'>{_CHEV_R}</button>
            </div>"""), unsafe_allow_html=True)
        st.html(_ARROW_JS, unsafe_allow_javascript=True)


def _why():
    with st.container(key="lpsec_why"):
        st.markdown(_h("""<span id='lp-why' class='lp-anchor'></span>
            <div class='lp-rise'><div class='lp-eyebrow on-dark'>02 &middot; Why it matters</div>
            <h2 class='lp-h2 on-dark wide'>Small habits.<br>A warming planet.</h2>
            <p class='lp-lead on-dark'>Greenhouse gases trap heat in the atmosphere. Burning fossil fuels for transport, power and industry
            is a major source.</p></div>
            <div class='lp-trio'>
              <div class='lp-glass lp-rise'><div class='num'>1.1&deg;C</div><h3>The planet is already warmer</h3>
                <p>Global surface temperature in 2011 to 2020 was about 1.1&deg;C above the 1850 to 1900 level.</p><span class='src'>Source: IPCC (2023)</span></div>
              <div class='lp-glass lp-rise'><div class='num'>5</div><h3>Five everyday areas add up</h3>
                <p>Transport, energy, food, shopping and waste all depend on daily habits, so two people can have very different footprints.</p></div>
              <div class='lp-glass lp-rise'><div class='num'>Why?</div><h3>A number alone is not enough</h3>
                <p>Knowing which habits drive an estimate is the first step to changing it. That is what explainable AI is for.</p></div>
            </div>
            <span class='lp-chip' style='margin-top:20px'>Supports UN Sustainable Development Goal 13: Climate Action</span>"""),
                    unsafe_allow_html=True)


def _module(kind, ic, num, title, text):
    return (f"<div class='lp-mod lp-rise {kind}'><span class='n'>{num}</span><span class='ic'>{icon(ic)}</span>"
            f"<h3>{escape(title)}</h3><p>{escape(text)}</p></div>")


def _help():
    with st.container(key="lpsec_help"):
        st.markdown(_h("""<span id='lp-help' class='lp-anchor'></span>
            <div class='lp-rise'><div class='lp-eyebrow'>03 &middot; How CarbonXAI helps</div>
            <h2 class='lp-h2 wide'>One dashboard. Four ways to understand your footprint.</h2>
            <p class='lp-lead'>Pick a module to open it, or start with Prediction.</p></div>"""), unsafe_allow_html=True)
        mods = [
            ("", "sliders", "01", "Prediction", "Enter your habits and get a monthly estimate in kg CO₂e, a level, and a comparison with the dataset.", "Prediction"),
            ("pink", "bars", "02", "Model comparison", "See how Random Forest, XGBoost and LightGBM score on unseen data, and which one the dashboard uses.", "Model comparison"),
            ("lime", "spark", "03", "SHAP explanations", "See which factors raise or lower the estimate, for your own result and across everyone.", "SHAP explanations"),
            ("", "leaf", "04", "Sustainability insights", "Find the lifestyle factors you can change and how strongly each one influences the estimate.", "Sustainability insights"),
        ]
        cols = st.columns(4, gap="medium")
        for col, (kind, ic, num, title, text, page) in zip(cols, mods):
            with col:
                st.markdown(_module(kind, ic, num, title, text), unsafe_allow_html=True)
                # OPEN MODULE: jumps to that page of the dashboard
                if st.button(f"Open {title}", key=f"lpb_line_{num}"):
                    go_dashboard(page)
        st.markdown(_h("""<div class='lp-flow lp-rise'>
            <span class='st'><b>1</b>You enter your habits</span><span class='ar'>&rarr;</span>
            <span class='st'><b>2</b>The model estimates your footprint</span><span class='ar'>&rarr;</span>
            <span class='st'><b>3</b>SHAP explains the reasons</span><span class='ar'>&rarr;</span>
            <span class='st'><b>4</b>You see what to change</span></div>"""), unsafe_allow_html=True)


def _act(ic, title, text):
    return f"<div class='lp-act lp-rise'><span class='ic'>{icon(ic, 24)}</span><h3>{escape(title)}</h3><p>{escape(text)}</p></div>"


def _action():
    with st.container(key="lpsec_action"):
        # Findings come from models/results.json and models/shap_sample.csv (mean absolute SHAP, 1,000 test records).
        acts = [
            _act("route", "Distance leads", "Monthly vehicle distance has the largest mean absolute SHAP value, about 461 kg CO₂e."),
            _act("plane", "Flying follows", "How often a person travels by air comes second, about 446 kg CO₂e."),
            _act("spark", "Demographic signals", "Body type and sex also rank high. This most likely reflects how the dataset was produced, not a real-world cause."),
            _act("bag", "Consumption adds up", "New clothes per month and waste bag count each add roughly 140 to 175 kg CO₂e."),
            _act("bars", "Model choice matters", "XGBoost reaches a test MAE of about 77 kg, against about 204 kg for Random Forest."),
        ]
        st.markdown(_h(f"""<span id='lp-action' class='lp-anchor'></span>
            <div class='lp-rise'><div class='lp-eyebrow'>04 &middot; From insight to interpretation</div>
            <h2 class='lp-h2 wide'>Read the drivers. Question the model.</h2>
            <p class='lp-lead' style='color:#3F4A22'>What the best model learned from this dataset, shown as mean absolute SHAP values across 1,000 test records.</p></div>
            <div class='lp-acts'>{''.join(acts)}</div>
            <div class='lp-fine' style='color:#4D5A2A'>SHAP describes what the model learned from the data, not cause and effect, and the dataset appears to be synthetic. Use the results to explore and learn, not as a certified carbon audit.</div>"""),
                    unsafe_allow_html=True)
        a1, a2, _ = st.columns([1.2, 1.5, 3.6], gap="small", vertical_alignment="center")
        with a1:
            # START PREDICTION: opens the Prediction page
            if st.button("Start prediction", key="lpb_dark_start"):
                go_dashboard("Prediction")
        with a2:
            if st.button("See what drives emissions", key="lpb_line_drivers"):
                go_dashboard("SHAP explanations")


def _feedback():
    with st.container(key="lpsec_feedback"):
        if FEEDBACK_URL:
            body = "<div class='ph'>Your feedback helps shape the final version of this project.</div>"
        else:
            body = "<div class='ph'>Insert your feedback form link here &middot; set <code>FEEDBACK_URL</code> in landing.py</div>"
        st.markdown(_h(f"""<span id='lp-feedback' class='lp-anchor'></span>
            <div class='lp-rise'><div class='lp-eyebrow on-dark'>05 &middot; Your turn</div>
            <h2 class='lp-h2 on-dark wide'>Help us improve CarbonXAI</h2>
            <p class='lp-lead on-dark'>Explore the dashboard, then tell us what worked and what did not. Your answers are part of the
            user acceptance test for this final year project.</p></div>
            <div class='lp-form lp-rise'><div class='lab'>User acceptance test</div><h3>User Acceptance Test Form</h3>{body}</div>"""),
                    unsafe_allow_html=True)
        f1, f2, _ = st.columns([1.35, 1.35, 3], gap="small", vertical_alignment="center")
        with f1:
            _feedback_button("lpb_lime_fb")
        with f2:
            if st.button("Proceed to dashboard", key="lpb_ghost_fb"):
                go_dashboard()
        st.markdown(f"<div class='lp-foot'>Final Year Project: {escape(PROJECT_TITLE)}.</div>", unsafe_allow_html=True)


def _feedback_button(key):
    """Real link when FEEDBACK_URL is set, otherwise a disabled placeholder."""
    if FEEDBACK_URL:
        st.link_button("Open Feedback Form", FEEDBACK_URL, key=key)
    else:
        st.button("Open Feedback Form", key=key, disabled=True)


# ═════════════════════════════ PUBLIC API ═════════════════════════════
def render():
    """Draw the whole landing page. Called from landing_page.py."""
    st.markdown(ui.CSS, unsafe_allow_html=True)       # same fonts, background and brand as the dashboard
    st.markdown(LANDING_CSS, unsafe_allow_html=True)
    st.markdown(_section_css(), unsafe_allow_html=True)
    st.markdown(ui.theme_toggle(), unsafe_allow_html=True)
    st.html(ui.THEME_TOGGLE_JS, unsafe_allow_javascript=True)
    _nav()
    _hero()
    _about()
    _why()
    _help()
    _action()
    _feedback()


def feedback_footer():
    """Slim feedback band for the bottom of the dashboard pages."""
    st.markdown("<style>.lp-dashfoot{margin-top:30px;padding:20px 26px;border-radius:28px;background:var(--cx-warn-bg);"
                "border:1px solid var(--cx-chip-border);backdrop-filter:blur(12px);display:flex;align-items:center;gap:14px;flex-wrap:wrap;color:var(--cx-ink)}"
                ".lp-dashfoot b{font-size:17px;font-weight:600}.lp-dashfoot span{color:var(--cx-muted);font-size:14px}"
                "[class*='st-key-lpb_dashfb'] button,[class*='st-key-lpb_dashfb'] a{border-radius:999px!important;padding:10px 22px!important;font-weight:700!important}"
                "[class*='st-key-lpb_dashfb'] button:disabled{opacity:.6}[class*='st-key-lpb_dashfb_lime'] button,[class*='st-key-lpb_dashfb_lime'] a{background:#C5E04F!important;color:#0F1110!important;border:1px solid #C5E04F!important}"
                "[class*='st-key-lpb_dashfb_line'] a{background:var(--cx-chip-bg)!important;color:var(--cx-ink)!important;border:1px solid var(--cx-chip-border)!important}"
                "[class*='st-key-dashback_wrap'] a{justify-content:flex-end!important;display:flex!important}"
                "</style>"
                "<div class='lp-dashfoot'><b>Tried CarbonXAI?</b><span>Tell us what worked and what did not. It is part of the user acceptance test.</span></div>",
                unsafe_allow_html=True)
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    c1, _, c2 = st.columns([1.5, 4.5, 1.5], vertical_alignment="center")
    with c1:
        if FEEDBACK_URL:
            st.link_button("Open Feedback Form", FEEDBACK_URL, key="lpb_dashfb_lime")
        else:
            st.button("Feedback form (coming soon)", key="lpb_dashfb_lime", disabled=True)
    with c2:
        with st.container(key="dashback_wrap"):
            st.page_link(INTRO_PAGE, label="Back to intro", icon=":material/arrow_back:")
