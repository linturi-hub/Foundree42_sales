import streamlit as st
import groq
import sqlite3
import json
import re
from datetime import datetime
 
st.set_page_config(
    page_title="Foundree42 | Lead Intelligence",
    page_icon="F",
    layout="wide"
)
 
# ── CSS ───────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #e8ecf1;
    }
    [data-testid="stSidebar"] {
        background-color: #e8ecf1;
        border-right: none;
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    h1, h2, h3 {
        color: #2d3748 !important;
        font-family: 'Segoe UI', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px !important;
    }
    p, li, .stMarkdown {
        color: #4a5568 !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    label {
        color: #718096 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #e8ecf1 !important;
        border: none !important;
        border-radius: 10px !important;
        color: #2d3748 !important;
        font-family: 'Segoe UI', sans-serif !important;
        font-size: 0.9rem !important;
        box-shadow:
            inset 3px 3px 6px #c5cad4,
            inset -3px -3px 6px #ffffff !important;
        padding: 10px 14px !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #a0aec0 !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        box-shadow:
            inset 4px 4px 8px #b8bec9,
            inset -4px -4px 8px #ffffff !important;
        outline: none !important;
    }
    .stSelectbox > div > div,
    .stSelectbox > div > div > div,
    .stSelectbox div[data-baseweb="select"],
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] span,
    .stSelectbox div[data-baseweb="select"] div,
    [data-baseweb="select"] > div {
        background: #e8ecf1 !important;
        border: none !important;
        border-radius: 10px !important;
        color: #2d3748 !important;
        font-family: 'Segoe UI', sans-serif !important;
        font-size: 0.9rem !important;
        box-shadow:
            inset 3px 3px 6px #c5cad4,
            inset -3px -3px 6px #ffffff !important;
    }
    [data-baseweb="select"] span,
    [data-baseweb="select"] div {
        color: #2d3748 !important;
    }
    [data-baseweb="popover"] {
        background: #e8ecf1 !important;
        border: none !important;
        box-shadow: 6px 6px 12px #c5cad4, -6px -6px 12px #ffffff !important;
        border-radius: 10px !important;
    }
    [data-baseweb="menu"] {
        background: #e8ecf1 !important;
    }
    [data-baseweb="option"] {
        background: #e8ecf1 !important;
        color: #2d3748 !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    [data-baseweb="option"]:hover {
        background: #dde1e7 !important;
    }
    .stButton > button {
        background: #e8ecf1 !important;
        color: #2d3748 !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Segoe UI', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 10px 24px !important;
        box-shadow:
            4px 4px 8px #c5cad4,
            -4px -4px 8px #ffffff !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        box-shadow:
            2px 2px 4px #c5cad4,
            -2px -2px 4px #ffffff !important;
        color: #4a6fa5 !important;
    }
    .stButton > button:active {
        box-shadow:
            inset 2px 2px 4px #c5cad4,
            inset -2px -2px 4px #ffffff !important;
    }
    .stButton > button[kind="primary"] {
        background: #4a6fa5 !important;
        color: #ffffff !important;
        box-shadow:
            4px 4px 8px #c5cad4,
            -4px -4px 8px #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #3d5d8f !important;
        color: #ffffff !important;
    }
    [data-testid="stMetric"] {
        background: #e8ecf1;
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow:
            5px 5px 10px #c5cad4,
            -5px -5px 10px #ffffff;
    }
    [data-testid="stMetricLabel"] {
        color: #718096 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    [data-testid="stMetricValue"] {
        color: #2d3748 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #e8ecf1;
        border-radius: 12px;
        padding: 4px;
        box-shadow:
            inset 3px 3px 6px #c5cad4,
            inset -3px -3px 6px #ffffff;
        gap: 4px;
        border-bottom: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #718096 !important;
        border-radius: 8px !important;
        font-family: 'Segoe UI', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        border: none !important;
        padding: 8px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        background: #e8ecf1 !important;
        color: #4a6fa5 !important;
        box-shadow:
            3px 3px 6px #c5cad4,
            -3px -3px 6px #ffffff !important;
    }
    .streamlit-expanderHeader {
        background: #e8ecf1 !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow:
            3px 3px 6px #c5cad4,
            -3px -3px 6px #ffffff !important;
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-family: 'Segoe UI', sans-serif !important;
        padding: 12px 16px !important;
    }
    .streamlit-expanderContent {
        background: #e8ecf1 !important;
        border: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 16px !important;
    }
    .stSlider > div > div > div > div {
        background: #4a6fa5 !important;
    }
    div[data-testid="stSuccessMessage"],
    div[data-testid="stInfoMessage"],
    div[data-testid="stWarningMessage"],
    div[data-testid="stErrorMessage"] {
        background: #e8ecf1 !important;
        border-radius: 10px !important;
        box-shadow:
            3px 3px 6px #c5cad4,
            -3px -3px 6px #ffffff !important;
        color: #2d3748 !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    div[data-testid="stSuccessMessage"] {
        border-left: 3px solid #68d391 !important;
    }
    div[data-testid="stInfoMessage"] {
        border-left: 3px solid #63b3ed !important;
    }
    div[data-testid="stWarningMessage"] {
        border-left: 3px solid #f6ad55 !important;
    }
    div[data-testid="stErrorMessage"] {
        border-left: 3px solid #fc8181 !important;
    }
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(
            to right, transparent, #c5cad4, transparent
        ) !important;
        margin: 1.5rem 0 !important;
    }
    .stSpinner > div {
        border-top-color: #4a6fa5 !important;
    }
    .sidebar-brand {
        background: #e8ecf1;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow:
            5px 5px 10px #c5cad4,
            -5px -5px 10px #ffffff;
        text-align: center;
    }
    .sidebar-brand h2 {
        font-size: 1.5rem !important;
        color: #2d3748 !important;
        margin: 0 !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    .sidebar-brand p {
        font-size: 0.7rem !important;
        color: #a0aec0 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        margin: 4px 0 0 0 !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    .stCaption, .stCaption p {
        color: #a0aec0 !important;
        font-size: 0.75rem !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    code {
        background: #dde1e7 !important;
        color: #2d3748 !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
        font-size: 0.85rem !important;
    }
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
 
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="paste your key here"
    )
 
    if api_key:
        st.session_state["api_key"] = api_key
        st.success("API key active")
 
    st.markdown("---")
 
    try:
        conn = sqlite3.connect("foundree42.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM leads")
        total = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(*) FROM leads WHERE score >= 80"
        )
        hot = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(*) FROM leads WHERE status=?",
            ("contacted",)
        )
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
def init_db():
    conn = sqlite3.connect("foundree42.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            industry TEXT, size TEXT, hq TEXT,
            ceo TEXT, current_crm TEXT,
            score INTEGER, overview TEXT,
            pain_points TEXT, recent_triggers TEXT,
            best_contact TEXT, pitch_angle TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT,
            linkedin_dm TEXT, cold_email TEXT,
            subject_line TEXT, followup TEXT,
            connection_note TEXT,
            icp_match TEXT, cta TEXT
        )
    """)
    conn.commit()
    conn.close()
 
def save_lead(data):
    conn = sqlite3.connect("foundree42.db")
    c = conn.cursor()
    c.execute(
        "SELECT id FROM leads WHERE company=?",
        (data.get("company",""),)
    )
    existing = c.fetchone()
    if existing:
        conn.close()
        return existing[0]
    c.execute("""
        INSERT INTO leads (
            company, industry, size, hq, ceo,
            current_crm, score, overview,
            pain_points, recent_triggers,
            best_contact, pitch_angle,
            status, created_at,
            icp_match, cta
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get("company",""),
        data.get("industry",""),
        data.get("size",""),
        data.get("hq",""),
        data.get("ceo",""),
        data.get("current_crm",""),
        data.get("score",0),
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
    lead_id = c.lastrowid
    conn.close()
    return lead_id
 
def save_messages(company, messages):
    conn = sqlite3.connect("foundree42.db")
    conn.execute("""
        UPDATE leads SET
        linkedin_dm=?, cold_email=?,
        subject_line=?, followup=?,
        connection_note=?
        WHERE company=?
    """, (
        messages.get("linkedin_dm",""),
        messages.get("cold_email",""),
        messages.get("subject_line",""),
        messages.get("followup",""),
        messages.get("connection_note",""),
        company
    ))
    conn.commit()
    conn.close()
 
def update_status(company, status):
    conn = sqlite3.connect("foundree42.db")
    conn.execute(
        "UPDATE leads SET status=? WHERE company=?",
        (status, company)
    )
    conn.commit()
    conn.close()
 
def get_all_leads():
    conn = sqlite3.connect("foundree42.db")
    c = conn.cursor()
    c.execute("SELECT * FROM leads ORDER BY score DESC")
    leads = c.fetchall()
    conn.close()
    return leads
 
# ── AI ────────────────────────────────────────────
def ask_ai(prompt):
    if not st.session_state.get("api_key"):
        return "ERROR: No API key"
    try:
        client = groq.Groq(
            api_key=st.session_state["api_key"]
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a sales intelligence analyst for Foundree42, "
                        "a senior-led Salesforce consultancy based in the UK. "
                        "Foundree42 serves 6 ideal client profiles: "
                        "ICP1: $1B+ firms with underperforming Salesforce partners needing a reset. "
                        "ICP2: $500M-$3B orgs needing platform governance and stewardship. "
                        "ICP3: $50M-$500M mid-market companies needing virtual Salesforce support. "
                        "ICP4: Companies with inherited messy Salesforce orgs needing an audit. "
                        "ICP5: Mid-market and enterprise replacing offshore Salesforce delivery. "
                        "ICP6: Companies needing trusted senior Salesforce delivery to reduce risk. "
                        "Key buyer roles: Salesforce Platform Owner, VP RevOps, COO, IT Director, "
                        "Enterprise Architect, Program/PMO Leader, Admin Lead. "
                        "Always return valid JSON only. No markdown. No explanation."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
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
 
def research_company(company, contact="", title=""):
    prompt = (
        "Research " + company + " for Foundree42, "
        "a senior-led Salesforce consultancy in the UK. "
        + ("Contact: " + contact + " " + title + ". " if contact else "")
        + "Identify which Foundree42 ICP they best match: "
        + "ICP1 ($1B+ needing reset), ICP2 ($500M-$3B governance), "
        + "ICP3 ($50M-$500M virtual support), ICP4 (messy org audit), "
        + "ICP5 (replacing offshore), ICP6 (trusted senior delivery). "
        + "Return ONLY this JSON with no markdown: "
        + '{"company":"' + company + '",'
        + '"overview":"2-3 sentence summary",'
        + '"industry":"their industry",'
        + '"size":"revenue and employee estimate",'
        + '"hq":"city and country",'
        + '"ceo":"CEO name",'
        + '"current_crm":"their Salesforce status or CRM",'
        + '"score":75,'
        + '"icp_match":"ICP number and one sentence why",'
        + '"pain_points":["specific Salesforce pain 1","pain 2","pain 3"],'
        + '"recent_triggers":["recent signal 1","recent signal 2"],'
        + '"best_contact_title":"exact role title to target",'
        + '"pitch_angle":"one sentence pitch referencing their specific situation",'
        + '"cta":"one of: Reset Assessment / Governance Workshop / Managed Services Quote / Automation Audit / Delivery Model Review / Talk to Senior Architect"}'
    )
    raw = ask_ai(prompt)
    if raw.startswith("ERROR"):
        return {"error": raw}
    return parse_json(raw)
 
def generate_messages(lead_data, feedback=""):
    prompt = (
        "Write personalised Salesforce consultancy "
        "outreach for " + lead_data.get("company","")
        + ". ICP match: " + lead_data.get("icp_match","")
        + ". Industry: " + lead_data.get("industry","")
        + ". Overview: " + lead_data.get("overview","")
        + ". Pain points: " + str(lead_data.get("pain_points",[]))
        + ". Triggers: " + str(lead_data.get("recent_triggers",[]))
        + ". Pitch: " + lead_data.get("pitch_angle","")
        + ". CTA: " + lead_data.get("cta","")
        + (". Apply this feedback: " + feedback if feedback else "")
        + ". Rules: reference specific company facts, "
        + "never say I hope this finds you well, "
        + "never say I wanted to reach out, "
        + "sound human not templated, "
        + "sign off as the Foundree42 team, "
        + "end with the recommended CTA. "
        + "Return ONLY this JSON with no markdown: "
        + '{"subject_line":"subject under 10 words",'
        + '"linkedin_dm":"DM under 180 words",'
        + '"cold_email":"email 150-200 words",'
        + '"followup":"followup under 120 words",'
        + '"connection_note":"connection note under 70 words"}'
    )
    raw = ask_ai(prompt)
    if raw.startswith("ERROR"):
        return {"error": raw}
    return parse_json(raw)
 
# ── ICP MAP ───────────────────────────────────────
icp_map = {
    "ICP 1 — $1B+ firms needing partner reset": {
        "size": "$1B+ revenue",
        "signals": (
            "Salesforce partner reset, project rescue, "
            "implementation failing, program turnaround, "
            "delivery risk, Salesforce org stabilization"
        ),
        "roles": (
            "VP of Salesforce, Director of CRM, "
            "Enterprise Architect, IT Director, Program Leader"
        )
    },
    "ICP 2 — $500M-$3B needing governance": {
        "size": "$500M-$3B revenue",
        "signals": (
            "Salesforce governance framework, Center of Excellence, "
            "multi-cloud Salesforce, operating model, "
            "standards and guardrails, platform stewardship"
        ),
        "roles": (
            "Salesforce Platform Owner, Head of CRM, "
            "Enterprise Architect, RevOps Leader, IT Applications Leader"
        )
    },
    "ICP 3 — $50M-$500M needing virtual support": {
        "size": "$50M-$500M revenue",
        "signals": (
            "virtual Salesforce admin, managed services, "
            "Salesforce support partner, optimization services, "
            "lean team, no internal Salesforce team, support backlog"
        ),
        "roles": (
            "COO, Head of Operations, VP RevOps, "
            "Salesforce Admin, CFO"
        )
    },
    "ICP 4 — Inherited messy Salesforce org": {
        "size": "any size",
        "signals": (
            "Salesforce org cleanup, automation audit, "
            "technical debt, Flow audit, inherited Salesforce, "
            "org complexity, Flow vs Apex, Salesforce mess"
        ),
        "roles": (
            "New Platform Owner, Admin Lead, Salesforce Manager, "
            "Solution Architect, IT Manager"
        )
    },
    "ICP 5 — Replacing offshore delivery model": {
        "size": "mid-market to enterprise",
        "signals": (
            "replace offshore Salesforce consulting, "
            "senior Salesforce consultants, delivery partner, "
            "quality issues, faster implementation, "
            "low-accountability delivery"
        ),
        "roles": (
            "IT Director, VP Applications, Delivery Leader, "
            "PMO, Program Owner, Procurement"
        )
    },
    "ICP 6 — Need trusted senior delivery partner": {
        "size": "any size",
        "signals": (
            "trusted Salesforce implementation partner, "
            "reduce implementation risk, project delivery partner, "
            "program governance, project rescue team, "
            "senior architecture"
        ),
        "roles": (
            "VP of Salesforce, IT Apps Leader, RevOps Leader, "
            "Architect, Program Leader"
        )
    }
}
 
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
        "Select your target ICP and the AI will find "
        "matching companies ready for Foundree42 outreach."
    )
    st.markdown("---")
 
    c1, c2 = st.columns(2)
    with c1:
        icp_select = st.selectbox(
            "Target ICP",
            list(icp_map.keys())
        )
        icp_location = st.text_input(
            "Location",
            placeholder="e.g. United States, United Kingdom"
        )
    with c2:
        icp_industry = st.text_input(
            "Industry (optional)",
            placeholder="e.g. Financial Services, Healthcare, Retail"
        )
        icp_count = st.slider(
            "Number of leads", 3, 10, 5
        )
 
    st.markdown("---")
 
    if st.button("Discover Leads", type="primary"):
        if not st.session_state.get("api_key"):
            st.error("Add your Groq API key in the sidebar.")
        elif not icp_location:
            st.error("Please enter a location.")
        else:
            selected = icp_map[icp_select]
            with st.spinner("Searching for matching companies..."):
                prompt = (
                    "Find " + str(icp_count) + " real companies "
                    "that are ideal clients for Foundree42, "
                    "a senior-led Salesforce consultancy. "
                    "Target profile: " + icp_select
                    + ". Company size: " + selected["size"]
                    + ". Location: " + icp_location
                    + (". Industry: " + icp_industry if icp_industry else "")
                    + ". Buying signals: " + selected["signals"]
                    + ". Best contacts: " + selected["roles"]
                    + ". Return ONLY a JSON array with no markdown: "
                    + '[{"company":"name",'
                    + '"industry":"industry",'
                    + '"size":"size",'
                    + '"location":"city, country",'
                    + '"revenue":"estimate",'
                    + '"why_fit":"specific reason they fit this ICP",'
                    + '"trigger":"specific buying signal",'
                    + '"best_contact":"exact job title to target",'
                    + '"score":80}]'
                    + " Use real, specific company names only."
                )
                raw = ask_ai(prompt)
                if raw.startswith("ERROR"):
                    st.error(raw)
                    found = []
                else:
                    result = parse_json(raw)
                    found = result if isinstance(result, list) else []
 
            if found:
                st.success("Found " + str(len(found)) + " leads")
                st.session_state["discovered"] = found
            else:
                st.warning(
                    "No leads found. Try a different location or ICP."
                )
 
    if st.session_state.get("discovered"):
        st.markdown("---")
        leads_sorted = sorted(
            st.session_state["discovered"],
            key=lambda x: x.get("score", 0),
            reverse=True
        )
        for i, lead in enumerate(leads_sorted):
            score = lead.get("score", 0)
            label = (
                "Hot" if score >= 80
                else "Warm" if score >= 60
                else "Cold"
            )
            with st.expander(
                lead.get("company","") +
                "   |   Score: " + str(score) +
                "/100   |   " + label,
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
                        lead.get("location","") +
                        "   ·   " + lead.get("size","")
                    )
                with col_b:
                    st.metric(
                        "Fit Score",
                        str(score) + "/100"
                    )
                st.markdown("---")
                if st.button(
                    "Research this company",
                    key="disc_" + str(i)
                ):
                    st.session_state["prefill"] = (
                        lead.get("company","")
                    )
                    st.info(
                        "Go to Company Research tab — "
                        + lead.get("company","") +
                        " is prefilled"
                    )
 
# ════════════════════════════════════════════════
# TAB 2 — COMPANY RESEARCH
# ════════════════════════════════════════════════
with tab2:
    st.markdown("## Company Research")
    st.markdown(
        "Full pipeline — Research, ICP match, "
        "Pitch Angle, CTA and Outreach Messages."
    )
    st.markdown("---")
 
    col1, col2 = st.columns(2)
    with col1:
        company_input = st.text_input(
            "Company Name",
            value=st.session_state.get("prefill",""),
            placeholder="e.g. Gymshark"
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
            placeholder=(
                "e.g. be more direct, "
                "lead with ROI, shorter messages..."
            ),
            height=104
        )
 
    st.markdown("---")
    col_x, col_y = st.columns(2)
    with col_x:
        run_pipeline = st.button(
            "Run Full Pipeline",
            type="primary"
        )
    with col_y:
        research_only = st.button("Research Only")
 
    if run_pipeline or research_only:
        if not st.session_state.get("api_key"):
            st.error("Add your API key in the sidebar.")
        elif not company_input:
            st.error("Enter a company name.")
        else:
            with st.spinner(
                "Researching " + company_input + "..."
            ):
                intel = research_company(
                    company_input,
                    contact_input,
                    title_input
                )
 
            if "error" not in intel and intel:
                score = intel.get("score", 0)
                st.markdown("---")
                st.markdown("### Intelligence Report")
 
                m1, m2, m3 = st.columns(3)
                m1.metric(
                    "Industry",
                    intel.get("industry","—")
                )
                m2.metric(
                    "Company Size",
                    intel.get("size","—")
                )
                m3.metric(
                    "Salesforce Fit",
                    str(score) + " / 100"
                )
 
                st.markdown("---")
                st.markdown("**Overview**")
                st.write(intel.get("overview",""))
 
                if intel.get("icp_match"):
                    st.info(
                        "ICP Match:   " +
                        intel.get("icp_match","")
                    )
 
                col_p, col_t = st.columns(2)
                with col_p:
                    st.markdown("**Pain Points**")
                    if intel.get("pain_points"):
                        for p in intel["pain_points"]:
                            st.markdown("— " + p)
                with col_t:
                    st.markdown("**Recent Triggers**")
                    if intel.get("recent_triggers"):
                        for t in intel["recent_triggers"]:
                            st.markdown("— " + t)
 
                st.markdown("---")
                st.markdown(
                    "**Best Contact:**   " +
                    intel.get("best_contact_title","—")
                )
                st.markdown(
                    "**Pitch Angle:**   " +
                    intel.get("pitch_angle","—")
                )
                if intel.get("cta"):
                    st.warning(
                        "Recommended CTA:   " +
                        intel.get("cta","")
                    )
 
                if run_pipeline:
                    st.markdown("---")
                    st.markdown("### Outreach Messages")
 
                    with st.spinner(
                        "Writing personalised messages..."
                    ):
                        messages = generate_messages(
                            intel, feedback_input
                        )
 
                    if "error" not in messages and messages:
                        mt1, mt2, mt3, mt4 = st.tabs([
                            "LinkedIn DM",
                            "Cold Email",
                            "Follow-up",
                            "Connection Note"
                        ])
                        with mt1:
                            st.text_area(
                                "Copy and paste into LinkedIn",
                                messages.get("linkedin_dm",""),
                                height=200,
                                key="li_msg"
                            )
                        with mt2:
                            st.markdown("**Subject Line**")
                            st.code(
                                messages.get("subject_line",""),
                                language=None
                            )
                            st.text_area(
                                "Email Body",
                                messages.get("cold_email",""),
                                height=200,
                                key="em_msg"
                            )
                        with mt3:
                            st.text_area(
                                "Send if no reply after 5 days",
                                messages.get("followup",""),
                                height=150,
                                key="fu_msg"
                            )
                        with mt4:
                            st.text_area(
                                "Use when sending connection request",
                                messages.get("connection_note",""),
                                height=100,
                                key="cn_msg"
                            )
 
                        st.markdown("---")
                        if st.button(
                            "Save Lead and Messages",
                            type="primary"
                        ):
                            save_lead(intel)
                            save_messages(
                                company_input, messages
                            )
                            st.success(
                                company_input +
                                " saved to your database"
                            )
                    else:
                        st.error(
                            "Message error: " +
                            str(messages.get("error",""))
                        )
            else:
                st.error(
                    "Research failed: " +
                    str(intel.get("error",""))
                )
 
# ════════════════════════════════════════════════
# TAB 3 — LINKEDIN WORKFLOW
# ════════════════════════════════════════════════
with tab3:
    st.markdown("## LinkedIn Workflow")
    st.markdown(
        "Step-by-step workflow for contacting each lead."
    )
    st.markdown("---")
 
    all_leads = get_all_leads()
 
    if not all_leads:
        st.info(
            "No leads saved yet. Research a company "
            "in the Company Research tab and save it."
        )
    else:
        for lead in all_leads:
            comp      = lead[1]
            target    = lead[11] or "VP of Sales"
            score     = lead[7] or 0
            status    = lead[13] or "new"
            conn_note = lead[19] if len(lead) > 19 else ""
            li_dm     = lead[15] if len(lead) > 15 else ""
 
            status_label = (
                "Replied" if status == "replied"
                else "Contacted" if status == "contacted"
                else "Closed" if status == "closed"
                else "New"
            )
 
            with st.expander(
                comp + "   |   " + str(score) +
                "/100   |   " + status_label
            ):
                search_url = (
                    "https://www.linkedin.com/"
                    "search/results/people/?keywords=" +
                    (target + " " + comp).replace(" ","%20")
                )
 
                st.markdown("**Target Role**")
                st.write(target)
 
                st.markdown(
                    "**Step 1 — Find them on LinkedIn**"
                )
                st.markdown(
                    "[Search LinkedIn for " + target +
                    " at " + comp + "](" + search_url + ")"
                )
 
                if conn_note:
                    st.markdown("---")
                    st.markdown(
                        "**Step 2 — Send connection request**"
                    )
                    st.text_area(
                        "Copy this note",
                        conn_note,
                        height=80,
                        key="cn_li_" + str(lead[0])
                    )
 
                if li_dm:
                    st.markdown("---")
                    st.markdown(
                        "**Step 3 — Send DM after connecting**"
                    )
                    st.text_area(
                        "Copy this message",
                        li_dm,
                        height=150,
                        key="dm_li_" + str(lead[0])
                    )
 
                if not conn_note and not li_dm:
                    st.info(
                        "Run Full Pipeline in Company Research "
                        "to generate messages for this lead."
                    )
 
                st.markdown("---")
                s1, s2, s3 = st.columns(3)
                with s1:
                    if st.button(
                        "Mark as Contacted",
                        key="c_" + str(lead[0])
                    ):
                        update_status(comp, "contacted")
                        st.rerun()
                with s2:
                    if st.button(
                        "Mark as Replied",
                        key="r_" + str(lead[0])
                    ):
                        update_status(comp, "replied")
                        st.rerun()
                with s3:
                    if st.button(
                        "Mark as Closed",
                        key="cl_" + str(lead[0])
                    ):
                        update_status(comp, "closed")
                        st.rerun()
 
# ════════════════════════════════════════════════
# TAB 4 — LEAD DATABASE
# ════════════════════════════════════════════════
with tab4:
    st.markdown("## Lead Database")
    st.markdown(
        "All saved leads with status tracking and filtering."
    )
    st.markdown("---")
 
    all_leads_db = get_all_leads()
 
    if not all_leads_db:
        st.info(
            "No leads saved yet. Research companies "
            "and save them to build your database."
        )
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads", len(all_leads_db))
        m2.metric(
            "Hot Leads",
            len([
                l for l in all_leads_db
                if (l[7] or 0) >= 80
            ])
        )
        m3.metric(
            "Contacted",
            len([
                l for l in all_leads_db
                if l[13] == "contacted"
            ])
        )
        m4.metric(
            "Replied",
            len([
                l for l in all_leads_db
                if l[13] == "replied"
            ])
        )
 
        st.markdown("---")
 
        fc1, fc2 = st.columns(2)
        with fc1:
            status_filter = st.selectbox(
                "Filter by Status",
                [
                    "All", "new", "ready_to_contact",
                    "contacted", "replied", "closed"
                ]
            )
        with fc2:
            min_score = st.slider(
                "Minimum Score", 0, 100, 0
            )
 
        filtered = [
            l for l in all_leads_db
            if (status_filter == "All" or
                l[13] == status_filter)
            and (l[7] or 0) >= min_score
        ]
 
        st.caption(
            "Showing " + str(len(filtered)) + " leads"
        )
        st.markdown("---")
 
        for lead in filtered:
            score = lead[7] or 0
            label = (
                "Hot" if score >= 80
                else "Warm" if score >= 60
                else "Cold"
            )
            with st.expander(
                lead[1] + "   |   " +
                str(score) + "/100   |   " +
                (lead[13] or "new").capitalize()
            ):
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown("**Industry**")
                    st.write(lead[2] or "—")
                    st.markdown("**Company Size**")
                    st.write(lead[3] or "—")
                    st.markdown("**HQ**")
                    st.write(lead[4] or "—")
                    st.markdown("**Best Contact**")
                    st.write(lead[11] or "—")
                with d2:
                    st.markdown("**Fit Score**")
                    st.write(str(score) + " / 100")
                    st.markdown("**Added**")
                    st.write(lead[14] or "—")
                    st.markdown("**Pitch Angle**")
                    st.write(lead[12] or "—")
 
                if len(lead) > 20 and lead[20]:
                    st.markdown("**ICP Match**")
                    st.write(lead[20])
 
                if len(lead) > 21 and lead[21]:
                    st.markdown("**Recommended CTA**")
                    st.write(lead[21])
 
                if lead[8]:
                    st.markdown("---")
                    st.markdown("**Overview**")
                    st.write(lead[8])
 
                st.markdown("---")
                new_status = st.selectbox(
                    "Update Status",
                    [
                        "new", "ready_to_contact",
                        "contacted", "replied", "closed"
                    ],
                    index=[
                        "new", "ready_to_contact",
                        "contacted", "replied", "closed"
                    ].index(lead[13] or "new"),
                    key="status_" + str(lead[0])
                )
                if new_status != (lead[13] or "new"):
                    update_status(lead[1], new_status)
                    st.success("Status updated")
                    st.rerun()
