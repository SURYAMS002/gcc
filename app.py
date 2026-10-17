import os
import sys
import json
import streamlit as st
import pandas as pd

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(__file__))

from config import get_gemini_api_key, APP_NAME, APP_TAGLINE
from rag.data_loader import (
    get_gcc_records, 
    get_city_intelligence, 
    get_service_providers, 
    get_sources_registry, 
    get_ecosystem_kpis,
    get_gcc_by_id
)
from rag.knowledge_indexer import build_or_load_gcc_index
from agent import GCCIntelAgent

# Streamlit Page Config
st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise B2B SaaS Styling
st.markdown("""
<style>
    /* Global Base */
    .stApp {
        background-color: #0B0F17;
        color: #E2E8F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Hero Header */
    .hero-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    .hero-title {
        color: #38BDF8;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-top: 6px;
        margin-bottom: 0px;
        line-height: 1.5;
    }
    .hero-badge {
        background-color: rgba(56, 189, 248, 0.12);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }

    /* KPI Metrics Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background-color: #131B2E;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 16px 20px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .kpi-card:hover {
        border-color: #38BDF8;
        transform: translateY(-2px);
    }
    .kpi-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0;
    }
    .kpi-label {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 4px;
    }
    .kpi-source {
        color: #64748B;
        font-size: 0.75rem;
        margin-top: 6px;
    }

    /* Verification & Status Badges */
    .badge-verified {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-announcement {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-estimate {
        background-color: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    /* Record & Content Cards */
    .intel-card {
        background-color: #131B2E;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }
    .intel-card:hover {
        border-color: #334155;
    }
    .card-title {
        color: #F8FAFC;
        font-size: 1.15rem;
        font-weight: 600;
        margin: 0 0 6px 0;
    }
    .card-subtitle {
        color: #94A3B8;
        font-size: 0.88rem;
        margin-bottom: 10px;
    }
    .chip {
        background-color: #1E293B;
        color: #93C5FD;
        border: 1px solid #334155;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        margin-right: 6px;
        margin-bottom: 4px;
        display: inline-block;
    }

    /* Source Links */
    .source-link {
        color: #38BDF8;
        text-decoration: none;
        font-size: 0.8rem;
    }
    .source-link:hover {
        text-decoration: underline;
    }

    /* Activity Feed in Agent */
    .agent-step {
        background-color: #1E293B;
        border-left: 3px solid #38BDF8;
        padding: 8px 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.82rem;
        margin-bottom: 6px;
        color: #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "agent_chat_history" not in st.session_state:
    st.session_state["agent_chat_history"] = []
if "selected_gcc_id" not in st.session_state:
    st.session_state["selected_gcc_id"] = None
if "vector_store" not in st.session_state:
    # Auto-load pre-built GCC vector index
    try:
        st.session_state["vector_store"] = build_or_load_gcc_index()
    except Exception:
        st.session_state["vector_store"] = None

# Sidebar - Brand & Navigation
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0;">
        <h2 style="color: #38BDF8; margin: 0; font-size: 1.6rem; font-weight: 700;">🏢 GCC Intel</h2>
        <p style="color: #94A3B8; margin: 2px 0 0 0; font-size: 0.85rem;">India's GCC Market Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    nav_choice = st.radio(
        "Navigation",
        [
            "🌐 Overview",
            "🏢 GCC Explorer",
            "🏙️ City Intelligence",
            "🧠 Ask GCC Intel",
            "🤝 Service Providers",
            "📚 Sources & Methodology"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    
    # Credential Check (Quiet Enterprise Pattern)
    active_key = get_gemini_api_key()
    if not active_key:
        st.markdown("**🔑 API Key Required**")
        user_key = st.text_input("Enter Gemini API Key", type="password", key="user_gemini_api_key")
        if user_key:
            st.success("API key stored for session.")
            active_key = user_key
        st.caption("Configured in .env or Streamlit Secrets for auto-login.")
    else:
        st.caption("🟢 **Intelligence Engine:** Gemini 3.8 Flash Active")

    st.markdown("---")
    kpis = get_ecosystem_kpis()
    st.markdown(f"""
    <div style="font-size: 0.78rem; color: #64748B;">
        <b>Curated Registry:</b> {kpis['curated_gcc_count']} GCCs<br>
        <b>Monitored Metros:</b> 5 Cities<br>
        <b>Tracked Workforce:</b> {kpis['total_tracked_headcount']:,} roles<br>
        <b>Data Verified:</b> Oct 2024
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. OVERVIEW VIEW
# -------------------------------------------------------------
if nav_choice == "🌐 Overview":
    st.markdown("""
    <div class="hero-card">
        <span class="hero-badge">Enterprise Market Intelligence</span>
        <h1 class="hero-title">🏢 GCC Intel</h1>
        <p class="hero-subtitle">
            The evidence-backed market intelligence platform for global enterprises evaluating, establishing, 
            and expanding Global Capability Centres (GCCs) across India's premier tech and business hubs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Macro Indicators with Verified Citations
    kpis = get_ecosystem_kpis()
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-val">{kpis['macro_india_gccs']}</div>
            <div class="kpi-label">Total GCCs in India</div>
            <div class="kpi-source">Source: {kpis['macro_source_label']}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val">{kpis['macro_talent_pool']}</div>
            <div class="kpi-label">Specialized Tech Workforce</div>
            <div class="kpi-source">Source: NASSCOM GCC 4.0 Report</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val">{kpis['macro_economic_value']}</div>
            <div class="kpi-label">Annual Economic Value</div>
            <div class="kpi-source">Projected $100B+ by 2030</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val">{kpis['curated_gcc_count']}</div>
            <div class="kpi-label">Audited Marquee GCCs</div>
            <div class="kpi-source">100% Sourced & Verified Records</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Jump to Research Question
    st.subheader("🔍 Quick Market Intelligence Research")
    quick_query = st.text_input(
        "Ask a strategic question about India's GCC landscape:",
        placeholder="e.g. Which cities should a US fintech company consider for a 300-person GCC?",
        key="quick_query_input"
    )
    col_ask, col_compare = st.columns([1, 4])
    with col_ask:
        if st.button("Research with AI ➔", type="primary") and quick_query:
            st.session_state["active_research_query"] = quick_query
            st.info("Tip: Click **🧠 Ask GCC Intel** in the sidebar to view the full verified research report!")

    st.markdown("---")

    # Recent GCC Investment & Expansion Highlights
    st.subheader("📰 Recent Marquee GCC Expansions & Government Milestones")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="intel-card">
            <div class="badge-verified">Verified Corporate Fact</div>
            <div class="card-title" style="margin-top: 6px;">Boeing Inaugurates 43-Acre Technology Campus</div>
            <div class="card-subtitle">Devanahalli Aerospace Park, Bengaluru • INR 1,600 Cr ($200M) Investment</div>
            <p style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 8px;">
                Boeing's largest engineering research facility outside the US, employing 6,000+ engineers developing flight control avionics, materials engineering, and aerodynamics software.
            </p>
            <a href="https://www.boeing.co.in/" target="_blank" class="source-link">View Boeing Press Release ↗</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="intel-card">
            <div class="badge-verified">Verified Corporate Fact</div>
            <div class="card-title" style="margin-top: 6px;">AstraZeneca Expands Chennai Global Technology Hub</div>
            <div class="card-subtitle">Ramanujan IT City, Taramani, Chennai • INR 250 Cr Expansion</div>
            <p style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 8px;">
                Adding 1,300+ clinical data scientists, bioinformaticians, and healthcare enterprise cloud engineers supporting global drug development and FDA filings.
            </p>
            <a href="https://www.astrazeneca.com/country-sites/india.html" target="_blank" class="source-link">View AstraZeneca Disclosure ↗</a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="intel-card">
            <div class="badge-announcement">Government Statutory Policy</div>
            <div class="card-title" style="margin-top: 6px;">Karnataka Launches Dedicated GCC Policy 2024–2029</div>
            <div class="card-subtitle">Dept of IT, Bt and S&T, Govt of Karnataka</div>
            <p style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 8px;">
                India's first dedicated state policy targeting 500 new GCCs by 2029, offering AI Co-Innovation matching grants (up to INR 1 Cr), Beyond-Bengaluru rental subsidies, and female hiring bonuses.
            </p>
            <a href="https://itbtst.karnataka.gov.in/policies/gcc-policy-2024" target="_blank" class="source-link">View Policy Notification ↗</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="intel-card">
            <div class="badge-verified">Verified Corporate Fact</div>
            <div class="card-title" style="margin-top: 6px;">Ford Submits LOI to Repurpose Chennai Complex</div>
            <div class="card-subtitle">Maraimalai Nagar, Chennai • Export Tech & Manufacturing Hub</div>
            <p style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 8px;">
                Expanding Ford Business Solutions' existing 12,000-person Chennai engineering footprint to engineer EV architectures and global software systems.
            </p>
            <a href="https://media.ford.com/" target="_blank" class="source-link">View Ford Announcement ↗</a>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. GCC EXPLORER VIEW
# -------------------------------------------------------------
elif nav_choice == "🏢 GCC Explorer":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="color: #38BDF8; margin: 0; font-size: 1.8rem; font-weight: 700;">🏢 GCC Explorer</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Search and filter verified Global Capability Centres operating across India's top tech hubs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Search & Filter Controls
    col_s1, col_s2, col_s3, col_s4 = st.columns([3, 2, 2, 2])
    with col_s1:
        search_kw = st.text_input("Search companies, functions, or keywords", placeholder="e.g. Goldman Sachs, Cyber, AI, Clinical...")
    with col_s2:
        city_filter = st.selectbox("City Filter", ["All Cities", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Gurugram"])
    with col_s3:
        industry_filter = st.selectbox("Industry Filter", [
            "All Industries", "BFSI", "Retail & CPG", "Tech & Software", 
            "Healthcare & Life Sciences", "Automotive & Mobility", "Aerospace & Defence", "Semiconductor & Hardware", "Energy & Resources"
        ])
    with col_s4:
        status_filter = st.selectbox("Data Confidence", ["All Statuses", "Verified Fact", "Company Announcement", "Industry Estimate"])

    col_sort1, col_sort2 = st.columns([2, 2])
    with col_sort1:
        sort_by = st.selectbox("Sort By", ["company_name", "headcount", "establishment_year", "city"], index=0)
    with col_sort2:
        sort_order = st.radio("Order", ["Ascending", "Descending"], horizontal=True, index=0)

    # Retrieve filtered records
    records = get_gcc_records(
        search_query=search_kw,
        city=city_filter,
        industry=industry_filter,
        verification_status=status_filter,
        sort_by=sort_by,
        sort_ascending=(sort_order == "Ascending")
    )

    st.markdown(f"**Showing {len(records)} audited GCC records**")

    # Render Records Table or Detailed Cards
    view_mode = st.radio("View Format", ["Structured Data Table", "Detailed Profiles"], horizontal=True)

    if view_mode == "Structured Data Table":
        # Format table data
        table_rows = []
        for r in records:
            badge = "🟢 Verified" if r["verification_status"] == "Verified Fact" else ("🔵 Announcement" if r["verification_status"] == "Company Announcement" else "🟡 Estimate")
            table_rows.append({
                "Company Name": r["company_name"],
                "Parent / HQ": f"{r['parent_company']} ({r['global_headquarters']})",
                "City": r["city"],
                "Industry": r["industry"],
                "Est. Year": r.get("establishment_year", "N/A"),
                "Tracked Size": f"{r['headcount']:,} ({r['headcount_type']})",
                "Confidence": badge,
                "Source Link": r["source_url"]
            })
        
        df = pd.DataFrame(table_rows)
        st.dataframe(
            df,
            column_config={
                "Source Link": st.column_config.LinkColumn("Source URL", display_text="View Source ↗")
            },
            use_container_width=True,
            hide_index=True
        )

    else:
        # Detailed Card Grid
        for r in records:
            status_badge_html = (
                f'<span class="badge-verified">✓ {r["verification_status"]}</span>' if r["verification_status"] == "Verified Fact"
                else (f'<span class="badge-announcement">ℹ {r["verification_status"]}</span>' if r["verification_status"] == "Company Announcement"
                else f'<span class="badge-estimate">⚠ {r["verification_status"]}</span>')
            )

            functions_chips = "".join([f'<span class="chip">{f}</span>' for f in r.get("business_functions", [])])
            headcount_text = f"{r['headcount']:,} employees ({r['headcount_type']})"

            with st.container():
                st.markdown(f"""
                <div class="intel-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span class="card-title">{r['company_name']}</span>
                            <span style="color: #64748B; font-size: 0.85rem; margin-left: 8px;">Est. {r.get('establishment_year', 'N/A')}</span>
                            <div class="card-subtitle">{r['parent_company']} • Global HQ: {r['global_headquarters']}</div>
                        </div>
                        <div>{status_badge_html}</div>
                    </div>
                    <div style="margin: 6px 0 10px 0;">
                        <b>Location:</b> {r['city']}, {r['state']} &nbsp;|&nbsp; 
                        <b>Industry:</b> {r['industry']} &nbsp;|&nbsp; 
                        <b>Workforce:</b> {headcount_text}
                    </div>
                    <div style="margin-bottom: 10px;">
                        <b>Core Functions:</b> {functions_chips}
                    </div>
                    <div style="background-color: #0B0F17; border-left: 3px solid #38BDF8; padding: 8px 12px; border-radius: 4px; font-size: 0.85rem; margin-bottom: 10px;">
                        <b>Recent Expansion / Activity:</b> {r['recent_announcement']}
                    </div>
                    <div style="font-size: 0.8rem; color: #94A3B8;">
                        <b>Source:</b> <a href="{r['source_url']}" target="_blank" class="source-link">{r['source_title']}</a> 
                        &nbsp;•&nbsp; Source Date: {r['source_date']} 
                        &nbsp;•&nbsp; Verified: {r['last_verified_date']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. CITY INTELLIGENCE & COMPARISON VIEW
# -------------------------------------------------------------
elif nav_choice == "🏙️ City Intelligence":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="color: #38BDF8; margin: 0; font-size: 1.8rem; font-weight: 700;">🏙️ City Intelligence & Comparison</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Compare India's top 5 GCC hubs across talent depth, office leasing benchmarks, state policies, and infrastructure.
        </p>
    </div>
    """, unsafe_allow_html=True)

    all_cities = get_city_intelligence()
    city_options = [c["name"] for c in all_cities]

    selected_cities = st.multiselect(
        "Select up to 3 Cities to Compare Side-by-Side:",
        options=city_options,
        default=["Bengaluru", "Hyderabad", "Chennai"],
        max_selections=3
    )

    if not selected_cities:
        st.warning("Please select at least 1 city to view intelligence benchmarks.")
    else:
        filtered_cities = [c for c in all_cities if c["name"] in selected_cities]

        # Multi-Column City Cards
        cols = st.columns(len(filtered_cities))
        for idx, c in enumerate(filtered_cities):
            with cols[idx]:
                st.markdown(f"""
                <div class="intel-card" style="min-height: 260px;">
                    <div class="badge-announcement">{c['tier']}</div>
                    <h3 style="color: #F8FAFC; margin: 8px 0 2px 0;">{c['name']}</h3>
                    <div style="color: #38BDF8; font-size: 0.85rem; margin-bottom: 8px;">{c['state']}</div>
                    <p style="color: #94A3B8; font-size: 0.82rem; font-style: italic; margin-bottom: 12px;">"{c['tagline']}"</p>
                    <div style="font-size: 0.85rem; line-height: 1.6;">
                        <b>Market Share:</b> {c['market_share_pct']}% of India GCCs<br>
                        <b>Est. GCC Count:</b> {c['estimated_gcc_count']}<br>
                        <b>Est. Workforce:</b> {c['estimated_workforce']}<br>
                        <b>Grade-A Rents:</b> INR {c['real_estate']['grade_a_avg_rent_inr_sqft_mo']}/sq.ft/mo
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### 📊 Side-by-Side Metric Comparison")

        # 1. Real Estate Benchmarks
        with st.expander("🏢 Commercial Real Estate & Micro-Markets (CBRE Q2 2024)", expanded=True):
            re_rows = []
            for c in filtered_cities:
                re = c["real_estate"]
                micros_str = " | ".join([f"{m['name']}: {m['rent_range']} (Vac: {m['vacancy_pct']})" for m in re["prime_micromarkets"]])
                re_rows.append({
                    "City": c["name"],
                    "Grade-A Avg Rental": f"INR {re['grade_a_avg_rent_inr_sqft_mo']} /sq.ft/month",
                    "Key Micro-Markets & Vacancy": micros_str,
                    "Data Confidence": re["data_type"],
                    "Source": re["source_label"]
                })
            st.dataframe(pd.DataFrame(re_rows), use_container_width=True, hide_index=True)

        # 2. Talent & Compensation Benchmarks
        with st.expander("💼 Talent Pool & Salary Benchmarks (Michael Page 2024)", expanded=True):
            sal_rows = []
            for c in filtered_cities:
                tb = c["talent_benchmarks"]
                sal_rows.append({
                    "City": c["name"],
                    "Software Eng (3-5y)": tb["median_ctc_inr_lpa"]["software_engineer_3_5_yrs"],
                    "Data Science / AI (3-5y)": tb["median_ctc_inr_lpa"]["data_scientist_ai_3_5_yrs"],
                    "Finance/Risk (3-5y)": tb["median_ctc_inr_lpa"]["finance_risk_analyst_3_5_yrs"],
                    "Eng Director (10-15y)": tb["median_ctc_inr_lpa"]["eng_director_manager_10_15_yrs"],
                    "Est. Attrition": tb["attrition_rate_est"]
                })
            st.dataframe(pd.DataFrame(sal_rows), use_container_width=True, hide_index=True)

        # 3. State Policy & Statutory Incentives
        with st.expander("📜 State GCC Policies & Statutory Incentives", expanded=True):
            for c in filtered_cities:
                pol = c["state_policy"]
                st.markdown(f"#### 🏛️ {c['name']} — {pol['policy_name']}")
                st.caption(f"Authority: {pol['department']} • Confidence: {pol['data_type']}")
                for inc in pol["key_incentives"]:
                    st.markdown(f"• {inc}")
                st.markdown("---")

        # 4. Strategic Pros & Cons
        with st.expander("⚖️ Strategic Trade-offs & Recommendation", expanded=True):
            for c in filtered_cities:
                to = c["strategic_tradeoffs"]
                st.markdown(f"#### {c['name']}")
                col_p, col_c = st.columns(2)
                with col_p:
                    st.markdown("**Core Advantages (Pros):**")
                    for p in to["pros"]:
                        st.markdown(f"✓ {p}")
                with col_c:
                    st.markdown("**Key Trade-offs (Cons):**")
                    for con in to["cons"]:
                        st.markdown(f"⚠ {con}")
                st.info(f"**Recommended Entrant Profile:** {to['recommended_for']}")

        # AI-Generated City Comparison Synthesis
        st.markdown("### 🤖 Evidence-Backed Executive Comparison Synthesis")
        if st.button("Generate Comparative Trade-off Advisory with AI", type="primary"):
            with st.spinner("Analyzing city benchmarks and synthesizing strategic entry trade-offs..."):
                agent = GCCIntelAgent()
                prompt_q = f"Compare {', '.join(selected_cities)} for a prospective global enterprise setting up a GCC in India. Detail the talent cost, real estate, and state incentive trade-offs."
                ai_res = agent.run(prompt_q)
                st.markdown(ai_res["final_answer"])

# -------------------------------------------------------------
# 4. ASK GCC INTEL VIEW (AI RESEARCH ASSISTANT)
# -------------------------------------------------------------
elif nav_choice == "🧠 Ask GCC Intel":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="color: #38BDF8; margin: 0; font-size: 1.8rem; font-weight: 700;">🧠 Ask GCC Intel</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Conversational market research assistant powered by LangGraph, FAISS semantic retrieval, 
            and automated source verification.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Preset Suggested Questions
    st.markdown("**Suggested Strategic Inquiries (Click to run):**")
    suggested_cols = st.columns(3)
    preset_q = None

    with suggested_cols[0]:
        if st.button("Fintech GCC for 300 People ➔"):
            preset_q = "Which cities should a US fintech company consider for a 300-person GCC?"
    with suggested_cols[1]:
        if st.button("GCCs in Chennai by Function ➔"):
            preset_q = "Find GCCs in Chennai that have finance, engineering, or analytics functions."
    with suggested_cols[2]:
        if st.button("Tamil Nadu State Incentives ➔"):
            preset_q = "What state incentives might be relevant when establishing a GCC in Tamil Nadu?"

    suggested_cols_2 = st.columns(2)
    with suggested_cols_2[0]:
        if st.button("Recent Marquee Expansions ➔"):
            preset_q = "Which companies have recently announced GCC expansions in India?"
    with suggested_cols_2[1]:
        if st.button("Compare Bengaluru vs Chennai ➔"):
            preset_q = "Compare Bengaluru and Chennai for an analytics-focused GCC."

    # Check if coming from Overview quick search
    initial_val = preset_q or st.session_state.get("active_research_query", "")

    user_query = st.text_input(
        "Enter your GCC research inquiry:",
        value=initial_val,
        placeholder="e.g. Compare office leasing costs and state incentives between Hyderabad and Bengaluru..."
    )

    col_btn, col_blank = st.columns([1, 4])
    with col_btn:
        run_query = st.button("Run Research Agent", type="primary")

    if (run_query or preset_q) and user_query:
        active_key = get_gemini_api_key()
        if not active_key:
            st.error("⚠️ GEMINI_API_KEY is missing. Please enter your Gemini API Key in the left sidebar.")
        else:
            with st.expander("⚙️ Agentic Execution Graph & Retrieval Telemetry", expanded=True):
                activity_container = st.container()
                with st.spinner("GCC Intel Agent executing multi-step retrieval and claim verification..."):
                    agent = GCCIntelAgent()
                    result = agent.run(user_query)

                with activity_container:
                    for step in result["status_log"]:
                        st.markdown(f'<div class="agent-step">⚙️ {step}</div>', unsafe_allow_html=True)

            # Verification Status Callout
            if result.get("abstained"):
                st.warning("⚠️ **Abstention Policy Active:** Insufficient verified evidence found in the dataset to answer reliably without hallucinating.")
            elif result.get("is_supported"):
                st.success("✓ **Fully Verified:** All substantive claims grounded in audited GCC Intel source dossiers.")

            st.markdown("### 📋 Executive Market Intelligence Briefing")
            st.markdown(result["final_answer"])

# -------------------------------------------------------------
# 5. SERVICE PROVIDERS DIRECTORY VIEW
# -------------------------------------------------------------
elif nav_choice == "🤝 Service Providers":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="color: #38BDF8; margin: 0; font-size: 1.8rem; font-weight: 700;">🤝 Service Provider Directory</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Curated ecosystem partners supporting GCC strategy, commercial real estate, legal structuring, recruitment, and Employer of Record (EOR) incubation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_cat, col_sp_search = st.columns([2, 3])
    with col_cat:
        category_choice = st.selectbox("Category Filter", [
            "All Categories",
            "Strategy & Market-Entry Consulting",
            "Commercial Real Estate",
            "Legal & Regulatory Services",
            "Recruitment & Executive Search",
            "Payroll & Employer of Record (EOR)"
        ])
    with col_sp_search:
        sp_kw = st.text_input("Search providers, services, or locations", placeholder="e.g. Incubation, EOR, Lease, SAM, CBRE...")

    providers = get_service_providers(category=category_choice, search_query=sp_kw)
    st.markdown(f"**Showing {len(providers)} vetted enablement partners**")

    for sp in providers:
        services_chips = "".join([f'<span class="chip">{s}</span>' for s in sp.get("services_offered", [])])
        locations_str = ", ".join(sp.get("locations_served", []))

        st.markdown(f"""
        <div class="intel-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span class="card-title">{sp['name']}</span>
                    <div class="card-subtitle">{sp['category']} • {sp['sub_category']}</div>
                </div>
                <div class="badge-verified">{sp['verification_status']}</div>
            </div>
            <div style="margin: 6px 0 10px 0; font-size: 0.85rem;">
                <b>Global HQ:</b> {sp['headquarters']} &nbsp;|&nbsp; 
                <b>Locations Served:</b> {locations_str}
            </div>
            <div style="margin-bottom: 10px;">
                <b>Core Capabilities:</b> {services_chips}
            </div>
            <div style="background-color: #0B0F17; border-left: 3px solid #10B981; padding: 8px 12px; border-radius: 4px; font-size: 0.85rem; margin-bottom: 10px;">
                <b>Documented GCC Track Record:</b> {sp['documented_track_record']}
            </div>
            <div>
                <a href="{sp['source_url']}" target="_blank" class="source-link">Visit Official Portal ↗</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 6. SOURCES & METHODOLOGY VIEW
# -------------------------------------------------------------
elif nav_choice == "📚 Sources & Methodology":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="color: #38BDF8; margin: 0; font-size: 1.8rem; font-weight: 700;">📚 Sources, Methodology & Data Quality</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Transparent provenance, government policy registries, and conflict resolution methodology.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 🛡️ Data Quality & Provenance Principles
    GCC Intel enforces strict enterprise data hygiene rules:
    1. **Zero Hallucination Policy:** If verified evidence is absent from our repository, the AI research assistant explicitly states what is missing rather than inventing statistics.
    2. **Multi-Source Triangulation:** We distinguish **Verified Facts** (official corporate releases, SEC/regulatory filings, state gazettes) from **Market Estimates** (salary surveys, broker forecasts).
    3. **Micro-Market Reality:** We do not publish single misleading city-wide real estate averages without listing micro-market ranges (e.g. Outer Ring Road vs Whitefield in Bengaluru).
    """)

    st.markdown("### 📋 Primary Sources Registry")
    sources = get_sources_registry()
    sources_data = []
    for s in sources:
        sources_data.append({
            "Source ID": s["id"],
            "Title / Publication": s["title"],
            "Publisher": s["publisher"],
            "Category": s["category"],
            "Publication Date": s["publication_date"],
            "Confidence Level": s["confidence_level"],
            "Canonical Link": s["url"]
        })

    df_sources = pd.DataFrame(sources_data)
    st.dataframe(
        df_sources,
        column_config={
            "Canonical Link": st.column_config.LinkColumn("Canonical URL", display_text="Open Source ↗")
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.markdown("""
    ### ⚖️ Handling Disagreeing & Conflicting Data
    - **Real Estate Rental Variances:** Commercial lease rates in Indian metros vary dramatically by sub-market and building grade. For example, DLF Cyber City in Gurugram commands INR 125-165/sq.ft/mo, whereas Sohna Road leases at INR 55-75/sq.ft/mo. GCC Intel presents granular micro-market ranges rather than blended averages.
    - **Headcount Discrepancies:** Companies frequently announce future target headcount (e.g. "Plans to hire 3,000 engineers") which differs from current on-the-ground employees. We tag each figure with `Verified Actual`, `Company Announcement`, or `Industry Estimate`.
    """)
