import streamlit as st
import groq
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
    .stSelectbox > div > div, .stSelectbox > div > div > div,
    .stSelectbox div[data-baseweb="select"], .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] span, .stSelectbox div[data-baseweb="select"] div,
    [data-baseweb="select"] > div {
        background: #e8ecf1 !important; border: none !important; border-radius: 10px !important;
        color: #2d3748 !important; font-family: 'Segoe UI', sans-serif !important; font-size: 0.9rem !important;
        box-shadow: inset 3px 3px 6px #c5cad4, inset -3px -3px 6px #ffffff !important;
    }
    [data-baseweb="select"] span, [data-baseweb="select"] div { color: #2d3748 !important; }
    [data-baseweb="popover"] { background: #e8ecf1 !important; border: none !important; box-shadow: 6px 6px 12px #c5cad4, -6px -6px 12px #ffffff !important; border-radius: 10px !important; }
    [data-baseweb="menu"] { background: #e8ecf1 !important; }
    [data-baseweb="option"] { background: #e8ecf1 !important; color: #2d3748 !important; font-family: 'Segoe UI', sans-serif !important; }
    [data-baseweb="option"]:hover { background: #dde1e7 !important; }
    .stButton > button {
        background: #e8ecf1 !important; color: #2d3748 !important; border: none !important;
        border-radius: 10px !important; font-family: 'Segoe UI', sans-serif !important;
        font-weight: 600 !important; font-size: 0.875rem !important; padding: 10px 24px !important;
        box-shadow: 4px 4px 8px #c5cad4, -4px -4px 8px #ffffff !important; transition: all 0.2s ease !important; width: 100% !important;
    }
    .stButton > button:hover { box-shadow: 2px 2px 4px #c5cad4, -2px -2px 4px #ffffff !important; color: #4a6fa5 !important; }
    .stButton > button[kind="primary"] { background: #4a6fa5 !important; color: #ffffff !important; }
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
    div[data-testid="stSuccessMessage"] { background: #e8ecf1 !important; border-radius: 10px !important; border-left: 3px solid #68d391 !important; color: #2d3748 !important; }
    div[data-testid="stInfoMessage"] { background: #e8ecf1 !important; border-radius: 10px !important; border-left: 3px solid #63b3ed !important; color: #2d3748 !important; }
    div[data-testid="stWarningMessage"] { background: #e8ecf1 !important; border-radius: 10px !important; border-left: 3px solid #f6ad55 !important; color: #2d3748 !important; }
    div[data-testid="stErrorMessage"] { background: #e8ecf1 !important; border-radius: 10px !important; border-left: 3px solid #fc8181 !important; color: #2d3748 !important; }
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

# ── SESSION STATE INIT ────────────────────────────
# Using session_state as the database — works 100% on Streamlit Cloud
if "leads_db" not in st.session_state:
    st.session_state["leads_db"] = []
if "discovered" not in st.session_state:
    st.session_state["discovered"] = []
if "prefill" not in st.session_state:
    st.session_state["prefill"] = ""
if "next_id" not in st.session_state:
    st.session_state["next_id"] = 1

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

    leads_db  = st.session_state["leads_db"]
    total     = len(leads_db)
    hot       = len([l for l in leads_db if l.get("score",0) >= 80])
    contacted = len([l for l in leads_db if l.get("status") == "contacted"])
    replied   = len([l for l in leads_db if l.get("status") == "replied"])

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total", total)
    with col_b:
        st.metric("Hot", hot)
    col_c, col_d = st.columns(2)
    with col_c:
        st.metric("Contacted", contacted)
    with col_d:
        st.metric("Replied", replied)

    st.markdown("---")
    st.caption("Foundree42 — US Market")
    st.caption("Data saves within this session")

# ── HELPER: SAVE LEAD ─────────────────────────────
def save_lead_to_db(intel, messages):
    """Save lead + messages into session state. Returns the lead dict."""
    company = intel.get("company","")

    # Check if already saved — update instead of duplicate
    for i, existing in enumerate(st.session_state["leads_db"]):
        if existing.get("company","").lower() == company.lower():
            st.session_state["leads_db"][i].update({
                "industry"       : intel.get("industry",""),
                "size"           : intel.get("size",""),
                "hq"             : intel.get("hq",""),
                "ceo"            : intel.get("ceo",""),
                "current_crm"    : intel.get("current_crm",""),
                "score"          : intel.get("score",0),
                "overview"       : intel.get("overview",""),
                "pain_points"    : intel.get("pain_points",[]),
                "recent_triggers": intel.get("recent_triggers",[]),
                "best_contact"   : intel.get("best_contact_title",""),
                "pitch_angle"    : intel.get("pitch_angle",""),
                "icp_match"      : intel.get("icp_match",""),
                "cta"            : intel.get("cta",""),
                "ideal_contacts" : intel.get("ideal_contacts",[]),
                "linkedin_dm"    : messages.get("linkedin_dm",""),
                "cold_email"     : messages.get("cold_email",""),
                "subject_line"   : messages.get("subject_line",""),
                "followup"       : messages.get("followup",""),
                "connection_note": messages.get("connection_note",""),
                "updated_at"     : datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            return st.session_state["leads_db"][i]

    # New lead
    lead = {
        "id"             : st.session_state["next_id"],
        "company"        : company,
        "industry"       : intel.get("industry",""),
        "size"           : intel.get("size",""),
        "hq"             : intel.get("hq",""),
        "ceo"            : intel.get("ceo",""),
        "current_crm"    : intel.get("current_crm",""),
        "score"          : intel.get("score",0),
        "overview"       : intel.get("overview",""),
        "pain_points"    : intel.get("pain_points",[]),
        "recent_triggers": intel.get("recent_triggers",[]),
        "best_contact"   : intel.get("best_contact_title",""),
        "pitch_angle"    : intel.get("pitch_angle",""),
        "icp_match"      : intel.get("icp_match",""),
        "cta"            : intel.get("cta",""),
        "ideal_contacts" : intel.get("ideal_contacts",[]),
        "linkedin_dm"    : messages.get("linkedin_dm",""),
        "cold_email"     : messages.get("cold_email",""),
        "subject_line"   : messages.get("subject_line",""),
        "followup"       : messages.get("followup",""),
        "connection_note": messages.get("connection_note",""),
        "status"         : "new",
        "created_at"     : datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at"     : datetime.now().strftime("%Y-%m-%d %H:%M"),
        "notes"          : ""
    }
    st.session_state["leads_db"].insert(0, lead)
    st.session_state["next_id"] += 1
    return lead

def update_lead_status(lead_id, new_status):
    for i, l in enumerate(st.session_state["leads_db"]):
        if l.get("id") == lead_id:
            st.session_state["leads_db"][i]["status"] = new_status
            break

def update_lead_notes(lead_id, notes):
    for i, l in enumerate(st.session_state["leads_db"]):
        if l.get("id") == lead_id:
            st.session_state["leads_db"][i]["notes"] = notes
            break

# ── AI SYSTEM PROMPT ──────────────────────────────
SYSTEM_PROMPT = (
    "You are a senior sales intelligence analyst for Foundree42, "
    "a US-based Salesforce consultancy that targets US companies. "
    "Foundree42 specialises in senior-led Salesforce implementations, "
    "platform governance, managed services, and project rescue. "
    "Foundree42 serves these 6 ideal client profiles: "
    "ICP1: $1B+ US firms with underperforming Salesforce partners needing a senior-led reset. "
    "ICP2: $500M-$3B US orgs with fragmented Salesforce needing platform governance. "
    "ICP3: $50M-$500M US mid-market with no internal Salesforce team needing virtual support. "
    "ICP4: US companies with inherited messy Salesforce orgs needing an automation audit. "
    "ICP5: US mid-market and enterprise replacing offshore Salesforce delivery. "
    "ICP6: US companies needing trusted senior Salesforce delivery to reduce project risk. "
    "Target buyer roles: Salesforce Platform Owner, VP RevOps, COO, CIO, IT Director, "
    "Enterprise Architect, PMO Leader, Admin Lead, Head of CRM, VP of Sales. "
    "Always return valid JSON only. No markdown fences. No explanation. No preamble."
)

def ask_ai(prompt):
    if not st.session_state.get("api_key"):
        return "ERROR: No API key set. Please paste your Groq API key in the sidebar."
    try:
        client = groq.Groq(api_key=st.session_state["api_key"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        return "ERROR: " + str(e)

def parse_json(raw):
    clean = re.sub(r"```json|```", "", raw).strip()
    # Try direct parse
    try:
        return json.loads(clean)
    except:
        pass
    # Try finding JSON object in the text
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    # Try finding JSON array
    match = re.search(r"\[.*\]", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return {}

# ── FREE ACCURACY BOOST: LIVE NEWS ───────────────
def get_live_news(company):
    """Pull real Google News headlines for this company — free."""
    try:
        url = "https://news.google.com/rss/search"
        params = {
            "q"  : '"' + company + '" Salesforce OR CRM OR funding OR hiring OR acquisition',
            "hl" : "en-US",
            "gl" : "US",
            "ceid": "US:en"
        }
        resp  = requests.get(url, params=params, timeout=6)
        items = re.findall(r"<title>(.*?)</title>", resp.text)[1:5]
        clean = [re.sub(r"<.*?>|&amp;|&quot;|&#39;", "", i).strip() for i in items]
        return [c for c in clean if len(c) > 10]
    except:
        return []

# ── FREE ACCURACY BOOST: JOB SIGNAL ──────────────
def check_hiring_signal(company):
    """Check if company is hiring Salesforce roles — free signal."""
    try:
        query  = company + " Salesforce Admin OR RevOps OR CRM Manager site:linkedin.com/jobs"
        url    = "https://news.google.com/rss/search"
        params = {"q": query, "hl": "en-US"}
        resp   = requests.get(url, params=params, timeout=5)
        items  = re.findall(r"<title>(.*?)</title>", resp.text)[1:3]
        return len(items) > 0
    except:
        return False

# ── RESEARCH ──────────────────────────────────────
def research_company(company, contact="", title=""):
    news         = get_live_news(company)
    hiring_signal = check_hiring_signal(company)

    news_context = ""
    if news:
        news_context = (
            " Live news found about this company: "
            + " | ".join(news[:3]) + "."
        )
    if hiring_signal:
        news_context += " They appear to be hiring Salesforce or CRM roles right now."

    prompt = (
        "Research the US company called " + company + "."
        + (" Contact person: " + contact + ", Title: " + title + "." if contact else "")
        + news_context
        + " Use all available knowledge to give accurate, specific details."
        + " Match to the most fitting Foundree42 ICP."
        + " Identify 3-5 real people at this company who are ideal contacts for Foundree42."
        + " Return ONLY this JSON object:"
        + "{"
        + '"company":"' + company + '",'
        + '"overview":"accurate 2-3 sentence company summary",'
        + '"industry":"specific industry vertical",'
        + '"size":"employee count and revenue range",'
        + '"hq":"city and state",'
        + '"ceo":"current CEO or President name",'
        + '"current_crm":"their known CRM platform or Salesforce maturity",'
        + '"score":0,'
        + '"icp_match":"ICP number and specific one-sentence reason why",'
        + '"pain_points":["specific operational pain 1","specific pain 2","specific pain 3"],'
        + '"recent_triggers":["specific recent signal 1","specific signal 2","specific signal 3"],'
        + '"ideal_contacts":['
        + '{"name":"real person name or likely role if unknown","title":"exact US job title","why":"one sentence why they are the right contact","linkedin_search":"search query to find them on LinkedIn"},'
        + '{"name":"second contact","title":"title","why":"why","linkedin_search":"search query"},'
        + '{"name":"third contact","title":"title","why":"why","linkedin_search":"search query"}'
        + '],'
        + '"best_contact_title":"single best job title to target",'
        + '"pitch_angle":"one very specific sentence pitch referencing their actual situation",'
        + '"cta":"one of: Reset Assessment / Governance Workshop / Managed Services Quote / Automation Audit / Delivery Model Review / Talk to Senior Architect"'
        + "}"
    )

    raw    = ask_ai(prompt)
    if raw.startswith("ERROR"):
        return {"error": raw}
    result = parse_json(raw)

    # Inject live news into triggers for accuracy
    if news and isinstance(result, dict):
        existing = result.get("recent_triggers", [])
        combined = news[:2] + [t for t in existing if t not in news]
        result["recent_triggers"] = combined[:4]

    return result

# ── DISCOVER ──────────────────────────────────────
def discover_leads(industry, location, revenue, size, signals, count):
    prompt = (
        "Find " + str(count) + " real US companies "
        "that are strong potential clients for Foundree42. "
        "Search criteria: "
        "Industry: " + industry + ". "
        "Location: " + location + ". "
        "Revenue: " + revenue + ". "
        "Size: " + size + ". "
        "Buying signals: " + signals + ". "
        "Match to Foundree42 ICPs. Focus on companies that:"
        " have Salesforce or need it, are growing their sales teams,"
        " have raised recent funding, or show signs of CRM investment. "
        "Return ONLY a JSON array:"
        + "["
        + "{"
        + '"company":"exact real US company name",'
        + '"industry":"specific industry",'
        + '"size":"size estimate",'
        + '"location":"city, state",'
        + '"revenue":"revenue estimate",'
        + '"why_fit":"specific ICP match reason",'
        + '"trigger":"specific buying signal",'
        + '"best_contact":"ideal job title",'
        + '"score":0'
        + "}"
        + "]"
        + " Real verified US companies only. No placeholders."
    )
    raw    = ask_ai(prompt)
    if raw.startswith("ERROR"):
        st.error(raw)
        return []
    result = parse_json(raw)
    if isinstance(result, list):
        return result
    # Try to get it from a nested key
    if isinstance(result, dict):
        for v in result.values():
            if isinstance(v, list):
                return v
    return []

# ── MESSAGES ──────────────────────────────────────
def generate_messages(lead_data, contact_name="", feedback=""):
    contacts_context = ""
    if lead_data.get("ideal_contacts"):
        best = lead_data["ideal_contacts"][0]
        contact_name = contact_name or best.get("name","")
        contacts_context = (
            " Primary contact: " + best.get("name","") +
            ", " + best.get("title","") + "."
        )

    first_name = ""
    if contact_name and contact_name.lower() not in ["unknown","not found","n/a",""]:
        parts      = contact_name.strip().split()
        first_name = parts[0] if parts else ""

    greeting = "Hi " + first_name if first_name else "Hi there"

    prompt = (
        "Write highly personalised Salesforce consultancy outreach "
        "for the US company " + lead_data.get("company","") + "."
        + contacts_context
        + " Greeting to use: " + greeting + "."
        + " ICP match: " + (lead_data.get("icp_match") or "") + "."
        + " Industry: " + (lead_data.get("industry") or "") + "."
        + " Overview: " + (lead_data.get("overview") or "") + "."
        + " Pain points: " + str(lead_data.get("pain_points") or []) + "."
        + " Recent triggers: " + str(lead_data.get("recent_triggers") or []) + "."
        + " Pitch: " + (lead_data.get("pitch_angle") or "") + "."
        + " CTA: " + (lead_data.get("cta") or "") + "."
        + (" Boss feedback to apply: " + feedback + "." if feedback else "")
        + " Rules:"
        + " Use the greeting provided."
        + " Reference at least 2 specific facts about this company."
        + " Never say I hope this finds you well."
        + " Never say I wanted to reach out."
        + " Never say I came across your profile."
        + " Sound like a senior consultant, not a salesperson."
        + " Sign off as The Foundree42 Team."
        + " End with the recommended CTA."
        + " Return ONLY this JSON:"
        + "{"
        + '"subject_line":"compelling subject line under 10 words",'
        + '"linkedin_dm":"LinkedIn DM under 180 words",'
        + '"cold_email":"cold email 150-200 words",'
        + '"followup":"follow-up under 120 words with different angle",'
        + '"connection_note":"LinkedIn connection request under 70 words"'
        + "}"
    )
    raw    = ask_ai(prompt)
    if raw.startswith("ERROR"):
        return {"error": raw}
    return parse_json(raw)

# ══════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "Lead Discovery",
    "Company Research",
    "Outreach Messages",
    "Lead Tracker"
])

# ════════════════════════════════════════════════
# TAB 1 — LEAD DISCOVERY
# ════════════════════════════════════════════════
with tab1:
    st.markdown("## Lead Discovery")
    st.markdown(
        "Define your search criteria and the AI finds "
        "matching US companies with live buying signals."
    )
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        icp_industry = st.text_input(
            "Industry",
            placeholder="e.g. Manufacturing, Financial Services, Healthcare"
        )
        icp_location = st.text_input(
            "Location",
            placeholder="e.g. Arizona, Texas, United States"
        )
        icp_signals = st.text_area(
            "Buying Signals",
            placeholder="e.g. hiring Salesforce Admin, recent funding, replacing CRM...",
            height=90
        )
    with c2:
        icp_revenue = st.selectbox("Revenue", [
            "Any revenue",
            "Under $10M",
            "Under $50M",
            "$50M - $500M",
            "$500M - $3B",
            "$1B+",
            "Over $3B"
        ])
        icp_size = st.selectbox("Company Size", [
            "Any size",
            "1 - 50 employees",
            "50 - 200 employees",
            "200 - 500 employees",
            "500 - 2,000 employees",
            "2,000 - 10,000 employees",
            "10,000+ employees"
        ])
        icp_count = st.slider("Number of leads to find", 3, 10, 5)

    st.markdown("---")

    if st.button("Discover Leads", type="primary"):
        if not st.session_state.get("api_key"):
            st.error("Add your Groq API key in the sidebar.")
        elif not icp_industry or not icp_location:
            st.error("Please fill in Industry and Location.")
        else:
            with st.spinner("Searching US market for matching companies..."):
                found = discover_leads(
                    industry = icp_industry,
                    location = icp_location,
                    revenue  = icp_revenue,
                    size     = icp_size,
                    signals  = icp_signals or "CRM investment, hiring sales ops, scaling",
                    count    = icp_count
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
            key=lambda x: x.get("score",0),
            reverse=True
        )
        for i, lead in enumerate(leads_sorted):
            score = lead.get("score",0)
            label = "Hot" if score >= 80 else "Warm" if score >= 60 else "Cold"
            with st.expander(
                lead.get("company","") + "   |   " +
                str(score) + "/100   |   " + label,
                expanded=(i == 0)
            ):
                col_a, col_b = st.columns([3,1])
                with col_a:
                    st.markdown("**Why they fit**")
                    st.write(lead.get("why_fit",""))
                    st.markdown("**Buying signal**")
                    st.write(lead.get("trigger",""))
                    st.markdown("**Best contact**")
                    st.write(lead.get("best_contact",""))
                    st.caption(
                        (lead.get("location","") or "") + "   ·   " +
                        (lead.get("size","") or "") + "   ·   " +
                        (lead.get("revenue","") or "")
                    )
                with col_b:
                    st.metric("Fit Score", str(score) + "/100")
                st.markdown("---")
                if st.button("Research this company", key="disc_" + str(i)):
                    st.session_state["prefill"] = lead.get("company","")
                    st.info(
                        "Go to Company Research tab — " +
                        lead.get("company","") + " is ready to research"
                    )

# ════════════════════════════════════════════════
# TAB 2 — COMPANY RESEARCH
# ════════════════════════════════════════════════
with tab2:
    st.markdown("## Company Research")
    st.markdown(
        "Full AI research pipeline: Company intelligence, "
        "ICP match, ideal contacts to reach, and pitch strategy."
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        company_input = st.text_input(
            "Company Name",
            value=st.session_state.get("prefill",""),
            placeholder="e.g. Rogers Corporation"
        )
    with col2:
        feedback_input = st.text_area(
            "Boss Feedback to Apply to Messages",
            placeholder="e.g. be more direct, lead with ROI, shorter messages...",
            height=68
        )

    st.markdown("---")
    if st.button("Research Company + Generate Everything", type="primary"):
        if not st.session_state.get("api_key"):
            st.error("Add your API key in the sidebar.")
        elif not company_input:
            st.error("Enter a company name.")
        else:
            # Stage 1 — Research
            with st.spinner("Stage 1 — Researching " + company_input + " with live data..."):
                intel = research_company(company_input)

            if "error" in intel or not intel:
                st.error("Research failed: " + str(intel.get("error","")))
            else:
                score = intel.get("score",0)

                # ── INTELLIGENCE REPORT ──
                st.markdown("---")
                st.markdown("### Company Intelligence")

                m1, m2, m3 = st.columns(3)
                m1.metric("Industry", intel.get("industry","—"))
                m2.metric("Size", intel.get("size","—"))
                m3.metric("Salesforce Fit", str(score) + "/100")

                st.markdown("**Overview**")
                st.write(intel.get("overview",""))

                if intel.get("icp_match"):
                    st.info("ICP Match:   " + intel.get("icp_match",""))

                if intel.get("cta"):
                    st.warning("Recommended CTA:   " + intel.get("cta",""))

                col_p, col_t = st.columns(2)
                with col_p:
                    st.markdown("**Pain Points**")
                    for p in (intel.get("pain_points") or []):
                        st.markdown("— " + str(p))
                with col_t:
                    st.markdown("**Recent Triggers and Live News**")
                    for t in (intel.get("recent_triggers") or []):
                        st.markdown("— " + str(t))

                # ── IDEAL CONTACTS ──
                st.markdown("---")
                st.markdown("### Ideal Contacts to Reach")
                st.markdown(
                    "These are the people at " + company_input +
                    " you should be contacting for Foundree42."
                )

                contacts = intel.get("ideal_contacts",[])
                if contacts:
                    for idx, contact in enumerate(contacts):
                        with st.expander(
                            "Contact " + str(idx+1) + " — " +
                            contact.get("title",""),
                            expanded=(idx == 0)
                        ):
                            cc1, cc2 = st.columns(2)
                            with cc1:
                                st.markdown("**Name**")
                                st.write(contact.get("name","—"))
                                st.markdown("**Job Title**")
                                st.write(contact.get("title","—"))
                            with cc2:
                                st.markdown("**Why Target Them**")
                                st.write(contact.get("why","—"))

                            search_q = contact.get("linkedin_search","")
                            if search_q:
                                li_url = (
                                    "https://www.linkedin.com/search/results/people/?keywords=" +
                                    search_q.replace(" ","%20")
                                )
                                st.markdown(
                                    "[Find on LinkedIn](" + li_url + ")"
                                )

                st.markdown("**Best single contact:**   " + (intel.get("best_contact_title") or "—"))
                st.markdown("**Pitch angle:**   " + (intel.get("pitch_angle") or "—"))

                # Stage 2 — Messages
                st.markdown("---")
                st.markdown("### Generating Outreach Messages...")

                best_contact_name = ""
                if contacts:
                    best_contact_name = contacts[0].get("name","")

                with st.spinner("Stage 2 — Writing personalised messages..."):
                    messages = generate_messages(
                        intel,
                        contact_name = best_contact_name,
                        feedback     = feedback_input
                    )

                if "error" in messages or not messages:
                    st.error("Message error: " + str(messages.get("error","")))
                else:
                    # Store in session for Outreach Messages tab
                    st.session_state["current_intel"]    = intel
                    st.session_state["current_messages"] = messages
                    st.session_state["current_company"]  = company_input

                    st.success(
                        "Research and messages ready. "
                        "Go to Outreach Messages tab to view and save."
                    )

    # Show current research summary if available
    if st.session_state.get("current_company"):
        st.markdown("---")
        st.info(
            "Current research: **" + st.session_state["current_company"] + "**   "
            "— Go to Outreach Messages tab to review and save."
        )

# ════════════════════════════════════════════════
# TAB 3 — OUTREACH MESSAGES
# ════════════════════════════════════════════════
with tab3:
    st.markdown("## Outreach Messages")
    st.markdown(
        "Review, copy and save your personalised outreach messages."
    )
    st.markdown("---")

    current_intel    = st.session_state.get("current_intel")
    current_messages = st.session_state.get("current_messages")
    current_company  = st.session_state.get("current_company","")

    if not current_intel or not current_messages:
        st.info(
            "No messages generated yet. "
            "Go to Company Research, enter a company name "
            "and click Research."
        )
    else:
        st.markdown(
            "### Messages for **" + current_company + "**"
        )

        # Show contacts reminder
        contacts = current_intel.get("ideal_contacts",[])
        if contacts:
            st.markdown("**Send these messages to:**")
            for c in contacts[:3]:
                li_q = c.get("linkedin_search","")
                if li_q:
                    li_url = (
                        "https://www.linkedin.com/search/results/people/?keywords=" +
                        li_q.replace(" ","%20")
                    )
                    st.markdown(
                        "— " + c.get("title","") +
                        "   [Find on LinkedIn](" + li_url + ")"
                    )
                else:
                    st.markdown("— " + c.get("title",""))

        st.markdown("---")

        # Subject line
        subj = current_messages.get("subject_line","")
        if subj:
            st.markdown("**Email Subject Line**")
            st.code(subj, language=None)
            st.markdown("---")

        # Message tabs
        mt1, mt2, mt3, mt4 = st.tabs([
            "LinkedIn DM",
            "Cold Email",
            "Follow-up",
            "Connection Note"
        ])
        with mt1:
            st.markdown(
                "Send this after connecting on LinkedIn. "
                "Under 180 words."
            )
            st.text_area(
                "LinkedIn DM",
                current_messages.get("linkedin_dm",""),
                height=220, key="msg_li"
            )
        with mt2:
            st.markdown("Cold email body. 150-200 words.")
            st.text_area(
                "Cold Email",
                current_messages.get("cold_email",""),
                height=220, key="msg_em"
            )
        with mt3:
            st.markdown("Send this if no reply after 5 days.")
            st.text_area(
                "Follow-up",
                current_messages.get("followup",""),
                height=180, key="msg_fu"
            )
        with mt4:
            st.markdown(
                "Send with your LinkedIn connection request. "
                "Under 70 words."
            )
            st.text_area(
                "Connection Note",
                current_messages.get("connection_note",""),
                height=120, key="msg_cn"
            )

        st.markdown("---")

        # ICP and CTA reminder
        if current_intel.get("icp_match"):
            st.markdown("**ICP Match:**   " + current_intel.get("icp_match",""))
        if current_intel.get("cta"):
            st.warning("Recommended CTA:   " + current_intel.get("cta",""))

        st.markdown("---")

        # ── SAVE BUTTON ──────────────────────────
        save_col, clear_col = st.columns(2)
        with save_col:
            if st.button("Save to Lead Tracker", type="primary"):
                saved_lead = save_lead_to_db(current_intel, current_messages)
                st.success(
                    current_company + " saved to Lead Tracker!"
                )
                # Clear current research after saving
                st.session_state["prefill"] = ""
        with clear_col:
            if st.button("Clear and Research New Company"):
                st.session_state["current_intel"]    = None
                st.session_state["current_messages"] = None
                st.session_state["current_company"]  = ""
                st.session_state["prefill"]          = ""
                st.rerun()

# ════════════════════════════════════════════════
# TAB 4 — LEAD TRACKER
# ════════════════════════════════════════════════
with tab4:
    st.markdown("## Lead Tracker")
    st.markdown("Track every lead, status, messages and notes.")
    st.markdown("---")

    leads_db = st.session_state["leads_db"]

    if not leads_db:
        st.info(
            "No leads saved yet. Go to Company Research, "
            "research a company and click Save to Lead Tracker."
        )
    else:
        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads",  len(leads_db))
        m2.metric("Hot (80+)",    len([l for l in leads_db if l.get("score",0) >= 80]))
        m3.metric("Contacted",    len([l for l in leads_db if l.get("status") == "contacted"]))
        m4.metric("Replied",      len([l for l in leads_db if l.get("status") == "replied"]))

        st.markdown("---")

        # Filters
        fc1, fc2 = st.columns(2)
        with fc1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All","new","contacted","replied","meeting","closed"]
            )
        with fc2:
            min_score = st.slider("Minimum Score", 0, 100, 0)

        filtered = [
            l for l in leads_db
            if (status_filter == "All" or l.get("status") == status_filter)
            and l.get("score",0) >= min_score
        ]

        st.caption("Showing " + str(len(filtered)) + " of " + str(len(leads_db)) + " leads")
        st.markdown("---")

        for lead in filtered:
            lead_id   = lead.get("id")
            company   = lead.get("company","")
            score     = lead.get("score",0)
            status    = lead.get("status","new")
            has_msgs  = bool(lead.get("linkedin_dm") or lead.get("cold_email"))
            msg_tag   = " — Messages saved" if has_msgs else ""

            with st.expander(
                company + "   |   " + str(score) + "/100" +
                "   |   " + status.capitalize() + msg_tag
            ):
                # Company details
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown("**Industry**")
                    st.write(lead.get("industry") or "—")
                    st.markdown("**Size**")
                    st.write(lead.get("size") or "—")
                    st.markdown("**HQ**")
                    st.write(lead.get("hq") or "—")
                    st.markdown("**CEO**")
                    st.write(lead.get("ceo") or "—")
                with d2:
                    st.markdown("**Fit Score**")
                    st.write(str(score) + " / 100")
                    st.markdown("**Best Contact**")
                    st.write(lead.get("best_contact") or "—")
                    st.markdown("**ICP Match**")
                    st.write(lead.get("icp_match") or "—")
                    st.markdown("**Recommended CTA**")
                    st.write(lead.get("cta") or "—")

                if lead.get("overview"):
                    st.markdown("---")
                    st.markdown("**Overview**")
                    st.write(lead.get("overview"))

                if lead.get("pitch_angle"):
                    st.markdown("**Pitch Angle**")
                    st.write(lead.get("pitch_angle"))

                # Ideal Contacts
                contacts = lead.get("ideal_contacts",[])
                if contacts:
                    st.markdown("---")
                    st.markdown("**Ideal Contacts**")
                    for c in contacts:
                        li_q = c.get("linkedin_search","")
                        li_url = (
                            "https://www.linkedin.com/search/results/people/?keywords=" +
                            li_q.replace(" ","%20")
                        ) if li_q else ""
                        contact_line = (
                            "— **" + (c.get("name") or "Unknown") + "** — " +
                            (c.get("title") or "")
                        )
                        if li_url:
                            contact_line += "   [Find on LinkedIn](" + li_url + ")"
                        st.markdown(contact_line)
                        st.caption(c.get("why",""))

                # Saved messages
                if has_msgs:
                    st.markdown("---")
                    st.markdown("**Saved Messages**")
                    tm1, tm2, tm3, tm4 = st.tabs([
                        "LinkedIn DM", "Cold Email",
                        "Follow-up", "Connection Note"
                    ])
                    with tm1:
                        st.text_area(
                            "LinkedIn DM",
                            lead.get("linkedin_dm","") or "—",
                            height=140,
                            key="tr_li_" + str(lead_id)
                        )
                    with tm2:
                        if lead.get("subject_line"):
                            st.markdown("**Subject:** " + lead.get("subject_line",""))
                        st.text_area(
                            "Email",
                            lead.get("cold_email","") or "—",
                            height=140,
                            key="tr_em_" + str(lead_id)
                        )
                    with tm3:
                        st.text_area(
                            "Follow-up",
                            lead.get("followup","") or "—",
                            height=120,
                            key="tr_fu_" + str(lead_id)
                        )
                    with tm4:
                        st.text_area(
                            "Connection Note",
                            lead.get("connection_note","") or "—",
                            height=80,
                            key="tr_cn_" + str(lead_id)
                        )

                # Notes field
                st.markdown("---")
                st.markdown("**Notes**")
                note_val = st.text_area(
                    "Add notes about this lead",
                    lead.get("notes",""),
                    height=70,
                    key="note_" + str(lead_id),
                    placeholder="e.g. Spoke to John, follow up next Tuesday..."
                )
                if note_val != lead.get("notes",""):
                    update_lead_notes(lead_id, note_val)

                # Status update
                st.markdown("---")
                valid_statuses = ["new","contacted","replied","meeting","closed"]
                current_s = status if status in valid_statuses else "new"

                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                status_buttons = {
                    "new"      : sc1,
                    "contacted": sc2,
                    "replied"  : sc3,
                    "meeting"  : sc4,
                    "closed"   : sc5
                }
                for s_label, s_col in status_buttons.items():
                    with s_col:
                        btn_type = "primary" if current_s == s_label else "secondary"
                        if st.button(
                            s_label.capitalize(),
                            key="s_" + s_label + "_" + str(lead_id),
                            type=btn_type
                        ):
                            update_lead_status(lead_id, s_label)
                            st.rerun()

                # Added date
                st.caption("Added: " + (lead.get("created_at") or "—"))
