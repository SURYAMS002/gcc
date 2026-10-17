import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 widescreen dimensions (13.333 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Institutional Executive Palette
    BG_DARK = RGBColor(8, 12, 20)        # #080C14 Deep Terminal Slate
    CARD_BG = RGBColor(14, 22, 38)       # #0E1626 Institutional Card
    ACCENT_CYAN = RGBColor(56, 189, 248) # #38BDF8 Sapphire Accent
    ACCENT_GREEN = RGBColor(16, 185, 129)# #10B981 Emerald
    ACCENT_AMBER = RGBColor(245, 158, 11)# #F59E0B Amber
    TEXT_WHITE = RGBColor(248, 250, 252) # #F8FAFC Heading White
    TEXT_MUTED = RGBColor(148, 163, 184) # #94A3B8 Secondary Text
    BORDER_BLUE = RGBColor(34, 50, 79)   # #22324F Subtle Border

    def apply_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.color.rgb = BG_DARK
        return bg

    def add_header(slide, tag_text, title_text, category="DELIVERABLE 1: PRODUCT STRATEGY DECK"):
        # Category Banner
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.7), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = f"{category}  |  {tag_text}".upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(23)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, title, items, border_color=BORDER_BLUE, header_color=ACCENT_CYAN):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(Inches(left + 0.22), Inches(top + 0.18), Inches(width - 0.44), Inches(height - 0.36))
        tf = tb.text_frame
        tf.word_wrap = True

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = header_color

        for item in items:
            p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_MUTED
            p.space_before = Pt(5)

    # -------------------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    apply_background(s1)

    main_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.0), Inches(11.3), Inches(5.5))
    main_card.fill.solid()
    main_card.fill.fore_color.rgb = CARD_BG
    main_card.line.color.rgb = ACCENT_CYAN
    main_card.line.width = Pt(2)

    tb = s1.shapes.add_textbox(Inches(1.6), Inches(1.5), Inches(10.1), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "FLEXIPLE PRODUCT INTERNSHIP EVALUATION"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p = tf.add_paragraph()
    p.text = "GCC INTEL — PRODUCT STRATEGY DECK"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(10)

    p = tf.add_paragraph()
    p.text = "India's AI-Powered Market Intelligence & Location Advisory Terminal"
    p.font.size = Pt(16)
    p.font.color.rgb = ACCENT_CYAN
    p.space_before = Pt(6)

    p = tf.add_paragraph()
    p.text = "Transforming multi-million dollar enterprise expansion decisions with audited GCC records, real-time OpEx simulation, and zero-hallucination agentic RAG."
    p.font.size = Pt(12.5)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_before = Pt(14)

    p = tf.add_paragraph()
    p.text = "🌐 Live Production Platform: https://cu5axikwdfpfurctzwhxtp.streamlit.app/\n💻 Source Code Repository: https://github.com/SURYAMS002/gcc\n👤 Author: Suryam S  |  Version: v1.0 Production  |  October 2026"
    p.font.size = Pt(10.5)
    p.font.color.rgb = ACCENT_CYAN
    p.space_before = Pt(22)

    # -------------------------------------------------------------------------
    # SLIDE 2: Executive Summary
    # -------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    apply_background(s2)
    add_header(s2, "EXECUTIVE SUMMARY", "Strategic Overview: Empowering Enterprise GCC Decisions")

    add_card(s2, 0.8, 1.65, 3.6, 5.2, "1. The Macro Shift", [
        "India's GCC sector is transitioning from cost-arbitrage support centers to strategic global transformation engines (GCC 4.0).",
        "Over 1,900 operational GCCs employ 1.9M+ professionals and generate $64.6B in direct economic value.",
        "Scaling toward 2,500+ GCCs and $100B+ economic output by 2030.",
        "Average setup involves $15M-$50M+ in capital outlays and multi-year lease commitments."
    ], ACCENT_CYAN, ACCENT_CYAN)

    add_card(s2, 4.8, 1.65, 3.6, 5.2, "2. The Critical Friction", [
        "Strategic leaders navigate fragmented, conflicting reports and opaque real estate broker averages.",
        "Press releases routinely conflate aspirational 5-year targets with actual ground-level operational staff.",
        "Complex state policies (Karnataka 2024, TN 2022, Telangana TS-iPASS) remain locked in state gazettes.",
        "Standard conversational AI models hallucinate office locations, invent salaries, and cite dead links."
    ], ACCENT_AMBER, ACCENT_AMBER)

    add_card(s2, 8.8, 1.65, 3.7, 5.2, "3. The GCC Intel Solution", [
        "Audited Enterprise Registry: 32 verified GCC case files across 5 hubs and 8 industries with 100% verified source provenance.",
        "Location OpEx Modeler: Real-time parametric simulation of Grade-A leases, base engineering payroll, and state grants.",
        "LangGraph Verifiable RAG: Multi-node audit pipeline with FAISS vector retrieval and zero-hallucination abstention.",
        "Production-Ready MVP: Live at cu5axikwdfpfurctzwhxtp.streamlit.app."
    ], ACCENT_GREEN, ACCENT_GREEN)

    # -------------------------------------------------------------------------
    # SLIDE 3: Problem Statement
    # -------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    apply_background(s3)
    add_header(s3, "PROBLEM STATEMENT", "The Enterprise GCC Information Gap: Four Critical Pain Points")

    add_card(s3, 0.8, 1.65, 2.7, 5.2, "1. Blended Real Estate", [
        "Reports quote generic city-wide averages.",
        "Bengaluru ORR (₹125/sqft/mo) vs Electronic City (₹55/sqft/mo) differ by over 120%.",
        "Lease decisions risk multi-crore budget variances without micro-market granularity."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s3, 3.8, 1.65, 2.7, 5.2, "2. Target Inflation", [
        "Corporate PR releases announce 5,000-seat multi-year aspirations.",
        "Actual day-1 operational headcount is often only 300-500 employees.",
        "Distorting competitor intelligence and market capacity assessments."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s3, 6.8, 1.65, 2.7, 5.2, "3. Obscure Subsidies", [
        "State governments offer substantial incentives, but details are buried in gazettes.",
        "Tamil Nadu offers ₹4,000/seat/mo training subsidies.",
        "Telangana TS-iPASS grants statutory 30-day deemed clearances.",
        "Most entrants fail to claim available subsidies due to lack of visibility."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s3, 9.8, 1.65, 2.7, 5.2, "4. LLM Hallucinations", [
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

    add_card(s4, 0.8, 1.65, 3.6, 5.2, "TAM: $4.8 Billion", [
        "Global Corporate Location Intelligence & Expansion Advisory.",
        "Enterprises worldwide spend billions on Big 4 retainers, location strategy, commercial lease consultancy, and talent benchmarking.",
        "Driven by nearshoring and global engineering decentralization."
    ], ACCENT_CYAN, ACCENT_CYAN)

    add_card(s4, 4.8, 1.65, 3.6, 5.2, "SAM: $720 Million", [
        "India-Specific GCC Advisory, EOR Incubation & Strategic Setup.",
        "Over 500 new GCCs projected to enter India between 2024 and 2030.",
        "Each incoming GCC allocates $200k-$1M+ in preliminary feasibility studies, vendor searches, and advisory services."
    ], ACCENT_GREEN, ACCENT_GREEN)

    add_card(s4, 8.8, 1.65, 3.7, 5.2, "SOM: $18 Million (Year 3)", [
        "Capturing 3.5% of annual incoming and expanding mid-market/enterprise GCC advisory workflows.",
        "Monetized via tiered B2B SaaS terminal seats ($5k-$25k/yr) and vendor referral commissions.",
        "Expanding into continuous talent & real estate benchmarking."
    ], ACCENT_AMBER, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 5: Target Customers & Decision-Making Personas
    # -------------------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    apply_background(s5)
    add_header(s5, "TARGET CUSTOMERS", "Multi-Stakeholder B2B Decision-Making Unit")

    add_card(s5, 0.8, 1.65, 2.7, 5.2, "CIO / VP Engineering", [
        "Profile: US/EU tech executives setting up a 150-500 person engineering hub.",
        "Key Need: Validating niche talent depth (AI/ML, Cloud, Quant Finance) and attrition risk.",
        "Value: Instant objective hub comparison without vendor bias."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s5, 3.8, 1.65, 2.7, 5.2, "CRE & Workplace Head", [
        "Profile: Real estate directors budgeting Grade-A office leases across tech corridors.",
        "Key Need: Micro-market rental spreads, vacancy rates, and seat ratio standards (90 sqft/seat).",
        "Value: Rapid parametric modeling of annual lease outlays in INR Cr & USD M."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s5, 6.8, 1.65, 2.7, 5.2, "PE / VC Operating Partner", [
        "Profile: Growth-stage portfolio operations leaders guiding SaaS companies to scale in India.",
        "Key Need: EOR (Employer of Record) vs. Captive entity cost-benefit analysis.",
        "Value: Bypassing $150k consulting fees for early feasibility."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s5, 9.8, 1.65, 2.7, 5.2, "State Investment Agencies", [
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

    add_card(s6, 0.8, 1.65, 3.6, 5.2, "1. Curated Enterprise Registry", [
        "32 Audited GCC Records: Goldman Sachs, Boeing, Walmart, AstraZeneca, Ford, etc.",
        "Granular Attributes: HQ, micro-market address, verified headcount, and expansion signals.",
        "Verification Tiers: Transparent 'Verified Fact', 'Announcement', and 'Estimate' tags.",
        "CSV Export: One-click directory download for offline modeling."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s6, 4.8, 1.65, 3.6, 5.2, "2. Parametric OpEx Modeler", [
        "Calculates Grade-A commercial lease budgets (INR Cr & USD M) using CBRE Q2 2024 rates.",
        "Models base engineering payroll using Michael Page 2024 compensation matrices.",
        "Applies statutory state incentives (TN training grants, Haryana employment subsidies).",
        "Recommends prime micro-markets with rent ranges and vacancy percentages."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s6, 8.8, 1.65, 3.7, 5.2, "3. Verifiable LangGraph Agent", [
        "5-Step Decision Loop: plan_and_search -> calculate -> draft -> verify -> finalize.",
        "FAISS Vector Retrieval: gemini-embedding-2 indexing policy gazettes & market reports.",
        "Strict Grounding: Mandatory primary source citations with working URLs.",
        "Zero-Hallucination Policy: Transparent abstention when verified data is unavailable."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 7: How GCC Intel Is Built (Technical Architecture)
    # -------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    apply_background(s7)
    add_header(s7, "TECHNICAL ARCHITECTURE", "How GCC Intel Is Built: Data Engineering & Agentic Stack")

    add_card(s7, 0.8, 1.65, 3.6, 5.2, "1. Structured Data Layer", [
        "4 Relational JSON Datasets: gcc_records.json (32 GCCs), city_intelligence.json (5 hubs), service_providers.json (8 partners), and sources_registry.json (15 sources).",
        "Strict Schema Validation: Normalized fields for company metadata, micro-markets, and statutory policies.",
        "High-Density Dossiers: Markdown repository compiling sector-specific GCC profiles and government gazettes."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s7, 4.8, 1.65, 3.6, 5.2, "2. Vector Indexing Pipeline", [
        "Embedding Model: gemini-embedding-2 generating 3072-dimensional dense semantic vectors.",
        "FAISS CPU Index: High-speed cosine similarity retrieval with persistent on-disk cache.",
        "1:1 Embedding Generation: Robust sequential chunk encoding ensuring zero multi-part aggregation bugs.",
        "Multi-City Semantic Retrieval: Fetches cross-metro data in under 200ms."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s7, 8.8, 1.65, 3.7, 5.2, "3. LangGraph & AST Engine", [
        "LangGraph StateGraph: Multi-node directed execution graph managing typed state transitions.",
        "Python AST Calculator: Deterministic mathematical expression evaluator preventing hallucinations.",
        "Gemini 3.8 Flash: High-speed, multimodal LLM reasoning engine.",
        "Frontend: Streamlit with responsive Altair charts and custom institutional CSS."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 8: Special Feature 1: Location OpEx & Setup Modeler
    # -------------------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    apply_background(s8)
    add_header(s8, "SPECIAL FEATURE: OPEX MODELER", "Parametric Real Estate, Payroll & Subsidy Simulation")

    add_card(s8, 0.8, 1.65, 3.6, 5.2, "Input Controls", [
        "Target Hub: Bengaluru, Hyderabad, Chennai, Pune, or Gurugram.",
        "Workforce Headcount: Interactive slider from 50 to 1,000 employees.",
        "Specialization: Cloud Engineering, AI/ML, Quant Finance, Embedded Hardware.",
        "Reactive Simulation: Instant recalculation upon any parameter adjustment."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s8, 4.8, 1.65, 3.6, 5.2, "Mathematical Engine", [
        "Floor Space Requirement = Headcount × 90 sq.ft (industry standard).",
        "Commercial Lease Outlay = Space × CBRE Q2 2024 Grade-A Rental Rates × 12.",
        "Base Tech Payroll = Headcount × Michael Page 2024 Market Salary Mean.",
        "Total Annual OpEx = Lease Outlay + Base Payroll - State Subsidies.",
        "Deterministic Math: Computed via Python AST parser to ensure zero calculation errors."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s8, 8.8, 1.65, 3.7, 5.2, "Executive Outputs", [
        "Dual Currency Display: High-contrast metric cards in INR Crores & USD Millions.",
        "Micro-Market Breakdown: Specific rental rates and vacancy percentages (e.g. HITEC City vs Financial District).",
        "State Policy Subsidies: Automatic callout of training subsidies (TN ₹4,000/seat/mo), EPF waivers, and hiring grants.",
        "Decision-Ready: Formatted for investment committee review."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 9: Special Feature 2: Curated GCC Registry & CSV Export
    # -------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    apply_background(s9)
    add_header(s9, "SPECIAL FEATURE: GCC REGISTRY", "32 Audited Enterprise Dossiers with One-Click CSV Export")

    add_card(s9, 0.8, 1.65, 3.6, 5.2, "Curated Enterprise Profiles", [
        "32 Audited Marquee GCCs: Covering BFSI, Tech, Retail, Automotive, Aerospace, and Life Sciences.",
        "Fortune 500 Leaders: Goldman Sachs, Boeing BIETC, JPMorgan, Walmart Global Tech, AstraZeneca, Mercedes-Benz, Ford, etc.",
        "Granular Attributes: HQ, micro-market address, verified headcount, and expansion signals."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s9, 4.8, 1.65, 3.6, 5.2, "Verification Tiers", [
        "Verified Fact (Green Badge): Backed by statutory regulatory filings and official government records.",
        "Company Announcement (Blue Badge): Backed by official executive press releases and verified media releases.",
        "Industry Estimate (Amber Badge): Grounded in NASSCOM, CBRE, and Michael Page benchmark ranges."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s9, 8.8, 1.65, 3.7, 5.2, "Interactive Filtering & CSV Export", [
        "Multi-Attribute Filtering: Search by company keyword, metro hub, industry vertical, or verification tier.",
        "Dual Display Modes: Executive Case Dossier Cards or Master Data Table.",
        "1-Click CSV Export: Instant download of the full 32-record directory for custom enterprise financial modeling."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 10: Special Feature 3: City Intelligence Matrix
    # -------------------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    apply_background(s10)
    add_header(s10, "SPECIAL FEATURE: CITY MATRIX", "Side-by-Side Benchmarking Across 5 Tier-1 Metros")

    add_card(s10, 0.8, 1.65, 3.6, 5.2, "5 Monitored Hubs", [
        "Bengaluru: India's GCC capital with 39.5% market share and deepest AI/ML talent pool.",
        "Hyderabad: Lowest Grade-A vacancy and premier TS-iPASS single-window statutory clearances.",
        "Chennai: SaaS and manufacturing R&D hub with lowest Grade-A office leasing rates.",
        "Pune: Automotive R&D and engineering center near financial capital Mumbai.",
        "Gurugram: North India's premier corporate and fintech hub with highest airport connectivity."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s10, 4.8, 1.65, 3.6, 5.2, "Comparative Dimensions", [
        "Ecosystem Scale: Market share %, active GCC center counts, and total workforce pool.",
        "Grade-A Real Estate: CBRE Q2 2024 monthly rental spreads and micro-market vacancy rates.",
        "Compensation Benchmarks: Junior, Mid, Senior, and Principal salary bands from Michael Page 2024.",
        "State Policies: Specific policy names, departments, and statutory subsidy schedules."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s10, 8.8, 1.65, 3.7, 5.2, "Strategic Trade-offs & AI Synthesis", [
        "Explicit Pros & Cons: Unbiased assessment of infrastructure bottlenecks and talent retention risks.",
        "Recommended Entrant Profile: Tailored fit (e.g. Best for Large Tech Captives vs. Regional Cost-Optimized Centers).",
        "AI Comparative Synthesis: One-click comparative brief generation powered by Gemini 3.8 Flash."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 11: Special Feature 4: LangGraph Research Agent
    # -------------------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    apply_background(s11)
    add_header(s11, "SPECIAL FEATURE: AI AGENT", "Multi-Step Verification with Zero-Hallucination Guardrails")

    add_card(s11, 0.8, 1.65, 3.6, 5.2, "LangGraph 5-Node Workflow", [
        "Node 1: Plan & Vector Search — Query decomposition and FAISS semantic chunk search.",
        "Node 2: AST Benchmark Calculator — Safe evaluation of cost and workforce formulas.",
        "Node 3: Draft Advisory Briefing — Gemini 3.8 Flash synthesizes raw briefing.",
        "Node 4: Market Evidence Verifier — Audits claims against retrieved text chunks.",
        "Node 5: Finalize Answer & Citations — Generates final response with hyperlinks."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s11, 4.8, 1.65, 3.6, 5.2, "Multi-Hop RAG Grounding", [
        "Vector Retrieval: gemini-embedding-2 indexing policy gazettes and real estate market reports.",
        "Working Hyperlinks: Every substantive fact cited with canonical URL.",
        "Pre-Built Strategic Prompts: 1-click execution cards across BFSI, Life Sciences, and State Policies.",
        "Audit Trail: Transparent expandable dropdown displaying retrieved vector chunks and confidence tiers."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s11, 8.8, 1.65, 3.7, 5.2, "Zero-Hallucination Policy", [
        "Traditional LLMs invent answers when data is missing.",
        "GCC Intel enforces automated evidence auditing.",
        "If verified facts are absent, the agent explicitly returns a refusal to speculate.",
        "Protects corporate decision-makers from multi-million dollar bad assumptions."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 12: Special Feature 5: Enablement & Sources Registry
    # -------------------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    apply_background(s12)
    add_header(s12, "SPECIAL FEATURE: PARTNERS & DATA", "Vetted Service Providers & Audited Sources Registry")

    add_card(s12, 0.8, 1.65, 3.6, 5.2, "8 Vetted Service Providers", [
        "Market Entry Strategy: ANSR, Zinnov, EY, PwC.",
        "Legal & Corporate Governance: Shardul Amarchand Mangaldas, Trilegal.",
        "Commercial Real Estate: CBRE, JLL.",
        "Executive Search & Talent: Michael Page.",
        "Employer of Record (EOR) Incubation: Deel, ANSR Workspace."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s12, 4.8, 1.65, 3.6, 5.2, "15 Canonical Sources Tracked", [
        "Industry Authorities: NASSCOM GCC 4.0 Report, Zinnov GCC Landscape 2024.",
        "Real Estate Benchmarks: CBRE India Office Figures Q2 2024.",
        "Salary Matrices: Michael Page India Talent Salary Guide 2024.",
        "State Gazettes: Karnataka GCC Policy 2024, Tamil Nadu R&D Policy 2022, Telangana TS-iPASS."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s12, 8.8, 1.65, 3.7, 5.2, "Data Conflict Resolution Methodology", [
        "Discrepancy Audits: Explicit documentation on why commercial rents differ by micro-market.",
        "Headcount Disambiguation: Separates multi-year target hiring PRs from actual day-1 operational staff.",
        "Confidence Scoring: Continuous data audit cycles ensure fresh, reliable benchmarks."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 13: Competitive Landscape & Market Positioning
    # -------------------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    apply_background(s13)
    add_header(s13, "COMPETITIVE POSITIONING", "The Convergence of Research Depth, Speed & Auditability")

    add_card(s13, 0.8, 1.65, 2.7, 5.2, "Big 4 Consulting", [
        "Players: McKinsey, EY, PwC, BCG.",
        "Pros: Deep custom strategic analysis.",
        "Cons: High cost ($150k-$300k+), slow turnaround (8-12 weeks), static decks.",
        "GCC Intel Difference: 95% faster initial feasibility at 1/10th the cost."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s13, 3.8, 1.65, 2.7, 5.2, "Real Estate Brokers", [
        "Players: CBRE, JLL, Cushman & Wakefield.",
        "Pros: Accurate Grade-A office inventory.",
        "Cons: Biased toward leasing transactions; zero talent or tech stack depth.",
        "GCC Intel Difference: Objective multi-variable modeler combining CRE + talent + policy."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s13, 6.8, 1.65, 2.7, 5.2, "Legacy Analysts", [
        "Players: Gartner, Everest Group, Zinnov.",
        "Pros: Reputable industry reports.",
        "Cons: Static annual PDFs, paywalled, cannot run dynamic parametric queries.",
        "GCC Intel Difference: Interactive software terminal with real-time custom simulation."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s13, 9.8, 1.65, 2.7, 5.2, "Generic AI Models", [
        "Players: ChatGPT, Claude, Perplexity.",
        "Pros: Broad natural language interface.",
        "Cons: Hallucinates addresses, invents salaries, dead links, no math verification.",
        "GCC Intel Difference: Domain-grounded vector database with LangGraph evidence auditing."
    ], BORDER_BLUE, ACCENT_GREEN)

    # -------------------------------------------------------------------------
    # SLIDE 14: Business Model & Monetization Tiers
    # -------------------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    apply_background(s14)
    add_header(s14, "BUSINESS MODEL", "Tiered B2B SaaS Subscriptions & Ecosystem Monetization")

    add_card(s14, 0.8, 1.65, 3.6, 5.2, "Freemium Terminal", [
        "Price: Free (Lead Acquisition Hook).",
        "Includes: Macro ecosystem KPIs, high-level city profiles, and 3 standard AI queries/month.",
        "Purpose: Establish GCC Intel as the default discovery starting point for expanding tech teams."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s14, 4.8, 1.65, 3.6, 5.2, "Professional License", [
        "Price: $499 / user / month (or $4,990 / yr).",
        "Includes: Full access to 32+ audited GCC dossiers, unlimited AI research agent queries, interactive OpEx modeler, and CSV directory export.",
        "Target: Strategy teams, corporate development directors, and mid-market CXOs."
    ], BORDER_BLUE, ACCENT_GREEN)

    add_card(s14, 8.8, 1.65, 3.7, 5.2, "Enterprise Advisory License", [
        "Price: $25,000 / year (Multi-seat).",
        "Includes: Dedicated tenant, custom headcount simulation models, EOR partner RFP module, quarterly dossier updates, and API access.",
        "Plus: Ecosystem referral revenue from vetted EOR providers, real estate firms, and legal counsels."
    ], BORDER_BLUE, ACCENT_AMBER)

    # -------------------------------------------------------------------------
    # SLIDE 15: Strategic Roadmap & Live Production Proof
    # -------------------------------------------------------------------------
    s15 = prs.slides.add_slide(blank_layout)
    apply_background(s15)
    add_header(s15, "ROADMAP & ACCESS", "Production Delivery Status & Strategic Execution Horizon")

    add_card(s15, 0.8, 1.65, 3.6, 5.2, "Current MVP (Ready Now)", [
        "STATUS: LIVE & 100% OPERATIONAL.",
        "Built and launched rapidly as an evaluation-ready institutional terminal.",
        "32 Audited GCC Profiles with primary source citations.",
        "5 Tier-1 Metros comparative intelligence matrix.",
        "Interactive OpEx & Location Setup Modeler.",
        "LangGraph multi-step research agent.",
        "Live on Streamlit Cloud & GitHub."
    ], ACCENT_GREEN, ACCENT_GREEN)

    add_card(s15, 4.8, 1.65, 3.6, 5.2, "Phase 1: Tier-2 Hubs (Months 1-2)", [
        "Expand to Tier-2 Emerging GCC Hubs: Kochi, Ahmedabad, Coimbatore, Chandigarh, Jaipur.",
        "EOR vs. Captive Cost Trade-Off Simulator.",
        "Commercial Real Estate API Integration for live vacancy feeds.",
        "Automated PDF Executive Board Briefing generator."
    ], BORDER_BLUE, ACCENT_CYAN)

    add_card(s15, 8.8, 1.65, 3.7, 5.2, "Phase 2: Enterprise Scale (Months 3-6)", [
        "Real-Time Talent Scraper & Attrition Tracker by micro-market.",
        "Enterprise Multi-Tenant Workspaces with SSO & Team Sharing.",
        "Partner Marketplace & Request-for-Proposal (RFP) Workflow.",
        "REST API & Python SDK for enterprise corporate real estate systems."
    ], BORDER_BLUE, ACCENT_AMBER)

    output_path = os.path.join(os.path.dirname(__file__), "GCC_Intel_Product_Strategy_Deck.pptx")
    prs.save(output_path)
    print(f"Successfully generated PowerPoint deck at: {output_path}")

if __name__ == "__main__":
    create_deck()
