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
st.set_page_config(page_title="Super App Nifty", layout="wide")

# ── Styling: Professional Dark ─────────────────────────────────────────────
st.markdown("""
<style>
:root {
  --bg-main: #09090E;
  --card-bg: #151520;
  --text-main: #FFFFFF;
  --text-muted: #8A8A9D;
  --primary: #8B5CF6;
  --border: #272736;
}
body, .stApp { font-family: 'DM Sans', sans-serif; background-color: var(--bg-main); color: var(--text-main); }

section[data-testid="stSidebar"] { background-color: var(--card-bg); border-right: 1px solid var(--border); }
.block-container { padding-top: 2rem; }

.panel {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border);
  margin-bottom: 20px;
}
.panel-h { color: var(--text-main); font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; }

input, select, textarea {
  background: #0D0D14 !important;
  color: #FFFFFF !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
}
.stButton > button { background: var(--primary); color: white; border: none; border-radius: 6px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Data Helpers (simplified for structure demonstration) ───────────────────
def init_gspread():
    if not HAS_GSPREAD or "gcp_service_account" not in st.secrets: return None
    try:
        creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]),
                scopes=["https://www.googleapis.com/auth/spreadsheets"])
        return gspread.authorize(creds)
    except: return None

def append_row(tab, row):
    client = init_gspread()
    if client and "sheet_id" in st.secrets:
        try: client.open_by_key(st.secrets["sheet_id"]).worksheet(tab).append_row(list(row.values()))
        except: pass

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Super App Nifty")
    page = st.radio("Navigation", ["Home", "Option Buying", "Option Selling", "Dashboard"])
    st.markdown("---")
    st.markdown(f"Status: Operational<br>Time: {datetime.datetime.now().strftime('%H:%M')} IST", unsafe_allow_html=True)

# ── Main Content ───────────────────────────────────────────────────────────
st.header(page)
today = datetime.date.today().isoformat()

if page == "Home":
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="panel"><div class="panel-h">Risk Assessment</div>', unsafe_allow_html=True)
        entry = st.number_input("Entry Price", value=150.0)
        sl = st.number_input("Stop Loss", value=135.0)
        if (entry - sl) > 18:
            st.error("Guardrail Violated: Risk > 18 points.")
        else:
            st.success("Risk Approved.")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="panel"><div class="panel-h">System Rules</div>', unsafe_allow_html=True)
        st.write("1. Time Window: 09:30 - 14:45\n2. Entry: Pullback + ADX Increasing\n3. Max SL: 18 pts")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Option Buying":
    with st.form("buy"):
        jc1, jc2 = st.columns(2)
        entry = jc1.number_input("Entry Price", value=150.0)
        exit = jc2.number_input("Exit Price", value=160.0)
        notes = st.text_area("Notes")
        if st.form_submit_button("Save Trade"):
            if (exit - entry) * 65 < 0 and not notes.strip():
                st.error("Losing trade requires mandatory notes.")
            else:
                append_row("Buy_Log", {"Date":today, "PnL":(exit-entry)*65, "Notes":notes})
                st.success("Saved.")
elif page == "Option Selling":
    st.info("Selling module...")
else:
    st.info("Dashboard...")
