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

# ── Styling: Professional Dark & Google Sans ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

/* Base Font & Color Palette */
:root {
  --bg-main: #09090E;
  --card-bg: #151520;
  --card-hover: #1C1C2B;
  --text-main: #F3F4F6;
  --text-muted: #9CA3AF;
  --text-dim: #6B7280;
  --primary: #8B5CF6;
  --primary-hover: #7C3AED;
  --border: #272736;
  --success: #10B981;
  --danger: #EF4444;
  --warning: #F59E0B;
  --cyan: #06B6D4;
}

html, body, [class*="css"], .stMarkdown, p, div, span, label, input, button {
  font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
  background-color: var(--bg-main);
  color: var(--text-main);
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; height: 0; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1440px; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background-color: var(--card-bg);
  border-right: 1px solid var(--border);
  min-width: 280px !important;
  width: 280px !important;
}
section[data-testid="stSidebar"] * { color: var(--text-main); }
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
[data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"], button[kind="header"] { display: none !important; }

.brand-title {
  font-size: 1.25rem; font-weight: 700; color: #FFFFFF;
  letter-spacing: -0.02em; margin: 0 0 0.2rem 0;
}
.brand-sub {
  font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;
  letter-spacing: 0.05em; font-weight: 500; margin-bottom: 1.5rem;
}

section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 0.4rem; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
  background: rgba(255,255,255,0.03); border: 1px solid var(--border);
  border-radius: 10px; padding: 0.65rem 1rem; width: 100%; cursor: pointer;
  transition: all 0.15s ease; font-weight: 500; font-size: 0.88rem;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
  background: rgba(139, 92, 246, 0.1); border-color: var(--primary);
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
  background: var(--primary); border-color: var(--primary);
  color: #FFFFFF; font-weight: 700;
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.35);
}

.side-divider { height: 1px; background: var(--border); margin: 1.25rem 0 1rem; }
.side-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); font-weight: 700; margin-bottom: 0.5rem; }
.side-row { display: flex; justify-content: space-between; font-size: 0.8rem; padding: 0.3rem 0; color: var(--text-muted); }
.side-row b { color: var(--text-main); font-weight: 600; }

/* Header Component */
.header-container {
  display: flex; align-items: flex-end; justify-content: space-between;
  margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border);
  flex-wrap: wrap; gap: 1rem;
}
.header-title { font-size: 1.75rem; font-weight: 700; color: #FFFFFF; margin: 0; letter-spacing: -0.02em; }
.header-sub { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem; font-weight: 400; }
.header-chip {
  display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.9rem;
  border-radius: 20px; font-size: 0.78rem; font-weight: 600;
  background: var(--card-bg); border: 1px solid var(--border); color: var(--text-main);
}
.chip-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--success); }

/* Card Panels */
.panel {
  background: var(--card-bg); border: 1px solid var(--border);
  border-radius: 16px; padding: 24px; margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}
.panel-h {
  font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin: 0 0 0.25rem 0;
}
.panel-sub { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1.25rem; }

/* KPI Grid */
.kpi-grid { display: grid; gap: 1rem; margin-bottom: 1.5rem; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
.kpi-card {
  background: var(--card-bg); border: 1px solid var(--border);
  border-radius: 14px; padding: 18px 20px; position: relative; overflow: hidden;
}
.kpi-card-positive { border-left: 4px solid var(--success); }
.kpi-card-negative { border-left: 4px solid var(--danger); }
.kpi-card-accent { border-left: 4px solid var(--primary); }
.kpi-card-neutral { border-left: 4px solid var(--cyan); }
.kpi-lbl { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 700; }
.kpi-val { font-size: 1.5rem; font-weight: 700; color: #FFFFFF; margin-top: 0.35rem; }
.kpi-sub { font-size: 0.75rem; color: var(--text-dim); margin-top: 0.2rem; }

/* Guardrails & Alerts */
.banner-danger {
  background: rgba(239, 68, 68, 0.1); border: 1px solid var(--danger);
  border-radius: 12px; padding: 16px; color: #FFFFFF; text-align: center; margin: 1rem 0;
}
.banner-danger h4 { color: var(--danger); margin: 0 0 0.25rem 0; font-size: 0.95rem; font-weight: 700; }
.banner-danger p { color: var(--text-muted); margin: 0; font-size: 0.82rem; }

.banner-success {
  background: rgba(16, 185, 129, 0.1); border: 1px solid var(--success);
  border-radius: 10px; padding: 12px 16px; color: var(--success); font-size: 0.85rem; font-weight: 600; margin: 1rem 0;
}

.alert-item {
  background: #0D0D14; border: 1px solid var(--border); border-radius: 10px;
  padding: 10px 14px; margin-bottom: 8px; font-size: 0.84rem; display: flex;
  justify-content: space-between; align-items: center; color: var(--text-main);
}
.badge-tag {
  background: var(--primary); color: #FFFFFF; padding: 3px 8px; border-radius: 6px;
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.05em;
}

/* Catalyst Cards */
.catalyst-grid { display: grid; gap: 0.85rem; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); margin-bottom: 0.5rem; }
.catalyst-card {
  border-radius: 12px; padding: 16px; position: relative; overflow: hidden;
  display: flex; flex-direction: column; gap: 0.4rem; font-size: 0.85rem; border: 1px solid var(--border);
  background: var(--card-bg);
}
.cat-type { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
.cat-title { font-size: 1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.2rem; }
.cat-meta { display: flex; gap: 1rem; color: var(--text-dim); font-size: 0.78rem; font-weight: 500; }
.cat-meta b { color: var(--text-muted); }

/* Catalyst Color Variations */
.cat-high { border-left: 4px solid var(--danger); background: rgba(239, 68, 68, 0.05); border-color: rgba(239, 68, 68, 0.2); }
.cat-high .cat-type { color: var(--danger); }

.cat-med { border-left: 4px solid var(--warning); background: rgba(245, 158, 11, 0.05); border-color: rgba(245, 158, 11, 0.2); }
.cat-med .cat-type { color: var(--warning); }

.cat-low { border-left: 4px solid var(--cyan); background: rgba(6, 182, 212, 0.04); border-color: rgba(6, 182, 212, 0.2); }
.cat-low .cat-type { color: var(--cyan); }

.cat-earn { border-left: 4px solid var(--primary); background: rgba(139, 92, 246, 0.05); border-color: rgba(139, 92, 246, 0.2); }
.cat-earn .cat-type { color: var(--primary); }

.cat-empty { background: rgba(16, 185, 129, 0.05); border: 1px dashed var(--success); color: var(--success); text-align: center; padding: 16px; border-radius: 12px; font-weight: 600; font-size: 0.85rem; }


/* Target Grid Table */
.data-table-custom { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.85rem; }
.data-table-custom th {
  background: #0D0D14; color: var(--text-muted); font-weight: 600;
  text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border);
  font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;
}
.data-table-custom td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.04); color: var(--text-main); }
.td-highlight { color: var(--primary); font-weight: 700; }
.td-success { color: var(--success); font-weight: 700; }

/* Rules List */
.rule-block { margin-bottom: 1rem; }
.rule-head { font-size: 0.8rem; font-weight: 700; color: var(--primary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem; }
.rule-body { margin: 0; padding-left: 1.2rem; font-size: 0.85rem; color: var(--text-muted); line-height: 1.6; }
.rule-body li { margin-bottom: 0.25rem; }
.rule-body b { color: var(--text-main); }

/* Quotes */
.quote-item { display: flex; gap: 0.6rem; align-items: flex-start; margin-bottom: 0.65rem; }
.quote-bullet { width: 6px; height: 6px; border-radius: 50%; background: var(--primary); margin-top: 0.4rem; flex-shrink: 0; }
.quote-txt { font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; }

/* Forms & Buttons */
label { font-size: 0.8rem !important; font-weight: 500 !important; color: var(--text-muted) !important; margin-bottom: 0.3rem !important; }
input, select, textarea {
  background-color: #0D0D14 !important; color: #FFFFFF !important;
  border: 1px solid var(--border) !important; border-radius: 8px !important;
  padding: 10px 12px !important; font-size: 0.88rem !important;
}
input:focus, select:focus, textarea:focus { border-color: var(--primary) !important; }

.stButton > button {
  background: var(--primary) !important; color: #FFFFFF !important;
  border: none !important; border-radius: 8px !important; font-weight: 600 !important;
  padding: 0.6rem 1.2rem !important; font-size: 0.88rem !important;
  transition: all 0.15s ease !important;
}
.stButton > button:hover { background: var(--primary-hover) !important; }
div[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Data Storage Layer ──────────────────────────────────────────────────────
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
    new_df = pd.DataFrame([row])
    st.session_state.db[tab] = pd.concat([st.session_state.db[tab], new_df], ignore_index=True)
    client = init_gspread()
    sheet_id = st.secrets.get("sheet_id", "") if "sheet_id" in st.secrets else ""
    if client and sheet_id:
        try:
            ws = client.open_by_key(sheet_id).worksheet(tab)
            ws.append_row(list(row.values()))
        except Exception as e:
            st.toast(f"Saved locally. Sheets sync issue: {e}")

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

# ── Sidebar Navigation ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand-title">Super App Nifty</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Matrix Trading Terminal</div>', unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "Home & Rules",
        "Option Buying",
        "Option Selling",
        "Events & Earnings",
        "Dashboard",
    ], label_visibility="collapsed")

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-label">System Specs</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-row"><span>Lot Size</span><b>65 Qty</b></div>'
        '<div class="side-row"><span>Max Risk (Buy)</span><b>18 Points</b></div>'
        '<div class="side-row"><span>SL Rule (Sell)</span><b>30 %</b></div>'
        '<div class="side-row"><span>Time Window</span><b>09:30 - 14:45</b></div>'
        '<div class="side-row"><span>Breakeven At</span><b>1:2 RR</b></div>',
        unsafe_allow_html=True)

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    today_formatted = datetime.date.today().strftime("%d %b %Y")
    now_formatted = datetime.datetime.now().strftime("%H:%M")
    st.markdown(
        f'<div class="side-row"><span>Date</span><b>{today_formatted}</b></div>'
        f'<div class="side-row"><span>Time</span><b>{now_formatted} IST</b></div>',
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
today_date = datetime.date.today()
today_iso = today_date.isoformat()

st.markdown(f"""
<div class="header-container">
  <div>
    <h1 class="header-title">{title_text}</h1>
    <div class="header-sub">{subtitle_text}</div>
  </div>
  <div>
    <span class="header-chip">
      <span class="chip-dot"></span>
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
    today_ev = df_ev[df_ev["Date"] == today_iso] if not df_ev.empty and "Date" in df_ev.columns else pd.DataFrame()
    today_re = df_re[df_re["Date"] == today_iso] if not df_re.empty and "Date" in df_re.columns else pd.DataFrame()

    if not today_ev.empty or not today_re.empty:
        st.markdown('<div class="panel" style="padding-bottom:12px;"><div class="panel-h">Today\'s Market Catalysts</div><div class="catalyst-grid">', unsafe_allow_html=True)
        for _, r in today_ev.iterrows():
            imp = str(r.get("Impact_Level", "MEDIUM")).upper()
            c_class = "cat-high" if imp == "HIGH" else "cat-low" if imp == "LOW" else "cat-med"
            st.markdown(f'''
            <div class="catalyst-card {c_class}">
              <div class="cat-type">{imp} IMPACT EVENT</div>
              <div class="cat-title">{r.get("Event_Name","")}</div>
              <div class="cat-meta">
                <span>Time: <b>{r.get("Time","")}</b></span>
                <span>Country: <b>{r.get("Country","")}</b></span>
              </div>
            </div>
            ''', unsafe_allow_html=True)

        for _, r in today_re.iterrows():
            st.markdown(f'''
            <div class="catalyst-card cat-earn">
              <div class="cat-type">CORPORATE EARNINGS</div>
              <div class="cat-title">{r.get("Company_Symbol","")}</div>
              <div class="cat-meta">
                <span>Timing: <b>{r.get("Time","")}</b></span>
              </div>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="panel"><div class="panel-h">Today\'s Market Catalysts</div><div class="cat-empty">No high-impact economic events or corporate earnings scheduled for today. Clear session.</div></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1.1, 1], gap="large")

    with col_l:
        st.markdown('<div class="panel"><div class="panel-h">Risk Planner</div><div class="panel-sub">Validate risk before placing orders (Max 18 pts)</div>', unsafe_allow_html=True)
        qc1, qc2, qc3 = st.columns(3)
        with qc1:
            h_entry = st.number_input("Entry Price (INR)", min_value=1.0, value=150.0, step=0.5, key="h_entry")
        with qc2:
            h_sl = st.number_input("Stop Loss (INR)", min_value=0.5, value=135.0, step=0.5, key="h_sl")
        with qc3:
            h_lots = st.number_input("Lots (65 Qty)", min_value=1, value=1, key="h_lots")

        risk_pts = round(h_entry - h_sl, 2)
        qty = h_lots * 65

        if risk_pts <= 0:
            st.warning("Stop loss must be lower than entry price.")
        elif risk_pts > 18.0:
            st.markdown(f"""
            <div class="banner-danger">
              <h4>NO TRADE — Guardrail Violated</h4>
              <p>Risk is <b>{risk_pts} points</b>. Maximum allowed risk is <b>18.0 points</b>.</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="banner-success">Trade Approved: {risk_pts} Points Risk &nbsp;·&nbsp; Total Risk: INR {risk_pts * qty:,.2f} ({h_lots} Lot)</div>', unsafe_allow_html=True)

            rows_html = ""
            prev = h_entry
            for i in range(1, 7):
                tgt = round(h_entry + risk_pts * i, 2)
                trail = "Entry (Breakeven)" if i == 1 else f"T{i-1} ({prev:.2f})"
                profit = round(risk_pts * i * qty, 2)
                rows_html += f'<tr><td class="td-highlight">1:{i}</td><td class="td-success">{tgt:.2f}</td><td>{trail}</td><td class="td-success">INR {profit:,.2f}</td></tr>'
                prev = tgt

            st.markdown(f"""
            <table class="data-table-custom">
              <thead><tr><th>Risk:Reward</th><th>Target Price</th><th>Trail SL To</th><th>Profit Projection</th></tr></thead>
              <tbody>{rows_html}</tbody>
            </table>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown("""
        <div class="panel">
          <div class="panel-h">The Matrix System</div>
          <div class="panel-sub">Core rules of engagement</div>

          <div class="rule-block">
            <div class="rule-head">1. Time Window</div>
            <ul class="rule-body">
              <li>Start: <b>09:30 AM</b> — Allow initial opening volatility to normalize.</li>
              <li>Cut-off: <b>02:45 PM</b> — No new positions permitted after this time.</li>
            </ul>
          </div>

          <div class="rule-block">
            <div class="rule-head">2. Valid Entry (Green Light)</div>
            <ul class="rule-body">
              <li>Wait for price pullback to the <b>VWMA / Supertrend baseline</b>.</li>
              <li>ADX MUST be <b>Increasing</b> or <b>Started Increasing</b> (92.5% WR Rule).</li>
            </ul>
          </div>

          <div class="rule-block">
            <div class="rule-head">3. No-Entry (Red Light)</div>
            <ul class="rule-body">
              <li>If ADX is Decreasing or Mixed → <b>Strict NO TRADE</b>.</li>
              <li>Do not chase vertical price spikes or gap-ups.</li>
              <li>If required Stop Loss exceeds 18 points → <b>NO TRADE</b>.</li>
            </ul>
          </div>

          <div class="rule-block">
            <div class="rule-head">4. Exit Rules</div>
            <ul class="rule-body">
              <li>Execution limit: <b>1 Lot</b>. Maximum risk <b>18 points</b>.</li>
              <li>At 1:2 Risk-Reward (30+ pts), adjust SL to <b>Breakeven</b>.</li>
              <li>Never allow a profitable trade to turn into a loss.</li>
            </ul>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="panel"><div class="panel-h">Trading Mindset</div>', unsafe_allow_html=True)
        quotes = [
            "A missed trade is better than a forced trade.",
            "Don't let fear of missing out drive your decisions.",
            "Control your emotions, not the market.",
            "Plan the trade and trade the plan. Never let emotions write your execution log.",
            "Cut your losses short and let your winners run — respect the 18pt guardrail."
        ]
        for q in quotes:
            st.markdown(f'<div class="quote-item"><div class="quote-bullet"></div><div class="quote-txt">{q}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2: OPTION BUYING
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Option Buying":

    col_l, col_r = st.columns([1.1, 1], gap="large")

    with col_l:
        st.markdown('<div class="panel"><div class="panel-h">Risk & Target Calculator</div><div class="panel-sub">Enforces 18-point maximum risk rule</div>', unsafe_allow_html=True)

        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            b_entry = st.number_input("Entry Price (INR)", min_value=1.0, value=150.0, step=0.5, key="b_entry")
            b_dir   = st.selectbox("Direction", ["BUY CE (Long)", "BUY PE (Short)"], key="b_dir")
        with bc2:
            b_sl    = st.number_input("Stop Loss (INR)", min_value=0.5, value=135.0, step=0.5, key="b_sl")
        with bc3:
            b_lots  = st.number_input("Lots (65 Qty)", min_value=1, value=1, key="b_lots")

        risk = round(b_entry - b_sl, 2)
        qty  = b_lots * 65

        if risk <= 0:
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
        st.markdown('<div class="panel"><div class="panel-h">Log Buying Trade</div><div class="panel-sub">Notes are mandatory for trades ending in loss</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="panel"><div class="panel-h">Buying Trade History</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="panel"><div class="panel-h">Stop Loss Calculator (30% Rule)</div><div class="panel-sub">Calculates precise SL price for option writing</div>', unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            s_entry = st.number_input("Entry Premium (INR)", min_value=1.0, value=100.0, step=0.5, key="s_entry")
        with sc2:
            s_pct   = st.number_input("SL Percentage (%)", min_value=1.0, max_value=200.0, value=30.0, step=1.0)
        with sc3:
            s_lots  = st.number_input("Lots (65 Qty)", min_value=1, value=1, key="s_lots")

        sl_price  = round(s_entry * (1 + s_pct / 100), 2)
        sl_pts    = round(sl_price - s_entry, 2)
        max_loss  = round(sl_pts * s_lots * 65, 2)

        st.markdown(f"""
        <div class="kpi-grid" style="margin-top: 1rem;">
          <div class="kpi-card kpi-card-negative">
            <div class="kpi-lbl">SL Trigger Price</div>
            <div class="kpi-val">INR {sl_price}</div>
            <div class="kpi-sub">{s_pct}% above entry</div>
          </div>
          <div class="kpi-card kpi-card-accent">
            <div class="kpi-lbl">Risk in Points</div>
            <div class="kpi-val">+{sl_pts} pts</div>
            <div class="kpi-sub">per quantity</div>
          </div>
          <div class="kpi-card kpi-card-neutral">
            <div class="kpi-lbl">Max Loss</div>
            <div class="kpi-val">INR {max_loss:,.2f}</div>
            <div class="kpi-sub">{s_lots} Lot ({s_lots*65} Qty)</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="panel"><div class="panel-h">Log Selling Trade</div><div class="panel-sub">Supports Multi-Leg (CE + PE) execution</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="panel"><div class="panel-h">Selling Trade History</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="panel"><div class="panel-h">Add Economic Event</div>', unsafe_allow_html=True)
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

        st.markdown('<div class="panel"><div class="panel-h">Economic Events Master List</div>', unsafe_allow_html=True)
        df_ev2 = get_data("Events")
        if not df_ev2.empty:
            st.dataframe(df_ev2, use_container_width=True, hide_index=True)
        else:
            st.info("No economic events scheduled.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="panel"><div class="panel-h">Add Corporate Earnings</div>', unsafe_allow_html=True)
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

        st.markdown('<div class="panel"><div class="panel-h">Corporate Earnings Master List</div>', unsafe_allow_html=True)
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

    pnl_card_type = "kpi-card-positive" if total_pnl >= 0 else "kpi-card-negative"

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card {pnl_card_type}">
        <div class="kpi-lbl">Total Cumulative PnL</div>
        <div class="kpi-val">INR {total_pnl:+,.2f}</div>
        <div class="kpi-sub">Combined Buying & Selling</div>
      </div>
      <div class="kpi-card kpi-card-accent">
        <div class="kpi-lbl">Buying PnL</div>
        <div class="kpi-val">INR {pnl_buy:+,.2f}</div>
        <div class="kpi-sub">{n_buy} trades logged</div>
      </div>
      <div class="kpi-card kpi-card-neutral">
        <div class="kpi-lbl">Selling PnL</div>
        <div class="kpi-val">INR {pnl_sell:+,.2f}</div>
        <div class="kpi-sub">{n_sell} trades logged</div>
      </div>
      <div class="kpi-card kpi-card-accent">
        <div class="kpi-lbl">Win Rate</div>
        <div class="kpi-val">{win_rate:.1f}%</div>
        <div class="kpi-sub">{wins_b + wins_s} Wins / {total_t} Executions</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    d_col1, d_col2 = st.columns(2, gap="large")

    with d_col1:
        st.markdown('<div class="panel"><div class="panel-h">Export Trade Journal</div><div class="panel-sub">Download complete log history in Excel format</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="panel"><div class="panel-h">Clear Database</div><div class="panel-sub">Reset active trade records for a new period</div>', unsafe_allow_html=True)
        with st.popover("Clear All Trade Records"):
            st.error("This action will clear all records from Buy_Log and Sell_Log.")
            chk = st.checkbox("Confirm database reset")
            if st.button("Permanently Clear Tables", disabled=not chk, use_container_width=True):
                clear_tab("Buy_Log")
                clear_tab("Sell_Log")
                st.success("Database reset complete.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-h">All Buying Trade Records</div>', unsafe_allow_html=True)
    if not df_buy.empty:
        st.dataframe(df_buy, use_container_width=True, hide_index=True)
    else:
        st.info("No buying records available.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-h">All Selling Trade Records</div>', unsafe_allow_html=True)
    if not df_sell.empty:
        st.dataframe(df_sell, use_container_width=True, hide_index=True)
    else:
        st.info("No selling records available.")
    st.markdown('</div>', unsafe_allow_html=True)
