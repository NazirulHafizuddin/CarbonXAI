"""
ui.py
Styling and HTML building blocks for the CarbonXAI dashboard (glass and soft-card look).
Only presentation lives here. Prediction, SHAP and model logic stay in app.py.

Notes for maintainers
- Cards are plain HTML rendered with st.markdown(unsafe_allow_html=True). st.html strips inline SVG.
- Markdown ends an HTML block at a blank line, so builders return strings with no blank lines.
- Avoid the dollar sign in text: Streamlit would try to render it as LaTeX.
"""

from html import escape
import math

INK = "#0F1110"
MUTED = "#6B6F73"
PINK = "#E2487A"      # raises emission
OLIVE = "#5E8C14"     # lowers emission (on light cards)
LIME = "#C5E04F"      # lowers emission (on dark panels)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ---------- page shell ---------- */
.stApp, .stApp :is(h1,h2,h3,h4,h5,h6,p,div,a,li,td,th,small,label,button,input,textarea,select,article,code),
.stApp span:not([data-testid="stIconMaterial"]) {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, 'Segoe UI', sans-serif;
  font-feature-settings: 'cv11', 'ss03'; -webkit-font-smoothing: antialiased;
}
.stApp { font-weight: 400; }
.stApp {
  background:
    radial-gradient(900px 520px at 88% -8%, #ffffff 0%, rgba(255,255,255,0) 60%),
    radial-gradient(700px 480px at -5% 40%, #F7F2F5 0%, rgba(247,242,245,0) 60%),
    linear-gradient(180deg, #EFEFF2 0%, #E3E4E8 100%);
  color: #0F1110;
}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"], footer { display: none !important; }
.block-container { max-width: 1480px; padding: 1.4rem 2.2rem 3rem 2.2rem; }
h1, h2, h3, h4 { color: #0F1110; letter-spacing: -0.02em; font-weight: 600; }

/* ---------- top bar and pill navigation ---------- */
.cx-brand { display:flex; align-items:center; gap:12px; font-weight:600; font-size:20px; letter-spacing:-.01em; height:44px; }
.cx-brand .mark { width:38px; height:38px; border-radius:12px; background:#0F1110; display:grid; place-items:center; }
.cx-chip { display:inline-flex; align-items:center; gap:8px; padding:9px 16px; border-radius:999px; background:rgba(255,255,255,.7);
  border:1px solid rgba(15,17,16,.08); font-size:14px; font-weight:600; backdrop-filter: blur(10px); }
.cx-chip i { width:8px; height:8px; border-radius:50%; background:#8DB600; display:inline-block; }
.cx-right { display:flex; justify-content:flex-end; }
.st-key-nav, .st-key-shapview { display:flex; justify-content:center; }
.st-key-nav [data-testid="stButtonGroup"] > div, .st-key-shapview [data-testid="stButtonGroup"] > div { gap: 8px; }
.st-key-nav button[role="radio"], .st-key-shapview button[role="radio"] {
  border-radius: 999px !important; padding: 8px 22px !important; border: 1px solid rgba(15,17,16,.12) !important;
  background: rgba(255,255,255,.65) !important; color: #0F1110 !important; font-weight: 600 !important;
  box-shadow: none !important; backdrop-filter: blur(10px);
}
.st-key-nav button[role="radio"] *, .st-key-shapview button[role="radio"] * { color: inherit !important; }
.st-key-shapview { justify-content:flex-start; margin-bottom:6px; }
.st-key-nav button[role="radio"][aria-checked="true"], .st-key-shapview button[role="radio"][aria-checked="true"] { background:#0F1110 !important; color:#fff !important; border-color:#0F1110 !important; }

/* ---------- hero text ---------- */
.cx-hero h1 { font-size: 50px; font-weight: 700; line-height: 1.04; margin: 18px 0 6px 0; letter-spacing: -.04em; }
.cx-hero p { color:#6B6F73; font-size:15px; margin:0 0 18px 0; max-width: 46ch; line-height:1.5; }

/* ---------- white cards ---------- */
.cx-grid { display:grid; grid-template-columns: 1.2fr 1fr 0.85fr; gap:16px; margin-top: 18px; }
.cx-card { background:#fff; border-radius:28px; padding:22px 26px; position:relative; overflow:hidden;
  box-shadow: 0 1px 0 rgba(255,255,255,.9) inset, 0 22px 44px -26px rgba(20,22,20,.30); }
.cx-label { font-size:14px; color:#6B6F73; font-weight:500; }
.cx-big { font-size:56px; font-weight:600; letter-spacing:-.035em; line-height:1.02; margin-top:6px; color:#0F1110; }
.cx-big small { font-size:20px; color:#6B6F73; font-weight:400; letter-spacing:0; margin-left:8px; }
.cx-note { font-size:13px; color:#6B6F73; line-height:1.5; margin-top:10px; }
.cx-main { grid-column: 1 / span 2; }
.cx-pinkwrap { grid-column: 3; grid-row: 1 / span 2; }
.cx-shapcard { grid-column: 1 / span 3; }
.cx-delta { display:inline-block; padding:5px 12px; border-radius:999px; font-size:13px; font-weight:600; margin-top:12px; }
.cx-delta.up { background:#FDE6EE; color:#B32A58; }
.cx-delta.down { background:#E8F1D3; color:#456B0D; }

/* dotted scale strip */
.cx-strip { display:flex; gap:5px; align-items:center; margin-top:20px; }
.cx-strip i { width:7px; height:7px; border-radius:50%; background:#D6D8DB; flex:none; }
.cx-strip i.on { background:#0F1110; }
.cx-strip i.mk { width:18px; height:18px; background:#fff; border:2px solid #0F1110; box-shadow:0 6px 14px -4px rgba(0,0,0,.4); }
.cx-strip-cap { display:flex; justify-content:space-between; font-size:12px; color:#8A8D91; margin-top:8px; }

/* SHAP rows */
.cx-shaprow { display:grid; grid-template-columns: 230px 1fr 74px; align-items:center; gap:12px; padding:7px 0; }
.cx-shaprow .nm { font-size:14px; letter-spacing:-.01em; font-weight:500; color:#0F1110; text-align:right; }
.cx-shaprow .tr { position:relative; height:14px; background: linear-gradient(90deg, transparent 49.8%, #E3E4E8 49.8%, #E3E4E8 50.2%, transparent 50.2%); }
.cx-shaprow .bar { position:absolute; top:1px; height:12px; border-radius:7px; }
.cx-shaprow .val { font-size:13.5px; font-weight:600; font-variant-numeric: tabular-nums; }
.cx-legend { display:flex; gap:18px; font-size:12.5px; color:#6B6F73; margin-top:8px; }
.cx-legend b { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; vertical-align:-1px; }

/* ---------- pink glass card ---------- */
.cx-pink { height:100%; min-height:300px; border-radius:30px; padding:22px 24px; position:relative; overflow:hidden; color:#fff;
  background: linear-gradient(165deg, #FFB6CD 0%, #FF7DA6 48%, #FF5088 100%);
  box-shadow: 0 30px 50px -28px rgba(255,80,136,.75), inset 0 1px 0 rgba(255,255,255,.7); }
.cx-pink .art { position:absolute; inset:0; opacity:.95; }
.cx-pink .lab { position:relative; font-size:14px; font-weight:600; opacity:.95; }
.cx-pink .glass { position:absolute; left:14px; right:14px; bottom:14px; padding:16px 18px; border-radius:22px;
  background: rgba(255,255,255,.26); border:1px solid rgba(255,255,255,.55); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); }
.cx-pink .pct { font-size:52px; font-weight:600; letter-spacing:-.035em; line-height:1; }
.cx-pink .cap { font-size:13px; margin-top:6px; opacity:.95; line-height:1.4; }
.cx-pink .lvl { position:relative; display:inline-block; margin-top:10px; padding:5px 14px; border-radius:999px; font-size:12.5px; font-weight:700;
  background: rgba(255,255,255,.3); border:1px solid rgba(255,255,255,.6); letter-spacing:.04em; }

/* ---------- dark panels ---------- */
.st-key-controls { background: linear-gradient(180deg,#171A17 0%,#0C0E0C 100%); border-radius: 32px; padding: 20px 22px 12px 22px;
  box-shadow: 0 30px 50px -30px rgba(0,0,0,.65), inset 0 1px 0 rgba(255,255,255,.08); }
.st-key-controls [data-testid="stWidgetLabel"] p, .st-key-controls label p { color:#C9CEC9 !important; font-size:13.5px !important; font-weight:500; }
.st-key-controls [data-testid="stCaptionContainer"], .st-key-controls [data-testid="stCaptionContainer"] p { color:#8E948E !important; }
.st-key-controls [role="tablist"] { gap:6px; border-bottom:none !important; background: rgba(255,255,255,.06); padding:5px; border-radius:999px; }
.st-key-controls [data-testid="stTab"] { padding:7px 16px; border-radius:999px; color:#9AA09A !important; font-weight:600; height:auto; }
.st-key-controls [data-testid="stTab"] p { color:inherit !important; font-size:14px; }
.st-key-controls [data-testid="stTab"][data-selected="true"] { background: rgba(255,255,255,.14); color:#fff !important; }
.st-key-controls .react-aria-SelectionIndicator { display:none; }
.st-key-controls [data-baseweb="select"] > div, .st-key-controls [data-baseweb="input"], .st-key-controls [data-baseweb="base-input"],
.st-key-controls [data-testid="stNumberInput"] [data-baseweb="input"] { background: rgba(255,255,255,.08) !important; border-color: rgba(255,255,255,.14) !important; border-radius:14px !important; }
.st-key-controls input, .st-key-controls [data-baseweb="select"] * { color:#fff !important; -webkit-text-fill-color:#fff; }
.st-key-controls [data-baseweb="select"] svg, .st-key-controls button svg { fill:#C9CEC9 !important; color:#C9CEC9 !important; }
.st-key-controls [data-baseweb="tag"] { background: rgba(197,224,79,.2) !important; border-radius:999px !important; }
.st-key-controls [data-testid="stSlider"] * { color:#E6EAE6; }
.st-key-controls [data-testid="stNumberInput"] button { background: rgba(255,255,255,.06) !important; }
/* react-aria widgets (Streamlit 1.65) */
.st-key-controls [data-testid="stSelectbox"] [role="group"],
.st-key-controls [data-testid="stMultiSelect"] [role="group"],
.st-key-controls [data-testid="stNumberInputContainer"] {
  background: rgba(255,255,255,.08) !important; border: 1px solid rgba(255,255,255,.14) !important; border-radius: 14px !important; overflow: hidden; }
.st-key-controls [data-testid="stSelectbox"] input, .st-key-controls [data-testid="stMultiSelect"] input,
.st-key-controls [data-testid="stNumberInputField"] { color:#fff !important; -webkit-text-fill-color:#fff !important; background:transparent !important; }
.st-key-controls [data-testid="stSelectbox"] input:disabled { -webkit-text-fill-color:#8E948E !important; color:#8E948E !important; }
.st-key-controls [data-testid="stSelectbox"] button, .st-key-controls [data-testid="stMultiSelect"] button,
.st-key-controls [data-testid="stNumberInputContainer"] button { background:transparent !important; color:#C9CEC9 !important; }
.st-key-controls [data-testid="stSelectbox"] svg, .st-key-controls [data-testid="stMultiSelect"] svg,
.st-key-controls [data-testid="stNumberInputContainer"] svg { fill:#C9CEC9 !important; }
.st-key-controls [data-testid="stMultiSelectTagsContainer"] span { color:#fff; }
[data-testid*="VirtualDropdown"], [data-testid*="VirtualDropdown"] [role="listbox"], [role="listbox"] { background:#161916 !important; border-radius:14px; }
[data-testid*="VirtualDropdown"] [role="option"], [role="listbox"] [role="option"] { color:#E9ECE9 !important; background:transparent !important; }
[role="listbox"] [role="option"]:hover, [role="listbox"] [role="option"][aria-selected="true"], [role="listbox"] [role="option"][data-focused="true"] { background: rgba(197,224,79,.16) !important; }
[data-baseweb="popover"] ul, [data-baseweb="popover"] [role="listbox"] { background:#161916 !important; }
[data-baseweb="popover"] li { color:#E9ECE9 !important; background:transparent !important; }
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] { background: rgba(197,224,79,.16) !important; }

/* ---------- bottom dark band ---------- */
.cx-band { margin-top: 22px; background: linear-gradient(180deg,#141714 0%,#090A09 100%); border-radius: 38px; padding: 30px 32px 34px 32px; color:#fff;
  box-shadow: 0 40px 70px -40px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.07);
  display:grid; grid-template-columns: 230px 1fr 250px; gap: 26px; align-items:center; }
.cx-band h3 { color:#fff; font-size:28px; font-weight:600; margin:0 0 8px 0; letter-spacing:-.025em; }
.cx-band p { color:#9AA09A; font-size:14px; line-height:1.5; margin:0; }
.cx-tiles { display:grid; grid-template-columns: repeat(3, 1fr); gap:18px; }
.cx-tile { color:#fff; position:relative; height:232px; border-radius:30px; overflow:hidden; padding:20px 20px;
  background: linear-gradient(168deg, #7C9A18 0%, #46570C 52%, #202807 100%);
  border:1px solid rgba(197,224,79,.38);
  box-shadow: 0 26px 40px -24px rgba(124,154,24,.55), inset 0 1px 0 rgba(255,255,255,.28); }
.cx-tile .art { position:absolute; left:-10%; right:-10%; bottom:-6%; height:62%; filter: blur(9px); opacity:.95; }
.cx-tile .t { position:relative; font-size:18px; font-weight:600; line-height:1.2; color:#fff; max-width: 16ch; }
.cx-tile .s { position:relative; font-size:13px; color:#D5E58F; margin-top:6px; }
.cx-tile .glass { position:absolute; left:12px; right:12px; bottom:12px; padding:11px 16px; border-radius:20px; display:flex; align-items:baseline; justify-content:space-between;
  background: rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.3); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); }
.cx-tile .sv { font-size:28px; font-weight:600; letter-spacing:-.025em; }
.cx-tile .un { font-size:12px; color:#E3EFB0; }
.cx-tile.empty { background: linear-gradient(168deg,#262A26,#121412); border-color: rgba(255,255,255,.1); box-shadow:none; }
.cx-tile.empty .t { color:#C9CEC9; } .cx-tile.empty .s { color:#7C827C; }
.cx-gauge { text-align:center; }
.cx-gauge .gl { font-size:13px; color:#9AA09A; margin-top:-6px; }
.cx-gauge .gv { font-size:34px; font-weight:600; letter-spacing:-.02em; }
.cx-gauge .gv small { font-size:16px; color:#9AA09A; margin-left:4px; }
.cx-foot { font-size:12.5px; color:#7C827C; margin-top: 14px; line-height:1.5; }

/* ---------- other pages ---------- */
.cx-models { display:grid; grid-template-columns: repeat(3, 1fr); gap:16px; margin-top:18px; }
.cx-model { background:#fff; border-radius:28px; padding:22px 26px; box-shadow: 0 22px 44px -26px rgba(20,22,20,.30); position:relative; overflow:hidden; }
.cx-model.best { color:#fff; background: linear-gradient(165deg, #FFB6CD 0%, #FF7DA6 48%, #FF5088 100%); box-shadow: 0 30px 50px -28px rgba(255,80,136,.7), inset 0 1px 0 rgba(255,255,255,.7); }
.cx-model.best .cx-big { color:#fff; }
.cx-model.best .cx-label, .cx-model.best .cx-big small, .cx-model.best .cx-note { color: rgba(255,255,255,.92); }
.cx-model .cx-big { font-size:50px; }
.cx-model .row { display:flex; justify-content:space-between; font-size:14px; padding:6px 0; border-top:1px solid rgba(120,120,120,.18); margin-top:6px; }
.cx-model.best .row { border-color: rgba(255,255,255,.4); }
.cx-badge { display:inline-block; padding:4px 12px; border-radius:999px; font-size:12px; font-weight:700; background:rgba(255,255,255,.3); border:1px solid rgba(255,255,255,.6); margin-bottom:6px; }
.cx-hbar { display:grid; grid-template-columns: 170px 1fr 70px; align-items:center; gap:12px; padding:6px 0; font-size:14px; }
.cx-hbar .tr { height:12px; background:#ECEDEF; border-radius:7px; position:relative; }
.cx-hbar .f { position:absolute; left:0; top:0; bottom:0; border-radius:7px; background:#0F1110; }
.cx-hbar .f.b { background: linear-gradient(90deg,#FF7DA6,#FF5088); }
.cx-dark { background: linear-gradient(180deg,#141714 0%,#090A09 100%); color:#fff; border-radius:34px; padding:28px 32px; margin-top:18px;
  box-shadow: 0 40px 70px -40px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.07); }
.cx-dark .cx-label { color:#9AA09A; }
.cx-dbar { display:grid; grid-template-columns: 230px 1fr 80px; align-items:center; gap:14px; padding:7px 0; }
.cx-dbar .nm { font-size:15px; text-align:right; color:#E6EAE6; }
.cx-dbar .tr { height:14px; background:rgba(255,255,255,.08); border-radius:8px; position:relative; overflow:hidden; }
.cx-dbar .f { position:absolute; left:0; top:0; bottom:0; border-radius:8px; background: linear-gradient(90deg,#7C9A18,#C5E04F); }
.cx-dbar .v { font-size:13.5px; color:#C9CEC9; font-variant-numeric: tabular-nums; }
.cx-warn { background: rgba(255,255,255,.7); border:1px solid rgba(15,17,16,.08); border-radius:22px; padding:16px 20px; font-size:14px; color:#3A3F3B; line-height:1.55; margin-top:16px; backdrop-filter: blur(12px); }
.cx-rank { display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:16px; margin-top:18px; }

@media (max-width: 1100px) {
  .cx-grid { grid-template-columns: 1fr; } .cx-main, .cx-pinkwrap, .cx-shapcard { grid-column: auto; grid-row: auto; }
  .cx-band { grid-template-columns: 1fr; } .cx-tiles, .cx-models { grid-template-columns: 1fr; }
  .cx-shaprow { grid-template-columns: 120px 1fr 64px; }
}
@media (prefers-reduced-motion: no-preference) { .cx-strip i.mk { transition: all .3s ease; } }
</style>
"""


def fmt(v, signed=False):
    return f"{v:+,.0f}" if signed else f"{v:,.0f}"


def brand():
    mark = ("<svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#C5E04F' stroke-width='2' "
            "stroke-linecap='round' stroke-linejoin='round'><path d='M5 19c0-8 5-13 14-14 0 9-5 14-14 14z'/>"
            "<path d='M5 19c3-4 6-7 10-9'/></svg>")
    return f"<div class='cx-brand'><span class='mark'>{mark}</span>CarbonXAI</div>"


def model_chip(name):
    return f"<div class='cx-right'><span class='cx-chip'><i></i>Active model: {escape(name)}</span></div>"


def hero(title, text):
    return f"<div class='cx-hero'><h1>{title}</h1><p>{text}</p></div>"


def dot_strip(pct, n=34):
    k = max(0, min(n - 1, int(round(pct / 100 * (n - 1)))))
    cells = []
    for i in range(n):
        cells.append("<i class='mk'></i>" if i == k else ("<i class='on'></i>" if i < k else "<i></i>"))
    return "<div class='cx-strip'>" + "".join(cells) + "</div>"


def shap_rows(series, top_n=8):
    s = series.reindex(series.abs().sort_values(ascending=False).index).head(top_n)
    m = float(s.abs().max()) or 1.0
    rows = []
    for name, v in s.items():
        w = abs(v) / m * 49.0
        if v >= 0:
            style = f"left:50%;width:{w:.1f}%;background:linear-gradient(90deg,#FF9DBB,{PINK});"
        else:
            style = f"left:{50 - w:.1f}%;width:{w:.1f}%;background:linear-gradient(90deg,#9CC63A,{OLIVE});"
        col = PINK if v >= 0 else OLIVE
        rows.append(f"<div class='cx-shaprow'><div class='nm'>{escape(name)}</div>"
                    f"<div class='tr'><div class='bar' style='{style}'></div></div>"
                    f"<div class='val' style='color:{col}'>{fmt(v, True)}</div></div>")
    return "".join(rows)


def pink_art():
    return ("<svg class='art' viewBox='0 0 260 340' preserveAspectRatio='xMidYMid slice' xmlns='http://www.w3.org/2000/svg'>"
            "<defs><radialGradient id='pg1' cx='50%' cy='40%' r='55%'><stop offset='0' stop-color='#fff' stop-opacity='.95'/>"
            "<stop offset='.55' stop-color='#fff' stop-opacity='.25'/><stop offset='1' stop-color='#fff' stop-opacity='0'/></radialGradient>"
            "<filter id='pb'><feGaussianBlur stdDeviation='9'/></filter></defs>"
            "<ellipse cx='130' cy='120' rx='86' ry='96' fill='url(#pg1)' filter='url(#pb)'/>"
            "<circle cx='130' cy='140' r='46' fill='none' stroke='#fff' stroke-opacity='.75' stroke-width='1.4' stroke-dasharray='2 5'/>"
            "<circle cx='130' cy='140' r='72' fill='none' stroke='#fff' stroke-opacity='.4' stroke-width='1'/>"
            "<circle cx='130' cy='140' r='8' fill='#fff'/></svg>")


def tile_art(i):
    shapes = [
        "M0,100 L0,60 C40,40 70,20 110,38 C150,56 170,10 220,34 L260,70 L260,100 Z",
        "M0,100 L0,70 L60,50 L100,22 L140,56 L190,30 L260,66 L260,100 Z",
        "M0,100 L0,52 C30,64 60,68 90,46 C120,22 150,30 176,52 C206,76 232,60 260,40 L260,100 Z",
    ]
    return ("<svg class='art' viewBox='0 0 260 100' preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg'>"
            f"<defs><linearGradient id='tg{i}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#E4F58A'/>"
            f"<stop offset='1' stop-color='#6F8C14'/></linearGradient></defs>"
            f"<path d='{shapes[i % 3]}' fill='url(#tg{i})'/></svg>")


def gauge(frac, value_text, unit_text, label_text):
    frac = max(0.0, min(1.0, frac))
    L = math.pi * 80
    x = 100 - 80 * math.cos(math.pi * frac)
    y = 100 - 80 * math.sin(math.pi * frac)
    return ("<div class='cx-gauge'><svg viewBox='0 0 200 120' width='100%' xmlns='http://www.w3.org/2000/svg'>"
            "<path d='M20 100 A80 80 0 0 1 180 100' fill='none' stroke='rgba(255,255,255,.16)' stroke-width='3' stroke-linecap='round'/>"
            f"<path d='M20 100 A80 80 0 0 1 180 100' fill='none' stroke='#fff' stroke-width='3' stroke-linecap='round' "
            f"stroke-dasharray='{L:.1f}' stroke-dashoffset='{L * (1 - frac):.1f}'/>"
            "<line x1='100' y1='14' x2='100' y2='24' stroke='rgba(255,255,255,.5)' stroke-width='2'/>"
            f"<circle cx='{x:.1f}' cy='{y:.1f}' r='6' fill='#fff'/></svg>"
            f"<div class='gv'>{value_text}<small>{unit_text}</small></div><div class='gl'>{label_text}</div></div>")
