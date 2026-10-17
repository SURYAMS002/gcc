import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Institutional Palette
    BG_DARK = RGBColor(8, 12, 20)        # #080C14
    CARD_BG = RGBColor(14, 22, 38)       # #0E1626
    ACCENT_CYAN = RGBColor(56, 189, 248) # #38BDF8
    ACCENT_GREEN = RGBColor(16, 185, 129)# #10B981
    ACCENT_AMBER = RGBColor(245, 158, 11)# #F59E0B
    TEXT_WHITE = RGBColor(248, 250, 252) # #F8FAFC
    TEXT_MUTED = RGBColor(148, 163, 184) # #94A3B8
    BORDER_BLUE = RGBColor(34, 50, 79)   # #22324F

    def apply_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.color.rgb = BG_DARK
        return bg

    def add_header(slide, tag_text, title_text, category="DELIVERABLE 1: PRODUCT STRATEGY DECK"):
        # Category Banner
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = f"{category}  |  {tag_text}".upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, title, items, border_color=BORDER_BLUE, header_color=ACCENT_CYAN):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(height - 0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = header_color

        for item in items:
            p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_MUTED
            p.space_before = Pt(6)

    # -------------------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    apply_background(s1)

    # Main Card
    main_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(10.9), Inches(5.1))
    main_card.fill.solid()
    main_card.fill.fore_color.rgb = CARD_BG
    main_card.line.color.rgb = ACCENT_CYAN
    main_card.line.width = Pt(2)

    tb = s1.shapes.add_textbox(Inches(1.8), Inches(1.8), Inches(9.7), Inches(3.9))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "FLEXIPLE PRODUCT INTERNSHIP EVALUATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p = tf.add_paragraph()
    p.text = "GCC INTEL — PRODUCT STRATEGY DECK"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(12)

    p = tf.add_paragraph()
    p.text = "India's AI-Powered Market Intelligence & Location Advisory Terminal"
    p.font.size = Pt(16)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(8)

    p = tf.add_paragraph()
    p.text = "Transforming enterprise GCC expansion decisions with verified data, real-time OpEx simulation, and zero-hallucination agentic RAG."
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_before = Pt(18)

    p = tf.add_paragraph()
    p.text = "🌐 Live Interactive App: https://cu5axikwdfpfurctzwhxtp.streamlit.app/\n💻 GitHub Repository: https://github.com/SURYAMS002/gcc\n👤 Author: Suryam S | October 2026"
    p.font.size = Pt(11)
    p.font.color.rgb = ACCENT_CYAN
    p.space_before = Pt(24)

    # -------------------------------------------------------------------------
    # SLIDE 2: Executive Summary
    # -------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    apply_background(s2)
    add_header(s2, "EXECUTIVE SUMMARY", "Strategic Overview: Empowering Enterprise GCC Decisions")

    add_card(s2, 0.8, 1.8, 3.6, 5.0, "1. The Macro Shift", [
        "India's GCC sector is transitioning from cost-arbitrage back-offices to strategic global innovation engines (GCC 4.0).",
        "Over 1,900 operational GCCs employ 1.9M+ professionals and generate $64.6B in direct economic value.",
        "Scaling toward 2,500+ GCCs and $100B+ economic impact by 2030.",
        "Average setup involves $15M-$50M+ in capital and multi-year lease commitments."
    ], ACCENT_CYAN, ACCENT_CYAN)

    add_card(s2, 4.8, 1.8, 3.6, 5.0, "2. The Critical Problem", [
        "Strategic leaders navigate fragmented, conflicting reports and opaque real estate broker numbers.",
        "Press releases conflate aspirational 5-year targets with actual ground-level operational workforce.",
        "Complex state policies (Karnataka 2024, TN 2022, Telangana TS-iPASS) remain locked in PDFs.",
        "Standard LLMs hallucinate office locations and invent salaries with zero auditability."
    ], ACCENT_AMBER, ACCENT_AMBER)

    add_card(s2, 8.8, 1.8, 3.7, 5.0, "3. The GCC Intel Solution", [
        "Audited Enterprise Knowledgebase: 32 verified GCC case files across 5 hubs and 8 sectors.",
        "Interactive OpEx Modeler: Real-time simulation of lease outlays, tech payroll, and state grants.",
        "Grounded Agentic RAG: LangGraph multi-step audit pipeline with FAISS vector retrieval.",
        "Production-Ready MVP: Live at cu5axikwdfpfurctzwhxtp.streamlit.app."
    ], ACCENT_GREEN, ACCENT_GREEN)

    # -------------------------------------------------------------------------
    # SLIDE 3: The Problem Statement
    # -------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    apply_background(s3)
    add_header(s3, "PROBLEM STATEMENT", "The Enterprise Information Gap in India GCC Expansion")

    add_card(s3, 0.8, 1.8, 2.7, 5.0, "1. Blended Real Estate", [
        "Reports quote generic city-wide averages.",
        "Bengaluru ORR (₹125/sqft/mo) vs Electronic City (₹55/sqft/mo) differ by over 120%.",
        "Lease decisions risk multi-crore budget variances without micro-market granularity."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s3, 3.8, 1.8, 2.7, 5.0, "2. Target Inflation", [
        "Corporate PR announcements routinely announce 5,000-seat multi-year aspirations.",
        "Actual day-1 operational headcount is often only 300-500 employees.",
        "Distorting competitor intelligence and market capacity assessments."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s3, 6.8, 1.8, 2.7, 5.0, "3. Obscure Subsidies", [
        "State governments offer substantial incentives, but details are buried in gazettes.",
        "Tamil Nadu offers ₹4,000/seat/mo training subsidies.",
        "Telangana TS-iPASS grants statutory 30-day deemed clearances.",
        "Most entrants fail to claim available subsidies due to lack of visibility."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s3, 9.8, 1.8, 2.7, 5.0, "4. LLM Hallucinations", [
        "Generic LLMs generate convincing falsehoods for high-stakes decisions.",
        "Invent non-existent tech centers, fabricate compensation bands, and cite dead links.",
        "Enterprises require strict mathematical accuracy and verified source citations."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 4: Business Opportunity & TAM / SAM / SOM
    # -------------------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    apply_background(s4)
    add_header(s4, "MARKET OPPORTUNITY", "A High-Margin B2B Market Driven by Historic Tailwinds")

    add_card(s4, 0.8, 1.8, 3.6, 5.0, "TAM: $4.8 Billion", [
        "Global Corporate Location Intelligence & Expansion Advisory.",
        "Enterprises worldwide spend billions on Big 4 retainers, location strategy, commercial lease consultancy, and talent benchmarking.",
        "Driven by nearshoring and global engineering decentralization."
    ], ACCENT_CYAN, ACCENT_CYAN)

    add_card(s4, 4.8, 1.8, 3.6, 5.0, "SAM: $720 Million", [
        "India-Specific GCC Advisory, EOR Incubation & Strategic Setup.",
        "Over 500 new GCCs projected to enter India by 2030.",
        "Each incoming GCC allocates $200k-$1M+ in preliminary feasibility studies, vendor searches, and advisory services."
    ], ACCENT_GREEN, ACCENT_GREEN)

    add_card(s4, 8.8, 1.8, 3.7, 5.0, "SOM: $18 Million (Year 3)", [
        "Capturing 3.5% of annual incoming and expanding mid-market/enterprise GCC advisory workflows.",
        "Monetized via tiered B2B SaaS terminal seats ($5k-$25k/yr) and vendor referral commissions.",
        "Expanding into continuous talent & real estate benchmarking."
    ], ACCENT_AMBER, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 5: Target Customer Personas
    # -------------------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    apply_background(s5)
    add_header(s5, "TARGET CUSTOMERS", "Multi-Stakeholder B2B Decision-Making Unit")

    add_card(s5, 0.8, 1.8, 2.7, 5.0, "CIO / VP Engineering", [
        "Profile: US/EU tech executives setting up a 150-500 person engineering hub.",
        "Key Need: Validating niche talent depth (AI/ML, Cloud, Quant Finance) and attrition risk.",
        "Value: Instant objective hub comparison without vendor bias."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s5, 3.8, 1.8, 2.7, 5.0, "Corporate Real Estate Head", [
        "Profile: Real estate directors budgeting Grade-A office leases across tech corridors.",
        "Key Need: Micro-market rental spreads, vacancy rates, and seat ratio standards (90 sqft/seat).",
        "Value: Rapid parametric modeling of annual lease outlays in INR Cr & USD M."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s5, 6.8, 1.8, 2.7, 5.0, "PE / VC Operating Partner", [
        "Profile: Growth-stage portfolio operations leaders guiding SaaS companies to scale in India.",
        "Key Need: EOR (Employer of Record) vs. Captive entity cost-benefit analysis.",
        "Value: Bypassing $150k consulting fees for early feasibility."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s5, 9.8, 1.8, 2.7, 5.0, "State Investment Agencies", [
        "Profile: State IT departments (e.g. Guidance TN, ITE&C Telangana) seeking investments.",
        "Key Need: Policy benchmarking vs. competitor states and promoting subsidies.",
        "Value: Platform visibility to global decision-makers evaluating expansion."
    ], BORDER_BLUE, ACCENT_GREEN)

    # -------------------------------------------------------------------------
    # SLIDE 6: Proposed Solution & Product Ecosystem
    # -------------------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    apply_background(s6)
    add_header(s6, "PROPOSED SOLUTION", "GCC Intel: The Institutional Intelligence Terminal")

    add_card(s6, 0.8, 1.8, 3.6, 5.0, "1. Curated Data Registry", [
        "32 Audited GCC Records: Goldman Sachs, Boeing, Walmart, AstraZeneca, Ford, etc.",
        "Granular Attributes: HQ, micro-market address, verified headcount, and expansion signals.",
        "Verification Tiers: Transparent 'Verified Fact', 'Announcement', and 'Estimate' tags.",
        "CSV Export: One-click directory download for offline modeling."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s6, 4.8, 1.8, 3.6, 5.0, "2. Parametric OpEx Modeler", [
        "Calculates Grade-A commercial lease budgets (INR Cr & USD M) using CBRE Q2 2024 rates.",
        "Models base engineering payroll using Michael Page 2024 compensation matrices.",
        "Applies statutory state incentives (TN training grants, Haryana employment subsidies).",
        "Recommends prime micro-markets with rent ranges and vacancy percentages."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s6, 8.8, 1.8, 3.7, 5.0, "3. Verifiable LangGraph Agent", [
        "5-Step Decision Loop: plan_and_search -> calculate -> draft -> verify -> finalize.",
        "FAISS Vector Retrieval: gemini-embedding-2 indexing policy gazettes & market reports.",
        "Strict Grounding: Mandatory primary source citations with working URLs.",
        "Zero-Hallucination Policy: Transparent abstention when verified data is unavailable."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 7: Deep Dive: Location OpEx & Setup Modeler
    # -------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    apply_background(s7)
    add_header(s7, "PARAMETRIC OPEX MODELER", "Simulating Commercial Leases, Payroll & State Subsidies")

    add_card(s7, 0.8, 1.8, 3.6, 5.0, "Input Parameters", [
        "Target Hub: Bengaluru, Hyderabad, Chennai, Pune, or Gurugram.",
        "Workforce Headcount: 50 to 1,000 employees (slider control).",
        "Functional Specialization: Cloud Engineering, AI/ML, Quant Finance, Embedded Hardware.",
        "Real-time reactive calculation upon slider modification."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s7, 4.8, 1.8, 3.6, 5.0, "Deterministic Math Engine", [
        "Office Space = Headcount × 90 sq.ft (industry standard).",
        "Annual Commercial Lease = Space × Grade-A Rent × 12 months.",
        "Annual Base Payroll = Headcount × Function-Specific Market Salary Mean.",
        "Annual Total OpEx = Commercial Lease + Base Payroll.",
        "Evaluated via safe Python AST math to guarantee calculation precision."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s7, 8.8, 1.8, 3.7, 5.0, "Executive Outputs", [
        "High-contrast financial metric tiles in INR Crores and USD Millions.",
        "Micro-market lease breakdown (e.g. HITEC City vs Financial District).",
        "Statutory state subsidies callouts (e.g. ₹4,000/seat/mo in TN, EPF reimbursement in KA).",
        "Direct export capability for executive investment committees."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 8: Deep Dive: Agentic RAG Architecture
    # -------------------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    apply_background(s8)
    add_header(s8, "AGENTIC RAG ARCHITECTURE", "Multi-Step Verification with Zero-Hallucination Guardrails")

    add_card(s8, 0.8, 1.8, 3.6, 5.0, "LangGraph StateGraph Loop", [
        "Node 1: Plan & Vector Search — Query decomposition and FAISS semantic chunk search.",
        "Node 2: AST Benchmark Calculator — Safe evaluation of cost and workforce formulas.",
        "Node 3: Draft Advisory Briefing — Gemini 3.8 Flash synthesizes raw briefing.",
        "Node 4: Market Evidence Verifier — Audits claims against retrieved text chunks.",
        "Node 5: Finalize Answer & Citations — Generates final response with hyperlinks."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s8, 4.8, 1.8, 3.6, 5.0, "Vector Retrieval Pipeline", [
        "gemini-embedding-2: 3072-dimensional vector embeddings.",
        "FAISS CPU Index: Cosine similarity vector search over high-density knowledge dossiers.",
        "Chunk Metadata: Tracks canonical source URL, publication date, and confidence level.",
        "Multi-city comparative retrieval enables cross-metro trade-off queries."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s8, 8.8, 1.8, 3.7, 5.0, "Zero-Hallucination Policy", [
        "Traditional LLMs invent answers when data is missing.",
        "GCC Intel enforces automated evidence auditing.",
        "If verified facts are absent, the agent explicitly returns a refusal to speculate.",
        "Protects corporate decision-makers from multi-million dollar bad assumptions."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 9: Market Positioning & Competitive Advantage
    # -------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    apply_background(s9)
    add_header(s9, "COMPETITIVE POSITIONING", "The Convergence of Research Depth, Speed & Auditability")

    add_card(s9, 0.8, 1.8, 2.7, 5.0, "Big 4 Consulting", [
        "Players: McKinsey, EY, PwC, BCG.",
        "Pros: Deep custom strategic analysis.",
        "Cons: High cost ($150k-$300k+), slow turnaround (8-12 weeks), static decks.",
        "GCC Intel Difference: 95% faster initial feasibility at 1/10th the cost."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s9, 3.8, 1.8, 2.7, 5.0, "Real Estate Brokers", [
        "Players: CBRE, JLL, Cushman & Wakefield.",
        "Pros: Accurate Grade-A office inventory.",
        "Cons: Biased toward leasing transactions; zero talent or tech stack depth.",
        "GCC Intel Difference: Objective multi-variable modeler combining CRE + talent + policy."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s9, 6.8, 1.8, 2.7, 5.0, "Legacy Analysts", [
        "Players: Gartner, Everest Group, Zinnov.",
        "Pros: Reputable industry reports.",
        "Cons: Static annual PDFs, paywalled, cannot run dynamic parametric queries.",
        "GCC Intel Difference: Interactive software terminal with real-time custom simulation."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s9, 9.8, 1.8, 2.7, 5.0, "Generic AI Models", [
        "Players: ChatGPT, Claude, Perplexity.",
        "Pros: Broad natural language interface.",
        "Cons: Hallucinates addresses, invents salaries, dead links, no math verification.",
        "GCC Intel Difference: Domain-grounded vector database with LangGraph evidence auditing."
    ], BORDER_BLUE, ACCENT_GREEN)

    # -------------------------------------------------------------------------
    # SLIDE 10: Business Model & Monetization Tiers
    # -------------------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    apply_background(s10)
    add_header(s10, "BUSINESS MODEL", "Tiered B2B SaaS Subscriptions & Ecosystem Monetization")

    add_card(s10, 0.8, 1.8, 3.6, 5.0, "Freemium Terminal", [
        "Price: Free (Lead Acquisition Hook).",
        "Includes: Macro ecosystem KPIs, high-level city profiles, and 3 standard AI queries/month.",
        "Purpose: Establish GCC Intel as the default discovery starting point for expanding tech teams."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s10, 4.8, 1.8, 3.6, 5.0, "Professional License", [
        "Price: $499 / user / month (or $4,990 / yr).",
        "Includes: Full access to 32+ audited GCC dossiers, unlimited AI research agent queries, interactive OpEx modeler, and CSV directory export.",
        "Target: Strategy teams, corporate development directors, and mid-market CXOs."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s10, 8.8, 1.8, 3.7, 5.0, "Enterprise Advisory License", [
        "Price: $25,000 / year (Multi-seat).",
        "Includes: Dedicated tenant, custom headcount simulation models, EOR partner RFP module, quarterly dossier updates, and API access.",
        "Plus: Ecosystem referral revenue from vetted EOR providers, real estate firms, and legal counsels."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 11: Product Roadmap (6-Month Horizon)
    # -------------------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    apply_background(s11)
    add_header(s11, "PRODUCT ROADMAP", "Strategic Execution Horizon: From Live MVP to Enterprise Scale")

    add_card(s11, 0.8, 1.8, 3.6, 5.0, "Current MVP (Ready Now)", [
        "STATUS: LIVE & 100% OPERATIONAL.",
        "Built and launched rapidly as an evaluation-ready platform.",
        "32 Audited GCC Profiles with primary source citations.",
        "5 Tier-1 Metros comparative intelligence matrix.",
        "Interactive OpEx & Location Setup Modeler.",
        "LangGraph multi-step research agent.",
        "Live on Streamlit Cloud & GitHub."
    ], ACCENT_GREEN, ACCENT_GREEN)

    add_card(s11, 4.8, 1.8, 3.6, 5.0, "Phase 1: Tier-2 Hubs (Months 1-2)", [
        "Expand to Tier-2 Emerging GCC Hubs: Kochi, Ahmedabad, Coimbatore, Chandigarh, Jaipur.",
        "EOR vs. Captive Cost Trade-Off Simulator.",
        "Commercial Real Estate API Integration for live vacancy feeds.",
        "Automated PDF Executive Board Briefing generator."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s11, 8.8, 1.8, 3.7, 5.0, "Phase 2: Enterprise Scale (Months 3-6)", [
        "Real-Time Talent Scraper & Attrition Tracker by micro-market.",
        "Enterprise Multi-Tenant Workspaces with SSO & Team Sharing.",
        "Partner Marketplace & Request-for-Proposal (RFP) Workflow.",
        "REST API & Python SDK for enterprise corporate real estate systems."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 12: Go-To-Market & Growth Strategy
    # -------------------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    apply_background(s12)
    add_header(s12, "GO-TO-MARKET STRATEGY", "Product-Led Inbound Growth & Institutional Distribution")

    add_card(s12, 0.8, 1.8, 3.6, 5.0, "1. Content-Led Inbound", [
        "Bi-weekly 'State of India GCCs' data reports published on LinkedIn and Substack.",
        "Focus on micro-market cost anomalies, state incentive comparisons, and tech talent migrations.",
        "Gated detailed breakdown models converting organic readers into active trial users."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s12, 4.8, 1.8, 3.6, 5.0, "2. Institutional Channel Partners", [
        "Co-marketing partnerships with US-India Business Council (USIBC) and NASSCOM.",
        "Integration with EOR platforms (Deel, Remote) seeking to advise customers transitioning to captive entities.",
        "Commercial real estate broker referral network."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s12, 8.8, 1.8, 3.7, 5.0, "3. Key Metrics & North Star", [
        "North Star Metric: Number of verified location feasibility reports generated and exported per week.",
        "Secondary Metrics:",
        "  - Free-to-Paid Subscription Conversion Rate (> 6%).",
        "  - Modeler Scenario Runs per User Session (> 4.2).",
        "  - Net Revenue Retention (NRR > 120%)."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 13: Summary & Production Proof
    # -------------------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    apply_background(s13)
    add_header(s13, "CONCLUSION & EVALUATION", "Production Delivery Summary & Live Platform Access")

    main_box = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.9))
    main_box.fill.solid()
    main_box.fill.fore_color.rgb = CARD_BG
    main_box.line.color.rgb = ACCENT_CYAN
    main_box.line.width = Pt(2)

    tb = s13.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.3), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "DELIVERABLE 1 COMPLETED — PRODUCTION-READY B2B PRODUCT"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p = tf.add_paragraph()
    p.text = "GCC Intel transforms high-stakes enterprise expansion decisions by bridging the gap between slow, exorbitant consulting retainers and unreliable, hallucinating AI chatbots."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(10)

    p = tf.add_paragraph()
    p.text = "Key Project Achievements:"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_before = Pt(14)

    achievements = [
        "100% Isolated Architecture: FinSight in c:\\FinSight and GCC Intel in c:\\gcc are completely independent repositories.",
        "Live Production Deployment: cu5axikwdfpfurctzwhxtp.streamlit.app deployed on Streamlit Community Cloud.",
        "Audited Multi-Hop Dataset: 32 GCC case files, 5 metros, 8 service providers, and 15 primary sources.",
        "Deterministic Financial Modeler: Parametric real estate lease outlays, tech payroll, and state subsidy calculations.",
        "LangGraph Verified RAG: Gemini 3.8 Flash + gemini-embedding-2 + FAISS with automated evidence verification."
    ]
    for ach in achievements:
        p = tf.add_paragraph()
        p.text = f"✓ {ach}"
        p.font.size = Pt(11)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_before = Pt(4)

    p = tf.add_paragraph()
    p.text = "Live Platform: https://cu5axikwdfpfurctzwhxtp.streamlit.app/  |  GitHub: https://github.com/SURYAMS002/gcc"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_before = Pt(14)

    output_path = os.path.join(os.path.dirname(__file__), "GCC_Intel_Product_Strategy_Deck.pptx")
    prs.save(output_path)
    print(f"Successfully generated PowerPoint deck at: {output_path}")

if __name__ == "__main__":
    create_deck()
