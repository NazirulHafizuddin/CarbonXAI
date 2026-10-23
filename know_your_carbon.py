"""
know_your_carbon.py
"Know Your Carbon" -- an educational page in the CarbonXAI dashboard, placed
before Prediction. It explains the difference between a carbon emission and
a carbon footprint, in plain language, before the user starts predicting
their own number.

Same conventions as landing.py / ui.py (read those files' docstrings first):
- Plain HTML rendered via st.markdown(unsafe_allow_html=True), collapsed to
  one line through _h() (markdown ends an HTML block at a blank line).
- Horizontal card rows reuse the same mechanism as landing.py's .lp-rail:
  CSS scroll-snap (desktop wheel/trackpad + mobile swipe need no JS at all)
  plus a small shared script that makes the round arrow buttons scroll the
  row by one card. Classes are namespaced "kyc-" / "st-key-kycsec_" so this
  page's CSS and JS never touch landing.py's own "lp-" screens.
- Avoid the dollar sign in text: Streamlit would try to render it as LaTeX.

Images: the photos used here live in assets/ as kyc_<name>_hero.jpg (the
16:9 hero banner) and kyc_<name>_card.jpg (~1.29:1 card crops used in the
"Where do emissions come from" / "Meet Amir" rails and the emission vs.
footprint compare cards). Swap a file at the same path to replace a photo;
nothing else needs to change. A missing file just falls back to a plain
colour card (_img() returns None), so this page never breaks if an asset
is deleted.
"""

import os

import streamlit as st

from landing import icon as _base_icon, _photo_uri

ASSETS_DIR = "assets"


def _h(s):
    """Collapse an HTML string to one line (see module docstring)."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def _img(filename):
    """Base64 data URI for a file in assets/, or None if it is missing --
    callers fall back to a plain colour card rather than force a photo in."""
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        return _photo_uri(path, os.path.getmtime(path))
    return None


# A couple of icons this page needs that landing.py's set does not have.
# Everything else (car, plane, bolt, food, bag, bin, co2, foot, sliders,
# spark, leaf, ...) is reused as-is from landing.icon() for consistency.
_EXTRA_ICONS = {
    "drop": "<path d='M12 2C12 2 5 11 5 15.5A7 7 0 0 0 19 15.5C19 11 12 2 12 2z'/>",
    "bucket": "<path d='M4 8h16l-1.6 11.2A2 2 0 0 1 16.4 21H7.6a2 2 0 0 1-2-1.8L4 8z'/><path d='M8 8V6a4 4 0 0 1 8 0v2'/>",
}


def icon(name, size=26, stroke=1.8):
    if name in _EXTRA_ICONS:
        return (f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='currentColor' "
                f"stroke-width='{stroke}' stroke-linecap='round' stroke-linejoin='round'>{_EXTRA_ICONS[name]}</svg>")
    return _base_icon(name, size, stroke)


# ═════════════════════════════ STYLE ═════════════════════════════
KYC_CSS = """
<style>
.kyc-eyebrow { font-size:13px; letter-spacing:.16em; text-transform:uppercase; font-weight:800; color:#6F9A12; }
.kyc-eyebrow.on-dark { color:#C5E04F; }
.kyc-h1 { font-size: clamp(32px, 4.4vw, 52px); font-weight:700; line-height:1.04; letter-spacing:-.04em; margin:12px 0 14px 0; color:#fff; }
.kyc-h2 { font-size: clamp(25px, 2.8vw, 34px); font-weight:700; line-height:1.14; letter-spacing:-.03em; margin:8px 0 10px 0; color:var(--cx-ink); max-width:28ch; }
.kyc-h2.on-dark { color:#fff; }
.kyc-lead { font-size:15.5px; line-height:1.6; color:var(--cx-muted); max-width:64ch; margin:0; }
.kyc-lead.on-dark { color:rgba(255,255,255,.80); }
.kyc-hint { font-size:13px; color:var(--cx-muted-2); display:flex; align-items:center; gap:8px; margin:12px 0 10px 0; }

/* ---------- hero banner ----------
   Styled on the container key itself (like landing.py's st-key-lpsec_*),
   not a nested div, so the box really does pick up this padding/sizing. */
[class*="st-key-kycsec_hero"] { position:relative; border-radius:38px; overflow:hidden; padding:56px 48px !important;
  min-height:300px; display:flex !important; flex-direction:column !important; justify-content:center;
  background-color:#0B0F0C; color:#fff; box-shadow: 0 40px 70px -40px rgba(0,0,0,.8); }
[class*="st-key-kycsec_hero"] .kyc-lead { max-width:58ch; }

/* ---------- horizontal rail (same mechanics as landing.py's .lp-rail) ---------- */
.kyc-rail { display:flex; gap:16px; overflow-x:auto; scroll-snap-type:x mandatory; scroll-padding-inline:4px;
  padding:14px 4px 28px 4px; margin:-14px -4px -10px -4px; scrollbar-width:thin;
  scrollbar-color: rgba(15,17,16,.5) rgba(15,17,16,.08); -webkit-overflow-scrolling:touch; overscroll-behavior-x: contain; }
.kyc-rail::-webkit-scrollbar { height:6px; }
.kyc-rail::-webkit-scrollbar-track { background:rgba(15,17,16,.08); border-radius:6px; }
.kyc-rail::-webkit-scrollbar-thumb { background:rgba(15,17,16,.5); border-radius:6px; }

.kyc-card { flex:0 0 min(78vw, 300px); min-height:280px; scroll-snap-align:start; border-radius:28px; padding:24px;
  background:var(--cx-card-bg); position:relative; overflow:hidden; display:flex; flex-direction:column; color:var(--cx-ink);
  box-shadow: 0 1px 0 var(--cx-card-shadow-inset) inset, 0 22px 42px -26px rgba(20,22,20,.32);
  transition: transform .3s ease, box-shadow .3s ease; }
.kyc-card:hover { transform:translateY(-6px); box-shadow: 0 1px 0 var(--cx-card-shadow-inset) inset, 0 32px 52px -26px rgba(20,22,20,.4); }
.kyc-card.wide { flex-basis:min(84vw, 360px); }
.kyc-card .ic { width:48px; height:48px; border-radius:15px; display:grid; place-items:center; background:var(--cx-icon-bg); color:var(--cx-ink); flex:none; }
.kyc-card h3 { font-size:20.5px; font-weight:600; letter-spacing:-.02em; margin:18px 0 8px 0; line-height:1.2; color:inherit; }
.kyc-card p { font-size:14.5px; line-height:1.52; margin:0; color:inherit; opacity:.86; }
.kyc-card .tag { margin-top:auto; padding-top:16px; font-size:12px; letter-spacing:.1em; text-transform:uppercase; font-weight:700; opacity:.55; }

.kyc-card.c-dark { background:linear-gradient(180deg,#171A17,#0C0E0C); color:#fff; }
.kyc-card.c-dark .ic { background:rgba(255,255,255,.14); color:#C5E04F; }
.kyc-card.c-blue { background:linear-gradient(165deg,#8FD3F4,#1C6FA8); color:#fff; }
.kyc-card.c-blue .ic { background:rgba(255,255,255,.2); color:#fff; }
.kyc-card.c-violet { background:linear-gradient(165deg,#C7C3FF,#5B4BC4); color:#fff; }
.kyc-card.c-violet .ic { background:rgba(255,255,255,.2); color:#fff; }
.kyc-card.c-pink { background:linear-gradient(165deg,#FFB6CD,#FF5088); color:#fff; }
.kyc-card.c-pink .ic { background:rgba(255,255,255,.22); color:#fff; }
.kyc-card.c-lime { background:linear-gradient(160deg,#DCEF86,#B4D13C); color:#1A1A12; }
.kyc-card.c-lime .ic { background:rgba(15,17,16,.1); color:#1A1A12; }
.kyc-card.c-green { background:linear-gradient(165deg,#8FE3A1,#1E8A47); color:#fff; }
.kyc-card.c-green .ic { background:rgba(255,255,255,.2); color:#fff; }

.kyc-card.photo { color:#fff; background-size:cover; background-position:center; }
.kyc-card.photo::before { content:""; position:absolute; inset:0;
  background:linear-gradient(180deg, rgba(8,11,9,.92) 0%, rgba(8,11,9,.46) 48%, rgba(8,11,9,.04) 78%); }
.kyc-card.photo .ic, .kyc-card.photo h3, .kyc-card.photo p, .kyc-card.photo .tag { position:relative; z-index:1; }
.kyc-card.photo .ic { background:rgba(255,255,255,.22); color:#fff; backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); }

/* ---------- rail arrows ---------- */
.kyc-arrows { display:flex; justify-content:flex-end; gap:10px; margin-top:-4px; }
.kyc-arrow { width:42px; height:42px; border-radius:50%; border:0; display:grid; place-items:center; cursor:pointer; padding:0;
  background:var(--cx-pill-bg); color:var(--cx-pill-text); transition: background .2s, transform .2s, opacity .2s; }
.kyc-arrow:hover:not(:disabled) { background:#0F1110; color:#fff; transform:scale(1.06); }
:root[data-theme="dark"] .kyc-arrow:hover:not(:disabled) { background:#C5E04F; color:#0F1110; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .kyc-arrow:hover:not(:disabled) { background:#C5E04F; color:#0F1110; } }
.kyc-arrow:focus-visible { outline:2px solid #6F9A12; outline-offset:2px; }
.kyc-arrow:disabled { opacity:.35; cursor:default; }
.kyc-arrow svg { width:18px; height:18px; }
@media (hover:none) and (max-width:760px) { .kyc-arrows { display:none; } }

/* ---------- emission vs footprint compare ---------- */
.kyc-compare { display:grid; grid-template-columns: 1fr 1fr; gap:18px; margin-top:22px; }
.kyc-compare-card { border-radius:32px; padding:30px 30px 26px 30px; position:relative; overflow:hidden; color:#fff;
  background-size:cover; background-position:center; }
.kyc-compare-card.emission { background-color:#0C0E0C; }
.kyc-compare-card.footprint { background-color:#1E6B3E; }
.kyc-compare-card::before { content:""; position:absolute; inset:0; z-index:0; }
.kyc-compare-card.emission::before { background:linear-gradient(165deg, rgba(10,12,10,.93) 0%, rgba(10,12,10,.62) 55%, rgba(10,12,10,.86) 100%); }
.kyc-compare-card.footprint::before { background:linear-gradient(165deg, rgba(40,90,62,.90) 0%, rgba(30,75,52,.60) 55%, rgba(20,60,45,.88) 100%); }
.kyc-compare-card > * { position:relative; z-index:1; }
.kyc-compare-card .ic { width:52px; height:52px; border-radius:16px; display:grid; place-items:center; background:rgba(255,255,255,.18); backdrop-filter: blur(4px); }
.kyc-compare-card h3 { font-size:24px; font-weight:600; margin:18px 0 10px 0; letter-spacing:-.02em; color:#fff; }
.kyc-compare-card p.def { font-size:15px; line-height:1.56; opacity:.88; margin:0 0 16px 0; }
.kyc-compare-card .phrase { display:inline-block; padding:8px 16px; border-radius:999px; font-weight:700; font-size:13.5px;
  background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.32); margin-bottom:16px; }
.kyc-compare-card .ex { font-size:14px; line-height:1.5; padding:14px 16px; border-radius:18px; background:rgba(255,255,255,.1);
  border:1px solid rgba(255,255,255,.18); }
.kyc-compare-card .ex b { color:#C5E04F; }
.kyc-compare-card.footprint .ex b { color:#FFF6C9; }

/* ---------- drop-to-bucket analogy ---------- */
[class*="st-key-kycsec_analogy"] { margin-top: 26px; }
.kyc-quote { font-size: clamp(23px, 2.8vw, 32px); font-weight:600; line-height:1.4; letter-spacing:-.02em; color:var(--cx-ink); margin:6px 0 16px 0; max-width:40ch; }
.kyc-quote b { color:#5E8C14; }
.kyc-flow { display:flex; align-items:center; gap:16px; flex-wrap:wrap; margin-top:26px; }
.kyc-drops { display:flex; flex-wrap:wrap; gap:10px; flex:1 1 420px; }
.kyc-drop { display:flex; align-items:center; gap:9px; padding:9px 14px 9px 9px; border-radius:999px; background:var(--cx-chip-bg);
  border:1px solid var(--cx-chip-border); font-weight:600; font-size:14px; color:var(--cx-ink); backdrop-filter: blur(10px); white-space:nowrap; }
.kyc-drop .ic { width:26px; height:26px; border-radius:50%; background:#0F1110; color:#C5E04F; display:grid; place-items:center; flex:none; }
.kyc-flow-arrow { color:#9AA09A; font-size:22px; flex:0 0 auto; }
.kyc-bucket { display:flex; align-items:center; gap:12px; padding:15px 24px; border-radius:999px; background:#0F1110; color:#fff;
  font-weight:700; font-size:16px; flex:0 0 auto; box-shadow:0 20px 40px -22px rgba(0,0,0,.5); }
.kyc-bucket .ic { width:36px; height:36px; border-radius:50%; background:#C5E04F; color:#0F1110; display:grid; place-items:center; flex:none; }

/* ---------- explainability panel ---------- */
.kyc-panel { background: var(--cx-warn-bg); border:1px solid var(--cx-chip-border); border-radius:28px; padding:26px 30px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); margin-top:16px; }
.kyc-panel h3 { font-size:18.5px; font-weight:600; margin:0 0 10px 0; color:var(--cx-ink); }
.kyc-panel p { font-size:14.5px; line-height:1.6; color:var(--cx-warn-text); margin:0; max-width:78ch; }

/* ---------- final CTA ---------- */
.kyc-cta { margin-top:32px; background: linear-gradient(180deg,#141714 0%,#090A09 100%); border-radius:40px; padding:48px 48px 44px 48px;
  color:#fff; text-align:center; box-shadow: 0 40px 70px -40px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.07); }
.kyc-cta h2 { color:#fff; font-size: clamp(25px, 3vw, 36px); margin:0 0 10px 0; letter-spacing:-.025em; }
.kyc-cta p { color:#9AA09A; font-size:15px; max-width:60ch; margin:0 auto 24px auto; line-height:1.55; }
.st-key-kycb_cta { display:flex; justify-content:flex-start; width:100% !important; }
.st-key-kycb_cta [data-testid="stButton"] { width:auto !important; }
.st-key-kycb_cta button { border-radius:999px !important; padding:16px 36px !important; min-height:0 !important; width:auto !important;
  font-weight:700 !important; font-size:16.5px !important; background:#C5E04F !important; color:#0F1110 !important;
  border:1px solid #C5E04F !important; box-shadow:0 14px 30px -14px rgba(197,224,79,.9) !important;
  transition: transform .25s ease, background .25s ease !important; }
.st-key-kycb_cta button:hover { transform:translateY(-2px); background:#D3EC6A !important; }
.st-key-kycb_cta button * { color:#0F1110 !important; font-weight:700 !important; font-size:16.5px !important; }

@media (max-width: 900px) {
  .kyc-compare { grid-template-columns: 1fr; }
}
</style>
"""

# Makes the round arrow buttons scroll a .kyc-rail by one card. Namespaced
# separately from landing.py's _ARROW_JS so the two pages never collide;
# installed once per browser tab, same pattern as landing.py.
_ARROW_JS = """<script>
(function () {
  if (window.__kycArrows) return; window.__kycArrows = true;
  function railOf(btn) { var sec = btn.closest('[class*="st-key-kycsec_"]'); return sec && sec.querySelector('.kyc-rail'); }
  function sync() {
    document.querySelectorAll('.kyc-arrows').forEach(function (box) {
      var sec = box.closest('[class*="st-key-kycsec_"]'), rail = sec && sec.querySelector('.kyc-rail'); if (!rail) return;
      var max = rail.scrollWidth - rail.clientWidth - 2;
      box.querySelectorAll('.kyc-arrow').forEach(function (b) {
        b.disabled = b.dataset.dir === '-1' ? rail.scrollLeft <= 2 : rail.scrollLeft >= max;
      });
    });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.kyc-arrow'); if (!b) return;
    var rail = railOf(b); if (!rail) return;
    var card = rail.querySelector('.kyc-card'), step = card ? card.getBoundingClientRect().width + 16 : 320;
    rail.scrollBy({ left: Number(b.dataset.dir) * step, behavior: 'smooth' });
  });
  document.addEventListener('scroll', sync, true);
  window.addEventListener('resize', sync);
  setInterval(sync, 500);
})();
</script>"""

_CHEV_L = "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'><path d='M15 5l-7 7 7 7'/></svg>"
_CHEV_R = "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'><path d='M9 5l7 7-7 7'/></svg>"


def _arrows():
    return _h(f"""<div class='kyc-arrows'>
        <button type='button' class='kyc-arrow' data-dir='-1' aria-label='Previous card'>{_CHEV_L}</button>
        <button type='button' class='kyc-arrow' data-dir='1' aria-label='Next card'>{_CHEV_R}</button>
        </div>""")


# ═════════════════════════════ SECTIONS ═════════════════════════════
def _hero_css():
    """Background image built here, separately from the static block above,
    because the data URI is only known once the photo file is read."""
    bg = _img("kyc_rainforest_hero.jpg")
    veil = "linear-gradient(90deg, rgba(8,11,9,.90) 0%, rgba(8,11,9,.58) 55%, rgba(8,11,9,.30) 100%)"
    if bg:
        return f"<style>.st-key-kycsec_hero {{ background: {veil}, url('{bg}') center / cover no-repeat; }}</style>"
    return ""


def _hero():
    with st.container(key="kycsec_hero"):
        st.markdown(_h("""
            <div class='kyc-eyebrow on-dark'>Understand emissions before exploring your footprint</div>
            <h1 class='kyc-h1'>Know Your Carbon</h1>
            <p class='kyc-lead on-dark'>Our everyday activities, from travelling and using electricity to eating,
            shopping and managing waste, can contribute to greenhouse gas emissions. But what is the difference
            between a carbon emission and a carbon footprint?</p>"""), unsafe_allow_html=True)


def _source_card(kind, ic, title, text, photo=None):
    if photo:
        img = _img(photo)
        style = f" style=\"background-image:url('{img}')\"" if img else ""
        kind = (kind + " photo").strip()
        return (f"<article class='kyc-card {kind}'{style}><span class='ic'>{icon(ic, 24)}</span>"
                f"<h3>{title}</h3><p>{text}</p></article>")
    return f"<article class='kyc-card {kind}'><span class='ic'>{icon(ic, 24)}</span><h3>{title}</h3><p>{text}</p></article>"


def _sources():
    with st.container(key="kycsec_sources"):
        cards = [
            _source_card("", "car", "Transport",
                         "Petrol and diesel vehicles release CO₂ from the tailpipe. Walking, cycling and "
                         "public transport usually release less.", photo="kyc_traffic_card.jpg"),
            _source_card("", "plane", "Air Travel",
                         "Flights burn large amounts of jet fuel, so even a few trips a year can add a lot to a "
                         "footprint.", photo="kyc_airtravel_card.jpg"),
            _source_card("", "bolt", "Energy",
                         "Electricity and heating release CO₂ when they come from coal, gas or other fossil "
                         "fuels.", photo="kyc_pylons_card.jpg"),
            _source_card("", "food", "Food &amp; Diet",
                         "Growing, processing and cooking food all release greenhouse gases, and some diets "
                         "release more than others.", photo="kyc_food_card.jpg"),
            _source_card("", "bag", "Shopping &amp; Consumption",
                         "Making and shipping clothes and everyday goods takes energy, so what and how often we "
                         "buy matters.", photo="kyc_shopping_card.jpg"),
            _source_card("", "bin", "Waste &amp; Recycling",
                         "Landfills release methane as waste breaks down, and recycling can cut the energy needed "
                         "to make new materials.", photo="kyc_landfill_card.jpg"),
        ]
        st.markdown(_h(f"""
            <div class='kyc-eyebrow'>01 &middot; The basics</div>
            <h2 class='kyc-h2'>Where do emissions come from?</h2>
            <p class='kyc-lead'>Six everyday areas, each adding its own share to the total.</p>
            <div class='kyc-hint'>Swipe or scroll sideways &rarr;</div>
            <div class='kyc-rail'>{''.join(cards)}</div>"""), unsafe_allow_html=True)
        st.markdown(_arrows(), unsafe_allow_html=True)


def _compare_card(kind, photo, ic, title, definition, phrase, example_html):
    img = _img(photo)
    style = f" style=\"background-image:url('{img}')\"" if img else ""
    return (f"<div class='kyc-compare-card {kind}'{style}><span class='ic'>{icon(ic, 26)}</span>"
            f"<h3>{title}</h3><p class='def'>{definition}</p>"
            f"<span class='phrase'>{phrase}</span>"
            f"<div class='ex'>{example_html}</div></div>")


def _compare():
    with st.container(key="kycsec_compare"):
        emission = _compare_card(
            "emission", "kyc_emission_card.jpg", "co2", "Carbon Emission",
            "A greenhouse gas emission associated with a specific activity or source.",
            "Emission = one source",
            "<b>Example:</b> Driving a petrol car creates carbon emissions.")
        footprint = _compare_card(
            "footprint", "kyc_footprint_card.jpg", "foot", "Carbon Footprint",
            "The combined emissions associated with different activities in a person's lifestyle.",
            "Footprint = total impact",
            "<b>Example:</b> Transport + Energy + Food + Shopping + Flights + Waste = Carbon Footprint")
        st.markdown(_h(f"""
            <div class='kyc-eyebrow'>02 &middot; Two different ideas</div>
            <h2 class='kyc-h2'>Carbon emission vs. carbon footprint</h2>
            <p class='kyc-lead'>They sound alike, but one is a single number and the other is the whole picture.</p>
            <div class='kyc-compare'>{emission}{footprint}</div>"""), unsafe_allow_html=True)


def _drop(ic, label_text):
    return f"<span class='kyc-drop'><span class='ic'>{icon(ic, 14)}</span>{label_text}</span>"


def _analogy():
    with st.container(key="kycsec_analogy"):
        drops = [
            _drop("car", "Car"), _drop("bolt", "Electricity"), _drop("plane", "Flight"),
            _drop("food", "Food"), _drop("bag", "Shopping"), _drop("bin", "Waste"),
        ]
        st.markdown(_h(f"""
            <div class='kyc-eyebrow'>03 &middot; A simple analogy</div>
            <p class='kyc-quote'>Carbon emission is one <b>drop of water</b>.<br>Your carbon footprint is the
            whole <b>bucket</b>.</p>
            <p class='kyc-lead'>Each activity contributes a portion of emissions. When these emissions are
            considered together, they form your overall carbon footprint.</p>
            <div class='kyc-flow'>
              <div class='kyc-drops'>{''.join(drops)}</div>
              <span class='kyc-flow-arrow'>&rarr;</span>
              <span class='kyc-bucket'><span class='ic'>{icon("bucket", 20)}</span>Your Carbon Footprint</span>
            </div>"""), unsafe_allow_html=True)


_AMIR_CARDS = [
    ("car", "Amir drives to university.", "kyc_traffic_card.jpg"),
    ("bolt", "He uses electricity for air conditioning and electronic devices.", "kyc_pylons_card.jpg"),
    ("food", "His dietary choices contribute to his environmental impact.", "kyc_food_card.jpg"),
    ("bag", "He buys clothes and other products.", "kyc_shopping_card.jpg"),
    ("plane", "He travels by air during holidays or semester breaks.", "kyc_airtravel_card.jpg"),
    ("bin", "His waste and recycling habits also contribute.", "kyc_landfill_card.jpg"),
]


def _amir():
    with st.container(key="kycsec_amir"):
        cards = [_source_card("", ic, "", text, photo=photo).replace("<h3></h3>", "")
                 for ic, text, photo in _AMIR_CARDS]
        final = ("<article class='kyc-card wide c-lime'><span class='ic'>" + icon("foot", 24) + "</span>"
                 "<h3>Amir's Carbon Footprint</h3>"
                 "<p>All these activities together form Amir's carbon footprint.</p>"
                 "<span class='tag'>The big picture</span></article>")
        st.markdown(_h(f"""
            <div class='kyc-eyebrow'>04 &middot; A Malaysian scenario</div>
            <h2 class='kyc-h2'>Meet Amir</h2>
            <p class='kyc-lead'>Amir is a fictional Malaysian university student. Here is an ordinary week in his
            life, one activity at a time.</p>
            <div class='kyc-hint'>Swipe or scroll sideways &rarr;</div>
            <div class='kyc-rail'>{''.join(cards)}{final}</div>"""), unsafe_allow_html=True)
        st.markdown(_arrows(), unsafe_allow_html=True)


def _why_card(ic, title, text):
    return f"<article class='kyc-card wide c-dark'><span class='ic'>{icon(ic, 24)}</span><h3>{title}</h3><p>{text}</p></article>"


def _why_carbonxai():
    with st.container(key="kycsec_why"):
        cards = [
            _why_card("sliders", "Predict", "Estimate an individual carbon emission value based on lifestyle and "
                      "consumption factors."),
            _why_card("spark", "Explain", "Understand which factors contribute most strongly to the prediction."),
            _why_card("leaf", "Explore", "Use interactive visualisations to examine carbon emission patterns and "
                      "sustainability insights."),
        ]
        st.markdown(_h(f"""
            <div class='kyc-eyebrow'>05 &middot; Why CarbonXAI</div>
            <h2 class='kyc-h2'>Knowing the number is only the beginning.</h2>
            <div class='kyc-rail'>{''.join(cards)}</div>"""), unsafe_allow_html=True)
        st.markdown(_arrows(), unsafe_allow_html=True)
        st.markdown(_h("""
            <div class='kyc-panel'><h3>Why does explanation matter?</h3>
            <p>Knowing whether a carbon emission value is high or low is useful, but understanding what
            contributes to that value can provide deeper insight. CarbonXAI therefore combines prediction with
            explainability to highlight the lifestyle and consumption factors that contribute most strongly to
            the model's prediction.</p></div>"""), unsafe_allow_html=True)


def _cta(on_explore):
    with st.container(key="kycsec_cta"):
        st.markdown(_h("""
            <div class='kyc-cta'><h2>Ready to Explore Your Carbon Footprint?</h2>
            <p>Continue to the prediction page to explore how different lifestyle and consumption factors are
            associated with a predicted carbon emission value.</p></div>"""), unsafe_allow_html=True)
        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
        if st.button("Explore My Carbon Footprint →", key="kycb_cta"):
            on_explore()


# ═════════════════════════════ PUBLIC API ═════════════════════════════
def render(on_explore):
    """Draw the whole Know Your Carbon page.

    `on_explore` is called when the final CTA button is clicked; the caller
    decides what "go to Prediction" means for its own navigation state (see
    dashboard.py, which mirrors the same `_goto` -> st.rerun() pattern the
    landing page already uses to jump to a specific tab).
    """
    st.markdown(KYC_CSS, unsafe_allow_html=True)
    st.markdown(_hero_css(), unsafe_allow_html=True)
    _hero()
    _sources()
    st.html(_ARROW_JS, unsafe_allow_javascript=True)
    _compare()
    _analogy()
    _amir()
    _why_carbonxai()
    _cta(on_explore)
