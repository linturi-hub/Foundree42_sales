import streamlit as st
import groq
import sqlite3
import json
import re
import requests
from datetime import datetime

st.set_page_config(
    page_title="Foundree42 | Lead Intelligence",
    page_icon="F",
    layout="wide"
)

# ── CSS ───────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #e8ecf1; }
    [data-testid="stSidebar"] { background-color: #e8ecf1; border-right: none; }
    [data-testid="stHeader"] { background: transparent; }
    .main .block-container { padding-top: 2rem; padding-left: 2rem; padding-right: 2rem; }
    h1, h2, h3 { color: #2d3748 !important; font-family: 'Segoe UI', sans-serif !important; font-weight: 600 !important; }
    p, li, .stMarkdown { color: #4a5568 !important; font-family: 'Segoe UI', sans-serif !important; }
    label { color: #718096 !important; font-size: 0.8rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; font-family: 'Segoe UI', sans-serif !important; }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background: #e8ecf1 !important; border: none !important; border-radius: 10px !important;
        color: #2d3748 !important; font-family: 'Segoe UI', sans-serif !important; font-size: 0.9rem !important;
        box-shadow: inset 3px 3px 6px #c5cad4, inset -3px -3px 6px #ffffff !important; padding: 10px 14px !important;
    }
    .stTextInput > div > div > input::placeholder, .stTextArea > div > div > textarea::placeholder { color: #a0aec0 !important; }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        box-shadow: inset 4px 4px 8px #b8bec9, inset -4px -4px 8px #ffffff !important; outline: none !important;
    }
    .stSelectbox > div > div, .stSelectbox > div > div > div,
    .stSelectbox div[data-baseweb="select"], .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] span, .stSelectbox div[data-baseweb="select"] div,
    [data-baseweb="select"] > div {
        background: #e8ecf1 !important; border: none !important; border-radius: 10px !important;
        color: #2d3748 !important; font-family: 'Segoe UI', sans-serif !important; font-size: 0.9rem !important;
        box-shadow: inset 3px 3px 6px #c5cad4, inset -3px -3px 6px #ffffff !important;
    }
    [data-baseweb="select"] span, [data-baseweb="select"] div { color: #2d3748 !important; }
    [data-baseweb="popover"] {
        background: #e8ecf1 !important; border: none !important;
        box-shadow: 6px 6px 12px #c5cad4, -6px -6px 12px #ffffff !important; border-radius: 10px !important;
    }
    [data-baseweb="menu"] { background: #e8ecf1 !important; }
    [data-baseweb="option"] { background: #e8ecf1 !important; color: #2d3748 !important; font-family: 'Segoe UI', sans-serif !important; }
    [data-baseweb="option"]:hover { background: #dde1e7 !important; }
    .stButton > button {
        background: #e8ecf1 !important; color: #2d3748 !important; border: none !important;
        border-radius: 10px !important; font-family: 'Segoe UI', sans-serif !important;
        font-weight: 600 !important; font-size: 0.875rem !important; padding: 10px 24px !important;
        box-shadow: 4px 4px 8px #c5cad4, -4px -4px 8px #ffffff !important;
        transition: all 0.2s ease !important; width: 100% !important;
    }
    .stButton > button:hover { box-shadow: 2px 2px 4px #c5cad4, -2px -2px 4px #ffffff !important; color: #4a6fa5 !important; }
    .stButton > button:active { box-shadow: inset 2px 2px 4px #c5cad4, inset -2px -2px 4px #ffffff !important; }
    .stButton > button[kind="primary"] { background: #4a6fa5 !important; color: #ffffff !important; box-shadow: 4px 4px 8px #c5cad4, -4px -4px 8px #ffffff !important; }
    .stButton > button[kind="primary"]:hover { background: #3d5d8f !important; color: #ffffff !important; }
    [data-testid="stMetric"] { background: #e8ecf1; border-radius: 14px; padding: 16px 20px; box-shadow: 5px 5px 10px #c5cad4, -5px -5px 10px #ffffff; }
    [data-testid="stMetricLabel"] { color: #718096 !important; font-size: 0.7rem !important; text-transform: uppercase !important; letter-spacing: 1px !important; font-family: 'Segoe UI', sans-serif !important; }
    [data-testid="stMetricValue"] { color: #2d3748 !important; font-size: 1.8rem !important; font-weight: 700 !important; font-family: 'Segoe UI', sans-serif !important; }
    .stTabs [data-baseweb="tab-list"] { background: #e8ecf1; border-radius: 12px; padding: 4px; box-shadow: inset 3px 3px 6px #c5cad4, inset -3px -3px 6px #ffffff; gap: 4px; border-bottom: none !important; }
    .stTabs [data-baseweb="tab"] { background: transparent !important; color: #718096 !important; border-radius: 8px !important; font-family: 'Segoe UI', sans-serif !important; font-weight: 500 !important; font-size: 0.875rem !important; border: none !important; padding: 8px 20px !important; }
    .stTabs [aria-selected="true"] { background: #e8ecf1 !important; color: #4a6fa5 !important; box-shadow: 3px 3px 6px #c5cad4, -3px -3px 6px #ffffff !important; }
    .streamlit-expanderHeader { background: #e8ecf1 !important; border-radius: 10px !important; border: none !important; box-shadow: 3px 3px 6px #c5cad4, -3px -3px 6px #ffffff !important; color: #2d3748 !important; font-weight: 600 !important; font-family: 'Segoe UI', sans-serif !important; padding: 12px 16px !important; }
    .streamlit-expanderContent { background: #e8ecf1 !important; border: none !important; border-radius: 0 0 10px 10px !important; padding: 16px !important; }
    .stSlider > div > div > div > div { background: #4a6fa5 !important; }
    div[data-testid="stSuccessMessage"] { background: #e8ecf1 !important; border-radius: 10px !important; border-left: 3px solid #68d391 !important; box-shadow: 3px 3px 6px #c5cad4, -3px -3px 6px #ffffff !important; color: #2d3748 !important; }
    div[data-testid="stInfoMessage"] { background: #e8ecf1 !important; border-radius: 10px !important; border-left: 3px solid #63b3ed !important; box-shadow: 3px 3px 6px #c5cad4, -3px -3px 6px #ffffff !important; color: #2d3748 !important; }
    div[data-testid="stWarningMessage"] { background: #e8ecf1 !important; border-radius: 10px !important; border-left: 3px solid #f6ad55 !important; box-shadow: 3px 3px 6px #c5cad4, -3px -3px 6px #ffffff !important; color: #2d3748 !important; }
    div[data-testid="stErrorMessage"] { background: #e8ecf1 !important; border-radius: 10px !important; border-left: 3px solid #fc8181 !important; box-shadow: 3px 3px 6px #c5cad4, -3px -3px 6px #ffffff !important; color: #2d3748 !important; }
    hr { border: none !important; height: 1px !important; background: linear-gradient(to right, transparent, #c5cad4, transparent) !important; margin: 1.5rem 0 !important; }
    .stSpinner > div { border-top-color: #4a6fa5 !important; }
    .sidebar-brand { background: #e8ecf1; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 5px 5px 10px #c5cad4, -5px -5px 10px #ffffff; text-align: center; }
    .sidebar-brand h2 { font-size: 1.5rem !important; color: #2d3748 !important; margin: 0 !important; font-family: 'Segoe UI', sans-serif !important; }
    .sidebar-brand p { font-size: 0.7rem !important; color: #a0aec0 !important; letter-spacing: 2px !important; text-transform: uppercase !important; margin: 4px 0 0 0 !important; font-family: 'Segoe UI', sans-serif !important; }
    .stCaption, .stCaption p { color: #a0aec0 !important; font-size: 0.75rem !important; font-family: 'Segoe UI', sans-serif !important; }
    code { background: #dde1e7 !important; color: #2d3748 !important; border-radius: 4px !important; padding: 2px 6px !important; font-size: 0.85rem !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>Foundree42</h2>
        <p>Lead Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    api_key = st.text_input("Groq API Key", type="password", placeholder="paste your key here")
    if api_key:
        st.session_state["api_key"] = api_key
        st.success("API key active")

    st.markdown("---")

    try:
        conn = sqlite3.connect("foundree42.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM leads")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM leads WHERE score >= 80")
        hot = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM leads WHERE status=?", ("contacted",))
        contacted = c.fetchone()[0]
        conn.close()
    except:
        total = hot = contacted = 0

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total", total)
    with col_b:
        st.metric("Hot", hot)
    st.metric("Contacted", contacted)
    st.markdown("---")
    st.caption("Built for Foundree42 Sales Team")

# ── DATABASE ──────────────────────────────────────
DB_PATH = "foundree42.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            company         TEXT NOT NULL,
            industry        TEXT DEFAULT '',
            size            TEXT DEFAULT '',
            hq              TEXT DEFAULT '',
            ceo             TEXT DEFAULT '',
            current_crm     TEXT DEFAULT '',
            score           INTEGER DEFAULT 0,
            overview        TEXT DEFAULT '',
            pain_points     TEXT DEFAULT '[]',
            recent_triggers TEXT DEFAULT '[]',
            best_contact    TEXT DEFAULT '',
            pitch_angle     TEXT DEFAULT '',
            status          TEXT DEFAULT 'new',
            created_at      TEXT DEFAULT '',
            linkedin_dm     TEXT DEFAULT '',
            cold_email      TEXT DEFAULT '',
            subject_line    TEXT DEFAULT '',
            followup        TEXT DEFAULT '',
            connection_note TEXT DEFAULT '',
            icp_match       TEXT DEFAULT '',
            cta             TEXT DEFAULT ''
        )
    """)
    # Safely add any missing columns for existing databases
    existing_cols = [
        row[1] for row in conn.execute("PRAGMA table_info(leads)").fetchall()
    ]
    new_cols = {
        "linkedin_dm": "TEXT DEFAULT ''",
        "cold_email": "TEXT DEFAULT ''",
        "subject_line": "TEXT DEFAULT ''",
        "followup": "TEXT DEFAULT ''",
        "connection_note": "TEXT DEFAULT ''",
        "icp_match": "TEXT DEFAULT ''",
        "cta": "TEXT DEFAULT ''"
    }
    for col, definition in new_cols.items():
        if col not in existing_cols:
            conn.execute(f"ALTER TABLE leads ADD COLUMN {col} {definition}")
    conn.commit()
    conn.close()

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

def save_lead(data):
    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM leads WHERE company=?",
        (data.get("company",""),)
    ).fetchone()
    if existing:
        lead_id = existing["id"]
        conn.close()
        return lead_id
    conn.execute("""
        INSERT INTO leads (
            company, industry, size, hq, ceo, current_crm,
            score, overview, pain_points, recent_triggers,
            best_contact, pitch_angle, status, created_at,
            icp_match, cta
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get("company",""),
        data.get("industry",""),
        data.get("size",""),
        data.get("hq",""),
        data.get("ceo",""),
        data.get("current_crm",""),
        int(data.get("score", 0)),
        data.get("overview",""),
        json.dumps(data.get("pain_points",[])),
        json.dumps(data.get("recent_triggers",[])),
        data.get("best_contact_title",""),
        data.get("pitch_angle",""),
        "new",
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        data.get("icp_match",""),
        data.get("cta","")
    ))
    conn.commit()
    lead_id = conn.execute(
        "SELECT id FROM leads WHERE company=?",
        (data.get("company",""),)
    ).fetchone()["id"]
    conn.close()
    return lead_id

def save_messages(lead_id, messages):
    conn = get_conn()
    conn.execute("""
        UPDATE leads SET
            linkedin_dm     = ?,
            cold_email      = ?,
            subject_line    = ?,
            followup        = ?,
            connection_note = ?
        WHERE id = ?
    """, (
        messages.get("linkedin_dm",""),
        messages.get("cold_email",""),
        messages.get("subject_line",""),
        messages.get("followup",""),
        messages.get("connection_note",""),
        lead_id
    ))
    conn.commit()
    conn.close()

def update_status(lead_id, status):
    conn = get_conn()
    conn.execute(
        "UPDATE leads SET status=? WHERE id=?",
        (status, lead_id)
    )
    conn.commit()
    conn.close()

def get_all_leads():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM leads ORDER BY score DESC"
    ).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]

def get_lead_by_id(lead_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM leads WHERE id=?", (lead_id,)
    ).fetchone()
    conn.close()
    return row_to_dict(row)

# ── AI ────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a sales intelligence analyst for Foundree42, "
    "a senior-led Salesforce consultancy based in the UK "
    "that primarily targets US-based companies. "
    "Foundree42 serves these ideal client profiles: "
    "ICP1: $1B+ firms with underperforming Salesforce partners needing a senior-led reset. "
    "ICP2: $500M-$3B orgs with fragmented partners needing platform governance. "
    "ICP3: $50M-$500M mid-market with no internal Salesforce team needing virtual support. "
    "ICP4: Companies with inherited messy Salesforce orgs needing an automation audit. "
    "ICP5: Mid-market and enterprise replacing offshore Salesforce delivery. "
    "ICP6: Companies needing trusted senior Salesforce delivery to reduce project risk. "
    "Key buyer roles: Salesforce Platform Owner, VP RevOps, COO, IT Director, "
    "Enterprise Architect, PMO Leader, Admin Lead, Head of CRM. "
    "Always return valid JSON only. No markdown. No explanation. No extra text."
)

def ask_ai(prompt):
    if not st.session_state.get("api_key"):
        return "ERROR: No API key"
    try:
        client = groq.Groq(api_key=st.session_state["api_key"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return "ERROR: " + str(e)

def parse_json(raw):
    clean = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(clean)
    except:
        return {}

# ── LIVE NEWS (free accuracy boost) ───────────────
def get_live_news(company):
    try:
        url = "https://news.google.com/rss/search"
        params = {"q": company + " Salesforce OR CRM OR funding OR hiring OR expansion", "hl": "en-US"}
        resp = requests.get(url, params=params, timeout=5)
        items = re.findall(r"<title>(.*?)</title>", resp.text)[1:4]
        return [re.sub(r"<.*?>", "", i) for i in items]
    except:
        return []

# ── RESEARCH ──────────────────────────────────────
def research_company(company, contact="", title=""):
    # Get live news first for accuracy
    news = get_live_news(company)
    news_context = ""
    if news:
        news_context = " Recent news: " + " | ".join(news) + "."

    prompt = (
        "Research the US company " + company + " for Foundree42."
        + ("Contact: " + contact + " " + title + "." if contact else "")
        + news_context
        + " Identify which Foundree42 ICP they best match."
        + " Return ONLY this JSON:"
        + '{"company":"' + company + '",'
        + '"overview":"2-3 sentence company summary",'
        + '"industry":"their specific industry",'
        + '"size":"employee count and revenue estimate",'
        + '"hq":"city and state, USA",'
        + '"ceo":"current CEO name",'
        + '"current_crm":"their known CRM or Salesforce status",'
        + '"score":75,'
        + '"icp_match":"ICP number and one sentence reason",'
        + '"pain_points":["specific Salesforce pain 1","pain 2","pain 3"],'
        + '"recent_triggers":["trigger 1","trigger 2"],'
        + '"best_contact_title":"exact US job title to target",'
        + '"pitch_angle":"one specific sentence pitch for this company",'
        + '"cta":"one of: Reset Assessment / Governance Workshop / Managed Services Quote / Automation Audit / Delivery Model Review / Talk to Senior Architect"}'
    )
    raw = ask_ai(prompt)
    if raw.startswith("ERROR"):
        return {"error": raw}
    result = parse_json(raw)
    # Inject live news as triggers if available
    if news and result:
        existing = result.get("recent_triggers", [])
        result["recent_triggers"] = (news + existing)[:4]
    return result

# ── DISCOVER ──────────────────────────────────────
def discover_leads(industry, location, revenue, size, signals, count):
    prompt = (
        "Find " + str(count) + " real US-based companies "
        "that are ideal Salesforce consultancy clients for Foundree42. "
        "Search criteria: "
        "Industry=" + industry
        + " Location=" + location
        + " Revenue=" + revenue
        + " Size=" + size
        + " Buying signals=" + signals
        + ". Match against Foundree42 ICPs. "
        "Return ONLY a JSON array:"
        + '[{"company":"exact company name",'
        + '"industry":"specific industry",'
        + '"size":"size estimate",'
        + '"location":"city, state",'
        + '"revenue":"revenue estimate",'
        + '"why_fit":"one sentence ICP match reason",'
        + '"trigger":"specific buying signal",'
        + '"best_contact":"exact US job title",'
        + '"score":80}]'
        + " Real companies only. No placeholders."
    )
    raw = ask_ai(prompt)
    if raw.startswith("ERROR"):
        st.error(raw)
        return []
    result = parse_json(raw)
    return result if isinstance(result, list) else []

# ── MESSAGES ──────────────────────────────────────
def generate_messages(lead_data, feedback=""):
    prompt = (
        "Write personalised Salesforce consultancy outreach "
        "for the US company " + lead_data.get("company","")
        + ". ICP: " + (lead_data.get("icp_match") or "")
        + ". Industry: " + (lead_data.get("industry") or "")
        + ". Overview: " + (lead_data.get("overview") or "")
        + ". Pains: " + str(lead_data.get("pain_points") or [])
        + ". Triggers: " + str(lead_data.get("recent_triggers") or [])
        + ". Pitch: " + (lead_data.get("pitch_angle") or "")
        + ". CTA: " + (lead_data.get("cta") or "")
        + (". Boss feedback to apply: " + feedback if feedback else "")
        + ". Rules: reference specific company facts, "
        "never say I hope this finds you well, "
        "never say I wanted to reach out, "
        "sound human not templated, "
        "sign off as the Foundree42 team. "
        "Return ONLY this JSON:"
        + '{"subject_line":"subject under 10 words",'
        + '"linkedin_dm":"DM under 180 words ending with the CTA",'
        + '"cold_email":"email 150-200 words ending with one easy question",'
        + '"followup":"followup under 120 words with a new angle",'
        + '"connection_note":"LinkedIn connection request under 70 words"}'
    )
    raw = ask_ai(prompt)
    if raw.startswith("ERROR"):
        return {"error": raw}
    return parse_json(raw)

# ── INIT ──────────────────────────────────────────
init_db()

# ── TABS ──────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Lead Discovery",
    "Company Research",
    "LinkedIn Workflow",
    "Lead Database"
])

# ════════════════════════════════════════════════
# TAB 1 — LEAD DISCOVERY
# ════════════════════════════════════════════════
with tab1:
    st.markdown("## Lead Discovery")
    st.markdown(
        "Define your search criteria and the AI will find "
        "matching US companies with buying signals."
    )
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        icp_industry = st.text_input(
            "Industry",
            placeholder="e.g. Financial Services, Healthcare, Manufacturing"
        )
        icp_location = st.text_input(
            "Location",
            placeholder="e.g. Arizona, New York, United States"
        )
        icp_signals = st.text_area(
            "Buying Signals",
            placeholder="e.g. hiring Salesforce Admin, replacing CRM, recent funding...",
            height=100
        )
    with c2:
        icp_revenue = st.selectbox("Revenue", [
            "Any revenue", "Under $10M", "Under $50M",
            "$50M - $500M", "$500M - $3B", "$1B+", "Over $3B"
        ])
        icp_size = st.selectbox("Company Size", [
            "Any size", "1-50 employees", "50-200 employees",
            "200-500 employees", "500-2,000 employees",
            "2,000-10,000 employees", "10,000+ employees"
        ])
        icp_count = st.slider("Number of leads", 3, 10, 5)

    st.markdown("---")

    if st.button("Discover Leads", type="primary"):
        if not st.session_state.get("api_key"):
            st.error("Add your Groq API key in the sidebar.")
        elif not icp_industry or not icp_location:
            st.error("Fill in Industry and Location.")
        else:
            with st.spinner("Searching for matching companies..."):
                found = discover_leads(
                    industry=icp_industry,
                    location=icp_location,
                    revenue=icp_revenue,
                    size=icp_size,
                    signals=icp_signals or "hiring sales roles, CRM investment, scaling",
                    count=icp_count
                )
            if found:
                st.success("Found " + str(len(found)) + " leads")
                st.session_state["discovered"] = found
            else:
                st.warning("No leads found. Try broader criteria.")

    if st.session_state.get("discovered"):
        st.markdown("---")
        leads_sorted = sorted(
            st.session_state["discovered"],
            key=lambda x: x.get("score", 0),
            reverse=True
        )
        for i, lead in enumerate(leads_sorted):
            score = lead.get("score", 0)
            label = "Hot" if score >= 80 else "Warm" if score >= 60 else "Cold"
            with st.expander(
                lead.get("company","") + "   |   " +
                str(score) + "/100   |   " + label,
                expanded=(i == 0)
            ):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown("**Why they fit**")
                    st.write(lead.get("why_fit",""))
                    st.markdown("**Buying signal**")
                    st.write(lead.get("trigger",""))
                    st.markdown("**Best contact**")
                    st.write(lead.get("best_contact",""))
                    st.caption(
                        lead.get("location","") + "   ·   " +
                        lead.get("size","") + "   ·   " +
                        lead.get("revenue","")
                    )
                with col_b:
                    st.metric("Fit Score", str(score) + "/100")
                st.markdown("---")
                if st.button("Research this company", key="disc_" + str(i)):
                    st.session_state["prefill"] = lead.get("company","")
                    st.info(
                        "Go to Company Research tab — " +
                        lead.get("company","") + " is prefilled"
                    )

# ════════════════════════════════════════════════
# TAB 2 — COMPANY RESEARCH
# ════════════════════════════════════════════════
with tab2:
    st.markdown("## Company Research")
    st.markdown("Research, ICP match, Pitch Angle, CTA and Outreach Messages.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        company_input = st.text_input(
            "Company Name",
            value=st.session_state.get("prefill",""),
            placeholder="e.g. Rogers Corporation"
        )
        contact_input = st.text_input(
            "Contact Name (optional)",
            placeholder="e.g. Sarah Johnson"
        )
    with col2:
        title_input = st.text_input(
            "Contact Title (optional)",
            placeholder="e.g. VP of Sales Operations"
        )
        feedback_input = st.text_area(
            "Boss Feedback to Apply",
            placeholder="e.g. be more direct, lead with ROI...",
            height=104
        )

    st.markdown("---")
    col_x, col_y = st.columns(2)
    with col_x:
        run_pipeline = st.button("Run Full Pipeline", type="primary")
    with col_y:
        research_only = st.button("Research Only")

    if run_pipeline or research_only:
        if not st.session_state.get("api_key"):
            st.error("Add your API key in the sidebar.")
        elif not company_input:
            st.error("Enter a company name.")
        else:
            with st.spinner("Researching " + company_input + "..."):
                intel = research_company(company_input, contact_input, title_input)

            if "error" not in intel and intel:
                score = intel.get("score", 0)
                st.markdown("---")
                st.markdown("### Intelligence Report")

                m1, m2, m3 = st.columns(3)
                m1.metric("Industry", intel.get("industry","—"))
                m2.metric("Company Size", intel.get("size","—"))
                m3.metric("Salesforce Fit", str(score) + " / 100")

                st.markdown("---")
                st.markdown("**Overview**")
                st.write(intel.get("overview",""))

                if intel.get("icp_match"):
                    st.info("ICP Match:   " + intel.get("icp_match",""))

                col_p, col_t = st.columns(2)
                with col_p:
                    st.markdown("**Pain Points**")
                    for p in (intel.get("pain_points") or []):
                        st.markdown("— " + str(p))
                with col_t:
                    st.markdown("**Recent Triggers / News**")
                    for t in (intel.get("recent_triggers") or []):
                        st.markdown("— " + str(t))

                st.markdown("---")
                st.markdown("**Best Contact:**   " + (intel.get("best_contact_title") or "—"))
                st.markdown("**Pitch Angle:**   " + (intel.get("pitch_angle") or "—"))
                if intel.get("cta"):
                    st.warning("Recommended CTA:   " + intel.get("cta",""))

                if run_pipeline:
                    st.markdown("---")
                    st.markdown("### Outreach Messages")

                    with st.spinner("Writing personalised messages..."):
                        messages = generate_messages(intel, feedback_input)

                    if "error" not in messages and messages:
                        mt1, mt2, mt3, mt4 = st.tabs([
                            "LinkedIn DM", "Cold Email",
                            "Follow-up", "Connection Note"
                        ])
                        with mt1:
                            st.text_area(
                                "Copy and paste into LinkedIn",
                                messages.get("linkedin_dm",""),
                                height=200, key="li_msg"
                            )
                        with mt2:
                            st.markdown("**Subject Line**")
                            st.code(messages.get("subject_line",""), language=None)
                            st.text_area(
                                "Email Body",
                                messages.get("cold_email",""),
                                height=200, key="em_msg"
                            )
                        with mt3:
                            st.text_area(
                                "Send if no reply after 5 days",
                                messages.get("followup",""),
                                height=150, key="fu_msg"
                            )
                        with mt4:
                            st.text_area(
                                "Use when sending connection request",
                                messages.get("connection_note",""),
                                height=100, key="cn_msg"
                            )

                        st.markdown("---")

                        # ── SAVE BUTTON ──────────────────────────────
                        if st.button("Save Lead and Messages", type="primary"):
                            lead_id = save_lead(intel)
                            save_messages(lead_id, messages)
                            # Clear prefill so Research tab resets
                            st.session_state["prefill"] = ""
                            st.session_state["last_saved"] = company_input
                            st.success(
                                company_input +
                                " saved. Go to LinkedIn Workflow tab to contact them."
                            )
                            st.rerun()

                    else:
                        st.error("Message error: " + str(messages.get("error","")))
            else:
                st.error("Research failed: " + str(intel.get("error","")))

    # Show confirmation if just saved
    if st.session_state.get("last_saved"):
        st.info(
            st.session_state["last_saved"] +
            " is saved. Check the LinkedIn Workflow tab."
        )

# ════════════════════════════════════════════════
# TAB 3 — LINKEDIN WORKFLOW
# ════════════════════════════════════════════════
with tab3:
    st.markdown("## LinkedIn Workflow")
    st.markdown("Step-by-step contact plan for each saved lead.")
    st.markdown("---")

    # Always fetch fresh from DB
    workflow_leads = get_all_leads()

    if not workflow_leads:
        st.info(
            "No leads saved yet. Go to Company Research, "
            "run the full pipeline and click Save."
        )
    else:
        st.caption(str(len(workflow_leads)) + " leads saved")
        st.markdown("---")

        for lead in workflow_leads:
            lead_id     = lead.get("id")
            comp        = lead.get("company","")
            target      = lead.get("best_contact","") or "VP of Sales"
            score       = lead.get("score", 0) or 0
            status      = lead.get("status","new") or "new"
            conn_note   = lead.get("connection_note","") or ""
            li_dm       = lead.get("linkedin_dm","") or ""
            icp         = lead.get("icp_match","") or ""
            cta_text    = lead.get("cta","") or ""
            has_messages = bool(conn_note or li_dm)

            status_label = (
                "Replied"   if status == "replied"
                else "Contacted" if status == "contacted"
                else "Closed"   if status == "closed"
                else "New"
            )

            msg_indicator = " [Messages ready]" if has_messages else " [No messages yet]"

            with st.expander(
                comp + "   |   " + str(score) + "/100" +
                "   |   " + status_label + msg_indicator
            ):
                search_url = (
                    "https://www.linkedin.com/search/results/people/?keywords=" +
                    (target + " " + comp).replace(" ","%20")
                )

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Target Role**")
                    st.write(target)
                with c2:
                    if icp:
                        st.markdown("**ICP Match**")
                        st.write(icp)

                if cta_text:
                    st.markdown("**Recommended CTA**")
                    st.write(cta_text)

                st.markdown("---")
                st.markdown("**Step 1 — Find them on LinkedIn**")
                st.markdown(
                    "[Search for " + target + " at " + comp + "](" + search_url + ")"
                )

                st.markdown("---")

                if conn_note:
                    st.markdown("**Step 2 — Send connection request**")
                    st.text_area(
                        "Copy this note",
                        conn_note,
                        height=80,
                        key="cn_li_" + str(lead_id)
                    )
                else:
                    st.markdown("**Step 2 — Connection Note**")
                    st.warning(
                        "No connection note saved for this lead. "
                        "Go to Company Research, run the Full Pipeline "
                        "and click Save to generate messages."
                    )

                if li_dm:
                    st.markdown("---")
                    st.markdown("**Step 3 — Send DM after connecting**")
                    st.text_area(
                        "Copy this message",
                        li_dm,
                        height=150,
                        key="dm_li_" + str(lead_id)
                    )

                st.markdown("---")
                s1, s2, s3 = st.columns(3)
                with s1:
                    if st.button("Mark as Contacted", key="c_" + str(lead_id)):
                        update_status(lead_id, "contacted")
                        st.rerun()
                with s2:
                    if st.button("Mark as Replied", key="r_" + str(lead_id)):
                        update_status(lead_id, "replied")
                        st.rerun()
                with s3:
                    if st.button("Mark as Closed", key="cl_" + str(lead_id)):
                        update_status(lead_id, "closed")
                        st.rerun()

# ════════════════════════════════════════════════
# TAB 4 — LEAD DATABASE
# ════════════════════════════════════════════════
with tab4:
    st.markdown("## Lead Database")
    st.markdown("All saved leads with status tracking.")
    st.markdown("---")

    all_leads_db = get_all_leads()

    if not all_leads_db:
        st.info("No leads saved yet.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads", len(all_leads_db))
        m2.metric("Hot Leads", len([l for l in all_leads_db if (l.get("score") or 0) >= 80]))
        m3.metric("Contacted",  len([l for l in all_leads_db if l.get("status") == "contacted"]))
        m4.metric("Replied",    len([l for l in all_leads_db if l.get("status") == "replied"]))

        st.markdown("---")

        fc1, fc2 = st.columns(2)
        with fc1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All","new","ready_to_contact","contacted","replied","closed"]
            )
        with fc2:
            min_score = st.slider("Minimum Score", 0, 100, 0)

        filtered = [
            l for l in all_leads_db
            if (status_filter == "All" or l.get("status") == status_filter)
            and (l.get("score") or 0) >= min_score
        ]

        st.caption("Showing " + str(len(filtered)) + " leads")
        st.markdown("---")

        for lead in filtered:
            lead_id = lead.get("id")
            score   = lead.get("score") or 0
            status  = lead.get("status") or "new"
            label   = "Hot" if score >= 80 else "Warm" if score >= 60 else "Cold"

            # Check if messages are saved
            has_msgs = bool(lead.get("linkedin_dm") or lead.get("cold_email"))
            msg_tag  = " [Messages saved]" if has_msgs else ""

            with st.expander(
                (lead.get("company") or "Unknown") +
                "   |   " + str(score) + "/100" +
                "   |   " + status.capitalize() + msg_tag
            ):
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown("**Industry**")
                    st.write(lead.get("industry") or "—")
                    st.markdown("**Company Size**")
                    st.write(lead.get("size") or "—")
                    st.markdown("**HQ**")
                    st.write(lead.get("hq") or "—")
                    st.markdown("**Best Contact**")
                    st.write(lead.get("best_contact") or "—")
                with d2:
                    st.markdown("**Fit Score**")
                    st.write(str(score) + " / 100")
                    st.markdown("**Added**")
                    st.write(lead.get("created_at") or "—")
                    st.markdown("**Pitch Angle**")
                    st.write(lead.get("pitch_angle") or "—")

                if lead.get("icp_match"):
                    st.markdown("**ICP Match**")
                    st.write(lead.get("icp_match"))

                if lead.get("cta"):
                    st.markdown("**Recommended CTA**")
                    st.write(lead.get("cta"))

                if lead.get("overview"):
                    st.markdown("---")
                    st.markdown("**Overview**")
                    st.write(lead.get("overview"))

                # Messages section
                li_dm      = lead.get("linkedin_dm","") or ""
                cold_email = lead.get("cold_email","") or ""
                followup   = lead.get("followup","") or ""
                subj       = lead.get("subject_line","") or ""
                conn_note  = lead.get("connection_note","") or ""

                if li_dm or cold_email or followup:
                    st.markdown("---")
                    st.markdown("**Saved Messages**")
                    mm1, mm2, mm3, mm4 = st.tabs([
                        "LinkedIn DM", "Cold Email",
                        "Follow-up", "Connection Note"
                    ])
                    with mm1:
                        st.text_area(
                            "LinkedIn DM", li_dm or "Not generated yet",
                            height=150, key="db_li_" + str(lead_id)
                        )
                    with mm2:
                        if subj:
                            st.markdown("**Subject:** " + subj)
                        st.text_area(
                            "Email", cold_email or "Not generated yet",
                            height=150, key="db_em_" + str(lead_id)
                        )
                    with mm3:
                        st.text_area(
                            "Follow-up", followup or "Not generated yet",
                            height=120, key="db_fu_" + str(lead_id)
                        )
                    with mm4:
                        st.text_area(
                            "Connection Note", conn_note or "Not generated yet",
                            height=80, key="db_cn_" + str(lead_id)
                        )
                else:
                    st.markdown("---")
                    st.info(
                        "No messages saved. Run Full Pipeline in "
                        "Company Research and click Save."
                    )

                st.markdown("---")
                valid_statuses = ["new","ready_to_contact","contacted","replied","closed"]
                current_status = status if status in valid_statuses else "new"
                new_status = st.selectbox(
                    "Update Status",
                    valid_statuses,
                    index=valid_statuses.index(current_status),
                    key="status_" + str(lead_id)
                )
                if new_status != current_status:
                    update_status(lead_id, new_status)
                    st.success("Status updated")
                    st.rerun()
