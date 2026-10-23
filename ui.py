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

/* ---------- theme tokens (light default, dark override) ----------
   Only the neutral "shell" surfaces (page background, body text, plain
   cards, nav pills, tracks, glass panels) are tokenised. The deliberately
   colourful / always-dark elements (brand gradient tiles, the dark
   .st-key-controls panel, .cx-band, .cx-pink, the lp-card/kyc-card colour
   variants, hero banners) keep their fixed colours in both themes -- they
   already read as an accent, not as "light mode". */
:root {
  --cx-page-bg: radial-gradient(900px 520px at 88% -8%, #ffffff 0%, rgba(255,255,255,0) 60%),
                radial-gradient(700px 480px at -5% 40%, #F7F2F5 0%, rgba(247,242,245,0) 60%),
                linear-gradient(180deg, #EFEFF2 0%, #E3E4E8 100%);
  --cx-ink: #0F1110; --cx-muted: #6B6F73; --cx-muted-2: #8A8D91;
  --cx-card-bg: #ffffff; --cx-card-shadow-inset: rgba(255,255,255,.9);
  --cx-chip-bg: rgba(255,255,255,.7); --cx-chip-border: rgba(15,17,16,.08);
  --cx-pill-bg: rgba(255,255,255,.65); --cx-pill-border: rgba(15,17,16,.12); --cx-pill-text: #0F1110;
  --cx-track-bg: #E3E4E8; --cx-hbar-track: #ECEDEF; --cx-row-border: rgba(120,120,120,.18);
  --cx-warn-bg: rgba(255,255,255,.7); --cx-warn-text: #3A3F3B;
  --cx-nav-bg: rgba(255,255,255,.92); --cx-nav-border: rgba(15,17,16,.08);
  --cx-icon-bg: rgba(15,17,16,.06);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --cx-page-bg: radial-gradient(900px 520px at 88% -8%, rgba(197,224,79,.06) 0%, rgba(197,224,79,0) 60%),
                  radial-gradient(700px 480px at -5% 40%, rgba(255,255,255,.03) 0%, rgba(255,255,255,0) 60%),
                  linear-gradient(180deg, #0D0F0D 0%, #07080A 100%);
    --cx-ink: #F1F3EF; --cx-muted: #9AA09A; --cx-muted-2: #7C827C;
    --cx-card-bg: #171A17; --cx-card-shadow-inset: rgba(255,255,255,.05);
    --cx-chip-bg: rgba(255,255,255,.08); --cx-chip-border: rgba(255,255,255,.14);
    --cx-pill-bg: rgba(255,255,255,.08); --cx-pill-border: rgba(255,255,255,.16); --cx-pill-text: #F1F3EF;
    --cx-track-bg: rgba(255,255,255,.1); --cx-hbar-track: rgba(255,255,255,.08); --cx-row-border: rgba(255,255,255,.14);
    --cx-warn-bg: rgba(255,255,255,.06); --cx-warn-text: #D7DBD6;
    --cx-nav-bg: rgba(14,16,14,.82); --cx-nav-border: rgba(255,255,255,.12);
    --cx-icon-bg: rgba(255,255,255,.12);
  }
}
:root[data-theme="dark"] {
  --cx-page-bg: radial-gradient(900px 520px at 88% -8%, rgba(197,224,79,.06) 0%, rgba(197,224,79,0) 60%),
                radial-gradient(700px 480px at -5% 40%, rgba(255,255,255,.03) 0%, rgba(255,255,255,0) 60%),
                linear-gradient(180deg, #0D0F0D 0%, #07080A 100%);
  --cx-ink: #F1F3EF; --cx-muted: #9AA09A; --cx-muted-2: #7C827C;
  --cx-card-bg: #171A17; --cx-card-shadow-inset: rgba(255,255,255,.05);
  --cx-chip-bg: rgba(255,255,255,.08); --cx-chip-border: rgba(255,255,255,.14);
  --cx-pill-bg: rgba(255,255,255,.08); --cx-pill-border: rgba(255,255,255,.16); --cx-pill-text: #F1F3EF;
  --cx-track-bg: rgba(255,255,255,.1); --cx-hbar-track: rgba(255,255,255,.08); --cx-row-border: rgba(255,255,255,.14);
  --cx-warn-bg: rgba(255,255,255,.06); --cx-warn-text: #D7DBD6;
  --cx-nav-bg: rgba(14,16,14,.82); --cx-nav-border: rgba(255,255,255,.12);
  --cx-icon-bg: rgba(255,255,255,.12);
}

/* ---------- theme toggle button (fixed, top-left) ---------- */
.cx-theme-toggle { position:fixed; top:14px; left:14px; z-index:1001; width:42px; height:42px; border-radius:50%; border:1px solid var(--cx-chip-border);
  display:grid; place-items:center; cursor:pointer; padding:0; background:var(--cx-chip-bg); color:var(--cx-ink);
  backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); box-shadow:0 14px 28px -16px rgba(0,0,0,.4);
  transition: background .2s, transform .2s; }
.cx-theme-toggle:hover { transform:scale(1.07); }
.cx-theme-toggle:focus-visible { outline:2px solid #6F9A12; outline-offset:2px; }
.cx-theme-toggle .sun, .cx-theme-toggle .moon { display:none; }
.cx-theme-toggle .sun { display:block; }
:root[data-theme="dark"] .cx-theme-toggle .sun { display:none; }
:root[data-theme="dark"] .cx-theme-toggle .moon { display:block; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) .cx-theme-toggle .sun { display:none; }
  :root:not([data-theme="light"]) .cx-theme-toggle .moon { display:block; }
}

/* ---------- page shell ---------- */
.stApp, .stApp :is(h1,h2,h3,h4,h5,h6,p,div,a,li,td,th,small,label,button,input,textarea,select,article,code),
.stApp span:not([data-testid="stIconMaterial"]) {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, 'Segoe UI', sans-serif;
  font-feature-settings: 'cv11', 'ss03'; -webkit-font-smoothing: antialiased;
}
.stApp { font-weight: 400; }
/* Streamlit silently attaches a "link to this heading" icon + anchor to every
   markdown heading (h1-h6) on every page. It is normally invisible, but certain
   layouts (a heading turned into a flex container, a heading that wraps to two
   lines) can make that hidden sibling participate in layout and become visible.
   Hiding it app-wide, once, here, keeps every page's headings in plain text flow. */
[data-testid="stHeaderActionElements"] { display:none !important; }
.stApp {
  background: var(--cx-page-bg);
  color: var(--cx-ink);
}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"], footer { display: none !important; }
.block-container { max-width: 1480px; padding: 1.4rem 2.2rem 3rem 2.2rem; }
h1, h2, h3, h4 { color: var(--cx-ink); letter-spacing: -0.02em; font-weight: 600; }

/* ---------- top bar and pill navigation ---------- */
.cx-brand { display:flex; align-items:center; gap:12px; font-weight:600; font-size:20px; letter-spacing:-.01em; height:44px; }
.cx-brand .mark { width:38px; height:38px; border-radius:12px; background:#0F1110; display:grid; place-items:center; }
.cx-chip { display:inline-flex; align-items:center; gap:8px; padding:9px 16px; border-radius:999px; background:var(--cx-chip-bg);
  border:1px solid var(--cx-chip-border); font-size:14px; font-weight:600; backdrop-filter: blur(10px); }
.cx-chip i { width:8px; height:8px; border-radius:50%; background:#8DB600; display:inline-block; }
.cx-right { display:flex; justify-content:flex-end; }
.st-key-nav, .st-key-shapview { display:flex; justify-content:center; }
.st-key-nav [data-testid="stButtonGroup"] > div, .st-key-shapview [data-testid="stButtonGroup"] > div { gap: 6px; flex-wrap: wrap; row-gap:8px; }
.st-key-nav button[role="radio"], .st-key-shapview button[role="radio"] {
  border-radius: 999px !important; padding: 7px 13px !important; border: 1px solid var(--cx-pill-border) !important;
  background: var(--cx-pill-bg) !important; color: var(--cx-pill-text) !important; font-weight: 600 !important;
  font-size: 13px !important; white-space: nowrap; box-shadow: none !important; backdrop-filter: blur(10px);
}
.st-key-nav button[role="radio"] *, .st-key-shapview button[role="radio"] * { color: inherit !important; }
.st-key-shapview { justify-content:flex-start; margin-bottom:6px; }
.st-key-nav button[role="radio"][aria-checked="true"], .st-key-shapview button[role="radio"][aria-checked="true"] { background:#0F1110 !important; color:#fff !important; border-color:#0F1110 !important; }
:root[data-theme="dark"] .st-key-nav button[role="radio"][aria-checked="true"],
:root[data-theme="dark"] .st-key-shapview button[role="radio"][aria-checked="true"] { background:#C5E04F !important; color:#0F1110 !important; border-color:#C5E04F !important; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) .st-key-nav button[role="radio"][aria-checked="true"],
  :root:not([data-theme="light"]) .st-key-shapview button[role="radio"][aria-checked="true"] { background:#C5E04F !important; color:#0F1110 !important; border-color:#C5E04F !important; }
}

/* ---------- hero text ---------- */
.cx-hero h1 { font-size: 50px; font-weight: 700; line-height: 1.04; margin: 18px 0 6px 0; letter-spacing: -.04em; }
.cx-hero p { color:var(--cx-muted); font-size:15px; margin:0 0 18px 0; max-width: 46ch; line-height:1.5; }

/* ---------- white cards ---------- */
.cx-grid { display:grid; grid-template-columns: 1.2fr 1fr 0.85fr; gap:16px; margin-top: 18px; }
.cx-card { background:var(--cx-card-bg); border-radius:28px; padding:22px 26px; position:relative; overflow:hidden;
  box-shadow: 0 1px 0 var(--cx-card-shadow-inset) inset, 0 22px 44px -26px rgba(20,22,20,.30); }
.cx-label { font-size:14px; color:var(--cx-muted); font-weight:500; }
.cx-big { font-size:56px; font-weight:600; letter-spacing:-.035em; line-height:1.02; margin-top:6px; color:var(--cx-ink); }
.cx-big small { font-size:20px; color:var(--cx-muted); font-weight:400; letter-spacing:0; margin-left:8px; }
.cx-note { font-size:13px; color:var(--cx-muted); line-height:1.5; margin-top:10px; }
.cx-main { grid-column: 1 / span 2; }
.cx-pinkwrap { grid-column: 3; grid-row: 1 / span 2; }
.cx-shapcard { grid-column: 1 / span 3; }
.cx-delta { display:inline-block; padding:5px 12px; border-radius:999px; font-size:13px; font-weight:600; margin-top:12px; }
.cx-delta.up { background:#FDE6EE; color:#B32A58; }
.cx-delta.down { background:#E8F1D3; color:#456B0D; }

/* dotted scale strip */
.cx-strip { display:flex; gap:5px; align-items:center; margin-top:20px; }
.cx-strip i { width:7px; height:7px; border-radius:50%; background:var(--cx-row-border); flex:none; }
.cx-strip i.on { background:var(--cx-ink); }
.cx-strip i.mk { width:18px; height:18px; background:var(--cx-card-bg); border:2px solid var(--cx-ink); box-shadow:0 6px 14px -4px rgba(0,0,0,.4); }
.cx-strip-cap { display:flex; justify-content:space-between; font-size:12px; color:var(--cx-muted-2); margin-top:8px; }

/* SHAP rows */
.cx-shaprow { display:grid; grid-template-columns: 230px 1fr 74px; align-items:center; gap:12px; padding:7px 0; }
.cx-shaprow .nm { font-size:14px; letter-spacing:-.01em; font-weight:500; color:var(--cx-ink); text-align:right; }
.cx-shaprow .tr { position:relative; height:14px; background: linear-gradient(90deg, transparent 49.8%, var(--cx-track-bg) 49.8%, var(--cx-track-bg) 50.2%, transparent 50.2%); }
.cx-shaprow .bar { position:absolute; top:1px; height:12px; border-radius:7px; }
.cx-shaprow .val { font-size:13.5px; font-weight:600; font-variant-numeric: tabular-nums; }
.cx-legend { display:flex; gap:18px; font-size:12.5px; color:var(--cx-muted); margin-top:8px; }
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

.cx-pink.lvl-low { background: linear-gradient(165deg, #9BF7B0 0%, #3DDC66 48%, #18A845 100%);
  box-shadow: 0 30px 50px -28px rgba(24,168,69,.75), inset 0 1px 0 rgba(255,255,255,.7); }
.cx-pink.lvl-medium { background: linear-gradient(165deg, #FFF3A3 0%, #FFDE3D 48%, #F5C518 100%);
  box-shadow: 0 30px 50px -28px rgba(245,197,24,.75), inset 0 1px 0 rgba(255,255,255,.7); color:#1A1A12; }
.cx-pink.lvl-medium .glass { background: rgba(0,0,0,.08); border:1px solid rgba(0,0,0,.18); }
.cx-pink.lvl-medium .lvl { background: rgba(0,0,0,.12); border:1px solid rgba(0,0,0,.22); color:#1A1A12; }
.cx-pink.lvl-medium .cap, .cx-pink.lvl-medium .lab { color:#1A1A12; }
.cx-pink.lvl-high { background: linear-gradient(165deg, #FFA3A3 0%, #FF5050 48%, #E51C1C 100%);
  box-shadow: 0 30px 50px -28px rgba(229,28,28,.75), inset 0 1px 0 rgba(255,255,255,.7); }

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
.cx-tile .s { position:relative; font-size:13px; color:rgba(255,255,255,.82); margin-top:6px; }
.cx-tile .glass { position:absolute; left:12px; right:12px; bottom:12px; padding:11px 16px; border-radius:20px; display:flex; align-items:baseline; justify-content:space-between;
  background: rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.3); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); }
.cx-tile .sv { font-size:28px; font-weight:600; letter-spacing:-.025em; }
.cx-tile .un { font-size:12px; color:rgba(255,255,255,.72); }
.cx-tile.empty { background: linear-gradient(168deg,#262A26,#121412); border-color: rgba(255,255,255,.1); box-shadow:none; }
.cx-tile.empty .t { color:#C9CEC9; } .cx-tile.empty .s { color:#7C827C; }

/* ---------- tile colour family (lever / insight cards) ---------- */
.cx-tile.c-green { background: linear-gradient(168deg, #8FE3A1 0%, #3FBE69 52%, #1E8A47 100%);
  border-color: rgba(143,227,161,.4); box-shadow: 0 26px 40px -24px rgba(31,138,71,.55), inset 0 1px 0 rgba(255,255,255,.28); }
.cx-tile.c-blue { background: linear-gradient(168deg, #8FD3F4 0%, #3E9FD9 52%, #1C6FA8 100%);
  border-color: rgba(143,211,244,.4); box-shadow: 0 26px 40px -24px rgba(28,111,168,.55), inset 0 1px 0 rgba(255,255,255,.28); }
.cx-tile.c-pink { background: linear-gradient(168deg, #FFB6CD 0%, #FF7DA6 52%, #D94C79 100%);
  border-color: rgba(255,182,205,.4); box-shadow: 0 26px 40px -24px rgba(217,76,121,.55), inset 0 1px 0 rgba(255,255,255,.28); }
.cx-tile.c-teal { background: linear-gradient(168deg, #7FE8D0 0%, #2EC4A6 52%, #15876E 100%);
  border-color: rgba(127,232,208,.4); box-shadow: 0 26px 40px -24px rgba(21,135,110,.55), inset 0 1px 0 rgba(255,255,255,.28); }
.cx-tile.c-violet { background: linear-gradient(168deg, #C7C3FF 0%, #8B7CF6 52%, #5B4BC4 100%);
  border-color: rgba(199,195,255,.4); box-shadow: 0 26px 40px -24px rgba(91,75,196,.55), inset 0 1px 0 rgba(255,255,255,.28); }
.cx-gauge { text-align:center; }
.cx-gauge .gl { font-size:13px; color:#9AA09A; margin-top:-6px; }
.cx-gauge .gv { font-size:34px; font-weight:600; letter-spacing:-.02em; }
.cx-gauge .gv small { font-size:16px; color:#9AA09A; margin-left:4px; }
.cx-foot { font-size:12.5px; color:#7C827C; margin-top: 14px; line-height:1.5; }

/* ---------- other pages ---------- */
.cx-models { display:grid; grid-template-columns: repeat(3, 1fr); gap:16px; margin-top:18px; }
.cx-model { background:var(--cx-card-bg); border-radius:28px; padding:22px 26px; box-shadow: 0 22px 44px -26px rgba(20,22,20,.30); position:relative; overflow:hidden; }
.cx-model.best { color:#fff; background: linear-gradient(165deg, #9FDBF7 0%, #4FAEE6 48%, #2680C2 100%); box-shadow: 0 30px 50px -28px rgba(38,128,194,.7), inset 0 1px 0 rgba(255,255,255,.7); }
.cx-model.best .cx-big { color:#fff; }
.cx-model.best .cx-label, .cx-model.best .cx-big small, .cx-model.best .cx-note { color: rgba(255,255,255,.92); }
.cx-model .cx-big { font-size:50px; }
.cx-model .row { display:flex; justify-content:space-between; font-size:14px; padding:6px 0; border-top:1px solid var(--cx-row-border); margin-top:6px; }
.cx-model.best .row { border-color: rgba(255,255,255,.4); }
.cx-badge { display:inline-block; padding:4px 12px; border-radius:999px; font-size:12px; font-weight:700; background:rgba(255,255,255,.3); border:1px solid rgba(255,255,255,.6); margin-bottom:6px; }
.cx-hbar { display:grid; grid-template-columns: 170px 1fr 70px; align-items:center; gap:12px; padding:6px 0; font-size:14px; }
.cx-hbar .tr { height:12px; background:var(--cx-hbar-track); border-radius:7px; position:relative; }
.cx-hbar .f { position:absolute; left:0; top:0; bottom:0; border-radius:7px; background:var(--cx-ink); }
.cx-hbar .f.b { background: linear-gradient(90deg,#4FAEE6,#2680C2); }
.cx-dark { background: linear-gradient(180deg,#141714 0%,#090A09 100%); color:#fff; border-radius:34px; padding:28px 32px; margin-top:18px;
  box-shadow: 0 40px 70px -40px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.07); }
.cx-dark .cx-label { color:#9AA09A; }
.cx-dbar { display:grid; grid-template-columns: 230px 1fr 80px; align-items:center; gap:14px; padding:7px 0; }
.cx-dbar .nm { font-size:15px; text-align:right; color:#E6EAE6; }
.cx-dbar .tr { height:14px; background:rgba(255,255,255,.08); border-radius:8px; position:relative; overflow:hidden; }
.cx-dbar .f { position:absolute; left:0; top:0; bottom:0; border-radius:8px; background: linear-gradient(90deg,#7C9A18,#C5E04F); }
.cx-dbar .v { font-size:13.5px; color:#C9CEC9; font-variant-numeric: tabular-nums; }
.cx-warn { background: var(--cx-warn-bg); border:1px solid var(--cx-chip-border); border-radius:22px; padding:16px 20px; font-size:14px; color:var(--cx-warn-text); line-height:1.55; margin-top:16px; backdrop-filter: blur(12px); }
.cx-rank { display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:16px; margin-top:18px; }

/* ---------- area / trend chart ---------- */
.cx-areawrap { width:100%; }
.cx-areawrap svg { width:100%; height:auto; display:block; overflow:visible; }
.cx-areawrap .grid { stroke: rgba(255,255,255,.10); stroke-width:1; stroke-dasharray:3 5; }
.cx-areawrap .ytick { fill:#7C827C; font-size:9.5px; font-family:'Inter',sans-serif; }
.cx-areawrap .xtick { fill:#9AA09A; font-size:9.5px; font-family:'Inter',sans-serif; }
.cx-areawrap .line { fill:none; stroke:#C5E04F; stroke-width:2.6; stroke-linecap:round; stroke-linejoin:round; }
.cx-areawrap .dot { fill:#0C0E0C; stroke:#C5E04F; stroke-width:2.4; }
.cx-areawrap .hit { fill:transparent; cursor:pointer; }
.cx-areawrap .hit:hover + .hovdot { opacity:1; }
.cx-areawrap .hovdot { fill:#0C0E0C; stroke:#C5E04F; stroke-width:2.2; opacity:0; pointer-events:none; transition:opacity .08s; }

@media (max-width: 1100px) {
  .cx-grid { grid-template-columns: 1fr; } .cx-main, .cx-pinkwrap, .cx-shapcard { grid-column: auto; grid-row: auto; }
  .cx-band { grid-template-columns: 1fr; } .cx-tiles, .cx-models { grid-template-columns: 1fr; }
  .cx-shaprow { grid-template-columns: 120px 1fr 64px; }
}
@media (prefers-reduced-motion: no-preference) { .cx-strip i.mk { transition: all .3s ease; } }
</style>
"""


# Applies a saved (or system) theme to <html data-theme="..."> on load, and
# wires up every .cx-theme-toggle button to flip + persist it. <html> lives
# outside Streamlit's own React root, so the attribute survives reruns;
# the singleton guard only needs to stop the click listener being attached
# twice, same pattern as the rail-arrow scripts in landing.py / know_your_carbon.py.
THEME_TOGGLE_JS = """<script>
(function () {
  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem('cx-theme', theme); } catch (e) {}
  }
  function current() {
    try {
      var saved = localStorage.getItem('cx-theme');
      if (saved === 'light' || saved === 'dark') return saved;
    } catch (e) {}
    return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  }
  apply(current());
  if (window.__cxTheme) return; window.__cxTheme = true;
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.cx-theme-toggle');
    if (!b) return;
    var now = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    apply(now);
  });
})();
</script>"""


def theme_toggle():
    """A small fixed, top-left sun/moon button. Install THEME_TOGGLE_JS once
    per page (st.html(..., unsafe_allow_javascript=True)) for it to work."""
    sun = ("<svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' "
           "stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='4.4'/>"
           "<path d='M12 2.5v2.4M12 19.1v2.4M4.4 4.4l1.7 1.7M17.9 17.9l1.7 1.7M2.5 12h2.4M19.1 12h2.4M4.4 19.6l1.7-1.7M17.9 6.1l1.7-1.7'/></svg>")
    moon = ("<svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' "
            "stroke-linecap='round' stroke-linejoin='round'><path d='M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5z'/></svg>")
    return (f"<button type='button' class='cx-theme-toggle' aria-label='Toggle dark mode'>"
            f"<span class='sun'>{sun}</span><span class='moon'>{moon}</span></button>")


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


TILE_COLORS = [
    ("c-green", "#D7FADF", "#1E8A47"),
    ("c-blue", "#D9F0FC", "#1C6FA8"),
    ("c-pink", "#FFE3EC", "#D94C79"),
    ("c-teal", "#D4FBF2", "#15876E"),
    ("c-violet", "#E8E5FF", "#5B4BC4"),
]


def tile_color_class(i):
    """The colour-variant CSS class for the i-th lever / insight tile, cycling
    through a cool, friendly palette (green, blue, pink, teal, violet)."""
    return TILE_COLORS[i % len(TILE_COLORS)][0]


def tile_art(i):
    shapes = [
        "M0,100 L0,60 C40,40 70,20 110,38 C150,56 170,10 220,34 L260,70 L260,100 Z",
        "M0,100 L0,70 L60,50 L100,22 L140,56 L190,30 L260,66 L260,100 Z",
        "M0,100 L0,52 C30,64 60,68 90,46 C120,22 150,30 176,52 C206,76 232,60 260,40 L260,100 Z",
    ]
    _, light, dark = TILE_COLORS[i % len(TILE_COLORS)]
    return ("<svg class='art' viewBox='0 0 260 100' preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg'>"
            f"<defs><linearGradient id='tg{i}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{light}'/>"
            f"<stop offset='1' stop-color='{dark}'/></linearGradient></defs>"
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


def _nice_step(raw_step):
    """Round a raw axis step up to a human-friendly 1 / 2 / 5 / 10 x 10^n value,
    so gridlines land on round numbers like 0, 50K, 100K instead of 0, 46K, 92K."""
    if raw_step <= 0:
        return 1.0
    exp = math.floor(math.log10(raw_step))
    frac = raw_step / (10 ** exp)
    nice = 1 if frac <= 1 else 2 if frac <= 2 else 5 if frac <= 5 else 10
    return nice * (10 ** exp)


def area_chart(x_labels, values, value_fmt=None, y_gridlines=4, x_tick_every=5, highlight_last=True):
    """A hand-rolled SVG area/trend chart in the dashboard's dark-panel, lime-accent
    theme (same visual family as the gauge and bar components above). `x_labels` are
    shown along the bottom (e.g. years); `values` is the matching numeric series.
    """
    value_fmt = value_fmt or (lambda v: f"{v:,.0f}")
    n = len(values)
    if n < 2:
        return "<div class='cx-areawrap'></div>"

    W, H = 760.0, 230.0
    pad_l, pad_r, pad_t, pad_b = 54.0, 16.0, 18.0, 28.0
    plot_w, plot_h = W - pad_l - pad_r, H - pad_t - pad_b

    # y-axis always starts at 0, with round gridline steps (0, 50K, 100K, ...)
    # rather than padded raw min/max, so the chart reads cleanly at a glance.
    vmin = 0.0
    raw_top = max(values) * 1.12 if max(values) > 0 else 1.0
    step = _nice_step(raw_top / y_gridlines)
    vmax = step * math.ceil(raw_top / step)
    if vmax <= vmin:
        vmax = vmin + step
    span = vmax - vmin

    def xf(i):
        return pad_l + (i / (n - 1)) * plot_w

    def yf(v):
        return pad_t + (1 - (v - vmin) / span) * plot_h

    pts = [(xf(i), yf(v)) for i, v in enumerate(values)]

    # gridlines + y-axis labels, one per round step from 0 up to vmax
    grid_svg, ytick_svg = [], []
    n_steps = int(round(vmax / step))
    for g in range(n_steps + 1):
        gv = vmin + step * g
        gy = yf(gv)
        grid_svg.append(f"<line class='grid' x1='{pad_l:.1f}' y1='{gy:.1f}' x2='{W - pad_r:.1f}' y2='{gy:.1f}'/>")
        ytick_svg.append(f"<text class='ytick' x='{pad_l - 10:.1f}' y='{gy + 4:.1f}' text-anchor='end'>"
                         f"{value_fmt(gv)}</text>")

    # x-axis labels: every `x_tick_every`-th point, plus the last one, but drop any
    # regular tick that would land too close (in pixels) to the final label so the
    # last two years never collide.
    min_gap_px = 30.0
    candidate_idx = [i for i in range(0, n, x_tick_every)]
    if candidate_idx and candidate_idx[-1] != n - 1:
        candidate_idx.append(n - 1)
    while len(candidate_idx) >= 2 and (xf(candidate_idx[-1]) - xf(candidate_idx[-2])) < min_gap_px:
        del candidate_idx[-2]

    xtick_svg = []
    for i in candidate_idx:
        xtick_svg.append(f"<text class='xtick' x='{xf(i):.1f}' y='{H - 6:.1f}' "
                         f"text-anchor='middle'>{escape(str(x_labels[i]))}</text>")

    line_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    base_y = pad_t + plot_h
    area_d = line_d + f" L {pts[-1][0]:.1f},{base_y:.1f} L {pts[0][0]:.1f},{base_y:.1f} Z"

    last_x, last_y = pts[-1]
    dot_svg = f"<circle class='dot' cx='{last_x:.1f}' cy='{last_y:.1f}' r='5'/>" if highlight_last else ""

    # per-point hover targets: a wide invisible hit circle (with a native tooltip
    # showing the year and value) plus a themed dot that fades in on hover via CSS
    hover_svg = []
    for i, (px, py) in enumerate(pts):
        tip = f"{escape(str(x_labels[i]))}: {escape(value_fmt(values[i]))}"
        hover_svg.append(
            f"<circle class='hit' cx='{px:.1f}' cy='{py:.1f}' r='10'><title>{tip}</title></circle>"
            f"<circle class='hovdot' cx='{px:.1f}' cy='{py:.1f}' r='4.5'/>"
        )

    return (
        f"<div class='cx-areawrap'><svg viewBox='0 0 {W:.0f} {H:.0f}' xmlns='http://www.w3.org/2000/svg'>"
        "<defs><linearGradient id='cxAreaFill' x1='0' y1='0' x2='0' y2='1'>"
        "<stop offset='0' stop-color='#C5E04F' stop-opacity='.42'/>"
        "<stop offset='1' stop-color='#C5E04F' stop-opacity='0'/></linearGradient></defs>"
        + "".join(grid_svg)
        + f"<path d='{area_d}' fill='url(#cxAreaFill)'/>"
        + f"<path class='line' d='{line_d}'/>"
        + dot_svg
        + "".join(ytick_svg) + "".join(xtick_svg)
        + "".join(hover_svg)
        + "</svg></div>"
    )
