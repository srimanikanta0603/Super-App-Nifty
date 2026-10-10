import streamlit as st
import pandas as pd
import datetime
import random
import io

# ── Optional Google Sheets ──────────────────────────────────────────────────
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_GSPREAD = True
except ImportError:
    HAS_GSPREAD = False

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Super App Nifty",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"], .stMarkdown, p, div, span, label {
  font-family: 'Plus Jakarta Sans', sans-serif;
}
.stApp {
  background:
    radial-gradient(1100px 500px at 12% -8%, #ffe9f4 0%, transparent 60%),
    radial-gradient(900px  460px at 92%  4%, #e9edff 0%, transparent 58%),
    #f7f5fb;
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; height: 0; }
.block-container { padding: 1rem 2rem 3rem; max-width: 1480px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #1c1030 0%, #2a1246 55%, #33144f 100%);
  border-right: none;
  min-width: 270px !important;
  width:      270px !important;
}
section[data-testid="stSidebar"] * { color: #ede7f6; }
section[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[kind="header"] { display: none !important; }

.brand {
  font-size: 1.12rem; font-weight: 800; letter-spacing: -.02em;
  color: #fff; display: flex; align-items: center; gap: .5rem; margin: 0 0 .2rem;
}
.brand-dot {
  width: 9px; height: 9px; border-radius: 50%;
  background: linear-gradient(135deg, #f472b6, #a78bfa);
  box-shadow: 0 0 12px rgba(244,114,182,.85);
  flex-shrink: 0;
}
.brand-sub {
  font-size: .72rem; color: #b9a8d4; margin-bottom: 1.5rem;
  letter-spacing: .04em; text-transform: uppercase; font-weight: 600;
}
section[data-testid="stSidebar"] div[role="radiogroup"] { gap: .3rem; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
  background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.06);
  border-radius: 11px; padding: .6rem .85rem; width: 100%; cursor: pointer;
  transition: all .16s ease; font-weight: 600; font-size: .9rem;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
  background: rgba(255,255,255,.11); transform: translateX(2px);
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
  background: linear-gradient(135deg, #ec4899, #a855f7);
  border-color: transparent; box-shadow: 0 6px 18px rgba(168,85,247,.35);
}
.side-sep { height: 1px; background: rgba(255,255,255,.09); margin: 1.2rem 0 .9rem; }
.side-lbl {
  font-size: .66rem; text-transform: uppercase; letter-spacing: .09em;
  color: #a692c4; font-weight: 700; margin-bottom: .4rem;
}
.side-kv { display: flex; justify-content: space-between; font-size: .76rem; padding: .28rem 0; color: #cfc2e4; }
.side-kv b { color: #fff; font-weight: 600; }

/* ── Header ── */
.hdr { display: flex; align-items: flex-end; justify-content: space-between; margin: .2rem 0 1.4rem; flex-wrap: wrap; gap: .8rem; }
.hdr h1 {
  font-size: 1.85rem; font-weight: 800; letter-spacing: -.03em; margin: 0;
  background: linear-gradient(120deg, #1e1035 20%, #7c3aed 60%, #ec4899 95%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hdr .subtitle { font-size: .85rem; color: #7c6f8c; margin-top: .15rem; font-weight: 500; }
.chip {
  display: inline-flex; align-items: center; gap: .4rem; padding: .42rem .85rem;
  border-radius: 99px; font-size: .76rem; font-weight: 700;
  background: #fff; border: 1px solid #ece3f5; box-shadow: 0 2px 8px rgba(80,20,120,.06);
}
.chip .dot { width: 7px; height: 7px; border-radius: 50%; }
.dot-green { background: #22c55e; box-shadow: 0 0 9px #22c55e; }

/* ── KPI cards ── */
.kpi-grid { display: grid; gap: .85rem; margin-bottom: 1.1rem; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); }
.kpi {
  border-radius: 18px; padding: 1.05rem 1.15rem; color: #fff; position: relative;
  overflow: hidden; box-shadow: 0 8px 22px rgba(90,25,120,.20);
  transition: transform .18s ease; min-width: 0;
}
.kpi:hover { transform: translateY(-3px); }
.kpi:after { content:""; position:absolute; right:-30px; top:-30px; width:88px; height:88px; border-radius:50%; background:rgba(255,255,255,.12); }
.kpi .lbl { font-size:.66rem; text-transform:uppercase; letter-spacing:.06em; font-weight:700; opacity:.92; }
.kpi .val { font-size:clamp(1.2rem,2vw,1.75rem); font-weight:800; letter-spacing:-.03em; line-height:1.2; margin-top:.3rem; }
.kpi .fin { font-size:.68rem; opacity:.88; margin-top:.2rem; font-weight:500; }
.g1  { background: linear-gradient(135deg,#f43f5e,#ec4899 55%,#d946ef); }
.g2  { background: linear-gradient(135deg,#8b5cf6,#6366f1 60%,#4f46e5); }
.g3  { background: linear-gradient(135deg,#06b6d4,#0ea5e9 60%,#3b82f6); }
.g4  { background: linear-gradient(135deg,#f59e0b,#f97316 60%,#ef4444); }
.g5  { background: linear-gradient(135deg,#10b981,#059669 60%,#047857); }
.gmute { background:linear-gradient(135deg,#e6e0ee,#efeaf6); color:#7c6f8c; box-shadow:none; border:1px dashed #ddd2ea; }
.gmute .val { color:#a99bbd; }

/* ── Panels ── */
.panel {
  background: rgba(255,255,255,.82); backdrop-filter: blur(6px);
  border-radius: 20px; padding: 1.25rem 1.4rem;
  border: 1px solid rgba(255,255,255,.9);
  box-shadow: 0 8px 26px rgba(80,20,120,.07); margin-bottom: 1.1rem;
}
.panel h4 { margin: 0 0 .75rem; font-size: 1rem; font-weight: 700; color: #1e1035; letter-spacing: -.01em; }
.panel .psub { font-size: .78rem; color: #8b7d9c; margin: -.4rem 0 .8rem; font-weight: 500; }
.panel-title { display:flex; align-items:center; justify-content:space-between; margin-bottom:.75rem; }
.panel-title h4 { margin: 0; font-size: 1rem; font-weight:700; color:#1e1035; letter-spacing:-.01em; }

/* ── Target table ── */
.tgt-table { width:100%; border-collapse:collapse; font-size:.85rem; }
.tgt-table th { padding:.55rem .8rem; text-align:left; color:#9b8aa6; font-weight:700; font-size:.7rem; text-transform:uppercase; letter-spacing:.06em; border-bottom:1px solid #f0e9f7; }
.tgt-table td { padding:.75rem .8rem; border-bottom:1px solid #f7f2fc; }
.tgt-table tr:last-child td { border-bottom:none; }
.cell-rr   { color:#7c3aed; font-weight:700; }
.cell-tgt  { color:#059669; font-weight:700; }
.cell-trail { color:#6b7280; font-size:.8rem; }

/* ── Rule cards ── */
.rule-group { margin-bottom:1rem; }
.rule-title { font-size:.75rem; font-weight:800; color:#7c3aed; text-transform:uppercase; letter-spacing:.06em; margin:0 0 .35rem; }
.rule-list { margin:0; padding-left:1.1rem; font-size:.84rem; color:#4b3f6b; line-height:1.65; }
.rule-list li { margin-bottom:.2rem; }
.rule-list span { color:#1e1035; font-weight:600; }
.rule-red { color: #dc2626; }

/* ── Quotes ── */
.quote-row { display:flex; gap:.6rem; align-items:flex-start; margin-bottom:.65rem; }
.quote-dot { width:7px; height:7px; border-radius:50%; background:linear-gradient(135deg,#ec4899,#a855f7); margin-top:.38rem; flex-shrink:0; }
.quote-text { font-size:.84rem; color:#4b3f6b; line-height:1.55; font-style:italic; }

/* ── Guardrail banner ── */
.guardrail {
  background: rgba(239,68,68,.08); border: 2px solid #ef4444;
  border-radius: 14px; padding: 1rem 1.2rem; text-align: center; margin-top: 1rem;
}
.guardrail h4 { color:#dc2626; margin:0 0 .3rem; font-size:.95rem; }
.guardrail p  { color:#7f1d1d; margin:0; font-size:.8rem; }

/* ── Alert banner ── */
.alert-item {
  background: #fff; border:1px solid #f0e9f7; border-radius:11px;
  padding:.7rem 1rem; margin-bottom:.5rem; font-size:.84rem; font-weight:600;
  display:flex; justify-content:space-between; align-items:center; color:#1e1035;
}
.tag-today {
  background:linear-gradient(135deg,#ec4899,#a855f7); color:#fff;
  padding:.25rem .6rem; border-radius:6px; font-size:.7rem; font-weight:700;
}

/* ── Streamlit widget overrides ── */
.stButton > button {
  border-radius: 13px; font-weight: 700; border: none; width: 100%;
  background: linear-gradient(135deg, #ec4899, #a855f7); color: #fff;
  padding: .62rem 1.2rem; letter-spacing: .01em;
  box-shadow: 0 6px 18px rgba(168,85,247,.32); transition: all .16s ease;
}
.stButton > button:hover { transform: translateY(-2px); color: #fff; box-shadow: 0 10px 24px rgba(168,85,247,.42); }
div[data-testid="stDataFrame"] { border-radius:14px; overflow:hidden; border:1px solid #efe6f6; box-shadow:0 3px 14px rgba(80,20,120,.05); }
div[data-baseweb="select"] > div, div[data-testid="stDateInput"] input { border-radius:11px !important; border-color:#eadff5 !important; }
</style>
""", unsafe_allow_html=True)

# ── Trading System Rules & Quotes ───────────────────────────────────────────
MINDSET_QUOTES = [
    "A missed trade is better than a forced trade.",
    "Don't let fear of missing out drive your decisions.",
    "Control your emotions, not the market.",
    "The market rewards patience, not activity.",
    "The best trades feel uncomfortable to take and comfortable to hold.",
    "Risk comes from not knowing what you're doing. — Warren Buffett",
    "Plan the trade and trade the plan. Never let emotions write your execution log.",
    "Cut your losses short and let your winners run — respect the 18pt guardrail.",
]

# ── Google Sheets ─────────────────────────────────────────────────────────────
@st.cache_resource(ttl=300)
def init_gspread():
    if not HAS_GSPREAD:
        return None
    try:
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"]),
                scopes=["https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"])
            return gspread.authorize(creds)
    except Exception:
        pass
    return None

def _ensure_local():
    if "db" not in st.session_state:
        st.session_state.db = {
            "Buy_Log": pd.DataFrame(columns=[
                "Date","Trade_ID","Instrument","Entry_Time","Exit_Time",
                "Entry_Price","Exit_Price","Points_SL","Points_Gained",
                "Lots","PnL","Result","Notes"]),
            "Sell_Log": pd.DataFrame(columns=[
                "Date","Trade_ID","Strategy","CE_Entry","CE_Exit",
                "PE_Entry","PE_Exit","SL_Percentage","Lots",
                "Total_PnL","Status","Notes"]),
            "Events": pd.DataFrame(columns=["Date","Time","Country","Event_Name","Impact_Level"]),
            "Results": pd.DataFrame(columns=["Date","Time","Company_Symbol","Market_Expectation"]),
        }

def get_data(tab):
    _ensure_local()
    client = init_gspread()
    sheet_id = st.secrets.get("sheet_id", "") if "sheet_id" in st.secrets else ""
    if client and sheet_id:
        try:
            ws = client.open_by_key(sheet_id).worksheet(tab)
            rec = ws.get_all_records()
            return pd.DataFrame(rec) if rec else pd.DataFrame()
        except Exception:
            pass
    return st.session_state.db.get(tab, pd.DataFrame())

def append_row(tab, row):
    _ensure_local()
    new = pd.DataFrame([row])
    st.session_state.db[tab] = pd.concat([st.session_state.db[tab], new], ignore_index=True)
    client = init_gspread()
    sheet_id = st.secrets.get("sheet_id", "") if "sheet_id" in st.secrets else ""
    if client and sheet_id:
        try:
            ws = client.open_by_key(sheet_id).worksheet(tab)
            ws.append_row(list(row.values()))
        except Exception as e:
            st.toast(f"Local save OK. Sheets sync failed: {e}", icon="⚠️")

def clear_tab(tab):
    _ensure_local()
    cols = st.session_state.db[tab].columns
    st.session_state.db[tab] = pd.DataFrame(columns=cols)
    client = init_gspread()
    sheet_id = st.secrets.get("sheet_id", "") if "sheet_id" in st.secrets else ""
    if client and sheet_id:
        try:
            ws = client.open_by_key(sheet_id).worksheet(tab)
            hdr = ws.row_values(1)
            ws.clear()
            if hdr:
                ws.append_row(hdr)
        except Exception:
            pass

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-dot"></span>Super App Nifty</div>'
        '<div class="brand-sub">Option Buying · Matrix System</div>',
        unsafe_allow_html=True)

    page = st.radio("nav", [
        "🏠  Home & Rules",
        "🟢  Option Buying",
        "🔴  Option Selling",
        "📅  Events & Earnings",
        "📊  Dashboard",
    ], label_visibility="collapsed")

    st.markdown('<div class="side-sep"></div><div class="side-lbl">System Constants</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-kv"><span>Lot size</span><b>65 qty</b></div>'
        '<div class="side-kv"><span>Max SL (buying)</span><b>18 pts</b></div>'
        '<div class="side-kv"><span>Selling SL rule</span><b>30 %</b></div>'
        '<div class="side-kv"><span>Entry window</span><b>09:30 – 14:45</b></div>'
        '<div class="side-kv"><span>Hard cut-off</span><b>14:45</b></div>'
        '<div class="side-kv"><span>Breakeven at</span><b>1:2 RR</b></div>',
        unsafe_allow_html=True)

    st.markdown('<div class="side-sep"></div>', unsafe_allow_html=True)
    today_str_ = datetime.date.today().strftime("%A, %d %b %Y")
    clock_str_ = datetime.datetime.now().strftime("%H:%M")
    st.markdown(
        f'<div class="side-kv"><span>Today</span><b>{today_str_}</b></div>'
        f'<div class="side-kv"><span>Time (IST)</span><b>{clock_str_}</b></div>',
        unsafe_allow_html=True)

# ── Common header ─────────────────────────────────────────────────────────────
PAGE_META = {
    "🏠  Home & Rules":     ("Home / Matrix Terminal", "Strict execution. No emotion."),
    "🟢  Option Buying":    ("Option Buying Module", "18-pt guardrail · 1:1 – 1:6 target grid"),
    "🔴  Option Selling":   ("Option Selling Module", "30% SL rule · Multi-leg journal"),
    "📅  Events & Earnings":("Events & Earnings Tracker", "Today's market catalysts"),
    "📊  Dashboard":        ("Performance Dashboard", "Cumulative PnL & trade history"),
}
title, subtitle = PAGE_META[page]

today = datetime.date.today()
today_iso = today.isoformat()

st.markdown(f"""
<div class="hdr">
  <div>
    <h1>{title}</h1>
    <div class="subtitle">{subtitle}</div>
  </div>
  <div>
    <span class="chip">
      <span class="dot dot-green"></span>
      {datetime.datetime.now().strftime("%H:%M")} &nbsp;·&nbsp; {today.strftime("%d %b %Y")}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — HOME & RULES
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠  Home & Rules":

    # Today's alerts
    df_ev = get_data("Events")
    df_re = get_data("Results")
    today_ev = df_ev[df_ev["Date"] == today_iso] if not df_ev.empty and "Date" in df_ev.columns else pd.DataFrame()
    today_re = df_re[df_re["Date"] == today_iso] if not df_re.empty and "Date" in df_re.columns else pd.DataFrame()

    if not today_ev.empty or not today_re.empty:
        st.markdown('<div class="panel"><div class="panel-title"><h4>🚨 Today\'s Market Catalysts</h4></div>', unsafe_allow_html=True)
        for _, r in today_ev.iterrows():
            st.markdown(f'<div class="alert-item"><span>📉 {r.get("Event_Name","Event")} &nbsp;·&nbsp; <span style="color:#9b8aa6">{r.get("Country","")}</span></span><span class="tag-today">TODAY</span></div>', unsafe_allow_html=True)
        for _, r in today_re.iterrows():
            st.markdown(f'<div class="alert-item"><span>📊 Earnings: <b>{r.get("Company_Symbol","")}</b> &nbsp;·&nbsp; <span style="color:#9b8aa6">{r.get("Time","")}</span></span><span class="tag-today">TODAY</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 1], gap="large")

    with col_left:
        # ── Quick Risk Calculator ──
        st.markdown('<div class="panel"><h4>⚡ Quick Risk Calculator</h4><div class="psub">Check before you enter — 18 pt guardrail enforced</div>', unsafe_allow_html=True)

        qc1, qc2, qc3 = st.columns(3)
        with qc1:
            h_entry = st.number_input("Entry Price", min_value=1.0, value=150.0, step=0.5, key="h_entry")
        with qc2:
            h_sl = st.number_input("Stop Loss", min_value=0.5, value=135.0, step=0.5, key="h_sl")
        with qc3:
            h_lots = st.number_input("Lots", min_value=1, value=1, key="h_lots")

        risk_pts = round(h_entry - h_sl, 2)
        qty = h_lots * 65

        if risk_pts <= 0:
            st.warning("⚠️ Stop loss must be below entry price.")
        elif risk_pts > 18:
            st.markdown(f"""
            <div class="guardrail">
              <h4>🚫 NO TRADE — Risk Exceeds 18 Points</h4>
              <p>Your risk is <b>{risk_pts} pts</b> · Max allowed is <b>18 pts</b>.<br>Adjust entry or widen stop.</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.success(f"✅ Risk approved: **{risk_pts} pts** | Max loss: ₹{risk_pts * qty:,.0f} ({h_lots} lot)")
            rows = []
            prev = h_entry
            for i in range(1, 7):
                tgt = round(h_entry + risk_pts * i, 2)
                trail = "Entry (breakeven)" if i == 1 else f"T{i-1} ({prev:.2f})"
                profit = round(risk_pts * i * qty, 2)
                rows.append((f"1:{i}", tgt, trail, f"₹{profit:,.0f}"))
                prev = tgt

            st.markdown('<table class="tgt-table"><thead><tr><th>RR</th><th>Target ₹</th><th>Trail SL to</th><th>Profit (est.)</th></tr></thead><tbody>', unsafe_allow_html=True)
            for rr, tgt, trail, prof in rows:
                st.markdown(f'<tr><td class="cell-rr">{rr}</td><td class="cell-tgt">{tgt}</td><td class="cell-trail">{trail}</td><td class="cell-tgt">{prof}</td></tr>', unsafe_allow_html=True)
            st.markdown('</tbody></table>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        # ── Matrix System Rules ──
        st.markdown("""
        <div class="panel">
          <h4>📋 The Matrix System</h4>
          <div class="psub">Non-negotiable trading rules</div>

          <div class="rule-group">
            <p class="rule-title">🕒 1. Time Window</p>
            <ul class="rule-list">
              <li>Start: <span>09:30 AM</span> — let morning volatility settle.</li>
              <li>Cut-off: <span>02:45 PM</span> — no new entries after this.</li>
            </ul>
          </div>

          <div class="rule-group">
            <p class="rule-title">🟢 2. Valid Entry (Green Light)</p>
            <ul class="rule-list">
              <li>Wait for price to pull back to the <span>VWMA / Supertrend baseline</span>.</li>
              <li>ADX MUST be <span>Increasing</span> or <span>Started Increasing</span>.<br>
                  <span style="color:#7c3aed;font-size:.8rem;">(92.5% Win Rate condition)</span></li>
            </ul>
          </div>

          <div class="rule-group">
            <p class="rule-title">🛑 3. No-Entry (Red Light)</p>
            <ul class="rule-list">
              <li>If ADX is Decreasing / Mixed → <span class="rule-red">Strict NO TRADE.</span></li>
              <li>Never chase vertical spikes or gap-ups.</li>
              <li>If required SL &gt; 18 points → <span class="rule-red">NO TRADE.</span></li>
            </ul>
          </div>

          <div class="rule-group">
            <p class="rule-title">🎯 4. Exit Rules</p>
            <ul class="rule-list">
              <li>Strictly <span>1 Lot</span>. Absolute max risk <span>18 pts</span>.</li>
              <li>At <span>1:2 RR (30+ pts)</span> → move SL to <span>Breakeven</span>.</li>
              <li>Never let a winner turn red after breakeven.</li>
            </ul>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Mindset ──
        st.markdown('<div class="panel"><h4>🧠 Mindset</h4>', unsafe_allow_html=True)
        for q in random.sample(MINDSET_QUOTES, min(4, len(MINDSET_QUOTES))):
            st.markdown(f'<div class="quote-row"><span class="quote-dot"></span><span class="quote-text">{q}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — OPTION BUYING
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🟢  Option Buying":

    col_l, col_r = st.columns([1.1, 1], gap="large")

    with col_l:
        # ── Calculator ──
        st.markdown('<div class="panel"><h4>📐 Risk & Target Calculator</h4><div class="psub">18-pt hard limit · Target grid 1:1 → 1:6</div>', unsafe_allow_html=True)

        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            b_entry = st.number_input("Entry Price ₹", min_value=1.0, value=150.0, step=0.5, key="b_entry")
            b_dir   = st.selectbox("Direction", ["BUY CE (Long)", "BUY PE (Short)"], key="b_dir")
        with bc2:
            b_sl    = st.number_input("Stop Loss ₹", min_value=0.5, value=135.0, step=0.5, key="b_sl")
        with bc3:
            b_lots  = st.number_input("Lots (65 qty)", min_value=1, value=1, key="b_lots")

        risk = round(b_entry - b_sl, 2)
        qty  = b_lots * 65

        if risk <= 0:
            st.warning("⚠️ Stop loss must be below entry price.")
        elif risk > 18:
            st.markdown(f"""
            <div class="guardrail">
              <h4>🚫 GUARDRAIL TRIGGERED — {risk} pts RISK</h4>
              <p>Maximum allowed is <b>18 points</b>. Do not execute this trade.</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.success(f"✅ **{risk} pts risk** approved &nbsp;|&nbsp; Max loss ₹{risk*qty:,.0f}")
            prev = b_entry
            st.markdown('<table class="tgt-table"><thead><tr><th>RR</th><th>Target ₹</th><th>Trail SL to</th><th>Profit est.</th></tr></thead><tbody>', unsafe_allow_html=True)
            for i in range(1, 7):
                tgt  = round(b_entry + risk * i, 2)
                trail = "Entry (BE)" if i == 1 else f"T{i-1} ({prev:.2f})"
                prof  = round(risk * i * qty, 2)
                prev  = tgt
                rr_color = "#7c3aed"
                st.markdown(f'<tr><td class="cell-rr">1:{i}</td><td class="cell-tgt">{tgt}</td><td class="cell-trail">{trail}</td><td class="cell-tgt">₹{prof:,.0f}</td></tr>', unsafe_allow_html=True)
            st.markdown('</tbody></table></div>', unsafe_allow_html=True)

    with col_r:
        # ── Journal Form ──
        st.markdown('<div class="panel"><h4>📝 Log Buying Trade</h4><div class="psub">Notes are MANDATORY if trade ends in loss</div>', unsafe_allow_html=True)

        with st.form("buy_form", clear_on_submit=True):
            jc1, jc2 = st.columns(2)
            with jc1:
                j_date  = st.date_input("Date", today)
                j_instr = st.text_input("Strike / Instrument", "NIFTY 24500 CE")
                j_entry_t = st.time_input("Entry Time", datetime.time(9, 30))
                j_exit_t  = st.time_input("Exit Time",  datetime.time(10, 0))
            with jc2:
                j_entry_p = st.number_input("Entry Price ₹", min_value=0.1, value=150.0, step=0.5)
                j_exit_p  = st.number_input("Exit Price ₹",  min_value=0.1, value=165.0, step=0.5)
                j_sl_pts  = st.number_input("SL Points Used", min_value=0.1, max_value=18.0, value=15.0)
                j_lots    = st.number_input("Lots Executed",  min_value=1, value=1)

            auto_pnl = round((j_exit_p - j_entry_p) * j_lots * 65, 2)
            result_label = "Profit" if auto_pnl > 0 else ("Loss" if auto_pnl < 0 else "Breakeven")

            note_label = "What went wrong? *(MANDATORY for loss)*" if auto_pnl < 0 else "Psychology Notes"
            j_notes = st.text_area(note_label, placeholder="Describe setup, emotion, execution quality...", height=90)

            submitted = st.form_submit_button("💾  Save Trade to Database", use_container_width=True)
            if submitted:
                if auto_pnl < 0 and not j_notes.strip():
                    st.error("🚫 Submission blocked: Trade is a LOSS — notes are mandatory!")
                else:
                    tid = f"BUY-{random.randint(1000,9999)}"
                    append_row("Buy_Log", {
                        "Date": str(j_date), "Trade_ID": tid,
                        "Instrument": j_instr,
                        "Entry_Time": str(j_entry_t), "Exit_Time": str(j_exit_t),
                        "Entry_Price": j_entry_p, "Exit_Price": j_exit_p,
                        "Points_SL": j_sl_pts,
                        "Points_Gained": round(j_exit_p - j_entry_p, 2),
                        "Lots": j_lots, "PnL": auto_pnl,
                        "Result": result_label, "Notes": j_notes,
                    })
                    st.success(f"✅ Trade {tid} saved! PnL: ₹{auto_pnl:,.2f}")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Trade History ──
    st.markdown('<div class="panel"><h4>📊 Buying Trade History</h4>', unsafe_allow_html=True)
    df_buy = get_data("Buy_Log")
    if not df_buy.empty:
        st.dataframe(df_buy, use_container_width=True, hide_index=True)
    else:
        st.info("No buying trades logged yet.")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — OPTION SELLING
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔴  Option Selling":

    col_l, col_r = st.columns([1.1, 1], gap="large")

    with col_l:
        st.markdown('<div class="panel"><h4>📐 Stop Loss Calculator  —  30% Rule</h4><div class="psub">Exact SL trigger price for short premium</div>', unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            s_entry = st.number_input("Entry Premium ₹", min_value=1.0, value=100.0, step=0.5, key="s_entry")
        with sc2:
            s_pct   = st.number_input("SL %", min_value=1.0, max_value=200.0, value=30.0, step=1.0)
        with sc3:
            s_lots  = st.number_input("Lots (65 qty)", min_value=1, value=1, key="s_lots")

        sl_price  = round(s_entry * (1 + s_pct / 100), 2)
        sl_pts    = round(sl_price - s_entry, 2)
        max_loss  = round(sl_pts * s_lots * 65, 2)

        st.markdown(f"""
        <div class="kpi-grid" style="margin-top:.8rem;">
          <div class="kpi g1"><div class="lbl">SL Trigger Price</div><div class="val">₹{sl_price}</div><div class="fin">at {s_pct}% above entry</div></div>
          <div class="kpi g4"><div class="lbl">Risk in Points</div><div class="val">{sl_pts} pts</div><div class="fin">per lot</div></div>
          <div class="kpi g2"><div class="lbl">Max Loss</div><div class="val">₹{max_loss:,.0f}</div><div class="fin">{s_lots} lot × 65 qty</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="panel"><h4>📝 Log Selling Trade</h4><div class="psub">Multi-leg (CE + PE) · Notes mandatory on loss</div>', unsafe_allow_html=True)

        with st.form("sell_form", clear_on_submit=True):
            s_strategy = st.selectbox("Strategy", ["Short Straddle","Short Strangle","Naked CE Sell","Naked PE Sell"])
            s_date = st.date_input("Date", today, key="s_date")
            s_lots_j = st.number_input("Lots Executed", min_value=1, value=1, key="s_lots_j")

            ce_c, pe_c = st.columns(2)
            with ce_c:
                st.markdown("**CE Leg**")
                ce_entry = st.number_input("CE Entry ₹", min_value=0.0, value=100.0, step=0.5)
                ce_exit  = st.number_input("CE Exit ₹",  min_value=0.0, value=70.0,  step=0.5)
            with pe_c:
                st.markdown("**PE Leg**")
                pe_entry = st.number_input("PE Entry ₹", min_value=0.0, value=100.0, step=0.5)
                pe_exit  = st.number_input("PE Exit ₹",  min_value=0.0, value=120.0, step=0.5)

            s_status = st.selectbox("Exit Status", ["Target Achieved","SL Hit","Squared off at Close"])
            sell_pnl = round(((ce_entry - ce_exit) + (pe_entry - pe_exit)) * s_lots_j * 65, 2)

            s_note_lbl = "What went wrong? *(MANDATORY for loss)*" if sell_pnl < 0 else "Trade Notes"
            s_notes = st.text_area(s_note_lbl, placeholder="IV, delta, adjustment rationale...", height=80)

            if st.form_submit_button("💾  Save Selling Trade", use_container_width=True):
                if sell_pnl < 0 and not s_notes.strip():
                    st.error("🚫 Notes are mandatory for a losing trade!")
                else:
                    tid = f"SELL-{random.randint(1000,9999)}"
                    append_row("Sell_Log", {
                        "Date": str(s_date), "Trade_ID": tid,
                        "Strategy": s_strategy,
                        "CE_Entry": ce_entry, "CE_Exit": ce_exit,
                        "PE_Entry": pe_entry, "PE_Exit": pe_exit,
                        "SL_Percentage": s_pct,
                        "Lots": s_lots_j, "Total_PnL": sell_pnl,
                        "Status": s_status, "Notes": s_notes,
                    })
                    st.success(f"✅ {tid} saved! PnL: ₹{sell_pnl:,.2f}")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><h4>📊 Selling Trade History</h4>', unsafe_allow_html=True)
    df_sell = get_data("Sell_Log")
    if not df_sell.empty:
        st.dataframe(df_sell, use_container_width=True, hide_index=True)
    else:
        st.info("No selling trades logged yet.")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — EVENTS & EARNINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📅  Events & Earnings":

    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown('<div class="panel"><h4>🌐 Add Economic Event</h4>', unsafe_allow_html=True)
        with st.form("ev_form", clear_on_submit=True):
            e_date    = st.date_input("Date", today, key="e_d")
            e_time    = st.time_input("Time", datetime.time(17, 30))
            e_country = st.selectbox("Country", ["INDIA","US","EU","UK","CHINA","JAPAN"])
            e_name    = st.text_input("Event Name", placeholder="RBI Rate Decision / US CPI")
            e_impact  = st.selectbox("Impact", ["HIGH","MEDIUM","LOW"])
            if st.form_submit_button("➕  Add Event", use_container_width=True):
                append_row("Events", {"Date": str(e_date), "Time": str(e_time),
                                      "Country": e_country, "Event_Name": e_name,
                                      "Impact_Level": e_impact})
                st.success("Event added!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4>📋 All Scheduled Events</h4>', unsafe_allow_html=True)
        df_ev2 = get_data("Events")
        if not df_ev2.empty:
            st.dataframe(df_ev2, use_container_width=True, hide_index=True)
        else:
            st.info("No events logged yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="panel"><h4>📊 Add Corporate Earnings</h4>', unsafe_allow_html=True)
        with st.form("re_form", clear_on_submit=True):
            r_date   = st.date_input("Date", today, key="r_d")
            r_time   = st.selectbox("Timing", ["Before Market Open","During Market Hours","After Market Close"])
            r_symbol = st.text_input("Company Symbol", placeholder="RELIANCE / TCS / INFY")
            r_exp    = st.text_input("Market Expectation", placeholder="PAT +12% YoY, margin expansion")
            if st.form_submit_button("➕  Add Result", use_container_width=True):
                append_row("Results", {"Date": str(r_date), "Time": r_time,
                                       "Company_Symbol": r_symbol,
                                       "Market_Expectation": r_exp})
                st.success("Result added!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4>📋 All Corporate Earnings</h4>', unsafe_allow_html=True)
        df_re2 = get_data("Results")
        if not df_re2.empty:
            st.dataframe(df_re2, use_container_width=True, hide_index=True)
        else:
            st.info("No earnings logged yet.")
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊  Dashboard":

    df_buy  = get_data("Buy_Log")
    df_sell = get_data("Sell_Log")

    pnl_buy  = pd.to_numeric(df_buy["PnL"],       errors="coerce").sum() if not df_buy.empty  and "PnL"       in df_buy.columns  else 0.0
    pnl_sell = pd.to_numeric(df_sell["Total_PnL"], errors="coerce").sum() if not df_sell.empty and "Total_PnL" in df_sell.columns else 0.0
    total_pnl = pnl_buy + pnl_sell

    n_buy  = len(df_buy)  if not df_buy.empty  else 0
    n_sell = len(df_sell) if not df_sell.empty else 0

    wins_b = len(df_buy [pd.to_numeric(df_buy ["PnL"],       errors="coerce") > 0]) if n_buy  else 0
    wins_s = len(df_sell[pd.to_numeric(df_sell["Total_PnL"], errors="coerce") > 0]) if n_sell else 0
    total_t = n_buy + n_sell
    win_rate = (wins_b + wins_s) / total_t * 100 if total_t else 0.0

    pnl_grad = "g5" if total_pnl >= 0 else "g1"

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi {pnl_grad}">
        <div class="lbl">Total PnL</div>
        <div class="val">₹{total_pnl:+,.0f}</div>
        <div class="fin">Buying + Selling combined</div>
      </div>
      <div class="kpi g2">
        <div class="lbl">Buying PnL</div>
        <div class="val">₹{pnl_buy:+,.0f}</div>
        <div class="fin">{n_buy} trades logged</div>
      </div>
      <div class="kpi g3">
        <div class="lbl">Selling PnL</div>
        <div class="val">₹{pnl_sell:+,.0f}</div>
        <div class="fin">{n_sell} trades logged</div>
      </div>
      <div class="kpi g4">
        <div class="lbl">Win Rate</div>
        <div class="val">{win_rate:.1f}%</div>
        <div class="fin">{wins_b + wins_s} wins / {total_t} trades</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Export & Reset ──
    d_col1, d_col2 = st.columns(2, gap="large")

    with d_col1:
        st.markdown('<div class="panel"><h4>📥 Export Journal</h4>', unsafe_allow_html=True)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            (df_buy  if not df_buy.empty  else pd.DataFrame()).to_excel(writer, sheet_name="Buy_Log",  index=False)
            (df_sell if not df_sell.empty else pd.DataFrame()).to_excel(writer, sheet_name="Sell_Log", index=False)
        st.download_button(
            "📦  Download Full Journal (Excel)",
            data=buf.getvalue(),
            file_name=f"SuperAppNifty_{today_iso}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with d_col2:
        st.markdown('<div class="panel"><h4>⚠️ Reset Database</h4><div class="psub">Use at the start of a new month or quarter</div>', unsafe_allow_html=True)
        with st.popover("🗑  Clear All Trade Records"):
            st.error("This will permanently delete all Buy_Log and Sell_Log records.")
            chk = st.checkbox("I understand — wipe everything")
            if st.button("Confirm Reset", disabled=not chk, use_container_width=True):
                clear_tab("Buy_Log")
                clear_tab("Sell_Log")
                st.success("Database cleared.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Full trade tables ──
    st.markdown('<div class="panel"><h4>📋 All Buying Trades</h4>', unsafe_allow_html=True)
    if not df_buy.empty:
        st.dataframe(df_buy, use_container_width=True, hide_index=True)
    else:
        st.info("No buying trades logged yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><h4>📋 All Selling Trades</h4>', unsafe_allow_html=True)
    if not df_sell.empty:
        st.dataframe(df_sell, use_container_width=True, hide_index=True)
    else:
        st.info("No selling trades logged yet.")
    st.markdown('</div>', unsafe_allow_html=True)
