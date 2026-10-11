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

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Super App Nifty",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling: Straddle Desk UI & Plus Jakarta Sans ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.stApp { background:
   radial-gradient(1100px 500px at 12% -8%, #ffe9f4 0%, transparent 60%),
   radial-gradient(900px 460px at 92% 4%, #e9edff 0%, transparent 58%),
   #f7f5fb; }
html, body, [class*="css"], .stMarkdown, p, div, span, label, input, button {
   font-family: 'Plus Jakarta Sans', sans-serif !important;
}
#MainMenu, footer { visibility:hidden; }
header[data-testid="stHeader"] { background:transparent; height:0; }

[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[kind="header"] { display:none !important; }

section[data-testid="stSidebar"] {
  visibility:visible !important;
  transform:none !important;
  margin-left:0 !important;
  min-width:290px !important;
  width:290px !important;
  background:linear-gradient(180deg,#1c1030 0%,#2a1246 55%,#33144f 100%) !important;
  border-right:none !important;
}
section[data-testid="stSidebar"] * { color:#ede7f6 !important; }
section[data-testid="stSidebar"] .block-container { padding-top:1.6rem; }

.brand { font-size:1.12rem; font-weight:800; letter-spacing:-.02em; color:#fff;
  display:flex; align-items:center; gap:.5rem; margin:0 0 .25rem 0; }
.brand-dot { width:9px; height:9px; border-radius:50%;
  background:linear-gradient(135deg,#f472b6,#a78bfa);
  box-shadow:0 0 12px rgba(244,114,182,.85); }
.brand-sub { font-size:.72rem; color:#b9a8d4; margin-bottom:1.5rem;
  letter-spacing:.04em; text-transform:uppercase; font-weight:600; }

/* Sidebar Nav Radio */
section[data-testid="stSidebar"] div[role="radiogroup"] { gap:.3rem; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
  background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.06);
  border-radius:11px; padding:.6rem .85rem; width:100%; cursor:pointer;
  transition:all .16s ease; font-weight:600; font-size:.9rem;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
  background:rgba(255,255,255,.11); transform:translateX(2px);
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display:none; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
  background:linear-gradient(135deg,#ec4899,#a855f7) !important;
  border-color:transparent !important; color:#ffffff !important; font-weight:700 !important;
  box-shadow:0 6px 18px rgba(168,85,247,.35);
}

.side-sep { height:1.1px; background:rgba(255,255,255,.09); margin:1.3rem 0 1rem; }
.side-lbl { font-size:.66rem; text-transform:uppercase; letter-spacing:.09em;
  color:#a692c4; font-weight:700; margin-bottom:.5rem; }
.side-kv { display:flex; justify-content:space-between; font-size:.76rem;
  padding:.3rem 0; color:#cfc2e4; }
.side-kv b { color:#fff; font-weight:600; }

.block-container { padding:1rem 2rem 3rem; max-width:1480px; }

/* Header */
.hdr { display:flex; align-items:flex-end; justify-content:space-between;
  margin:.2rem 0 1.4rem; flex-wrap:wrap; gap:.8rem; }
.hdr h1 { font-size:1.85rem; font-weight:800; letter-spacing:-.03em; margin:0;
  background:linear-gradient(120deg,#1e1035 20%,#7c3aed 60%,#ec4899 95%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.chip { display:inline-flex; align-items:center; gap:.4rem; padding:.42rem .85rem;
  border-radius:99px; font-size:.76rem; font-weight:700; background:#fff;
  border:1px solid #ece3f5; box-shadow:0 2px 8px rgba(80,20,120,.06); color:#3f2c56; }
.chip .dot { width:7px; height:7px; border-radius:50%; background:#22c55e; box-shadow:0 0 9px #22c55e; }

/* Panels */
.panel { background:rgba(255,255,255,.82); backdrop-filter:blur(6px);
  border-radius:20px; padding:1.25rem 1.4rem; border:1px solid rgba(255,255,255,.9);
  box-shadow:0 8px 26px rgba(80,20,120,.07); margin-bottom:1.1rem; }
.panel h4 { margin:0; font-size:1.02rem; font-weight:700; color:#1e1035; letter-spacing:-.01em; }
.panel .sub { font-size:.79rem; color:#8b7d9c; margin-top:.2rem; font-weight:500; }

/* KPI Grid */
.kpi-grid { display:grid; gap:.85rem; margin-bottom:1.1rem;
  grid-template-columns:repeat(auto-fit, minmax(190px, 1fr)); }
.kpi { border-radius:18px; padding:1.05rem 1.15rem; color:#fff; position:relative;
  overflow:hidden; box-shadow:0 8px 22px rgba(90,25,120,.20);
  transition:transform .18s ease; min-width:0; }
.kpi:hover { transform:translateY(-3px); }
.kpi:after { content:""; position:absolute; right:-30px; top:-30px; width:88px;
  height:88px; border-radius:50%; background:rgba(255,255,255,.12); }
.kpi .lbl { font-size:.66rem; text-transform:uppercase; letter-spacing:.06em;
  font-weight:700; opacity:.92; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.kpi .val { font-size:clamp(1.25rem, 2.1vw, 1.8rem); font-weight:800;
  letter-spacing:-.03em; line-height:1.2; margin-top:.3rem;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.kpi .fin { font-size:.68rem; opacity:.88; margin-top:.2rem; font-weight:500; white-space:nowrap; }

.g1 { background:linear-gradient(135deg,#f43f5e,#ec4899 55%,#d946ef); }
.g2 { background:linear-gradient(135deg,#8b5cf6,#6366f1 60%,#4f46e5); }
.g3 { background:linear-gradient(135deg,#06b6d4,#0ea5e9 60%,#3b82f6); }
.g4 { background:linear-gradient(135deg,#f59e0b,#f97316 60%,#ef4444); }
.g5 { background:linear-gradient(135deg,#10b981,#059669 60%,#047857); }
.gneg { background:linear-gradient(135deg,#475569,#64748b); }
.gmute { background:linear-gradient(135deg,#e6e0ee,#efeaf6); color:#7c6f8c; box-shadow:none; border:1px dashed #ddd2ea; }
.gmute .val { color:#a99bbd; }

/* Stat Tile */
.stat { background:#fff; border-radius:16px; padding:.95rem 1.1rem;
  border:1px solid #f0e9f7; box-shadow:0 2px 10px rgba(80,20,120,.045); margin-bottom:.8rem; }
.stat .lbl { font-size:.68rem; color:#9b8aa6; text-transform:uppercase; letter-spacing:.08em; font-weight:700; }
.stat .val { font-size:1.32rem; font-weight:800; color:#1e1035; letter-spacing:-.02em; margin-top:.15rem; }

/* Catalyst Cards */
.cat-high { background:linear-gradient(135deg,#fff1f2,#ffe4e6); border-left:4px solid #f43f5e; padding:12px; border-radius:12px; margin-bottom:8px; }
.cat-med  { background:linear-gradient(135deg,#fffbeb,#fef3c7); border-left:4px solid #f59e0b; padding:12px; border-radius:12px; margin-bottom:8px; }
.cat-low  { background:linear-gradient(135deg,#f0fdf4,#dcfce7); border-left:4px solid #10b981; padding:12px; border-radius:12px; margin-bottom:8px; }
.cat-earn { background:linear-gradient(135deg,#f5f3ff,#ede9fe); border-left:4px solid #8b5cf6; padding:12px; border-radius:12px; margin-bottom:8px; }

/* Tables & Custom buttons */
.stButton>button { border-radius:13px; font-weight:700; border:none; width:100%;
  background:linear-gradient(135deg,#ec4899,#a855f7); color:#fff;
  padding:.62rem 1.2rem; letter-spacing:.01em;
  box-shadow:0 6px 18px rgba(168,85,247,.32); transition:all .16s ease; }
.stButton>button:hover { transform:translateY(-2px); color:#fff;
  box-shadow:0 10px 24px rgba(168,85,247,.42); }
div[data-testid="stDataFrame"] { border-radius:14px; overflow:hidden;
  border:1px solid #efe6f6; box-shadow:0 3px 14px rgba(80,20,120,.05); }
div[data-baseweb="select"]>div, div[data-testid="stDateInput"] input {
  border-radius:11px !important; border-color:#eadff5 !important; }
.stProgress > div > div > div { background:linear-gradient(90deg,#ec4899,#a855f7); }

.banner-danger { background:#fff1f2; border:1px solid #fecdd3; border-radius:14px; padding:1rem; color:#9f1239; margin-bottom:1rem; }
.banner-success { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:14px; padding:1rem; color:#166534; font-weight:700; margin-bottom:1rem; }

.data-table-custom { width:100%; border-collapse:collapse; margin-top:.8rem; font-size:.88rem; }
.data-table-custom th { background:#f3edf9; color:#3f2c56; font-weight:700; padding:.6rem .8rem; text-align:left; border-bottom:1px solid #e2d2f0; }
.data-table-custom td { padding:.55rem .8rem; border-bottom:1px solid #f2ecf8; color:#2d1b42; }
.td-highlight { font-weight:700; color:#7c3aed; }
.td-success { font-weight:700; color:#059669; }

.quote-item { display:flex; align-items:flex-start; gap:.6rem; padding:.5rem 0; border-bottom:1px solid #f2ecf8; font-size:.88rem; color:#3f2c56; }
.quote-bullet { width:6px; height:6px; border-radius:50%; background:#a855f7; margin-top:.45rem; flex-shrink:0; }
</style>
""", unsafe_allow_html=True)

# ── Data Storage Layer (Google Sheets Two-Way Sync) ─────────────────────────
def init_gspread():
    if not HAS_GSPREAD:
        return None
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            return gspread.authorize(creds)
    except Exception:
        pass
    return None

def _ensure_local():
    if "db" not in st.session_state:
        st.session_state.db = {
            "Buy_Log": pd.DataFrame(columns=[
                "Date", "Trade_ID", "Instrument", "Entry_Time", "Exit_Time",
                "Entry_Price", "Exit_Price", "Points_SL", "Points_Gained", "Lots", "PnL", "Result", "Notes"
            ]),
            "Sell_Log": pd.DataFrame(columns=[
                "Date", "Trade_ID", "Strategy", "CE_Entry", "CE_Exit", "PE_Entry", "PE_Exit",
                "SL_Percentage", "Lots", "Total_PnL", "Status", "Notes"
            ]),
            "Events": pd.DataFrame(columns=["Date", "Time", "Country", "Event_Name", "Impact_Level"]),
            "Results": pd.DataFrame(columns=["Date", "Time", "Company_Symbol", "Market_Expectation"])
        }

def get_data(tab):
    _ensure_local()
    client = init_gspread()
    sheet_id = st.secrets.get("sheet_id", "") if "sheet_id" in st.secrets else ""
    if client and sheet_id:
        try:
            ws = client.open_by_key(sheet_id).worksheet(tab)
            rec = ws.get_all_records()
            if rec:
                df_remote = pd.DataFrame(rec)
                st.session_state.db[tab] = df_remote
                return df_remote
        except Exception:
            pass
    return st.session_state.db.get(tab, pd.DataFrame())

def append_row(tab, row):
    _ensure_local()
    client = init_gspread()
    sheet_id = st.secrets.get("sheet_id", "") if "sheet_id" in st.secrets else ""
    if client and sheet_id:
        try:
            ws = client.open_by_key(sheet_id).worksheet(tab)
            ws.append_row(list(row.values()))
        except Exception as e:
            st.toast(f"Sheets sync warning: {e}")
    # Local update
    df = st.session_state.db[tab]
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    st.session_state.db[tab] = df
    get_data(tab)

def clear_tab(tab):
    _ensure_local()
    client = init_gspread()
    sheet_id = st.secrets.get("sheet_id", "") if "sheet_id" in st.secrets else ""
    if client and sheet_id:
        try:
            ws = client.open_by_key(sheet_id).worksheet(tab)
            ws.clear()
            hdr = list(st.session_state.db[tab].columns)
            if hdr:
                ws.append_row(hdr)
        except Exception:
            pass
    st.session_state.db[tab] = st.session_state.db[tab].iloc[0:0]

# ── Sidebar Navigation ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-dot"></span>Super App Nifty</div>'
                '<div class="brand-sub">Matrix Trading Terminal</div>', unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "Home & Rules",
        "Option Buying",
        "Option Selling",
        "Events & Earnings",
        "Dashboard",
    ], label_visibility="collapsed")

    st.markdown('<div class="side-sep"></div><div class="side-lbl">System Specs</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-kv"><span>Lot Size</span><b>65 Qty</b></div>'
        '<div class="side-kv"><span>Max Risk (Buy)</span><b>18 Points</b></div>'
        '<div class="side-kv"><span>SL Rule (Sell)</span><b>30 %</b></div>'
        '<div class="side-kv"><span>Time Window</span><b>09:30 - 14:45</b></div>'
        '<div class="side-kv"><span>Breakeven At</span><b>1:2 RR</b></div>',
        unsafe_allow_html=True)

    st.markdown('<div class="side-sep"></div>', unsafe_allow_html=True)
    today_date = datetime.date.today()
    now_formatted = datetime.datetime.now().strftime("%H:%M")
    st.markdown(
        f'<div class="side-kv"><span>Date</span><b>{today_date.strftime("%d %b %Y")}</b></div>'
        f'<div class="side-kv"><span>Time</span><b>{now_formatted} IST</b></div>',
        unsafe_allow_html=True)

# ── Main Header ────────────────────────────────────────────────────────────
PAGE_TITLES = {
    "Home & Rules":     ("Home / Matrix Terminal", "Execution parameters and market rules"),
    "Option Buying":    ("Option Buying Module", "18-Point Risk Guardrail and Target Engine"),
    "Option Selling":   ("Option Selling Module", "30% SL Rule and Multi-Leg Strategy Journal"),
    "Events & Earnings":("Events & Earnings Tracker", "Scheduled market catalysts"),
    "Dashboard":        ("Performance Dashboard", "Trade metrics and ledger management"),
}
title_text, subtitle_text = PAGE_TITLES[page]
today_iso = today_date.isoformat()

st.markdown(f"""
<div class="hdr">
  <div>
    <h1>{title_text}</h1>
    <div style="font-size:.85rem; color:#7c6f8c; margin-top:.15rem; font-weight:500;">{subtitle_text}</div>
  </div>
  <div>
    <span class="chip">
      <span class="dot"></span>
      {now_formatted} IST &nbsp;·&nbsp; {today_date.strftime("%d %b %Y")}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1: HOME & RULES
# ═══════════════════════════════════════════════════════════════════════════
if page == "Home & Rules":

    df_ev = get_data("Events")
    df_re = get_data("Results")

    col_l, col_r = st.columns([1.2, 1], gap="large")

    with col_l:
        st.markdown('<div class="panel"><h4>Market Catalysts Today</h4><div class="sub">High-impact economic events and corporate earnings</div></div>', unsafe_allow_html=True)

        if not df_ev.empty or not df_re.empty:
            if not df_ev.empty:
                st.markdown("**Economic Events:**")
                for _, row in df_ev.iterrows():
                    imp = str(row.get("Impact_Level", "MEDIUM")).upper()
                    cls = "cat-high" if imp == "HIGH" else ("cat-med" if imp == "MEDIUM" else "cat-low")
                    st.markdown(f"""
                    <div class="{cls}">
                      <b>{row.get('Event_Name','')}</b> ({row.get('Country','')})<br>
                      <span style="font-size:0.78rem; opacity:0.8;">Date: {row.get('Date','')} · Time: {row.get('Time','')} · Impact: {imp}</span>
                    </div>""", unsafe_allow_html=True)

            if not df_re.empty:
                st.markdown("**Corporate Results:**")
                for _, row in df_re.iterrows():
                    st.markdown(f"""
                    <div class="cat-earn">
                      <b>{row.get('Company_Symbol','')} Results</b><br>
                      <span style="font-size:0.78rem; opacity:0.8;">Date: {row.get('Date','')} · Timing: {row.get('Time','')} · Expectation: {row.get('Market_Expectation','')}</span>
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="panel">
              <div class="empty">
                <div class="ico">◇</div>
                <div class="t">No Catalysts Logged for Today</div>
                <div class="s">Add upcoming economic events or earnings in the Events & Earnings tab.</div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4>Matrix System Core Rules</h4><div class="sub">Mandatory risk guardrails for professional trading discipline</div></div>', unsafe_allow_html=True)
        rules = [
            ("18-Point Option Buying Risk Guardrail", "Maximum allowed risk per trade is strictly capped at 18 points. Any trade setup exceeding 18 points is automatically blocked."),
            ("30% Option Selling Stop Loss Rule", "For option writing, stop loss is pinned at exactly 30% above entry premium. Breaches trigger immediate exit."),
            ("Mandatory Post-Mortem Loss Notes", "If any trade closes in a negative PnL, detailed notes explaining what went wrong are strictly mandatory before submission."),
            ("Target & Trailing SL Ladder", "1:1 to 1:6 target progression with breakeven trail on T1 achievement to protect accumulated capital.")
        ]
        for title, desc in rules:
            st.markdown(f"""
            <div class="stat">
              <div class="lbl">{title}</div>
              <div style="font-size:0.88rem; color:#3f2c56; margin-top:0.3rem; font-weight:500;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="panel"><h4>Terminal Performance Metrics</h4><div class="sub">Real-time ledger overview</div></div>', unsafe_allow_html=True)

        df_buy_m = get_data("Buy_Log")
        df_sell_m = get_data("Sell_Log")
        pnl_b = pd.to_numeric(df_buy_m["PnL"], errors="coerce").sum() if not df_buy_m.empty and "PnL" in df_buy_m.columns else 0.0
        pnl_s = pd.to_numeric(df_sell_m["Total_PnL"], errors="coerce").sum() if not df_sell_m.empty and "Total_PnL" in df_sell_m.columns else 0.0
        total_pnl_m = pnl_b + pnl_s

        st.markdown(f"""
        <div class="kpi-grid">
          <div class="kpi {'g1' if total_pnl_m < 0 else 'g5'}">
            <div class="lbl">Combined Net PnL</div>
            <div class="val">INR {total_pnl_m:+,.2f}</div>
            <div class="fin">Live session aggregate</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stat">
          <div class="lbl">Total Trades Logged</div>
          <div class="val">{len(df_buy_m) + len(df_sell_m)} Executions</div>
        </div>
        <div class="stat">
          <div class="lbl">Google Sheets Status</div>
          <div class="val" style="color: #059669; font-size:1.1rem; font-weight:700;">{"Connected & Synchronized" if HAS_GSPREAD and st.secrets.get("sheet_id") else "Local Memory Active"}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4>Trading Mindset</h4><div class="sub">Discipline framework</div></div>', unsafe_allow_html=True)
        quotes = [
            "A missed trade is better than a forced trade.",
            "Don't let fear of missing out drive your decisions.",
            "Control your emotions, not the market.",
            "Plan the trade and trade the plan. Never let emotions write your execution log.",
            "Cut your losses short and let your winners run — respect the 18pt guardrail."
        ]
        for q in quotes:
            st.markdown(f'<div class="quote-item"><div class="quote-bullet"></div><div class="quote-txt">{q}</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2: OPTION BUYING
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Option Buying":

    col_l, col_r = st.columns([1.1, 1], gap="large")

    with col_l:
        st.markdown('<div class="panel"><h4>Risk & Target Calculator</h4><div class="sub">Enforces 18-point maximum risk rule</div></div>', unsafe_allow_html=True)

        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            b_entry = st.number_input("Entry Price (INR)", min_value=0.0, value=0.0, step=0.5, key="b_entry")
            b_dir   = st.selectbox("Direction", ["BUY CE (Long)", "BUY PE (Short)"], key="b_dir")
        with bc2:
            b_sl    = st.number_input("Stop Loss (INR)", min_value=0.0, value=0.0, step=0.5, key="b_sl")
        with bc3:
            b_lots  = st.number_input("Lots (65 Qty)", min_value=1, value=1, key="b_lots")

        risk = round(b_entry - b_sl, 2)
        qty  = b_lots * 65

        if b_entry == 0.0 or b_sl == 0.0:
            st.info("Enter Entry Price and Stop Loss above to calculate target grid and risk parameters.")
        elif risk <= 0:
            st.warning("Stop loss must be lower than entry price.")
        elif risk > 18.0:
            st.markdown(f"""
            <div class="banner-danger">
              <h4>GUARDRAIL VIOLATED — {risk} POINTS RISK</h4>
              <p>Maximum allowed risk is 18.0 points. Position rejected.</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="banner-success">Risk Approved: {risk} Points &nbsp;·&nbsp; Total Risk: INR {risk*qty:,.2f}</div>', unsafe_allow_html=True)
            prev = b_entry
            rows_h = ""
            for i in range(1, 7):
                tgt  = round(b_entry + risk * i, 2)
                trail = "Entry (Breakeven)" if i == 1 else f"T{i-1} ({prev:.2f})"
                prof  = round(risk * i * qty, 2)
                prev  = tgt
                rows_h += f'<tr><td class="td-highlight">1:{i}</td><td class="td-success">{tgt:.2f}</td><td>{trail}</td><td class="td-success">INR {prof:,.2f}</td></tr>'

            st.markdown(f"""
            <table class="data-table-custom">
              <thead><tr><th>Risk:Reward</th><th>Target Price</th><th>Trail SL To</th><th>Profit Projection</th></tr></thead>
              <tbody>{rows_h}</tbody>
            </table>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="panel"><h4>Log Buying Trade</h4><div class="sub">Notes are mandatory for trades ending in loss</div></div>', unsafe_allow_html=True)

        with st.form("buy_form", clear_on_submit=True):
            jc1, jc2 = st.columns(2)
            with jc1:
                j_date  = st.date_input("Date", today_date)
                j_instr = st.text_input("Strike / Instrument", "NIFTY 24500 CE")
                j_entry_t = st.time_input("Entry Time", datetime.time(9, 30))
                j_exit_t  = st.time_input("Exit Time",  datetime.time(10, 0))
            with jc2:
                j_entry_p = st.number_input("Entry Price (INR)", min_value=0.1, value=150.0, step=0.5)
                j_exit_p  = st.number_input("Exit Price (INR)",  min_value=0.1, value=165.0, step=0.5)
                j_sl_pts  = st.number_input("SL Points Used", min_value=0.1, max_value=18.0, value=15.0)
                j_lots    = st.number_input("Lots Executed",  min_value=1, value=1)

            auto_pnl = round((j_exit_p - j_entry_p) * j_lots * 65, 2)
            result_label = "Profit" if auto_pnl > 0 else ("Loss" if auto_pnl < 0 else "Breakeven")

            note_label = "What went wrong? (MANDATORY for Loss)" if auto_pnl < 0 else "Execution Notes"
            j_notes = st.text_area(note_label, placeholder="Describe setup, market context, or mistakes...", height=85)

            if st.form_submit_button("Save Trade to Database", use_container_width=True):
                if auto_pnl < 0 and not j_notes.strip():
                    st.error("Submission blocked: Trade resulted in a loss. Detailed notes are mandatory.")
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
                    st.success(f"Trade {tid} saved successfully. PnL: INR {auto_pnl:,.2f}")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><h4>Buying Trade History</h4><div class="sub">Executed option buying ledger</div></div>', unsafe_allow_html=True)
    df_buy = get_data("Buy_Log")
    if not df_buy.empty:
        st.dataframe(df_buy, use_container_width=True, hide_index=True)
    else:
        st.info("No buying trades recorded yet.")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3: OPTION SELLING
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Option Selling":

    col_l, col_r = st.columns([1.1, 1], gap="large")

    with col_l:
        st.markdown('<div class="panel"><h4>Stop Loss Calculator (30% Rule)</h4><div class="sub">Calculates precise SL price for option writing</div></div>', unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            s_entry = st.number_input("Entry Premium (INR)", min_value=0.0, value=0.0, step=0.5, key="s_entry")
        with sc2:
            s_pct   = st.number_input("SL Percentage (%)", min_value=1.0, max_value=200.0, value=30.0, step=1.0)
        with sc3:
            s_lots  = st.number_input("Lots (65 Qty)", min_value=1, value=1, key="s_lots")

        if s_entry == 0.0:
            st.info("Enter Entry Premium above to calculate stop-loss trigger price and max risk.")
        else:
            sl_price  = round(s_entry * (1 + s_pct / 100), 2)
            sl_pts    = round(sl_price - s_entry, 2)
            max_loss  = round(sl_pts * s_lots * 65, 2)

            st.markdown(f"""
            <div class="kpi-grid" style="margin-top: 1rem;">
              <div class="kpi g1">
                <div class="lbl">SL Trigger Price</div>
                <div class="val">INR {sl_price}</div>
                <div class="fin">{s_pct}% above entry</div>
              </div>
              <div class="kpi g2">
                <div class="lbl">Risk in Points</div>
                <div class="val">+{sl_pts} pts</div>
                <div class="fin">per quantity</div>
              </div>
              <div class="kpi g3">
                <div class="lbl">Max Loss</div>
                <div class="val">INR {max_loss:,.2f}</div>
                <div class="fin">{s_lots} Lot ({s_lots*65} Qty)</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="panel"><h4>Log Selling Trade</h4><div class="sub">Supports Multi-Leg (CE + PE) execution</div></div>', unsafe_allow_html=True)

        with st.form("sell_form", clear_on_submit=True):
            s_strategy = st.selectbox("Strategy Type", ["Short Straddle","Short Strangle","Naked CE Sell","Naked PE Sell"])
            s_date = st.date_input("Date", today_date, key="s_date")
            s_lots_j = st.number_input("Lots Executed", min_value=1, value=1, key="s_lots_j")

            ce_c, pe_c = st.columns(2)
            with ce_c:
                st.markdown("**CE Leg**")
                ce_entry = st.number_input("CE Entry (INR)", min_value=0.0, value=100.0, step=0.5)
                ce_exit  = st.number_input("CE Exit (INR)",  min_value=0.0, value=70.0,  step=0.5)
            with pe_c:
                st.markdown("**PE Leg**")
                pe_entry = st.number_input("PE Entry (INR)", min_value=0.0, value=100.0, step=0.5)
                pe_exit  = st.number_input("PE Exit (INR)",  min_value=0.0, value=120.0, step=0.5)

            s_status = st.selectbox("Exit Status", ["Target Achieved","SL Hit","Squared off at Close"])
            sell_pnl = round(((ce_entry - ce_exit) + (pe_entry - pe_exit)) * s_lots_j * 65, 2)

            s_note_lbl = "What went wrong? (MANDATORY for Loss)" if sell_pnl < 0 else "Trade Remarks"
            s_notes = st.text_area(s_note_lbl, placeholder="Describe entry reasons, delta adjustments, or IV remarks...", height=80)

            if st.form_submit_button("Save Selling Trade", use_container_width=True):
                if sell_pnl < 0 and not s_notes.strip():
                    st.error("Submission blocked: Notes are mandatory for losing trades.")
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
                    st.success(f"Selling trade {tid} saved. Total PnL: INR {sell_pnl:,.2f}")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><h4>Selling Trade History</h4><div class="sub">Executed option writing ledger</div></div>', unsafe_allow_html=True)
    df_sell = get_data("Sell_Log")
    if not df_sell.empty:
        st.dataframe(df_sell, use_container_width=True, hide_index=True)
    else:
        st.info("No selling trades recorded yet.")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4: EVENTS & EARNINGS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Events & Earnings":

    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown('<div class="panel"><h4>Add Economic Event</h4><div class="sub">Record macro catalysts and releases</div></div>', unsafe_allow_html=True)
        with st.form("ev_form", clear_on_submit=True):
            e_date    = st.date_input("Date", today_date, key="e_d")
            e_time    = st.time_input("Time", datetime.time(17, 30))
            e_country = st.selectbox("Country", ["INDIA","US","EU","UK","CHINA","JAPAN"])
            e_name    = st.text_input("Event Name", placeholder="RBI Rate Decision / US CPI Data")
            e_impact  = st.selectbox("Impact Level", ["HIGH","MEDIUM","LOW"])
            if st.form_submit_button("Add Event", use_container_width=True):
                append_row("Events", {"Date": str(e_date), "Time": str(e_time),
                                      "Country": e_country, "Event_Name": e_name,
                                      "Impact_Level": e_impact})
                st.success("Event added successfully.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4>Economic Events Master List</h4><div class="sub">Scheduled calendar events</div></div>', unsafe_allow_html=True)
        df_ev2 = get_data("Events")
        if not df_ev2.empty:
            st.dataframe(df_ev2, use_container_width=True, hide_index=True)
        else:
            st.info("No economic events scheduled.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="panel"><h4>Add Corporate Earnings</h4><div class="sub">Record quarterly company earnings</div></div>', unsafe_allow_html=True)
        with st.form("re_form", clear_on_submit=True):
            r_date   = st.date_input("Date", today_date, key="r_d")
            r_time   = st.selectbox("Timing", ["Before Market Open","During Market Hours","After Market Close"])
            r_symbol = st.text_input("Company Symbol", placeholder="RELIANCE / TCS / INFOSYS")
            r_exp    = st.text_input("Market Expectation", placeholder="PAT +12% YoY, margin expansion")
            if st.form_submit_button("Add Corporate Result", use_container_width=True):
                append_row("Results", {"Date": str(r_date), "Time": r_time,
                                       "Company_Symbol": r_symbol,
                                       "Market_Expectation": r_exp})
                st.success("Corporate result added successfully.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4>Corporate Earnings Master List</h4><div class="sub">Scheduled results calendar</div></div>', unsafe_allow_html=True)
        df_re2 = get_data("Results")
        if not df_re2.empty:
            st.dataframe(df_re2, use_container_width=True, hide_index=True)
        else:
            st.info("No corporate results scheduled.")
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 5: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Dashboard":

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

    pnl_card_grad = "g5" if total_pnl >= 0 else "g1"

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi {pnl_card_grad}">
        <div class="lbl">Total Cumulative PnL</div>
        <div class="val">INR {total_pnl:+,.2f}</div>
        <div class="fin">Combined Buying & Selling</div>
      </div>
      <div class="kpi g2">
        <div class="lbl">Buying PnL</div>
        <div class="val">INR {pnl_buy:+,.2f}</div>
        <div class="fin">{n_buy} trades logged</div>
      </div>
      <div class="kpi g3">
        <div class="lbl">Selling PnL</div>
        <div class="val">INR {pnl_sell:+,.2f}</div>
        <div class="fin">{n_sell} trades logged</div>
      </div>
      <div class="kpi g4">
        <div class="lbl">Win Rate</div>
        <div class="val">{win_rate:.1f}%</div>
        <div class="fin">{wins_b + wins_s} Wins / {total_t} Executions</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    d_col1, d_col2 = st.columns(2, gap="large")

    with d_col1:
        st.markdown('<div class="panel"><h4>Export Trade Journal</h4><div class="sub">Download complete log history in Excel format</div></div>', unsafe_allow_html=True)
        buf = io.BytesIO()
        try:
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                (df_buy  if not df_buy.empty  else pd.DataFrame()).to_excel(writer, sheet_name="Buy_Log",  index=False)
                (df_sell if not df_sell.empty else pd.DataFrame()).to_excel(writer, sheet_name="Sell_Log", index=False)
            excel_data = buf.getvalue()
        except Exception:
            excel_data = (df_buy.to_csv(index=False) if not df_buy.empty else "").encode('utf-8')

        st.download_button(
            "Export Journal (Excel)",
            data=excel_data,
            file_name=f"Super_App_Nifty_Journal_{today_iso}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with d_col2:
        st.markdown('<div class="panel"><h4>Clear Database</h4><div class="sub">Reset active trade records for a new period</div></div>', unsafe_allow_html=True)
        with st.popover("Clear All Trade Records"):
            st.error("This action will clear all records from Buy_Log and Sell_Log.")
            chk = st.checkbox("Confirm database reset")
            if st.button("Permanently Clear Tables", disabled=not chk, use_container_width=True):
                clear_tab("Buy_Log")
                clear_tab("Sell_Log")
                st.success("Database reset complete.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><h4>All Buying Trade Records</h4><div class="sub">Complete option buying ledger</div></div>', unsafe_allow_html=True)
    if not df_buy.empty:
        st.dataframe(df_buy, use_container_width=True, hide_index=True)
    else:
        st.info("No buying records available.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><h4>All Selling Trade Records</h4><div class="sub">Complete option selling ledger</div></div>', unsafe_allow_html=True)
    if not df_sell.empty:
        st.dataframe(df_sell, use_container_width=True, hide_index=True)
    else:
        st.info("No selling records available.")
    st.markdown('</div>', unsafe_allow_html=True)
