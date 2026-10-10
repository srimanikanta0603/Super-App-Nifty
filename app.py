import streamlit as st
import pandas as pd
import datetime
import random
import json
import io

# Optional gspread imports with graceful fallback
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_GSPREAD = True
except ImportError:
    HAS_GSPREAD = False

# ==========================================
# PAGE CONFIGURATION & NEON DARK THEME
# ==========================================
st.set_page_config(
    page_title="SUPER APP NIFTY | Trading Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Neon Dark CSS Styling
st.markdown("""
<style>
    /* Dark Neon Palette */
    :root {
        --bg-main: #08090C;
        --bg-card: #10141D;
        --bg-card-hover: #161C28;
        --neon-green: #00FF85;
        --neon-red: #FF2E5B;
        --neon-cyan: #00F5FF;
        --neon-yellow: #FFD700;
        --text-primary: #ECEFF4;
        --text-muted: #8892B0;
        --border-color: #1E293B;
    }

    /* Base Styling */
    .stApp {
        background-color: var(--bg-main);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Header Cards */
    .neon-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    .neon-card-green {
        border-left: 4px solid var(--neon-green);
        box-shadow: 0 0 15px rgba(0, 255, 133, 0.15);
    }

    .neon-card-red {
        border-left: 4px solid var(--neon-red);
        box-shadow: 0 0 15px rgba(255, 46, 91, 0.15);
    }

    .neon-card-cyan {
        border-left: 4px solid var(--neon-cyan);
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.15);
    }

    /* Neon Titles */
    .neon-text-green { color: var(--neon-green); font-weight: 700; text-shadow: 0 0 8px rgba(0, 255, 133, 0.4); }
    .neon-text-red { color: var(--neon-red); font-weight: 700; text-shadow: 0 0 8px rgba(255, 46, 91, 0.4); }
    .neon-text-cyan { color: var(--neon-cyan); font-weight: 700; text-shadow: 0 0 8px rgba(0, 245, 255, 0.4); }
    .neon-text-yellow { color: var(--neon-yellow); font-weight: 700; text-shadow: 0 0 8px rgba(255, 215, 0, 0.4); }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-green { background: rgba(0, 255, 133, 0.15); color: var(--neon-green); border: 1px solid var(--neon-green); }
    .badge-red { background: rgba(255, 46, 91, 0.15); color: var(--neon-red); border: 1px solid var(--neon-red); }
    .badge-cyan { background: rgba(0, 245, 255, 0.15); color: var(--neon-cyan); border: 1px solid var(--neon-cyan); }

    /* Guardrail Alert Box */
    .guardrail-alert {
        background-color: rgba(255, 46, 91, 0.15);
        border: 2px solid var(--neon-red);
        border-radius: 10px;
        padding: 15px;
        color: #FFFFFF;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 0 20px rgba(255, 46, 91, 0.5);
        margin: 15px 0;
        animation: pulse 1.5s infinite alternate;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 10px rgba(255, 46, 91, 0.4); }
        100% { box-shadow: 0 0 25px rgba(255, 46, 91, 0.8); }
    }

    /* Metric Cards Custom */
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
    }

    /* Target Grid Table */
    .target-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .target-table th {
        background-color: rgba(0, 245, 255, 0.1);
        color: var(--neon-cyan);
        padding: 10px;
        border: 1px solid var(--border-color);
        text-align: center;
    }
    .target-table td {
        padding: 10px;
        border: 1px solid var(--border-color);
        text-align: center;
        background-color: var(--bg-card);
    }

    /* Quote Banner */
    .quote-box {
        font-style: italic;
        color: #A0AEC0;
        border-left: 3px solid var(--neon-yellow);
        padding-left: 12px;
        margin: 10px 0 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# TRADING QUOTES DATABASE
# ==========================================
TRADING_QUOTES = [
    "“Plan the trade and trade the plan. Never let emotions write your execution log.”",
    "“The goal of a successful trader is to make the best trades. Money is secondary.” — Alexander Elder",
    "“Risk comes from not knowing what you're doing.” — Warren Buffett",
    "“In trading, discipline is not optional. It is your ultimate edge.”",
    "“Cut your losses short and let your winners run — respect the 18pt guardrail.”",
    "“The market is a device for transferring money from the impatient to the patient.” — Benjamin Graham"
]

# ==========================================
# GOOGLE SHEETS CONNECTION HANDLER
# ==========================================
@st.cache_resource(ttl=300)
def init_gspread():
    """Initializes gspread client using Streamlit Secrets or fallback."""
    if not HAS_GSPREAD:
        return None, "gspread library not installed."

    try:
        # Check if secrets contain service account credentials
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(creds)
            return client, None
        else:
            return None, "No 'gcp_service_account' key found in st.secrets."
    except Exception as e:
        return None, str(e)

def get_sheet_data(sheet_name):
    """Fetch dataframe from a specific tab in Google Sheets."""
    client, error = init_gspread()
    sheet_id = st.secrets.get("sheet_id", None) if "sheet_id" in st.secrets else None

    # Session state local fallback if no Google Sheets configured
    if "session_db" not in st.session_state:
        st.session_state.session_db = {
            "Buy_Log": pd.DataFrame(columns=["Date", "Trade_ID", "Instrument", "Entry_Time", "Exit_Time", "Entry_Price", "Exit_Price", "Points_SL", "Points_Gained", "Lots", "PnL", "Notes"]),
            "Sell_Log": pd.DataFrame(columns=["Date", "Trade_ID", "Strategy", "CE_Entry", "CE_Exit", "PE_Entry", "PE_Exit", "SL_Percentage", "Lots", "Total_PnL", "Status", "Notes"]),
            "Events": pd.DataFrame(columns=["Date", "Time", "Country", "Event_Name", "Impact_Level"]),
            "Results": pd.DataFrame(columns=["Date", "Time", "Company_Symbol", "Market_Expectation"])
        }

    if client and sheet_id:
        try:
            spreadsheet = client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            records = worksheet.get_all_records()
            if records:
                df = pd.DataFrame(records)
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            st.warning(f"Google Sheets Sync Warning ({sheet_name}): {e}. Using local storage fallback.")
            return st.session_state.session_db.get(sheet_name, pd.DataFrame())
    else:
        return st.session_state.session_db.get(sheet_name, pd.DataFrame())

def append_sheet_row(sheet_name, row_data):
    """Append a row to a tab in Google Sheets or local fallback."""
    client, error = init_gspread()
    sheet_id = st.secrets.get("sheet_id", None) if "sheet_id" in st.secrets else None

    # Always update local state for immediate reactivity
    if sheet_name in st.session_state.session_db:
        new_df = pd.DataFrame([row_data])
        st.session_state.session_db[sheet_name] = pd.concat(
            [st.session_state.session_db[sheet_name], new_df], ignore_index=True
        )

    if client and sheet_id:
        try:
            spreadsheet = client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.append_row(list(row_data.values()))
            return True, "Successfully synced to Google Sheets!"
        except Exception as e:
            return False, f"Row saved locally, but Google Sheets update failed: {e}"
    else:
        return True, "Row saved to local session database."

def clear_sheet_tab(sheet_name):
    """Clears all data in a tab except headers."""
    client, error = init_gspread()
    sheet_id = st.secrets.get("sheet_id", None) if "sheet_id" in st.secrets else None

    if sheet_name in st.session_state.session_db:
        cols = st.session_state.session_db[sheet_name].columns
        st.session_state.session_db[sheet_name] = pd.DataFrame(columns=cols)

    if client and sheet_id:
        try:
            spreadsheet = client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            headers = worksheet.row_values(1)
            worksheet.clear()
            if headers:
                worksheet.append_row(headers)
            return True
        except Exception as e:
            return False
    return True

# ==========================================
# APP HEADER & ALERT SYSTEM
# ==========================================
today_str = datetime.date.today().strftime("%Y-%m-%d")

st.markdown(f"""
<div class="neon-card neon-card-cyan" style="padding: 15px 25px;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 2rem;" class="neon-text-cyan">⚡ SUPER APP NIFTY</h1>
            <p style="margin: 5px 0 0 0; color: #8892B0; font-size: 0.9rem;">
                Execution Engine • Risk Guardrails • Multi-Leg Trading Journal
            </p>
        </div>
        <div style="text-align: right;">
            <span class="badge badge-cyan">📅 {datetime.datetime.now().strftime("%A, %b %d, %Y")}</span>
            <span class="badge badge-green" style="margin-left: 8px;">🟢 NIFTY LOT = 65 QTY</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Quote Banner
quote_of_day = random.choice(TRADING_QUOTES)
st.markdown(f'<div class="quote-box">{quote_of_day}</div>', unsafe_allow_html=True)

# Load database tables
df_buy = get_sheet_data("Buy_Log")
df_sell = get_sheet_data("Sell_Log")
df_events = get_sheet_data("Events")
df_results = get_sheet_data("Results")

# Today's Market Alerts Header
today_events = df_events[df_events["Date"] == today_str] if not df_events.empty and "Date" in df_events.columns else pd.DataFrame()
today_results = df_results[df_results["Date"] == today_str] if not df_results.empty and "Date" in df_results.columns else pd.DataFrame()

if not today_events.empty or not today_results.empty:
    st.markdown(f"""
    <div class="neon-card neon-card-green">
        <h4 style="margin:0 0 10px 0;" class="neon-text-yellow">🚨 TODAY'S MARKET ALERTS ({today_str})</h4>
    </div>
    """, unsafe_allow_html=True)

    col_e, col_r = st.columns(2)
    with col_e:
        if not today_events.empty:
            st.write("##### 🌐 Economic Events Today")
            for _, row in today_events.iterrows():
                st.markdown(f"• **{row.get('Time','--')}** | `{row.get('Country','ALL')}` - **{row.get('Event_Name','Event')}** (Impact: `{row.get('Impact_Level','High')}`)")
    with col_r:
        if not today_results.empty:
            st.write("##### 📊 Corporate Earnings Today")
            for _, row in today_results.iterrows():
                st.markdown(f"• **{row.get('Company_Symbol','Company')}** | Time: `{row.get('Time','--')}` | Expectation: `{row.get('Market_Expectation','N/A')}`")

# Main Navigation Tabs
tab_dash, tab_buy, tab_sell, tab_events = st.tabs([
    "🏠 Dashboard & Metrics",
    "🟢 Option Buying (Max 18pt Risk)",
    "🔴 Option Selling (30% SL Rule)",
    "📅 Events & Earnings Tracker"
])

# ==========================================
# TAB 1: DASHBOARD & SUMMARY METRICS
# ==========================================
with tab_dash:
    st.markdown("### 📈 Performance Overview")

    # Calculate Total PnL
    pnl_buy = pd.to_numeric(df_buy["PnL"], errors="coerce").sum() if not df_buy.empty and "PnL" in df_buy.columns else 0.0
    pnl_sell = pd.to_numeric(df_sell["Total_PnL"], errors="coerce").sum() if not df_sell.empty and "Total_PnL" in df_sell.columns else 0.0
    total_pnl = pnl_buy + pnl_sell

    count_buy = len(df_buy) if not df_buy.empty else 0
    count_sell = len(df_sell) if not df_sell.empty else 0
    total_trades = count_buy + count_sell

    wins_buy = len(df_buy[pd.to_numeric(df_buy["PnL"], errors="coerce") > 0]) if not df_buy.empty and "PnL" in df_buy.columns else 0
    wins_sell = len(df_sell[pd.to_numeric(df_sell["Total_PnL"], errors="coerce") > 0]) if not df_sell.empty and "Total_PnL" in df_sell.columns else 0
    win_rate = ((wins_buy + wins_sell) / total_trades * 100) if total_trades > 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        pnl_color = "normal" if total_pnl >= 0 else "inverse"
        st.metric("Total Cumulative PnL", f"₹{total_pnl:,.2f}", delta=f"₹{total_pnl:,.2f}", delta_color=pnl_color)
    with m2:
        st.metric("Option Buying PnL", f"₹{pnl_buy:,.2f}", delta=f"{count_buy} Trades")
    with m3:
        st.metric("Option Selling PnL", f"₹{pnl_sell:,.2f}", delta=f"{count_sell} Trades")
    with m4:
        st.metric("Overall Win Rate", f"{win_rate:.1f}%", delta=f"{total_trades} Total Executions")

    st.divider()

    st.markdown("### 🛠️ Data & Database Management")
    c_d1, c_d2 = st.columns(2)

    with c_d1:
        st.write("##### 📥 Export Trade Logs")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_buy.to_excel(writer, sheet_name='Buy_Log', index=False)
            df_sell.to_excel(writer, sheet_name='Sell_Log', index=False)
            df_events.to_excel(writer, sheet_name='Events', index=False)
            df_results.to_excel(writer, sheet_name='Results', index=False)

        st.download_button(
            label="📦 Download Complete Journal (Excel)",
            data=buffer.getvalue(),
            file_name=f"Super_App_Nifty_Journal_{today_str}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )

    with c_d2:
        st.write("##### ⚠️ Wipe Database (New Month / Quarter)")
        with st.popover("🚨 Clear Database Tables"):
            st.error("Warning: This will clear data from your active tabs.")
            confirm_check = st.checkbox("I confirm I want to wipe all records.")
            if st.button("🔴 Permanently Clear All Tables", disabled=not confirm_check, use_container_width=True):
                clear_sheet_tab("Buy_Log")
                clear_sheet_tab("Sell_Log")
                st.success("Database reset successfully!")
                st.rerun()

# ==========================================
# TAB 2: OPTION BUYING (CALCULATOR & JOURNAL)
# ==========================================
with tab_buy:
    st.markdown("""
    <div class="neon-card neon-card-green">
        <h3 class="neon-text-green" style="margin:0;">🟢 OPTION BUYING MODULE</h3>
        <p style="margin:5px 0 0 0; color:#8892B0;">Strict 18-Point Risk Limit Guardrail • Target & Trailing SL Engine</p>
    </div>
    """, unsafe_allow_html=True)

    # --- TOP SECTION: CALCULATOR ---
    st.write("#### 📐 1. Risk & Target Calculator")

    calc_c1, calc_c2, calc_c3 = st.columns(3)
    with calc_c1:
        buy_entry = st.number_input("Entry Price (₹)", min_value=1.0, value=150.0, step=0.5, key="b_entry")
    with calc_c2:
        buy_sl = st.number_input("Stop Loss Price (₹)", min_value=0.5, value=135.0, step=0.5, key="b_sl")
    with calc_c3:
        buy_lots = st.number_input("Number of Lots (65 Qty/Lot)", min_value=1, value=1, step=1, key="b_lots")

    risk_points = buy_entry - buy_sl
    total_qty = buy_lots * 65
    max_risk_inr = risk_points * total_qty

    # --- GUARDRAIL CHECK ---
    if risk_points > 18.0:
        st.markdown(f"""
        <div class="guardrail-alert">
            🚨 GUARDRAIL VIOLATED! RISK IS {risk_points:.1f} POINTS (MAX ALLOWED IS 18.0 POINTS)<br/>
            <span style="font-size:0.9rem; font-weight:normal;">Do NOT execute this trade! Adjust your entry or reduce stop loss points.</span>
        </div>
        """, unsafe_allow_html=True)
    elif risk_points <= 0:
        st.warning("Stop Loss must be strictly below Entry Price.")
    else:
        st.success(f"✅ Risk Approved: **{risk_points:.1f} Pts** | Total Risk: **₹{max_risk_inr:,.2f}** ({buy_lots} Lot / {total_qty} Qty)")

        # Target Grid Table (1:1 to 1:6)
        ratios = [1, 2, 3, 4, 5, 6]
        targets_data = []
        for r in ratios:
            target_pts = risk_points * r
            target_price = buy_entry + target_pts
            proj_profit = target_pts * total_qty
            trailing_sl = buy_entry + (risk_points * (r - 1)) if r > 1 else buy_entry
            targets_data.append({
                "Risk : Reward": f"1 : {r}",
                "Target Price (₹)": f"{target_price:.2f}",
                "Target Points": f"+{target_pts:.1f} pts",
                "Profit Projection": f"₹{proj_profit:,.2f}",
                "Recommended Trailing SL": f"{trailing_sl:.2f} ₹" if r > 1 else "At Entry"
            })

        df_targets = pd.DataFrame(targets_data)
        st.table(df_targets)

    st.divider()

    # --- BOTTOM SECTION: BUYING JOURNAL ---
    st.write("#### 📝 2. Log Option Buying Trade")

    with st.form("buy_trade_form", clear_on_submit=True):
        j_c1, j_c2, j_c3, j_c4 = st.columns(4)
        with j_c1:
            log_date = st.date_input("Trade Date", datetime.date.today())
            log_instrument = st.text_input("Strike / Instrument", value="NIFTY 24500 CE")
        with j_c2:
            log_entry_time = st.time_input("Entry Time", datetime.time(9, 20))
            log_exit_time = st.time_input("Exit Time", datetime.time(9, 45))
        with j_c3:
            log_entry_price = st.number_input("Actual Entry Price (₹)", min_value=0.1, value=150.0, step=0.5)
            log_exit_price = st.number_input("Actual Exit Price (₹)", min_value=0.1, value=165.0, step=0.5)
        with j_c4:
            log_sl_pts = st.number_input("SL Points Used", min_value=0.1, max_value=18.0, value=min(15.0, max(0.1, risk_points)))
            log_lots = st.number_input("Lots Executed", min_value=1, value=1)

        st.markdown("##### 📝 Trade Notes & Post-Mortem")
        log_notes = st.text_area(
            "Notes (MANDATORY if trade ended in LOSS)",
            placeholder="Describe setup, emotional state, rationale, or mistake analysis..."
        )

        submit_buy = st.form_submit_button("🚀 Submit Buying Trade Log", use_container_width=True)

        if submit_buy:
            calc_pts = log_exit_price - log_entry_price
            calc_pnl = calc_pts * (log_lots * 65)

            # MANDATORY LOSS NOTES GUARDRAIL
            if calc_pnl < 0 and not log_notes.strip():
                st.error("🚨 SUBMISSION REJECTED: Trade resulted in a LOSS! Detailed notes are strictly MANDATORY.")
            else:
                trade_id = f"BUY-{random.randint(1000,9999)}"
                row_data = {
                    "Date": str(log_date),
                    "Trade_ID": trade_id,
                    "Instrument": log_instrument,
                    "Entry_Time": str(log_entry_time),
                    "Exit_Time": str(log_exit_time),
                    "Entry_Price": log_entry_price,
                    "Exit_Price": log_exit_price,
                    "Points_SL": log_sl_pts,
                    "Points_Gained": round(calc_pts, 2),
                    "Lots": log_lots,
                    "PnL": round(calc_pnl, 2),
                    "Notes": log_notes
                }

                success, msg = append_sheet_row("Buy_Log", row_data)
                if success:
                    st.success(f"✅ Trade {trade_id} Logged! PnL: ₹{calc_pnl:,.2f}")
                    st.rerun()
                else:
                    st.error(msg)

    # Table of Recent Buying Trades
    st.write("##### 📊 Buying Trade History")
    df_buy_show = get_sheet_data("Buy_Log")
    if not df_buy_show.empty:
        st.dataframe(df_buy_show, use_container_width=True)
    else:
        st.info("No buying trades logged yet.")

# ==========================================
# TAB 3: OPTION SELLING (30% SL & MULTI-LEG)
# ==========================================
with tab_sell:
    st.markdown("""
    <div class="neon-card neon-card-red">
        <h3 class="neon-text-red" style="margin:0;">🔴 OPTION SELLING MODULE</h3>
        <p style="margin:5px 0 0 0; color:#8892B0;">Default 30% SL Rule Calculator • Multi-Leg Straddle/Strangle Journal</p>
    </div>
    """, unsafe_allow_html=True)

    # --- TOP SECTION: 30% SL CALCULATOR ---
    st.write("#### 📐 1. Stop Loss Calculator (30% Rule)")

    s_c1, s_c2, s_c3 = st.columns(3)
    with s_c1:
        sell_entry = st.number_input("Entry Premium Price (₹)", min_value=1.0, value=100.0, step=0.5, key="s_entry")
    with s_c2:
        sl_pct = st.number_input("SL Percentage (%)", min_value=1.0, max_value=100.0, value=30.0, step=1.0, key="s_pct")
    with s_c3:
        sell_lots = st.number_input("Number of Lots (65 Qty/Lot)", min_value=1, value=1, step=1, key="s_lots")

    sl_trigger_price = sell_entry * (1 + (sl_pct / 100.0))
    risk_pts_sell = sl_trigger_price - sell_entry
    total_qty_sell = sell_lots * 65
    max_loss_sell = risk_pts_sell * total_qty_sell

    st.markdown(f"""
    <div class="neon-card neon-card-cyan" style="padding:15px; text-align:center;">
        <span style="font-size:1.1rem;">Exact SL Trigger Price: <strong class="neon-text-red">₹{sl_trigger_price:.2f}</strong></span> |
        <span>Risk: <strong>+{risk_pts_sell:.2f} Pts</strong> ({sl_pct}%)</span> |
        <span>Max Loss: <strong class="neon-text-red">₹{max_loss_sell:,.2f}</strong></span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- BOTTOM SECTION: SELLING MULTI-LEG JOURNAL ---
    st.write("#### 📝 2. Log Option Selling Trade (Multi-Leg Supported)")

    with st.form("sell_trade_form", clear_on_submit=True):
        strategy_name = st.selectbox("Strategy Type", ["Short Straddle", "Short Strangle", "Naked CE Sell", "Naked PE Sell"])

        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("##### 🟢 CE Leg (Call Option)")
            ce_entry = st.number_input("CE Entry Price (₹)", min_value=0.0, value=100.0, step=0.5)
            ce_exit = st.number_input("CE Exit Price (₹)", min_value=0.0, value=70.0, step=0.5)
        with sc2:
            st.markdown("##### 🔴 PE Leg (Put Option)")
            pe_entry = st.number_input("PE Entry Price (₹)", min_value=0.0, value=100.0, step=0.5)
            pe_exit = st.number_input("PE Exit Price (₹)", min_value=0.0, value=130.0, step=0.5)

        st.divider()
        sc3, sc4, sc5 = st.columns(3)
        with sc3:
            s_date = st.date_input("Trade Date", datetime.date.today(), key="s_date")
        with sc4:
            s_lots_log = st.number_input("Lots Executed", min_value=1, value=1, key="s_lots_log")
        with sc5:
            s_status = st.selectbox("Status", ["SL Hit", "Target Achieved", "Square-off at Close"])

        s_notes = st.text_area("Trade Notes / Strategy Remarks", placeholder="Reason for entry, IV remarks, delta adjust notes...")

        submit_sell = st.form_submit_button("🚀 Submit Selling Trade Log", use_container_width=True)

        if submit_sell:
            ce_pnl_pts = ce_entry - ce_exit
            pe_pnl_pts = pe_entry - pe_exit
            total_sell_pts = ce_pnl_pts + pe_pnl_pts
            total_sell_pnl = total_sell_pts * (s_lots_log * 65)

            # MANDATORY LOSS NOTES CHECK
            if total_sell_pnl < 0 and not s_notes.strip():
                st.error("🚨 SUBMISSION REJECTED: Selling trade resulted in a LOSS! Detailed notes are strictly MANDATORY.")
            else:
                trade_id = f"SELL-{random.randint(1000,9999)}"
                row_data = {
                    "Date": str(s_date),
                    "Trade_ID": trade_id,
                    "Strategy": strategy_name,
                    "CE_Entry": ce_entry,
                    "CE_Exit": ce_exit,
                    "PE_Entry": pe_entry,
                    "PE_Exit": pe_exit,
                    "SL_Percentage": sl_pct,
                    "Lots": s_lots_log,
                    "Total_PnL": round(total_sell_pnl, 2),
                    "Status": s_status,
                    "Notes": s_notes
                }

                success, msg = append_sheet_row("Sell_Log", row_data)
                if success:
                    st.success(f"✅ Selling Trade {trade_id} Logged! Total PnL: ₹{total_sell_pnl:,.2f}")
                    st.rerun()
                else:
                    st.error(msg)

    # Table of Selling Trades
    st.write("##### 📊 Selling Trade History")
    df_sell_show = get_sheet_data("Sell_Log")
    if not df_sell_show.empty:
        st.dataframe(df_sell_show, use_container_width=True)
    else:
        st.info("No selling trades logged yet.")

# ==========================================
# TAB 4: EVENTS & RESULTS TRACKER
# ==========================================
with tab_events:
    st.markdown("### 📅 Economic Events & Corporate Earnings Manager")

    col_ev1, col_ev2 = st.columns(2)

    with col_ev1:
        st.markdown("#### 🌐 Add Economic Event")
        with st.form("form_event", clear_on_submit=True):
            e_date = st.date_input("Date", datetime.date.today(), key="e_d")
            e_time = st.time_input("Time", datetime.time(17, 30), key="e_t")
            e_country = st.selectbox("Country", ["US", "INDIA", "EU", "UK", "CHINA"])
            e_name = st.text_input("Event Name", placeholder="US CPI Data / RBI Rate Decision")
            e_impact = st.selectbox("Impact Level", ["HIGH", "MEDIUM", "LOW"])

            if st.form_submit_button("➕ Add Economic Event", use_container_width=True):
                row_data = {
                    "Date": str(e_date),
                    "Time": str(e_time),
                    "Country": e_country,
                    "Event_Name": e_name,
                    "Impact_Level": e_impact
                }
                append_sheet_row("Events", row_data)
                st.success("Event Added!")
                st.rerun()

    with col_ev2:
        st.markdown("#### 📊 Add Corporate Earnings Result")
        with st.form("form_result", clear_on_submit=True):
            r_date = st.date_input("Date", datetime.date.today(), key="r_d")
            r_time = st.selectbox("Timing", ["Before Market Open", "During Market Hours", "After Market Close"])
            r_symbol = st.text_input("Company Symbol", placeholder="RELIANCE / INFOSYS / TCS")
            r_exp = st.text_input("Market Expectation", placeholder="PAT +12% YoY, Margin expansion")

            if st.form_submit_button("➕ Add Corporate Result", use_container_width=True):
                row_data = {
                    "Date": str(r_date),
                    "Time": r_time,
                    "Company_Symbol": r_symbol,
                    "Market_Expectation": r_exp
                }
                append_sheet_row("Results", row_data)
                st.success("Result Added!")
                st.rerun()

    st.divider()

    st.write("#### 📜 Scheduled Events & Earnings Database")
    ev_c1, ev_c2 = st.columns(2)
    with ev_c1:
        st.write("##### Economic Events")
        st.dataframe(get_sheet_data("Events"), use_container_width=True)
    with ev_c2:
        st.write("##### Corporate Earnings")
        st.dataframe(get_sheet_data("Results"), use_container_width=True)
