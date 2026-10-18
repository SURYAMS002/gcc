import os
import sys
import json
import streamlit as st
import pandas as pd
import altair as alt

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

# Streamlit Page Config - Wide Executive View
st.set_page_config(
    page_title="GCC INTEL | Market Intelligence Terminal for India GCCs",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Institutional Enterprise CSS Theme
st.markdown("""
<style>
    /* Global Base */
    .stApp {
        background-color: #080C14;
        color: #E2E8F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* Institutional Header Banner */
    .terminal-header {
        background: linear-gradient(135deg, #0D1527 0%, #162035 50%, #0F172A 100%);
        border: 1px solid #22324F;
        border-radius: 10px;
        padding: 22px 28px;
        margin-bottom: 20px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
    }
    .terminal-tag {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #38BDF8;
        background-color: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 10px;
    }
    .terminal-title {
        color: #F8FAFC;
        font-size: 2.1rem;
        font-weight: 750;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .terminal-subtitle {
        color: #94A3B8;
        font-size: 0.98rem;
        margin-top: 8px;
        line-height: 1.55;
        max-width: 950px;
    }
    
    /* Live Telemetry Ribbon */
    .telemetry-ribbon {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 10px 18px;
        margin-bottom: 22px;
        font-size: 0.8rem;
        color: #94A3B8;
    }
    .telemetry-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .telemetry-item b {
        color: #F1F5F9;
    }

    /* KPI Metric Tiles */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 14px;
        margin-bottom: 22px;
    }
    .kpi-tile {
        background-color: #0E1626;
        border: 1px solid #1E2D4A;
        border-radius: 8px;
        padding: 16px 18px;
        border-top: 3px solid #38BDF8;
    }
    .kpi-tile.emerald { border-top-color: #10B981; }
    .kpi-tile.amber { border-top-color: #F59E0B; }
    .kpi-tile.purple { border-top-color: #A855F7; }

    .kpi-number {
        font-size: 1.75rem;
        font-weight: 750;
        color: #F8FAFC;
        margin: 0;
        line-height: 1.2;
    }
    .kpi-desc {
        color: #94A3B8;
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 4px;
    }
    .kpi-cite {
        color: #64748B;
        font-size: 0.72rem;
        margin-top: 6px;
    }

    /* Actionable Prompt Question Buttons */
    .prompt-card {
        background-color: #0E1626;
        border: 1px solid #1E2D4A;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        transition: border-color 0.2s ease;
    }
    .prompt-card:hover {
        border-color: #38BDF8;
    }

    /* Card styling */
    .intel-card {
        background-color: #0E1626;
        border: 1px solid #1E2D4A;
        border-radius: 8px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }
    .intel-card:hover {
        border-color: #2E436E;
    }

    /* Badges */
    .badge-verified {
        background-color: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-announcement {
        background-color: rgba(56, 189, 248, 0.12);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-estimate {
        background-color: rgba(245, 158, 11, 0.12);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .chip {
        background-color: #172338;
        color: #93C5FD;
        border: 1px solid #223554;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 0.72rem;
        margin-right: 5px;
        margin-bottom: 4px;
        display: inline-block;
    }
    .agent-step {
        background-color: #0F172A;
        border-left: 3px solid #38BDF8;
        padding: 7px 12px;
        font-family: monospace;
        font-size: 0.8rem;
        margin-bottom: 5px;
        color: #CBD5E1;
    }
    .calc-result-box {
        background: linear-gradient(135deg, #0F1E36 0%, #132747 100%);
        border: 1px solid #264673;
        border-radius: 8px;
        padding: 18px 22px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "agent_chat_history" not in st.session_state:
    st.session_state["agent_chat_history"] = []
if "research_prompt_input" not in st.session_state:
    st.session_state["research_prompt_input"] = ""
if "trigger_agent_run" not in st.session_state:
    st.session_state["trigger_agent_run"] = False
if "last_research_result" not in st.session_state:
    st.session_state["last_research_result"] = None
if "last_research_query" not in st.session_state:
    st.session_state["last_research_query"] = ""
if "vector_store" not in st.session_state:
    try:
        st.session_state["vector_store"] = build_or_load_gcc_index()
    except Exception:
        st.session_state["vector_store"] = None

# Sidebar Configuration
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0;">
        <span style="font-size: 0.7rem; font-weight: 700; color: #38BDF8; letter-spacing: 1px;">INSTITUTIONAL SUITE</span>
        <h2 style="color: #F8FAFC; margin: 2px 0 0 0; font-size: 1.55rem; font-weight: 750;">GCC INTEL</h2>
        <p style="color: #94A3B8; margin: 2px 0 0 0; font-size: 0.82rem;">India's Market Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    nav_choice = st.radio(
        "Navigation",
        [
            "🌐 Overview & Market Signals",
            "🧮 Location Cost & Setup Modeler",
            "🏢 GCC Explorer & Dossiers",
            "🏙️ City Intelligence & Analytics",
            "🧠 Ask GCC Intel (AI Research Agent)",
            "🤝 Service Providers & EOR",
            "📚 Data Quality & Sources Registry"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    
    # Credential Check
    active_key = get_gemini_api_key()
    if not active_key:
        st.markdown("**🔑 API Key Required**")
        user_key = st.text_input("Enter Gemini API Key", type="password", key="user_gemini_api_key")
        if user_key:
            st.success("API key stored for session.")
            active_key = user_key
        st.caption("Configured in .env or Streamlit Secrets for auto-login.")
        st.caption("🟢 **AI Inference:** Gemini 3.8 Flash Active")

    st.markdown("---")
    kpis = get_ecosystem_kpis()
    st.markdown(f"""
    <div style="font-size: 0.76rem; color: #64748B; line-height: 1.55;">
        <b>Audited GCCs:</b> {kpis['curated_gcc_count']} records<br>
        <b>Tracked Workforce:</b> {kpis['total_tracked_headcount']:,} employees<br>
        <b>Monitored Hubs:</b> 5 Tier-1 Metros<br>
        <b>Verification Cycle:</b> October 2024 Audit<br>
        <hr style="margin: 8px 0; border: none; border-top: 1px solid #1E293B;">
        🌐 <a href="https://cu5axikwdfpfurctzwhxtp.streamlit.app/" target="_blank" style="color: #38BDF8; text-decoration: none; font-weight: 600;">Live Cloud Terminal ↗</a><br>
        💻 <a href="https://github.com/SURYAMS002/gcc" target="_blank" style="color: #94A3B8; text-decoration: none;">GitHub Source ↗</a>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. OVERVIEW & MARKET SIGNALS
# -------------------------------------------------------------
if nav_choice == "🌐 Overview & Market Signals":
    st.markdown("""
    <div class="terminal-header">
        <span class="terminal-tag">Institutional Market Intelligence Terminal</span>
        <h1 class="terminal-title">India GCC Ecosystem Advisory Platform</h1>
        <p class="terminal-subtitle">
            An evidence-backed market intelligence terminal engineered for global enterprise executives, 
            private equity sponsors, and strategy teams evaluating location feasibility, state incentives, 
            real estate dynamics, and talent economics across India.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Telemetry Ribbon
    st.markdown("""
    <div class="telemetry-ribbon">
        <div class="telemetry-item">🟢 Live Index: <b>32 Audited GCCs</b></div>
        <div class="telemetry-item">🏛️ Policies: <b>Karnataka 2024 | Tamil Nadu 2022 | Telangana TS-iPASS</b></div>
        <div class="telemetry-item">🏢 Real Estate: <b>CBRE Q2 2024</b></div>
        <div class="telemetry-item">💼 Compensation: <b>Michael Page 2024 Guide</b></div>
    </div>
    """, unsafe_allow_html=True)

    # Macro Indicators
    kpis = get_ecosystem_kpis()
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-tile">
            <div class="kpi-number">{kpis['macro_india_gccs']}</div>
            <div class="kpi-desc">Total Operational GCCs in India</div>
            <div class="kpi-cite">Source: {kpis['macro_source_label']}</div>
        </div>
        <div class="kpi-tile emerald">
            <div class="kpi-number">{kpis['macro_talent_pool']}</div>
            <div class="kpi-desc">Specialized Tech & R&D Workforce</div>
            <div class="kpi-cite">Source: NASSCOM GCC 4.0 Report</div>
        </div>
        <div class="kpi-tile amber">
            <div class="kpi-number">{kpis['macro_economic_value']}</div>
            <div class="kpi-desc">Annual Direct Economic Value</div>
            <div class="kpi-cite">Projected $100B+ by 2030</div>
        </div>
        <div class="kpi-tile purple">
            <div class="kpi-number">{kpis['curated_gcc_count']}</div>
            <div class="kpi-desc">Audited Marquee GCC Case Files</div>
            <div class="kpi-cite">100% Primary Source Backed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Strategic Inquiries Showcase (What You Can Ask)")
    st.markdown("""
    Below are real-world strategic decision questions global executives and consultants evaluate. 
    **Click any card to instantly run the AI Research Agent with source verification:**
    """)

    col_q1, col_q2 = st.columns(2)

    with col_q1:
        st.markdown("**🏦 BFSI, FinTech & Strategy**")
        if st.button("💳 Which cities should a US fintech company consider for a 300-person GCC?"):
            st.session_state["research_prompt_input"] = "Which cities should a US fintech company consider for a 300-person GCC?"
            st.session_state["trigger_agent_run"] = True
            st.info("✓ Query queued! Navigate to **🧠 Ask GCC Intel** in the sidebar to view full briefing.")

        if st.button("⚖️ Compare Bengaluru vs Hyderabad for financial software & risk modelling"):
            st.session_state["research_prompt_input"] = "Compare Bengaluru and Hyderabad for financial software, quantitative risk modelling, and real estate costs."
            st.session_state["trigger_agent_run"] = True
            st.info("✓ Query queued! Navigate to **🧠 Ask GCC Intel** in the sidebar to view full briefing.")

        st.markdown("**🧬 Healthcare, Pharma & Life Sciences**")
        if st.button("🔬 Where are India's leading healthcare & pharmaceutical R&D GCCs located?"):
            st.session_state["research_prompt_input"] = "Where are India's leading healthcare and pharmaceutical R&D GCCs located, and what functions do AstraZeneca and Novartis run?"
            st.session_state["trigger_agent_run"] = True
            st.info("✓ Query queued! Navigate to **🧠 Ask GCC Intel** in the sidebar to view full briefing.")

    with col_q2:
        st.markdown("**📜 State Policies, Grants & Subsidies**")
        if st.button("🏛️ What state incentives are available in Tamil Nadu vs Karnataka for a new GCC?"):
            st.session_state["research_prompt_input"] = "What state incentives are available in Tamil Nadu vs Karnataka for a new GCC, including lease subsidies and training grants?"
            st.session_state["trigger_agent_run"] = True
            st.info("✓ Query queued! Navigate to **🧠 Ask GCC Intel** in the sidebar to view full briefing.")

        if st.button("⚡ How does Telangana's TS-iPASS single-window clearance guarantee approval timelines?"):
            st.session_state["research_prompt_input"] = "How does Telangana's TS-iPASS single-window clearance guarantee approval timelines for new IT and GCC investments?"
            st.session_state["trigger_agent_run"] = True
            st.info("✓ Query queued! Navigate to **🧠 Ask GCC Intel** in the sidebar to view full briefing.")

        st.markdown("**🛡️ Zero-Hallucination Audit Test**")
        if st.button("🔍 Test Abstention: Does Apple or Tesla have an audited secret GCC in Antarctica?"):
            st.session_state["research_prompt_input"] = "Does Apple or Tesla have an audited secret GCC in Antarctica?"
            st.session_state["trigger_agent_run"] = True
            st.info("✓ Query queued! Navigate to **🧠 Ask GCC Intel** to watch the agent strictly refuse to hallucinate.")

    st.markdown("---")

    # Visual Snapshot: India GCC Market Share & Grade-A Lease Comparison
    st.subheader("📊 Market Intelligence Telemetry")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("**India GCC Hub Market Share (% of Total Centers)**")
        share_data = pd.DataFrame({
            "City": ["Bengaluru", "Hyderabad", "Delhi-NCR", "Chennai", "Pune"],
            "Market Share (%)": [39.5, 21.0, 14.5, 13.5, 11.5]
        })
        chart_share = alt.Chart(share_data).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#38BDF8").encode(
            x=alt.X("Market Share (%):Q", title="Market Share (%)"),
            y=alt.Y("City:N", sort="-x", title="Metropolitan Hub"),
            tooltip=["City", "Market Share (%)"]
        ).properties(height=240)
        st.altair_chart(chart_share, use_container_width=True)
        st.caption("Source: NASSCOM & Zinnov India GCC Landscape Report 2024")

    with col_chart2:
        st.markdown("**Commercial Real Estate: Grade-A Lease Rates (INR/sq.ft/mo)**")
        rent_data = pd.DataFrame({
            "City": ["Bengaluru", "Gurugram", "Hyderabad", "Pune", "Chennai"],
            "Min Rent": [85, 80, 65, 60, 55],
            "Max Rent": [125, 135, 90, 85, 80]
        })
        rent_melted = pd.melt(rent_data, id_vars=["City"], value_vars=["Min Rent", "Max Rent"], var_name="Range", value_name="INR_sqft_mo")
        chart_rent = alt.Chart(rent_melted).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("City:N", title="City"),
            y=alt.Y("INR_sqft_mo:Q", title="Monthly Lease (INR / sq.ft)"),
            color=alt.Color("Range:N", scale=alt.Scale(domain=["Min Rent", "Max Rent"], range=["#223D69", "#38BDF8"])),
            tooltip=["City", "Range", "INR_sqft_mo"]
        ).properties(height=240)
        st.altair_chart(chart_rent, use_container_width=True)
        st.caption("Source: CBRE Research India Office Figures Q2 2024")

# -------------------------------------------------------------
# 2. INTERACTIVE LOCATION COST & SETUP MODELER (NEW FEATURE!)
# -------------------------------------------------------------
elif nav_choice == "🧮 Location Cost & Setup Modeler":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <span class="terminal-tag">Executive Modeling Tool</span>
        <h2 style="color: #F8FAFC; margin: 2px 0 0 0; font-size: 1.8rem; font-weight: 750;">🧮 GCC Location Setup & OpEx Modeler</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Simulate annual real estate lease outlays, engineering payroll bases, and state policy incentives across Indian tech hubs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_inp1, col_inp2, col_inp3 = st.columns(3)
    with col_inp1:
        target_city = st.selectbox("Target Location Hub", ["Bengaluru", "Hyderabad", "Chennai", "Pune", "Gurugram"])
    with col_inp2:
        team_size = st.slider("Target Workforce Headcount", min_value=50, max_value=1000, value=250, step=25)
    with col_inp3:
        primary_function = st.selectbox("Primary Business Function", [
            "Software & Cloud Engineering",
            "Data Science & AI / ML",
            "Quantitative Finance & Risk",
            "Embedded Hardware / Automotive R&D"
        ])

    # Benchmarks lookup
    city_intel = get_city_intelligence(target_city)
    
    # Square footage assumption: 90 sq. ft. per employee (industry standard for Grade-A tech parks)
    total_sqft = team_size * 90
    
    # Rental calculations
    # Parse rental rate string e.g. "85 - 125"
    rent_str = city_intel["real_estate"]["grade_a_avg_rent_inr_sqft_mo"]
    rent_parts = [float(x.strip()) for x in rent_str.split("-")]
    min_rent, max_rent = rent_parts[0], rent_parts[1]
    avg_rent = (min_rent + max_rent) / 2.0
    
    # Annual Real Estate Cost = sqft * avg_rent * 12
    annual_re_inr = total_sqft * avg_rent * 12
    annual_re_cr = annual_re_inr / 10_000_000.0  # In INR Crores
    annual_re_usd = annual_re_inr / (83.5 * 10_000_000.0) # In USD Millions (~83.5 INR/USD)

    # Payroll benchmarks lookup
    if "AI" in primary_function:
        avg_ctc_lpa = 20.0
    elif "Finance" in primary_function:
        avg_ctc_lpa = 14.5
    elif "Hardware" in primary_function:
        avg_ctc_lpa = 15.0
    else:
        avg_ctc_lpa = 17.5

    annual_payroll_inr = team_size * (avg_ctc_lpa * 100_000.0)
    annual_payroll_cr = annual_payroll_inr / 10_000_000.0
    annual_payroll_usd = annual_payroll_inr / (83.5 * 10_000_000.0)

    # State incentive potential
    subsidy_notes = []
    estimated_savings_cr = 0.0
    if target_city == "Chennai":
        # TN R&D Training Subsidy: up to INR 6,000/employee/mo for 12 months = INR 72,000/emp
        tn_training_cr = (team_size * 72_000) / 10_000_000.0
        estimated_savings_cr += tn_training_cr
        subsidy_notes.append(f"Tamil Nadu R&D Training Subsidy: Potential ~INR {tn_training_cr:.2f} Cr (INR 6k/emp/mo for 12 mos)")
        subsidy_notes.append("50% Stamp Duty Exemption on office lease agreement")
    elif target_city == "Karnataka":
        subsidy_notes.append("Karnataka GCC Policy 2024: Up to INR 1 Cr AI Co-Innovation Matching Grant")
        subsidy_notes.append("100% Electricity Duty Exemption for 5 years")
    elif target_city == "Hyderabad":
        subsidy_notes.append("TS-iPASS: 100% Stamp Duty reimbursement on office registration")
        subsidy_notes.append("Power tariff rebate of INR 1.00/unit for 3 years")
    elif target_city == "Pune":
        subsidy_notes.append("Maharashtra IT Policy: 100% Stamp Duty Exemption + 10-15y Electricity Duty Waiver")
    elif target_city == "Gurugram":
        # Haryana ESDM: up to INR 48,000/employee/year
        hr_emp_cr = (team_size * 48_000) / 10_000_000.0
        estimated_savings_cr += hr_emp_cr
        subsidy_notes.append(f"Haryana Employment Generation Subsidy: Potential ~INR {hr_emp_cr:.2f} Cr/year for 5 years")

    # Render Simulation Summary Cards
    st.markdown("### 📊 Simulated Annual Operating Outlay (Indicative Model)")
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)

    with col_r1:
        st.metric(
            label="Total Space Requirement",
            value=f"{total_sqft:,} sq.ft",
            help="Calculated at 90 sq. ft. per seat (Grade-A tech park standard)."
        )
    with col_r2:
        st.metric(
            label="Est. Annual Office Lease",
            value=f"₹{annual_re_cr:.2f} Cr",
            delta=f"${annual_re_usd:.2f}M USD",
            delta_color="off"
        )
    with col_r3:
        st.metric(
            label="Est. Base Talent Payroll",
            value=f"₹{annual_payroll_cr:.2f} Cr",
            delta=f"${annual_payroll_usd:.2f}M USD",
            delta_color="off"
        )
    with col_r4:
        total_opex_cr = annual_re_cr + annual_payroll_cr
        st.metric(
            label="Est. Annual Core OpEx",
            value=f"₹{total_opex_cr:.2f} Cr",
            delta=f"${total_opex_cr / 8.35:.2f}M USD",
            delta_color="off"
        )

    # Detailed Micro-Market Breakdown
    st.markdown(f"#### 📍 Recommended Micro-Markets in {target_city}")
    micros = city_intel["real_estate"]["prime_micromarkets"]
    col_m = st.columns(len(micros))
    for idx, m in enumerate(micros):
        with col_m[idx]:
            st.markdown(f"""
            <div class="intel-card" style="padding: 12px 14px;">
                <div style="font-weight: 700; color: #F8FAFC; font-size: 0.95rem;">{m['name']}</div>
                <div style="color: #38BDF8; font-size: 0.85rem; margin-top: 4px;">{m['rent_range']}</div>
                <div style="color: #94A3B8; font-size: 0.78rem; margin-top: 2px;">Vacancy: {m['vacancy_pct']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Subsidies & Policy Callout
    if subsidy_notes:
        st.markdown("""
        <div class="calc-result-box">
            <span style="font-size: 0.75rem; font-weight: 700; color: #34D399; letter-spacing: 1px;">STATUTORY INCENTIVE OPPORTUNITIES</span>
            <h4 style="color: #F8FAFC; margin: 4px 0 10px 0;">Applicable State Policy Concessions</h4>
        """, unsafe_allow_html=True)
        for s in subsidy_notes:
            st.markdown(f"• **{s}**")
        st.caption(f"Authority: {city_intel['state_policy']['department']} ({city_intel['state_policy']['policy_name']})")
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. GCC EXPLORER & DOSSIERS
# -------------------------------------------------------------
elif nav_choice == "🏢 GCC Explorer & Dossiers":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <span class="terminal-tag">Curated Case Registry</span>
        <h2 style="color: #F8FAFC; margin: 2px 0 0 0; font-size: 1.8rem; font-weight: 750;">🏢 GCC Explorer & Case Dossiers</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Filter and inspect 32 audited Global Capability Centres with verified locations, workforce scales, and expansions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Filter Controls
    col_s1, col_s2, col_s3, col_s4 = st.columns([3, 2, 2, 2])
    with col_s1:
        search_kw = st.text_input("Search company, parent, or capability", placeholder="e.g. Goldman, Boeing, Cyber, Clinical...")
    with col_s2:
        city_filter = st.selectbox("City Filter", ["All Cities", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Gurugram"])
    with col_s3:
        industry_filter = st.selectbox("Industry Filter", [
            "All Industries", "BFSI", "Retail & CPG", "Tech & Software", 
            "Healthcare & Life Sciences", "Automotive & Mobility", "Aerospace & Defence", "Semiconductor & Hardware", "Energy & Resources"
        ])
    with col_s4:
        status_filter = st.selectbox("Verification Tier", ["All Statuses", "Verified Fact", "Company Announcement", "Industry Estimate"])

    records = get_gcc_records(
        search_query=search_kw,
        city=city_filter,
        industry=industry_filter,
        verification_status=status_filter
    )

    col_cnt, col_exp = st.columns([3, 1])
    with col_cnt:
        st.markdown(f"**Showing {len(records)} Audited GCC Case Profiles**")
    with col_exp:
        # Export as CSV button
        if records:
            df_export = pd.DataFrame(records)
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Directory (CSV)",
                data=csv_data,
                file_name="gcc_intel_directory.csv",
                mime="text/csv"
            )

    view_mode = st.radio("Display Mode", ["Executive Case Cards", "Master Data Table"], horizontal=True)

    if view_mode == "Master Data Table":
        table_rows = []
        for r in records:
            badge = "🟢 Verified" if r["verification_status"] == "Verified Fact" else ("🔵 Announcement" if r["verification_status"] == "Company Announcement" else "🟡 Estimate")
            table_rows.append({
                "Company": r["company_name"],
                "Parent & Global HQ": f"{r['parent_company']} ({r['global_headquarters']})",
                "City": r["city"],
                "Industry": r["industry"],
                "Est. Year": r.get("establishment_year", "N/A"),
                "Headcount": f"{r['headcount']:,} ({r['headcount_type']})",
                "Confidence": badge,
                "Source Link": r["source_url"]
            })
        st.dataframe(
            pd.DataFrame(table_rows),
            column_config={
                "Source Link": st.column_config.LinkColumn("Primary Source", display_text="Open Disclosure ↗")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        for r in records:
            badge_html = (
                f'<span class="badge-verified">✓ {r["verification_status"]}</span>' if r["verification_status"] == "Verified Fact"
                else (f'<span class="badge-announcement">ℹ {r["verification_status"]}</span>' if r["verification_status"] == "Company Announcement"
                else f'<span class="badge-estimate">⚠ {r["verification_status"]}</span>')
            )
            functions_chips = "".join([f'<span class="chip">{f}</span>' for f in r.get("business_functions", [])])

            st.markdown(f"""
            <div class="intel-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">{r['company_name']}</span>
                        <span style="color: #64748B; font-size: 0.85rem; margin-left: 8px;">Est. {r.get('establishment_year', 'N/A')}</span>
                        <div style="color: #94A3B8; font-size: 0.86rem; margin-top: 2px;">{r['parent_company']} • Global HQ: {r['global_headquarters']}</div>
                    </div>
                    <div>{badge_html}</div>
                </div>
                <div style="margin: 8px 0; font-size: 0.85rem;">
                    <b>Hub:</b> {r['city']}, {r['state']} &nbsp;|&nbsp; 
                    <b>Industry:</b> {r['industry']} &nbsp;|&nbsp; 
                    <b>Tracked Size:</b> {r['headcount']:,} roles ({r['headcount_type']})
                </div>
                <div style="margin-bottom: 8px;">
                    {functions_chips}
                </div>
                <div style="background-color: #070B12; border-left: 3px solid #38BDF8; padding: 8px 12px; border-radius: 4px; font-size: 0.84rem; margin-bottom: 8px;">
                    <b>Recent Expansion Activity:</b> {r['recent_announcement']}
                </div>
                <div style="font-size: 0.78rem; color: #94A3B8;">
                    <b>Source:</b> <a href="{r['source_url']}" target="_blank" style="color: #38BDF8; text-decoration: none;">{r['source_title']}</a> 
                    • Published: {r['source_date']} • Verified: {r['last_verified_date']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. CITY INTELLIGENCE & ANALYTICS
# -------------------------------------------------------------
elif nav_choice == "🏙️ City Intelligence & Analytics":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <span class="terminal-tag">Comparative Location Analytics</span>
        <h2 style="color: #F8FAFC; margin: 2px 0 0 0; font-size: 1.8rem; font-weight: 750;">🏙️ City Intelligence & Policy Benchmarks</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Direct side-by-side comparison across talent pools, Grade-A real estate rentals, state incentive frameworks, and infrastructure.
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
        st.warning("Please select at least 1 city to view intelligence.")
    else:
        filtered_cities = [c for c in all_cities if c["name"] in selected_cities]

        # Top Macro Cards
        cols = st.columns(len(filtered_cities))
        for idx, c in enumerate(filtered_cities):
            with cols[idx]:
                st.markdown(f"""
                <div class="intel-card" style="min-height: 230px;">
                    <span class="badge-announcement">{c['tier']}</span>
                    <h3 style="color: #F8FAFC; margin: 6px 0 2px 0;">{c['name']}</h3>
                    <div style="color: #38BDF8; font-size: 0.85rem; margin-bottom: 6px;">{c['state']}</div>
                    <p style="color: #94A3B8; font-size: 0.8rem; font-style: italic; margin-bottom: 10px;">"{c['tagline']}"</p>
                    <div style="font-size: 0.82rem; line-height: 1.55;">
                        <b>Market Share:</b> {c['market_share_pct']}% of India GCCs<br>
                        <b>Est. Centers:</b> {c['estimated_gcc_count']}<br>
                        <b>Grade-A Rents:</b> INR {c['real_estate']['grade_a_avg_rent_inr_sqft_mo']}/sq.ft/mo<br>
                        <b>Tech Workforce:</b> {c['estimated_workforce']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### 📊 Detailed Matrix Comparison")

        # 1. Real Estate
        with st.expander("🏢 Commercial Real Estate & Vacancy Rates (CBRE Q2 2024)", expanded=True):
            re_rows = []
            for c in filtered_cities:
                re = c["real_estate"]
                micros_str = " | ".join([f"{m['name']}: {m['rent_range']} (Vac: {m['vacancy_pct']})" for m in re["prime_micromarkets"]])
                re_rows.append({
                    "City": c["name"],
                    "Grade-A Lease Range": f"INR {re['grade_a_avg_rent_inr_sqft_mo']} /sq.ft/mo",
                    "Prime Micro-Markets & Vacancy": micros_str,
                    "Source": re["source_label"]
                })
            st.dataframe(pd.DataFrame(re_rows), use_container_width=True, hide_index=True)

        # 2. Talent
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
                    "Attr. Rate": tb["attrition_rate_est"]
                })
            st.dataframe(pd.DataFrame(sal_rows), use_container_width=True, hide_index=True)

        # 3. State Policy
        with st.expander("📜 State GCC Policies & Statutory Subsidies", expanded=True):
            for c in filtered_cities:
                pol = c["state_policy"]
                st.markdown(f"#### 🏛️ {c['name']} — {pol['policy_name']}")
                st.caption(f"Authority: {pol['department']}")
                for inc in pol["key_incentives"]:
                    st.markdown(f"• {inc}")
                st.markdown("---")

        # 4. Strategic Tradeoffs
        with st.expander("⚖️ Strategic Trade-offs & Best-Fit Profile", expanded=True):
            for c in filtered_cities:
                to = c["strategic_tradeoffs"]
                st.markdown(f"#### {c['name']}")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Key Advantages (Pros):**")
                    for p in to["pros"]:
                        st.markdown(f"✓ {p}")
                with c2:
                    st.markdown("**Key Trade-offs (Cons):**")
                    for con in to["cons"]:
                        st.markdown(f"⚠ {con}")
                st.info(f"**Recommended For:** {to['recommended_for']}")

        # AI Comparative Synthesis
        st.markdown("### 🤖 Generate Executive City Synthesis with AI")
        if st.button("Synthesize Location Trade-offs ➔", type="primary"):
            with st.spinner("Analyzing location trade-offs across talent, real estate, and state policies..."):
                agent = GCCIntelAgent()
                prompt_q = f"Compare {', '.join(selected_cities)} for a prospective global enterprise setting up a GCC in India. Detail the talent cost, real estate, and state incentive trade-offs."
                ai_res = agent.run(prompt_q)
                st.markdown(ai_res["final_answer"])

# -------------------------------------------------------------
# 5. ASK GCC INTEL (AI RESEARCH AGENT)
# -------------------------------------------------------------
elif nav_choice == "🧠 Ask GCC Intel (AI Research Agent)":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <span class="terminal-tag">Agentic Intelligence Engine</span>
        <h2 style="color: #F8FAFC; margin: 2px 0 0 0; font-size: 1.8rem; font-weight: 750;">🧠 Ask GCC Intel</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Conversational market research agent built with LangGraph, FAISS semantic vector retrieval, and automated source verification.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # API Key Verification & Inline Entry
    active_key = get_gemini_api_key()
    if not active_key:
        st.warning("⚠️ **Gemini API Key Required:** Please configure `GEMINI_API_KEY` in Streamlit Cloud Secrets, or enter your key below to unlock AI research queries:")
        col_k1, col_k2 = st.columns([4, 1])
        with col_k1:
            direct_api_key = st.text_input("Enter Gemini API Key (stored securely for this session):", type="password", key="inline_agent_key")
        with col_k2:
            st.write("")
            st.write("")
            if st.button("Unlock Terminal ➔", type="primary"):
                if direct_api_key.strip():
                    st.session_state["user_gemini_api_key"] = direct_api_key.strip()
                    st.success("✓ API Key activated!")
                    st.rerun()
                else:
                    st.error("Please enter a valid Gemini API key.")

    # Pre-set questions with 1-click execution
    st.markdown("**Click any curated strategic prompt to execute immediately:**")
    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1:
        if st.button("💳 FinTech 300-person GCC ➔", use_container_width=True):
            st.session_state["research_prompt_input"] = "Which cities should a US fintech company consider for a 300-person GCC?"
            st.session_state["trigger_agent_run"] = True
            st.rerun()
    with c_p2:
        if st.button("🏢 Chennai Tech & Functions ➔", use_container_width=True):
            st.session_state["research_prompt_input"] = "Find GCCs in Chennai that have finance, engineering, or analytics functions."
            st.session_state["trigger_agent_run"] = True
            st.rerun()
    with c_p3:
        if st.button("📜 Tamil Nadu State Subsidies ➔", use_container_width=True):
            st.session_state["research_prompt_input"] = "What state incentives might be relevant when establishing a GCC in Tamil Nadu?"
            st.session_state["trigger_agent_run"] = True
            st.rerun()

    # Form with persistent input
    with st.form("research_agent_form", clear_on_submit=False):
        user_query_input = st.text_input(
            "Enter strategic GCC inquiry:",
            value=st.session_state.get("research_prompt_input", ""),
            placeholder="e.g. Compare office leasing costs and state incentives between Hyderabad and Bengaluru..."
        )
        submit_clicked = st.form_submit_button("Execute Research Agent ➔", type="primary")

    # Determine execution trigger
    should_run = False
    query_to_execute = ""

    if submit_clicked and user_query_input.strip():
        query_to_execute = user_query_input.strip()
        st.session_state["research_prompt_input"] = query_to_execute
        should_run = True
    elif st.session_state.get("trigger_agent_run", False) and st.session_state.get("research_prompt_input", "").strip():
        query_to_execute = st.session_state["research_prompt_input"].strip()
        st.session_state["trigger_agent_run"] = False
        should_run = True

    if should_run and query_to_execute:
        active_key = get_gemini_api_key()
        if not active_key:
            st.error("⚠️ GEMINI_API_KEY is missing. Please enter your API key in the field above or in the left sidebar to execute research.")
        else:
            try:
                with st.status("⚙️ Executing Multi-Step Market Intelligence Research...", expanded=True) as status_box:
                    st.write(f"🔍 **Inquiry:** *\"{query_to_execute}\"*")
                    st.write("📚 Retrieving verified evidence from NASSCOM, CBRE Q2 2024 & State Policy dossiers...")
                    
                    agent = GCCIntelAgent()
                    result = agent.run(query_to_execute)
                    
                    for step in result.get("status_log", []):
                        st.write(f"✓ {step}")
                        
                    status_box.update(label="✓ Market Intelligence Research Completed & Audited", state="complete", expanded=False)

                # Store persistently in session state so results don't vanish on rerun
                st.session_state["last_research_result"] = result
                st.session_state["last_research_query"] = query_to_execute
            except Exception as e:
                err_msg = str(e)
                st.error(f"❌ **Research Execution Error:** {err_msg}")
                if "401" in err_msg or "UNAUTHENTICATED" in err_msg or "API key not valid" in err_msg:
                    st.info("""
                    **💡 How to Resolve (401 Invalid Key):**
                    The API key configured in Streamlit Secrets was rejected by Google AI Studio (`ACCESS_TOKEN_TYPE_UNSUPPORTED`).
                    
                    1. Go to **[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)** (it is completely free).
                    2. Click **Create API Key**. (Valid Gemini API keys start with **`AIzaSy...`**).
                    3. Update your key in Streamlit App Settings ➔ Secrets:
                       ```toml
                       GEMINI_API_KEY="AIzaSyYourNewKeyHere"
                       ```
                    4. Or paste it directly into the input field above and click **Unlock Terminal**.
                    """)

    # Render persistent research dossier
    if st.session_state.get("last_research_result"):
        res = st.session_state["last_research_result"]
        q_label = st.session_state.get("last_research_query", "Strategic Inquiry")

        st.markdown("---")
        st.markdown(f"### 📋 Strategic Advisory Dossier: *{q_label}*")

        if res.get("abstained"):
            st.warning("⚠️ **Abstention Policy Active:** Data not found in audited knowledge base. Agent strictly refused to fabricate.")
        elif res.get("is_supported"):
            st.success("✓ **Fully Verified:** Claims audited and grounded against primary GCC Intel dossiers.")

        st.markdown(res.get("final_answer", ""))

# -------------------------------------------------------------
# 6. SERVICE PROVIDERS & EOR
# -------------------------------------------------------------
elif nav_choice == "🤝 Service Providers & EOR":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <span class="terminal-tag">Enablement Partner Ecosystem</span>
        <h2 style="color: #F8FAFC; margin: 2px 0 0 0; font-size: 1.8rem; font-weight: 750;">🤝 GCC Service Providers & Incubation Partners</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Vetted enablement partners for turnkey GCC setup, corporate legal structuring, Grade-A real estate brokerage, and Employer of Record (EOR) hiring.
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
        sp_kw = st.text_input("Filter by capability or location", placeholder="e.g. Incubation, EOR, Lease, SAM, CBRE...")

    providers = get_service_providers(category=category_choice, search_query=sp_kw)
    st.markdown(f"**Showing {len(providers)} Vetted Partners**")

    for sp in providers:
        chips = "".join([f'<span class="chip">{s}</span>' for s in sp.get("services_offered", [])])
        st.markdown(f"""
        <div class="intel-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span style="font-size: 1.2rem; font-weight: 700; color: #F8FAFC;">{sp['name']}</span>
                    <div style="color: #38BDF8; font-size: 0.85rem;">{sp['category']} • {sp['sub_category']}</div>
                </div>
                <div class="badge-verified">{sp['verification_status']}</div>
            </div>
            <div style="margin: 8px 0; font-size: 0.85rem;">
                <b>Global HQ:</b> {sp['headquarters']} &nbsp;|&nbsp; 
                <b>Locations Served:</b> {', '.join(sp.get('locations_served', []))}
            </div>
            <div style="margin-bottom: 8px;">{chips}</div>
            <div style="background-color: #070B12; border-left: 3px solid #10B981; padding: 8px 12px; border-radius: 4px; font-size: 0.84rem; margin-bottom: 8px;">
                <b>Documented GCC Experience:</b> {sp['documented_track_record']}
            </div>
            <div>
                <a href="{sp['source_url']}" target="_blank" style="color: #38BDF8; font-size: 0.8rem; text-decoration: none;">Visit Partner Portal ↗</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 7. DATA QUALITY & SOURCES REGISTRY
# -------------------------------------------------------------
elif nav_choice == "📚 Data Quality & Sources Registry":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <span class="terminal-tag">Data Governance & Provenance</span>
        <h2 style="color: #F8FAFC; margin: 2px 0 0 0; font-size: 1.8rem; font-weight: 750;">📚 Sources, Methodology & Data Quality</h2>
        <p style="color: #94A3B8; margin-top: 4px; font-size: 0.95rem;">
            Full provenance registry, government policy gazettes, and handling of conflicting data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 🛡️ Enterprise Data Governance Framework
    GCC Intel enforces strict data auditing protocols:
    1. **Zero Hallucination Policy:** If verified evidence is absent from our repository, the research agent explicitly states what is missing instead of fabricating plausible-sounding facts.
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

    st.dataframe(
        pd.DataFrame(sources_data),
        column_config={
            "Canonical Link": st.column_config.LinkColumn("Primary Source", display_text="Open Publication ↗")
        },
        use_container_width=True,
        hide_index=True
    )
