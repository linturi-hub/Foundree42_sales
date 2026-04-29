import streamlit as st
import groq
import json
import re
import requests
from datetime import datetime
from urllib.parse import quote_plus

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
    [data-baseweb="popover"] { background: #e8ecf1 !important; border: none !important; box-shadow: 6px 6px 12px #c5cad4, -6px -6px 12px #ffffff !important; border-radius: 10px !important; }
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

    /* Chat bubbles */
    .chat-user {
        background: #4a6fa5;
        color: #ffffff !important;
        border-radius: 14px 14px 4px 14px;
        padding: 10px 14px;
        margin: 6px 0 6px 20%;
        font-family: 'Segoe UI', sans-serif;
        font-size: 0.875rem;
        line-height: 1.5;
        box-shadow: 3px 3px 6px #c5cad4;
    }
    .chat-ai {
        background: #e8ecf1;
        color: #2d3748 !important;
        border-radius: 14px 14px 14px 4px;
        padding: 10px 14px;
        margin: 6px 20% 6px 0;
        font-family: 'Segoe UI', sans-serif;
        font-size: 0.875rem;
        line-height: 1.5;
        box-shadow: 3px 3px 6px #c5cad4, -3px -3px 6px #ffffff;
    }
    .chat-label-user { text-align: right; font-size: 0.7rem; color: #a0aec0; margin: 2px 4px; font-family: 'Segoe UI', sans-serif; }
    .chat-label-ai { text-align: left; font-size: 0.7rem; color: #a0aec0; margin: 2px 4px; font-family: 'Segoe UI', sans-serif; }
    .chat-container { max-height: 400px; overflow-y: auto; padding: 8px 4px; margin-bottom: 12px; }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INIT ────────────────────────────
defaults = {
    "leads_db"         : [],
    "discovered"       : [],
    "prefill"          : "",
    "next_id"          : 1,
    "current_intel"    : None,
    "current_messages" : None,
    "current_company"  : "",
    "chat_history"     : [],
    "active_msg_type"  : "linkedin_dm",
    "api_key"          : ""
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
        placeholder="paste your key here",
        value=st.session_state["api_key"]
    )
    if api_key:
        st.session_state["api_key"] = api_key
        st.success("API key active")

    st.markdown("---")

    db        = st.session_state["leads_db"]
    total     = len(db)
    hot       = len([l for l in db if l.get("score",0) >= 80])
    contacted = len([l for l in db if l.get("status") == "contacted"])
    replied   = len([l for l in db if l.get("status") == "replied"])

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total",     total)
    with col_b:
        st.metric("Hot",       hot)
    col_c, col_d = st.columns(2)
    with col_c:
        st.metric("Contacted", contacted)
    with col_d:
        st.metric("Replied",   replied)

    st.markdown("---")
    st.caption("Foundree42 — US Market")
    st.caption("Data saves within this session")

# ── DB HELPERS ────────────────────────────────────
def save_lead_to_db(intel, messages):
    company = intel.get("company","")
    for i, existing in enumerate(st.session_state["leads_db"]):
        if existing.get("company","").lower() == company.lower():
            st.session_state["leads_db"][i].update({
                **intel,
                "linkedin_dm"    : messages.get("linkedin_dm",""),
                "cold_email"     : messages.get("cold_email",""),
                "subject_line"   : messages.get("subject_line",""),
                "followup"       : messages.get("followup",""),
                "connection_note": messages.get("connection_note",""),
                "updated_at"     : datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            return st.session_state["leads_db"][i]

    lead = {
        "id"             : st.session_state["next_id"],
        "status"         : "new",
        "created_at"     : datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at"     : datetime.now().strftime("%Y-%m-%d %H:%M"),
        "notes"          : "",
        "linkedin_dm"    : messages.get("linkedin_dm",""),
        "cold_email"     : messages.get("cold_email",""),
        "subject_line"   : messages.get("subject_line",""),
        "followup"       : messages.get("followup",""),
        "connection_note": messages.get("connection_note",""),
        **intel
    }
    st.session_state["leads_db"].insert(0, lead)
    st.session_state["next_id"] += 1
    return lead

def update_lead_field(lead_id, field, value):
    for i, l in enumerate(st.session_state["leads_db"]):
        if l.get("id") == lead_id:
            st.session_state["leads_db"][i][field] = value
            break

# ── AI ────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a senior sales intelligence analyst for Foundree42, "
    "a US-based Salesforce consultancy specialising in senior-led "
    "implementations, platform governance, managed services, and project rescue. "
    "Foundree42 targets US companies with these 6 ideal client profiles: "
    "ICP1: $1B+ firms with underperforming Salesforce partners needing a senior-led reset. "
    "ICP2: $500M-$3B orgs with fragmented Salesforce needing platform governance and stewardship. "
    "ICP3: $50M-$500M mid-market with no internal Salesforce team needing virtual managed support. "
    "ICP4: Companies with inherited messy Salesforce orgs needing an automation audit. "
    "ICP5: Mid-market and enterprise replacing offshore Salesforce delivery for better outcomes. "
    "ICP6: Companies needing trusted senior Salesforce delivery to reduce project risk. "
    "Target buyer roles: Salesforce Platform Owner, VP RevOps, COO, CIO, IT Director, "
    "Enterprise Architect, PMO Leader, Salesforce Admin Lead, Head of CRM, VP Sales. "
    "ACCURACY RULES: Never invent specific employee names. If you are not highly confident a "
    "person is currently at this company in this role, leave name fields empty and return only "
    "the role title. Only include facts you have grounded knowledge of. Mark uncertainty honestly. "
    "Always return valid JSON only. No markdown fences. No explanation. No preamble."
)

def ask_ai(prompt, system_override=None, json_mode=False, temperature=0.3, max_tokens=2500):
    if not st.session_state.get("api_key"):
        return "ERROR: No API key. Please paste your Groq key in the sidebar."
    try:
        client = groq.Groq(api_key=st.session_state["api_key"])
        kwargs = {
            "model"       : "llama-3.3-70b-versatile",
            "messages"    : [
                {"role": "system", "content": system_override or SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            "temperature" : temperature,
            "max_tokens"  : max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content
    except Exception as e:
        return "ERROR: " + str(e)

def ask_ai_chat(messages_history, temperature=0.5):
    """For the message refinement chatbot — maintains full conversation."""
    if not st.session_state.get("api_key"):
        return "ERROR: No API key set."
    try:
        client = groq.Groq(api_key=st.session_state["api_key"])
        resp   = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_history,
            temperature=temperature,
            max_tokens=1200
        )
        return resp.choices[0].message.content
    except Exception as e:
        return "ERROR: " + str(e)

def parse_json(raw):
    if not isinstance(raw, str):
        return {}
    clean = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(clean)
    except Exception:
        pass
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    match = re.search(r"\[.*\]", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {}

# ── GROUNDING SIGNALS ─────────────────────────────
def get_live_news(company):
    try:
        url    = "https://news.google.com/rss/search"
        params = {
            "q"   : '"' + company + '" Salesforce OR CRM OR funding OR hiring OR acquisition OR expansion',
            "hl"  : "en-US",
            "gl"  : "US",
            "ceid": "US:en"
        }
        resp  = requests.get(url, params=params, timeout=6)
        items = re.findall(r"<title>(.*?)</title>", resp.text)[1:6]
        clean = [re.sub(r"<.*?>|&amp;|&quot;|&#39;|&lt;|&gt;", "", i).strip() for i in items]
        return [c for c in clean if len(c) > 15]
    except Exception:
        return []

def get_hiring_signal(company):
    try:
        url    = "https://news.google.com/rss/search"
        params = {"q": company + " Salesforce Administrator OR RevOps OR CRM Manager hiring", "hl": "en-US"}
        resp   = requests.get(url, params=params, timeout=5)
        items  = re.findall(r"<title>(.*?)</title>", resp.text)[1:3]
        return len(items) > 0
    except Exception:
        return False

def get_funding_signal(company):
    try:
        url    = "https://news.google.com/rss/search"
        params = {"q": '"' + company + '" funding OR Series OR acquired OR IPO', "hl": "en-US"}
        resp   = requests.get(url, params=params, timeout=5)
        items  = re.findall(r"<title>(.*?)</title>", resp.text)[1:3]
        return len(items) > 0
    except Exception:
        return False

def get_company_homepage_blurb(company):
    """Best-effort fetch of the company's homepage to ground the LLM in current text."""
    try:
        slug = re.sub(r"[^a-z0-9]", "", company.lower())
        if not slug:
            return ""
        candidates = [
            "https://www." + slug + ".com",
            "https://" + slug + ".com",
            "https://www." + slug + ".io",
        ]
        for url in candidates:
            try:
                resp = requests.get(
                    url,
                    timeout=4,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; Foundree42Bot/1.0)"}
                )
                if resp.status_code == 200 and len(resp.text) > 200:
                    html  = resp.text
                    parts = []
                    title_m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
                    if title_m:
                        parts.append("Title: " + title_m.group(1).strip()[:200])
                    desc_m = re.search(
                        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
                        html, re.IGNORECASE
                    )
                    if desc_m:
                        parts.append("Description: " + desc_m.group(1).strip()[:400])
                    og_m = re.search(
                        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)',
                        html, re.IGNORECASE
                    )
                    if og_m and not desc_m:
                        parts.append("OG: " + og_m.group(1).strip()[:400])
                    if parts:
                        return " | ".join(parts)
            except Exception:
                continue
        return ""
    except Exception:
        return ""

# ── DETERMINISTIC SCORING ─────────────────────────
def linkedin_profile_search_url(query):
    """Google search scoped to LinkedIn profiles - far more accurate than LinkedIn's own search."""
    if not query:
        return ""
    return "https://www.google.com/search?q=" + quote_plus("site:linkedin.com/in/ " + query)

def compute_fit_score(features):
    """
    Deterministic 0-100 fit score from extracted features.
    Same features -> same score, every time. No LLM randomness.
    Weights are tuned for Foundree42's 6 ICPs.
    """
    score = 0
    reasons = []

    # Revenue band fit (max 25)
    rb = (features.get("revenue_band") or "").lower()
    if any(k in rb for k in ["3b", "10b", "1b+"]):
        score += 25; reasons.append("Enterprise revenue (ICP1/2 fit)")
    elif "1b" in rb or "billion" in rb:
        score += 24; reasons.append("$1B+ revenue (ICP1 fit)")
    elif "500m" in rb or "500m-3b" in rb:
        score += 22; reasons.append("$500M-3B revenue (ICP2 fit)")
    elif "50m" in rb or "100m" in rb or "200m" in rb or "50-500m" in rb:
        score += 18; reasons.append("Mid-market revenue (ICP3 fit)")
    elif "10m" in rb or "10-50m" in rb:
        score += 8;  reasons.append("Sub-mid-market revenue")
    elif "<10m" in rb or "under" in rb:
        score += 3;  reasons.append("SMB revenue (below ICP)")
    else:
        score += 10; reasons.append("Revenue unknown")

    # ICP match (max 22)
    icp = features.get("icp_match_number")
    try:
        icp_num = int(icp) if icp is not None else 0
    except (TypeError, ValueError):
        icp_num = 0
    if 1 <= icp_num <= 6:
        score += 22; reasons.append("Maps to ICP" + str(icp_num))
    else:
        score += 6;  reasons.append("No clear ICP match")

    # Salesforce status (max 20)
    sf = (features.get("salesforce_status") or "").lower()
    if "uses_salesforce" in sf or "uses salesforce" in sf or "current" in sf or "implementing" in sf:
        score += 20; reasons.append("Active Salesforce user")
    elif "evaluating" in sf or "considering" in sf or "replacing" in sf:
        score += 17; reasons.append("Salesforce in motion")
    elif "no_salesforce" in sf or "no salesforce" in sf or "none" in sf:
        score += 4;  reasons.append("No Salesforce footprint")
    else:
        score += 9;  reasons.append("Salesforce status unknown")

    # Hiring signal (max 10)
    if features.get("hiring_signal"):
        score += 10; reasons.append("Hiring CRM/RevOps roles")

    # Funding / growth (max 10)
    if features.get("funding_signal"):
        score += 10; reasons.append("Recent funding or M&A")
    elif features.get("growth_signal"):
        score += 6;  reasons.append("Growth signals")

    # Org complexity (max 13) — multi-cloud, M&A debt, fragmented stack favor Foundree42
    cx = (features.get("complexity") or "").lower()
    if "high" in cx:
        score += 13; reasons.append("High org complexity")
    elif "medium" in cx or "moderate" in cx or "med" in cx:
        score += 8;  reasons.append("Moderate org complexity")
    elif "low" in cx:
        score += 2;  reasons.append("Low org complexity")
    else:
        score += 5

    score = min(100, max(0, score))
    return score, reasons

def score_label(score):
    if score >= 80: return "Hot"
    if score >= 60: return "Warm"
    return "Cold"

# ── RESEARCH ──────────────────────────────────────
def research_company(company, contact="", title=""):
    news      = get_live_news(company)
    hiring    = get_hiring_signal(company)
    funding   = get_funding_signal(company)
    homepage  = get_company_homepage_blurb(company)

    grounding = ""
    if homepage:
        grounding += "\nHOMEPAGE EXCERPT (current): " + homepage[:700]
    if news:
        grounding += "\nRECENT NEWS (last 30 days): " + " | ".join(news[:4])
    if hiring:
        grounding += "\nHIRING SIGNAL: actively posting Salesforce/CRM/RevOps roles."
    if funding:
        grounding += "\nFUNDING/M&A SIGNAL: recent funding or acquisition activity detected."

    contact_ctx = ""
    if contact:
        contact_ctx = " Known contact: " + contact + (" (" + title + ")" if title else "") + "."

    prompt = (
        "Research the US company: " + company + "."
        + contact_ctx
        + grounding
        + "\n\nCRITICAL ACCURACY RULES:"
        + "\n- DO NOT invent or guess employee names. If you cannot name a real current employee with high confidence, leave 'name' as empty string and return only the role title."
        + "\n- For revenue and headcount, use the bands provided. If unsure, choose the broader band."
        + "\n- For salesforce_status, only say 'uses_salesforce' if you have grounded evidence (job postings, news, homepage)."
        + "\n- Pain points and triggers must reference the homepage excerpt or news above when possible."
        + "\n- If the homepage or news is empty and you have low confidence, set salesforce_status to 'unknown' and complexity to 'unknown'."
        + "\n\nReturn ONLY this JSON object:"
        + "\n{"
        + '\n  "company": "' + company + '",'
        + '\n  "overview": "2-3 sentence accurate summary grounded in the homepage excerpt or news above",'
        + '\n  "industry": "specific industry vertical",'
        + '\n  "size": "headcount range and revenue range",'
        + '\n  "revenue_band": "one of: <10M | 10-50M | 50-500M | 500M-3B | 1B+ | 3B+ | unknown",'
        + '\n  "headcount_band": "one of: <50 | 50-200 | 200-500 | 500-2000 | 2000-10000 | 10000+ | unknown",'
        + '\n  "hq": "city, state",'
        + '\n  "ceo": "current CEO full name only if you are highly confident, else empty string",'
        + '\n  "current_crm": "their CRM stack and Salesforce usage details if known, else empty",'
        + '\n  "salesforce_status": "one of: uses_salesforce | evaluating | considering_replacement | no_salesforce | unknown",'
        + '\n  "icp_match_number": 0,'
        + '\n  "icp_match": "ICP X — one specific sentence why they match",'
        + '\n  "complexity": "one of: high | medium | low | unknown",'
        + '\n  "hiring_signal": false,'
        + '\n  "funding_signal": false,'
        + '\n  "growth_signal": false,'
        + '\n  "pain_points": ["specific pain 1", "specific pain 2", "specific pain 3"],'
        + '\n  "recent_triggers": ["specific signal 1", "signal 2", "signal 3"],'
        + '\n  "ideal_contacts": ['
        + '\n    {"name": "real current employee name ONLY if high confidence else empty", "title": "exact US job title", "why": "one specific reason this role matters", "search_query": "Job Title at Company Name"},'
        + '\n    {"name": "", "title": "second target role", "why": "why they matter", "search_query": "..."},'
        + '\n    {"name": "", "title": "third target role", "why": "why they matter", "search_query": "..."}'
        + '\n  ],'
        + '\n  "best_contact_title": "single best target job title",'
        + '\n  "pitch_angle": "one specific sentence pitch referencing a real detail from the grounding above",'
        + '\n  "cta": "one of: Reset Assessment | Governance Workshop | Managed Services Quote | Automation Audit | Delivery Model Review | Talk to Senior Architect"'
        + "\n}"
    )

    raw = ask_ai(prompt, json_mode=True, temperature=0.0, max_tokens=2500)
    if isinstance(raw, str) and raw.startswith("ERROR"):
        return {"error": raw}
    result = parse_json(raw)
    if not isinstance(result, dict) or not result:
        return {"error": "Could not parse research response."}

    # Override model-claimed signals with our live detection (live wins)
    result["hiring_signal"] = bool(hiring or result.get("hiring_signal", False))
    result["funding_signal"] = bool(funding or result.get("funding_signal", False))

    # Inject live news as triggers (live wins)
    if news:
        existing = result.get("recent_triggers", []) or []
        merged = news[:2] + [t for t in existing if t and t not in news]
        result["recent_triggers"] = merged[:4]

    # Compute deterministic score from features (replaces LLM-decided score)
    score, reasons = compute_fit_score(result)
    result["score"] = score
    result["score_breakdown"] = reasons

    # Build accurate Google-scoped LinkedIn URLs for each contact
    contacts = result.get("ideal_contacts", []) or []
    for c in contacts:
        # Prefer name-based search if name is real, else title + company
        name = (c.get("name") or "").strip()
        title_str = (c.get("title") or "").strip()
        if name and name.lower() not in ["unknown", "n/a", "none", "not found", ""]:
            q = name + " " + company
        else:
            q = title_str + " " + company
            c["name"] = ""  # blank rather than fake
        c["search_query"] = q
        c["linkedin_url"] = linkedin_profile_search_url(q)
    result["ideal_contacts"] = contacts

    return result

# ── DISCOVER ──────────────────────────────────────
def discover_leads(industry, location, revenue, size, signals, count):
    prompt = (
        "Find " + str(count) + " real US companies that are strong Salesforce "
        "consultancy prospects for Foundree42. "
        "Search criteria: Industry=" + industry
        + " | Location=" + location
        + " | Revenue=" + revenue
        + " | Size=" + size
        + " | Buying signals=" + signals + ". "
        + "\n\nACCURACY RULES:"
        + "\n- Only return REAL US companies you have grounded knowledge of. Do not invent."
        + "\n- For each, return STRUCTURED FEATURES — do not return a holistic score. The app computes the score deterministically."
        + "\n- If you cannot find " + str(count) + " strong matches, return fewer rather than padding with weak ones."
        + "\n\nReturn ONLY a JSON object with key 'leads' containing an array:"
        + '\n{"leads": [{'
        + '\n  "company": "exact real US company name",'
        + '\n  "industry": "specific industry vertical",'
        + '\n  "headcount_band": "one of: <50 | 50-200 | 200-500 | 500-2000 | 2000-10000 | 10000+ | unknown",'
        + '\n  "revenue_band": "one of: <10M | 10-50M | 50-500M | 500M-3B | 1B+ | 3B+ | unknown",'
        + '\n  "location": "city, state",'
        + '\n  "salesforce_status": "uses_salesforce | evaluating | considering_replacement | no_salesforce | unknown",'
        + '\n  "icp_match_number": 0,'
        + '\n  "why_fit": "specific ICP match reason referencing a real detail",'
        + '\n  "trigger": "specific buying signal",'
        + '\n  "best_contact": "ideal US job title to target",'
        + '\n  "complexity": "high | medium | low | unknown",'
        + '\n  "hiring_signal": false,'
        + '\n  "funding_signal": false,'
        + '\n  "growth_signal": false'
        + "\n}]}"
    )
    raw = ask_ai(prompt, json_mode=True, temperature=0.0, max_tokens=2500)
    if isinstance(raw, str) and raw.startswith("ERROR"):
        st.error(raw)
        return []
    result = parse_json(raw)
    leads = []
    if isinstance(result, list):
        leads = result
    elif isinstance(result, dict):
        if "leads" in result and isinstance(result["leads"], list):
            leads = result["leads"]
        else:
            for v in result.values():
                if isinstance(v, list):
                    leads = v
                    break

    # Compute deterministic score per lead, normalize fields
    scored = []
    for lead in leads:
        if not isinstance(lead, dict):
            continue
        score, reasons = compute_fit_score(lead)
        lead["score"] = score
        lead["score_breakdown"] = reasons
        # Friendly aliases for display
        if not lead.get("size"):
            lead["size"] = lead.get("headcount_band", "unknown")
        if not lead.get("revenue"):
            lead["revenue"] = lead.get("revenue_band", "unknown")
        scored.append(lead)
    return scored

# ── GENERATE MESSAGES ─────────────────────────────
GOOD_MESSAGE_EXAMPLE = (
    'Example of a strong Foundree42 LinkedIn DM:\n'
    '"Hi Sarah — saw the Acme + BrightCo announcement last month and your team is now '
    'integrating two Salesforce orgs. We have led 14 post-merger Salesforce consolidations '
    'in the last two years; the pattern we keep seeing is 6-8 weeks of governance work '
    'before any rebuild starts, otherwise the same data debt resurfaces six months later. '
    'Worth a 20-minute call to compare notes on where Acme is in that arc? '
    '— The Foundree42 Team"\n\n'
    'Why this works: opens with a real, recent fact about their company; states a specific '
    'number from our experience; offers a concrete observation, not a pitch; ends with a '
    'low-friction CTA tied to their situation.'
)

def generate_messages(lead_data, contact_name="", feedback=""):
    contacts = lead_data.get("ideal_contacts", []) or []
    contact_name = contact_name or (contacts[0].get("name", "") if contacts else "")
    first_name = ""
    if contact_name and contact_name.lower() not in ["unknown", "not found", "n/a", ""]:
        parts      = contact_name.strip().split()
        first_name = parts[0] if parts else ""

    greeting = "Hi " + first_name if first_name else "Hi there"

    contact_role = ""
    if contacts:
        best = contacts[0]
        contact_role = best.get("title", "") or ""

    pain_str    = "; ".join([str(p) for p in (lead_data.get("pain_points") or [])])
    trigger_str = "; ".join([str(t) for t in (lead_data.get("recent_triggers") or [])])

    prompt = (
        GOOD_MESSAGE_EXAMPLE
        + "\n\nNow write Salesforce consultancy outreach for the US company: "
        + lead_data.get("company", "") + "."
        + "\nGreeting to use: " + greeting + "."
        + "\nTarget role: " + (contact_role or lead_data.get("best_contact_title", "")) + "."
        + "\nICP: " + (lead_data.get("icp_match") or "") + "."
        + "\nIndustry: " + (lead_data.get("industry") or "") + "."
        + "\nOverview: " + (lead_data.get("overview") or "") + "."
        + "\nPain points: " + pain_str + "."
        + "\nReal recent triggers: " + trigger_str + "."
        + "\nPitch angle: " + (lead_data.get("pitch_angle") or "") + "."
        + "\nCTA: " + (lead_data.get("cta") or "") + "."
        + (("\nUser style instructions: " + feedback) if feedback else "")
        + "\n\nMUST follow the GOOD example pattern above. Each message must:"
        + "\n  1. Reference at least 2 specific real facts from the triggers/overview above."
        + "\n  2. Include one concrete number, timeframe, or observation from senior consulting experience."
        + "\n  3. End with a low-friction question or the recommended CTA — never both."
        + "\n  4. Sound like a senior consultant comparing notes, not a salesperson pitching."
        + "\n  5. Sign off as 'The Foundree42 Team'."
        + "\nAvoid these openers entirely: 'I hope this finds you well', 'I wanted to reach out', 'I came across your profile'."
        + "\n\nReturn ONLY this JSON object:"
        + "\n{"
        + '\n  "subject_line": "compelling subject under 10 words referencing a real fact",'
        + '\n  "linkedin_dm": "150-180 words, conversational, ends with soft question",'
        + '\n  "cold_email": "160-200 words, professional, ends with one direct question",'
        + '\n  "followup": "under 120 words, completely different angle from the first message",'
        + '\n  "connection_note": "under 60 words, warm and specific to their company"'
        + "\n}"
    )
    raw = ask_ai(prompt, json_mode=True, temperature=0.6, max_tokens=2000)
    if isinstance(raw, str) and raw.startswith("ERROR"):
        return {"error": raw}
    return parse_json(raw)

# ── MESSAGE CHATBOT ───────────────────────────────
def build_chat_system_prompt(intel, msg_type, current_msg):
    msg_labels = {
        "linkedin_dm"    : "LinkedIn DM",
        "cold_email"     : "Cold Email",
        "followup"       : "Follow-up message",
        "connection_note": "LinkedIn Connection Note",
        "subject_line"   : "Email Subject Line"
    }
    label = msg_labels.get(msg_type, "outreach message")
    return (
        "You are a senior sales writing consultant for Foundree42, a US-based Salesforce consultancy. "
        "You are helping refine a " + label + " for the US company " + intel.get("company", "") + ".\n\n"
        "Company context:\n"
        "- Industry: " + (intel.get("industry") or "") + "\n"
        "- Size: " + (intel.get("size") or "") + "\n"
        "- ICP: " + (intel.get("icp_match") or "") + "\n"
        "- Pain points: " + "; ".join([str(p) for p in (intel.get("pain_points") or [])]) + "\n"
        "- Triggers: " + "; ".join([str(t) for t in (intel.get("recent_triggers") or [])]) + "\n"
        "- Pitch angle: " + (intel.get("pitch_angle") or "") + "\n"
        "- CTA: " + (intel.get("cta") or "") + "\n\n"
        "Current " + label + ":\n---\n" + current_msg + "\n---\n\n"
        "RESPONSE FORMAT — return JSON ONLY:\n"
        '{"intent": "rewrite" or "chat", "content": "..."}\n'
        "- Use intent=\"rewrite\" when the user asks you to change, shorten, lengthen, rewrite, "
        "or adjust the message. The 'content' field must contain ONLY the new message text "
        "with no explanation, preamble, or labels.\n"
        "- Use intent=\"chat\" when the user asks a question or wants advice. The 'content' "
        "field contains your conversational reply.\n\n"
        "All rewrites must keep referencing real facts about " + intel.get("company", "") + ". "
        "Never produce generic copy."
    )

def parse_chat_response(raw):
    """Parses the chatbot JSON response. Returns (intent, content)."""
    obj = parse_json(raw)
    if isinstance(obj, dict) and "intent" in obj and "content" in obj:
        intent = (obj.get("intent") or "chat").lower()
        if intent not in ("rewrite", "chat"):
            intent = "chat"
        return intent, str(obj.get("content") or "").strip()
    # Fallback: treat raw as chat reply
    return "chat", (raw or "").strip()

def ask_ai_chat_json(messages_history, temperature=0.5):
    """Chat call with JSON mode forced."""
    if not st.session_state.get("api_key"):
        return "ERROR: No API key set."
    try:
        client = groq.Groq(api_key=st.session_state["api_key"])
        resp   = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_history,
            temperature=temperature,
            max_tokens=1200,
            response_format={"type": "json_object"}
        )
        return resp.choices[0].message.content
    except Exception as e:
        return "ERROR: " + str(e)

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
            "Any revenue", "Under $10M", "Under $50M",
            "$50M - $500M", "$500M - $3B", "$1B+", "Over $3B"
        ])
        icp_size = st.selectbox("Company Size", [
            "Any size", "1-50 employees", "50-200 employees",
            "200-500 employees", "500-2,000 employees",
            "2,000-10,000 employees", "10,000+ employees"
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
                    signals  = icp_signals or "CRM investment, hiring sales ops, scaling sales team",
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
            label = score_label(score)
            with st.expander(
                lead.get("company","") + "   |   Score: " +
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
                        (lead.get("location") or "") + "   ·   " +
                        (lead.get("size") or "") + "   ·   " +
                        (lead.get("revenue") or "")
                    )
                with col_b:
                    st.metric("Fit Score", str(score) + "/100")
                breakdown = lead.get("score_breakdown") or []
                if breakdown:
                    with st.expander("How this score was computed", expanded=False):
                        for r in breakdown:
                            st.markdown("— " + str(r))
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
        "Full AI pipeline: company intelligence, ICP match, "
        "ideal contacts, pitch strategy and outreach messages."
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
            "Message Style Instructions (optional)",
            placeholder="e.g. more direct, lead with ROI, reference their funding round...",
            height=68
        )

    st.markdown("---")

    if st.button("Research and Generate Everything", type="primary"):
        if not st.session_state.get("api_key"):
            st.error("Add your API key in the sidebar.")
        elif not company_input:
            st.error("Enter a company name.")
        else:
            with st.spinner("Stage 1 — Researching " + company_input + " with live signals..."):
                intel = research_company(company_input)

            if "error" in intel or not intel:
                st.error("Research failed: " + str(intel.get("error","")))
            else:
                score = intel.get("score",0)
                st.markdown("---")
                st.markdown("### Company Intelligence")

                m1, m2, m3 = st.columns(3)
                m1.metric("Industry",      intel.get("industry","—"))
                m2.metric("Size",          intel.get("size","—"))
                m3.metric("Salesforce Fit", str(score) + " / 100")

                st.markdown("**Overview**")
                st.write(intel.get("overview",""))

                if intel.get("icp_match"):
                    st.info("ICP Match:   " + intel.get("icp_match",""))
                if intel.get("cta"):
                    st.warning("Recommended CTA:   " + intel.get("cta",""))

                breakdown = intel.get("score_breakdown") or []
                if breakdown:
                    with st.expander("Score breakdown (deterministic)", expanded=False):
                        for r in breakdown:
                            st.markdown("— " + str(r))

                col_p, col_t = st.columns(2)
                with col_p:
                    st.markdown("**Pain Points**")
                    for p in (intel.get("pain_points") or []):
                        st.markdown("— " + str(p))
                with col_t:
                    st.markdown("**Recent Triggers and Live News**")
                    for t in (intel.get("recent_triggers") or []):
                        st.markdown("— " + str(t))

                # Ideal Contacts
                st.markdown("---")
                st.markdown("### Ideal Contacts to Reach")
                contacts = intel.get("ideal_contacts",[])
                if contacts:
                    for idx, contact in enumerate(contacts):
                        title_disp = contact.get("title","") or "—"
                        name_disp  = contact.get("name","") or "(role only — name not verified)"
                        with st.expander(
                            "Contact " + str(idx+1) + " — " + title_disp,
                            expanded=(idx == 0)
                        ):
                            cc1, cc2 = st.columns(2)
                            with cc1:
                                st.markdown("**Name**")
                                st.write(name_disp)
                                st.markdown("**Job Title**")
                                st.write(title_disp)
                            with cc2:
                                st.markdown("**Why Target Them**")
                                st.write(contact.get("why","—"))
                            li_url = contact.get("linkedin_url") or linkedin_profile_search_url(contact.get("search_query",""))
                            if li_url:
                                st.markdown("[Find on LinkedIn (Google profile search)](" + li_url + ")")

                st.markdown("**Best contact role:**   " + (intel.get("best_contact_title") or "—"))
                st.markdown("**Pitch angle:**   " + (intel.get("pitch_angle") or "—"))

                # Messages
                st.markdown("---")
                st.markdown("### Generating Outreach Messages...")
                best_name = contacts[0].get("name","") if contacts else ""

                with st.spinner("Stage 2 — Writing personalised messages..."):
                    messages = generate_messages(intel, best_name, feedback_input)

                if "error" in messages or not messages:
                    st.error("Message error: " + str(messages.get("error","")))
                else:
                    st.session_state["current_intel"]    = intel
                    st.session_state["current_messages"] = messages
                    st.session_state["current_company"]  = company_input
                    st.session_state["chat_history"]     = []
                    st.session_state["prefill"]          = ""
                    # Clear any stale per-message edit widgets so the new content shows
                    for mk in ["linkedin_dm", "cold_email", "followup", "connection_note"]:
                        widget_key = "msg_edit_" + mk
                        if widget_key in st.session_state:
                            del st.session_state[widget_key]
                        chat_key = "chat_" + mk
                        st.session_state[chat_key] = []

                    st.success(
                        "Research and messages ready. "
                        "Go to Outreach Messages tab to review, refine and save."
                    )

    if st.session_state.get("current_company"):
        st.markdown("---")
        st.info(
            "Current research: **" + st.session_state["current_company"] + "**"
            "   — Go to Outreach Messages to review, refine and save."
        )

# ════════════════════════════════════════════════
# TAB 3 — OUTREACH MESSAGES
# ════════════════════════════════════════════════
with tab3:
    st.markdown("## Outreach Messages")
    st.markdown(
        "Review your messages, use the AI assistant to refine them, "
        "then save to your Lead Tracker."
    )
    st.markdown("---")

    intel    = st.session_state.get("current_intel")
    messages = st.session_state.get("current_messages")
    company  = st.session_state.get("current_company","")

    if not intel or not messages:
        st.info(
            "No messages yet. Go to Company Research, "
            "enter a company name and click Research."
        )
    else:
        st.markdown("### Messages for **" + company + "**")

        # Contacts reminder
        contacts = intel.get("ideal_contacts",[])
        if contacts:
            st.markdown("**Send to:**")
            for c in contacts[:3]:
                li_url = c.get("linkedin_url") or linkedin_profile_search_url(c.get("search_query",""))
                title_disp = c.get("title","") or ""
                name_disp  = c.get("name","") or ""
                line = "— " + title_disp
                if name_disp:
                    line = "— **" + name_disp + "** — " + title_disp
                if li_url:
                    line += "   [Find on LinkedIn](" + li_url + ")"
                st.markdown(line)

        st.markdown("---")

        # Subject line
        subj = messages.get("subject_line","")
        if subj:
            st.markdown("**Email Subject Line**")
            st.code(subj, language=None)

        # ── MESSAGE TABS ──────────────────────────
        mt1, mt2, mt3, mt4 = st.tabs([
            "LinkedIn DM",
            "Cold Email",
            "Follow-up",
            "Connection Note"
        ])

        msg_type_map = {
            0: ("linkedin_dm",     "LinkedIn DM"),
            1: ("cold_email",      "Cold Email"),
            2: ("followup",        "Follow-up"),
            3: ("connection_note", "Connection Note"),
        }

        for tab_idx, msg_tab in enumerate([mt1, mt2, mt3, mt4]):
            msg_key, msg_label = msg_type_map[tab_idx]
            with msg_tab:
                widget_key = "msg_edit_" + msg_key
                # Initialise widget value from current_messages on first render
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = messages.get(msg_key, "")

                edited = st.text_area(
                    msg_label,
                    height=200 if msg_key != "connection_note" else 120,
                    key=widget_key
                )

                # Sync widget value back into current_messages for saving
                if st.session_state[widget_key] != messages.get(msg_key, ""):
                    st.session_state["current_messages"][msg_key] = st.session_state[widget_key]

                st.markdown("---")

                # ── AI REFINEMENT CHATBOT ──────────
                st.markdown("**AI Message Assistant**")
                st.caption(
                    "Tell the AI how to improve this specific message. "
                    "It will rewrite it for you and apply it on confirmation."
                )

                # Quick action buttons (auto-apply the rewrite)
                qa1, qa2, qa3, qa4 = st.columns(4)
                quick_actions = {
                    "Make it shorter"      : qa1,
                    "Make it more direct"  : qa2,
                    "More formal tone"     : qa3,
                    "Add a specific detail": qa4,
                }

                for action_label, action_col in quick_actions.items():
                    with action_col:
                        if st.button(action_label, key="qa_" + msg_key + "_" + action_label.replace(" ","_")):
                            chat_sys = build_chat_system_prompt(
                                intel, msg_key,
                                st.session_state["current_messages"].get(msg_key, "")
                            )
                            history  = [
                                {"role": "system", "content": chat_sys},
                                {"role": "user",   "content": action_label + ". Return only the rewritten message in the JSON format described."}
                            ]
                            with st.spinner("Rewriting..."):
                                raw = ask_ai_chat_json(history)
                            if isinstance(raw, str) and raw.startswith("ERROR"):
                                st.error(raw)
                            else:
                                intent, content = parse_chat_response(raw)
                                new_msg = content if content else ""
                                if new_msg:
                                    # Programmatically update the widget BEFORE next render
                                    st.session_state[widget_key] = new_msg
                                    st.session_state["current_messages"][msg_key] = new_msg
                                    st.rerun()

                # Chat history display
                chat_key = "chat_" + msg_key
                if chat_key not in st.session_state:
                    st.session_state[chat_key] = []

                if st.session_state[chat_key]:
                    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
                    for entry in st.session_state[chat_key]:
                        if entry["role"] == "user":
                            st.markdown(
                                "<div class='chat-label-user'>You</div>"
                                "<div class='chat-user'>" + entry["content"] + "</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            label_html = "Foundree42 AI"
                            if entry.get("intent") == "rewrite":
                                label_html += " — proposed rewrite"
                            st.markdown(
                                "<div class='chat-label-ai'>" + label_html + "</div>"
                                "<div class='chat-ai'>" + entry["content"].replace("\n", "<br>") + "</div>",
                                unsafe_allow_html=True
                            )
                            # Apply button for proposed rewrites
                            if entry.get("intent") == "rewrite" and not entry.get("applied"):
                                btn_id = "apply_" + msg_key + "_" + str(entry.get("ts",""))
                                if st.button("Apply this as the new " + msg_label, key=btn_id):
                                    st.session_state[widget_key] = entry["content"]
                                    st.session_state["current_messages"][msg_key] = entry["content"]
                                    entry["applied"] = True
                                    st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                # Chat input — uses a session-keyed input we can clear after send
                input_key = "chat_input_" + msg_key
                if input_key not in st.session_state:
                    st.session_state[input_key] = ""

                chat_input = st.text_input(
                    "Ask the AI to refine this message",
                    placeholder="e.g. Reference their recent Series B funding... make it shorter... change the CTA...",
                    key=input_key
                )

                send_col, clear_col = st.columns([3,1])
                with send_col:
                    if st.button("Send", key="chat_send_" + msg_key):
                        user_text = (st.session_state.get(input_key) or "").strip()
                        if user_text:
                            chat_sys = build_chat_system_prompt(
                                intel, msg_key,
                                st.session_state["current_messages"].get(msg_key, "")
                            )
                            history = [{"role": "system", "content": chat_sys}]
                            for entry in st.session_state[chat_key]:
                                # Pass prior chat as plain content, not nested JSON
                                history.append({"role": entry["role"], "content": entry["content"]})
                            history.append({"role": "user", "content": user_text})

                            with st.spinner("Thinking..."):
                                raw = ask_ai_chat_json(history)

                            if isinstance(raw, str) and raw.startswith("ERROR"):
                                st.error(raw)
                            else:
                                intent, content = parse_chat_response(raw)
                                ts = datetime.now().strftime("%H%M%S%f")
                                st.session_state[chat_key].append({
                                    "role": "user", "content": user_text, "ts": ts
                                })
                                st.session_state[chat_key].append({
                                    "role": "assistant",
                                    "content": content or "(no content returned)",
                                    "intent": intent,
                                    "ts": ts,
                                    "applied": False
                                })
                                # Clear the input widget for next turn
                                st.session_state[input_key] = ""
                                st.rerun()

                with clear_col:
                    if st.button("Clear chat", key="chat_clear_" + msg_key):
                        st.session_state[chat_key] = []
                        st.session_state[input_key] = ""
                        st.rerun()

        st.markdown("---")

        # ICP and CTA context
        if intel.get("icp_match"):
            st.markdown("**ICP Match:**   " + intel.get("icp_match",""))
        if intel.get("cta"):
            st.warning("Recommended CTA:   " + intel.get("cta",""))

        st.markdown("---")

        # Save and clear buttons
        sv1, sv2 = st.columns(2)
        with sv1:
            if st.button("Save to Lead Tracker", type="primary"):
                save_lead_to_db(intel, st.session_state["current_messages"])
                st.success(company + " saved to Lead Tracker!")
        with sv2:
            if st.button("Clear and Research New Company"):
                st.session_state["current_intel"]    = None
                st.session_state["current_messages"] = None
                st.session_state["current_company"]  = ""
                st.session_state["prefill"]          = ""
                # Clear all chat histories and message edit widgets
                for key in list(st.session_state.keys()):
                    if key.startswith("chat_") or key.startswith("msg_edit_") or key.startswith("chat_input_"):
                        if isinstance(st.session_state[key], list):
                            st.session_state[key] = []
                        else:
                            del st.session_state[key]
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
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads", len(leads_db))
        m2.metric("Hot (80+)",   len([l for l in leads_db if l.get("score",0) >= 80]))
        m3.metric("Contacted",   len([l for l in leads_db if l.get("status") == "contacted"]))
        m4.metric("Replied",     len([l for l in leads_db if l.get("status") == "replied"]))

        st.markdown("---")

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
            lead_id  = lead.get("id")
            company  = lead.get("company","")
            score    = lead.get("score",0)
            status   = lead.get("status","new")
            has_msgs = bool(lead.get("linkedin_dm") or lead.get("cold_email"))
            msg_tag  = " — Messages saved" if has_msgs else ""

            with st.expander(
                company + "   |   " + str(score) + "/100" +
                "   |   " + status.capitalize() + msg_tag
            ):
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
                    st.write(lead.get("best_contact") or lead.get("best_contact_title") or "—")
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

                breakdown = lead.get("score_breakdown") or []
                if breakdown:
                    with st.expander("Score breakdown", expanded=False):
                        for r in breakdown:
                            st.markdown("— " + str(r))

                # Ideal contacts
                contacts = lead.get("ideal_contacts",[])
                if contacts:
                    st.markdown("---")
                    st.markdown("**Ideal Contacts**")
                    for c in contacts:
                        li_url = c.get("linkedin_url") or linkedin_profile_search_url(c.get("search_query",""))
                        title_disp = c.get("title","") or ""
                        name_disp  = c.get("name","") or "(role only)"
                        line = "— **" + name_disp + "** — " + title_disp
                        if li_url:
                            line += "   [Find on LinkedIn](" + li_url + ")"
                        st.markdown(line)
                        if c.get("why"):
                            st.caption(c.get("why"))

                # Messages
                if has_msgs:
                    st.markdown("---")
                    st.markdown("**Saved Messages**")
                    tm1, tm2, tm3, tm4 = st.tabs([
                        "LinkedIn DM","Cold Email","Follow-up","Connection Note"
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
                else:
                    st.markdown("---")
                    st.info("No messages saved for this lead.")

                # Notes
                st.markdown("---")
                st.markdown("**Notes**")
                note_val = st.text_area(
                    "Add notes",
                    lead.get("notes",""),
                    height=70,
                    key="note_" + str(lead_id),
                    placeholder="e.g. Spoke to John, follow up next Tuesday..."
                )
                if note_val != lead.get("notes",""):
                    update_lead_field(lead_id, "notes", note_val)

                # Status buttons
                st.markdown("---")
                valid_statuses = ["new","contacted","replied","meeting","closed"]
                current_s = status if status in valid_statuses else "new"

                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                for s_label, s_col in zip(valid_statuses, [sc1,sc2,sc3,sc4,sc5]):
                    with s_col:
                        is_active  = current_s == s_label
                        btn_type   = "primary" if is_active else "secondary"
                        if st.button(
                            s_label.capitalize(),
                            key="s_" + s_label + "_" + str(lead_id),
                            type=btn_type
                        ):
                            update_lead_field(lead_id, "status", s_label)
                            st.rerun()

                st.caption("Added: " + (lead.get("created_at") or "—"))
