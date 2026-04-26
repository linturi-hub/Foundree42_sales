import streamlit as st
import google.generativeai as genai
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

# ── SIDEBAR ───────────────────────────────────────
with st.sidebar:
    st.markdown("## Foundree42")
    st.markdown("#### Lead Intelligence Platform")
    st.divider()

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="paste your key here"
    )

    if api_key:
        genai.configure(api_key=api_key)
        st.session_state["api_key"] = api_key
        st.success("API key set")

    st.divider()

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

    st.metric("Total Leads", total)
    st.metric("Hot Leads 80+", hot)
    st.metric("Contacted", contacted)
    st.divider()
    st.caption("Built by Foundree42 Sales Team")

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
            connection_note TEXT
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
            status, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
        datetime.now().strftime("%Y-%m-%d %H:%M")
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
    c.execute(
        "SELECT * FROM leads ORDER BY score DESC"
    )
    leads = c.fetchall()
    conn.close()
    return leads

# ── AI FUNCTIONS ──────────────────────────────────
def get_model():
    if not st.session_state.get("api_key"):
        return None
    return genai.GenerativeModel(
        model_name="models/gemini-2.0-flash"
    )

def research_company(company, contact="", title=""):
    model = get_model()
    if not model:
        return {"error": "No API key"}

    prompt = """
You are a sales intelligence analyst for Foundree42,
a Salesforce consultancy based in the UK.

Research this company and provide detailed intelligence:
Company: """ + company + """
""" + (f"Contact: {contact}, Title: {title}" if contact else "") + """

Based on your knowledge of this company provide:

Return ONLY valid JSON with no markdown:
{
    "company": \"""" + company + """\",
    "overview": "detailed 2-3 sentence summary",
    "industry": "specific industry",
    "size": "employee count estimate",
    "hq": "city and country",
    "ceo": "CEO or founder name",
    "current_crm": "CRM they likely use or Unknown",
    "score": integer 0-100 for Salesforce fit,
    "pain_points": [
        "specific pain point 1",
        "specific pain point 2",
        "specific pain point 3"
    ],
    "recent_triggers": [
        "recent news or signal 1",
        "recent news or signal 2"
    ],
    "best_contact_title": "ideal job title to target",
    "key_people": ["Name - Title"],
    "pitch_angle": "one specific sentence how Foundree42 can help"
}

Return ONLY the JSON object. No explanation. No markdown.
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text
        clean = re.sub(r"```json|```", "", raw).strip()
        return json.loads(clean)
    except Exception as e:
        return {"error": str(e)}

def discover_leads(
    industry, location, revenue,
    company_type, size, signals, count
):
    model = get_model()
    if not model:
        return []

    prompt = """
You are a lead generation specialist for Foundree42,
a Salesforce consultancy based in the UK.

Find """ + str(count) + """ real companies that are
ideal Salesforce consultancy clients matching:

- Industry: """ + industry + """
- Location: """ + location + """
- Revenue: """ + revenue + """
- Size: """ + size + """
- Type: """ + company_type + """
- Buying Signals: """ + signals + """

Think about companies that:
- Are growing their sales teams rapidly
- Have recently raised funding
- Are expanding into new markets
- Are likely using basic or outdated CRM tools
- Have posted jobs mentioning CRM or Sales Operations
- Would benefit from Salesforce implementation

Return ONLY a valid JSON array with no markdown:
[
    {
        "company": "Real company name",
        "industry": "specific industry",
        "size": "employee estimate",
        "location": "city, country",
        "revenue": "revenue estimate",
        "why_fit": "specific reason they need Salesforce",
        "trigger": "specific buying signal",
        "best_contact": "ideal job title",
        "score": integer 0-100
    }
]

Return ONLY the JSON array. No explanation. No markdown.
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text
        clean = re.sub(r"```json|```", "", raw).strip()
        return json.loads(clean)
    except Exception as e:
        st.error("Discovery error: " + str(e))
        return []

def generate_messages(lead_data, feedback=""):
    model = get_model()
    if not model:
        return {"error": "No API key"}

    feedback_text = ""
    if feedback:
        feedback_text = "\nApply this feedback: " + feedback

    prompt = """
You are a senior sales writer at Foundree42,
a Salesforce consultancy firm based in the UK.

Write personalised outreach messages for:
Company: """ + lead_data.get("company","") + """
Industry: """ + lead_data.get("industry","") + """
Overview: """ + lead_data.get("overview","") + """
Pain Points: """ + str(lead_data.get("pain_points",[])) + """
Recent Triggers: """ + str(lead_data.get("recent_triggers",[])) + """
Pitch Angle: """ + lead_data.get("pitch_angle","") + """
""" + feedback_text + """

Rules:
- Reference SPECIFIC facts about this company
- Never say 'I hope this finds you well'
- Never say 'I wanted to reach out'
- Sound human, not templated
- Sign off as the Foundree42 team
- Focus on THEIR problem not our features

Return ONLY valid JSON with no markdown:
{
    "subject_line": "compelling subject under 10 words",
    "linkedin_dm": "LinkedIn DM under 180 words ending with soft CTA",
    "cold_email": "cold email 150-200 words ending with one easy question",
    "followup": "follow-up under 120 words with new angle",
    "connection_note": "LinkedIn connection request under 70 words"
}

Return ONLY the JSON. No explanation. No markdown.
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text
        clean = re.sub(r"```json|```", "", raw).strip()
        return json.loads(clean)
    except Exception as e:
        return {"error": str(e)}

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
        "Describe your ideal client and AI will find "
        "matching companies with buying signals."
    )

    c1, c2 = st.columns(2)
    with c1:
        icp_type = st.selectbox(
            "Company Type", ["B2B", "B2C", "Both"]
        )
        icp_industry = st.text_input(
            "Industry *",
            placeholder="e.g. Manufacturing, SaaS, Retail"
        )
        icp_location = st.text_input(
            "Location *",
            placeholder="e.g. Arizona, United States"
        )
    with c2:
        icp_size = st.selectbox("Company Size", [
            "50-200 employees",
            "200-500 employees",
            "500-2000 employees",
            "2000-5000 employees",
            "Any size"
        ])
        icp_revenue = st.selectbox("Revenue", [
            "Under $10M", "Under $100M",
            "Under $500M", "Under $1 billion",
            "Over $1 billion", "Any revenue"
        ])
        icp_count = st.slider(
            "Number of leads to find", 3, 10, 5
        )

    icp_signals = st.text_area(
        "Buying Signals to Look For",
        placeholder=(
            "e.g. hiring sales roles, recent funding, "
            "scaling operations, new CRM job postings..."
        )
    )

    if st.button("Discover Leads", type="primary"):
        if not st.session_state.get("api_key"):
            st.error("Add your Gemini API key in the sidebar.")
        elif not icp_industry or not icp_location:
            st.error("Please fill in Industry and Location.")
        else:
            with st.spinner(
                "Searching for matching companies..."
            ):
                found = discover_leads(
                    industry=icp_industry,
                    location=icp_location,
                    revenue=icp_revenue,
                    company_type=icp_type,
                    size=icp_size,
                    signals=icp_signals or "hiring, funding, scaling",
                    count=icp_count
                )

            if found:
                st.success(
                    "Found " + str(len(found)) + " leads!"
                )
                st.session_state["discovered"] = found
            else:
                st.warning(
                    "No leads found. Try broader criteria."
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
                "🟢 HOT" if score >= 80
                else "🟡 WARM" if score >= 60
                else "🔴 COLD"
            )
            with st.expander(
                lead.get("company","") + " — " +
                str(score) + "/100 " + label,
                expanded=(i == 0)
            ):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(
                        "**Why they fit:** " +
                        lead.get("why_fit","")
                    )
                    st.markdown(
                        "**Buying signal:** " +
                        lead.get("trigger","")
                    )
                    st.markdown(
                        "**Best contact:** " +
                        lead.get("best_contact","")
                    )
                    st.caption(
                        lead.get("location","") +
                        " · " + lead.get("size","")
                    )
                with col_b:
                    st.metric(
                        "Fit Score",
                        str(score) + "/100"
                    )

                if st.button(
                    "Research this company →",
                    key="disc_" + str(i)
                ):
                    st.session_state["prefill"] = (
                        lead.get("company","")
                    )
                    st.info(
                        "Go to Company Research tab "
                        "for " + lead.get("company","")
                    )

# ════════════════════════════════════════════════
# TAB 2 — COMPANY RESEARCH
# ════════════════════════════════════════════════
with tab2:
    st.markdown("## Company Research Pipeline")
    st.markdown(
        "Full AI pipeline: "
        "Research → Pitch Angle → Outreach Messages"
    )

    col1, col2 = st.columns(2)
    with col1:
        company_input = st.text_input(
            "Company Name *",
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
            placeholder="e.g. VP of Sales"
        )
        feedback_input = st.text_area(
            "Boss Feedback to Apply",
            placeholder=(
                "e.g. be more direct, "
                "lead with ROI, shorter messages..."
            ),
            height=100
        )

    col_x, col_y = st.columns(2)
    with col_x:
        run_pipeline = st.button(
            "Run Full Pipeline", type="primary"
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

            if "error" not in intel:
                score = intel.get("score", 0)
                m1, m2, m3 = st.columns(3)
                m1.metric(
                    "Industry",
                    intel.get("industry","—")
                )
                m2.metric(
                    "Size",
                    intel.get("size","—")
                )
                m3.metric(
                    "Fit Score",
                    str(score) + "/100"
                )

                st.markdown(
                    "**Overview:** " +
                    intel.get("overview","")
                )

                col_p, col_t = st.columns(2)
                with col_p:
                    if intel.get("pain_points"):
                        st.markdown("**🔴 Pain Points:**")
                        for p in intel["pain_points"]:
                            st.markdown("- " + p)
                with col_t:
                    if intel.get("recent_triggers"):
                        st.markdown("**🟢 Recent Triggers:**")
                        for t in intel["recent_triggers"]:
                            st.markdown("- " + t)

                st.info(
                    "🎯 Best Contact: " +
                    intel.get("best_contact_title","")
                )
                st.success(
                    "💡 Pitch Angle: " +
                    intel.get("pitch_angle","")
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

                    if "error" not in messages:
                        mt1, mt2, mt3, mt4 = st.tabs([
                            "LinkedIn DM",
                            "Cold Email",
                            "Follow-up",
                            "Connection Note"
                        ])
                        with mt1:
                            st.text_area(
                                "LinkedIn DM — copy and paste",
                                messages.get("linkedin_dm",""),
                                height=200,
                                key="li_msg"
                            )
                        with mt2:
                            st.markdown(
                                "**Subject Line:** `" +
                                messages.get("subject_line","") +
                                "`"
                            )
                            st.text_area(
                                "Email Body",
                                messages.get("cold_email",""),
                                height=200,
                                key="em_msg"
                            )
                        with mt3:
                            st.text_area(
                                "Follow-up Message",
                                messages.get("followup",""),
                                height=150,
                                key="fu_msg"
                            )
                        with mt4:
                            st.text_area(
                                "Connection Note",
                                messages.get("connection_note",""),
                                height=100,
                                key="cn_msg"
                            )

                        st.markdown("---")
                        if st.button(
                            "💾 Save Lead + Messages",
                            type="primary"
                        ):
                            save_lead(intel)
                            save_messages(
                                company_input, messages
                            )
                            st.success(
                                "✅ " + company_input +
                                " saved to database!"
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
        "One-click workflow to contact each lead."
    )

    all_leads = get_all_leads()

    if not all_leads:
        st.info(
            "No leads yet. Run Lead Discovery or "
            "Company Research first then save leads."
        )
    else:
        for lead in all_leads:
            comp      = lead[1]
            target    = lead[11] or "VP of Sales"
            score     = lead[7] or 0
            status    = lead[13] or "new"
            conn_note = lead[19] if len(lead) > 19 else ""
            li_dm     = lead[15] if len(lead) > 15 else ""

            status_icon = (
                "🟢" if status == "replied"
                else "🟡" if status == "contacted"
                else "⚪"
            )

            with st.expander(
                status_icon + " " + comp +
                " — " + str(score) + "/100 — " + status
            ):
                search_url = (
                    "https://www.linkedin.com/"
                    "search/results/people/?keywords=" +
                    (target + " " + comp).replace(
                        " ", "%20"
                    )
                )

                st.markdown(
                    "**Target Role:** " + target
                )
                st.markdown(
                    "**[🔗 Find on LinkedIn](" +
                    search_url + ")**"
                )
                st.caption(
                    "Click link → find the person → "
                    "send connection note below"
                )

                if conn_note:
                    st.markdown("**Connection Note:**")
                    st.text_area(
                        "Copy for connection request",
                        conn_note,
                        height=80,
                        key="cn_li_" + str(lead[0])
                    )
                if li_dm:
                    st.markdown(
                        "**LinkedIn DM** "
                        "(send after they accept):"
                    )
                    st.text_area(
                        "Copy this DM",
                        li_dm,
                        height=150,
                        key="dm_li_" + str(lead[0])
                    )
                if not conn_note and not li_dm:
                    st.info(
                        "Run Full Pipeline in Company "
                        "Research tab to generate messages."
                    )

                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    if st.button(
                        "✅ Mark Contacted",
                        key="c_" + str(lead[0])
                    ):
                        update_status(comp, "contacted")
                        st.success("Updated!")
                        st.rerun()
                with col_s2:
                    if st.button(
                        "💬 Mark Replied",
                        key="r_" + str(lead[0])
                    ):
                        update_status(comp, "replied")
                        st.success("Updated!")
                        st.rerun()
                with col_s3:
                    if st.button(
                        "🏁 Mark Closed",
                        key="cl_" + str(lead[0])
                    ):
                        update_status(comp, "closed")
                        st.success("Updated!")
                        st.rerun()

# ════════════════════════════════════════════════
# TAB 4 — LEAD DATABASE
# ════════════════════════════════════════════════
with tab4:
    st.markdown("## Lead Database")

    all_leads_db = get_all_leads()

    if not all_leads_db:
        st.info(
            "No leads saved yet. Research companies "
            "and save them to see them here."
        )
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads", len(all_leads_db))
        m2.metric(
            "Hot 80+",
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

        status_filter = st.selectbox(
            "Filter by status",
            [
                "All", "new", "ready_to_contact",
                "contacted", "replied", "closed"
            ]
        )

        min_score = st.slider(
            "Minimum score", 0, 100, 0
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

        for lead in filtered:
            score = lead[7] or 0
            icon = (
                "🟢" if score >= 80
                else "🟡" if score >= 60
                else "🔴"
            )
            with st.expander(
                icon + " " + lead[1] +
                " | " + str(score) + "/100 | " +
                (lead[13] or "new")
            ):
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown(
                        "**Industry:** " +
                        (lead[2] or "—")
                    )
                    st.markdown(
                        "**Size:** " + (lead[3] or "—")
                    )
                    st.markdown(
                        "**HQ:** " + (lead[4] or "—")
                    )
                    st.markdown(
                        "**Best Contact:** " +
                        (lead[11] or "—")
                    )
                with d2:
                    st.markdown(
                        "**Score:** " +
                        str(score) + "/100"
                    )
                    st.markdown(
                        "**Added:** " +
                        (lead[14] or "—")
                    )
                    st.markdown(
                        "**Pitch:** " +
                        (lead[12] or "—")
                    )

                if lead[8]:
                    st.markdown(
                        "**Overview:** " + lead[8]
                    )

                new_status = st.selectbox(
                    "Update status",
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
                    st.success("Status updated!")
                    st.rerun()
