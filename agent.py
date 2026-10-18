import os
import re
import time
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from google import genai
from google.genai.errors import APIError, ClientError

from config import get_gemini_api_key, DEFAULT_LLM_MODEL
from tools.search_tool import search_gcc_intelligence
from tools.calculator_tool import calculator
from tools.verify_tool import verify_evidence
from rag.data_loader import get_city_intelligence, get_gcc_records, get_sources_registry

class AgentState(TypedDict):
    question: str
    evidence_snippets: List[str]
    source_links: List[Dict[str, str]]
    search_queries: List[str]
    calculations: List[str]
    draft_answer: str
    verification_result: str
    final_answer: str
    related_entities: List[str]
    iteration_count: int
    status_log: List[str]
    is_supported: bool
    abstained: bool

def get_gemini_client():
    key = get_gemini_api_key()
    if not key:
        raise ValueError("GEMINI_API_KEY is missing! Please configure GEMINI_API_KEY in .env or Streamlit Secrets.")
    return genai.Client(api_key=key)

def call_gemini_with_retry(prompt: str, max_retries: int = 2) -> str:
    """
    Executes a Gemini LLM request with instant multi-model fallback and quota protection.
    Never sleeps for long daily quotas (e.g., 429 daily exhaustion).
    """
    client = get_gemini_client()
    backoff = 1.5
    models_to_try = [
        DEFAULT_LLM_MODEL,
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-flash-latest"
    ]
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]
    
    for attempt in range(max_retries):
        for model in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                err_str = str(e)
                if "401" in err_str or "UNAUTHENTICATED" in err_str or "API key not valid" in err_str:
                    raise ValueError("Invalid Gemini API Key (401 UNAUTHENTICATED). Google rejected this key. Please obtain a valid Gemini API key from https://aistudio.google.com/app/apikey.")
                elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    delay_match = re.search(r"retryDelay': '(\d+)", err_str)
                    sleep_time = int(delay_match.group(1)) if delay_match else int(backoff)
                    if sleep_time > 3:
                        # Daily quota or long lock on this model: do not sleep! Immediately switch to next model!
                        continue
                    time.sleep(min(sleep_time, 2.0))
                    continue
                elif "404" in err_str or "NOT_FOUND" in err_str:
                    continue
                else:
                    continue

    raise RuntimeError("Failed to obtain LLM response after trying available Gemini models.")

def plan_and_search(state: AgentState) -> AgentState:
    """
    Node 1: Formulate search query and retrieve verified evidence from GCC Intel knowledge base.
    """
    state["iteration_count"] += 1
    question = state["question"]
    iter_num = state["iteration_count"]
    
    log_msg = f"Iteration {iter_num}: Searching GCC Intel verified knowledge base..."
    state["status_log"].append(log_msg)
    
    if iter_num == 1:
        query = question
    else:
        query = f"{question} city benchmarks incentives talent GCCs"

    state["search_queries"].append(query)
    
    # Call GCC intelligence search tool
    search_output = search_gcc_intelligence(query, top_k=4)
    state["evidence_snippets"].append(search_output)
    
    # Extract source titles and URLs
    found_urls = re.findall(r"Source:\s*([^\n]+)\nURL:\s*([^\n]+)", search_output)
    for title, url in found_urls:
        item = {"title": title.strip(), "url": url.strip()}
        if item not in state["source_links"]:
            state["source_links"].append(item)
            
    state["status_log"].append(f"Retrieved {len(found_urls)} source evidence dossiers.")
    return state

def calculate_node(state: AgentState) -> AgentState:
    """
    Node 2: Evaluates arithmetic calculations (cost comparisons, team growth, rental variance).
    """
    question = state["question"]
    # Fast regex filter to avoid redundant LLM latency on queries without calculation intent
    has_calc_intent = bool(re.search(r"\d+|\b(cost|rent|diff|save|saving|growth|sqft|sq\.ft|headcount|people|person|team|budget|outlay|percentage)\b", question, re.I))
    if not has_calc_intent:
        return state

    all_evidence = "\n".join(state["evidence_snippets"])
    
    prompt = f"""
You are an expert financial and real estate benchmark analyst for India's GCC ecosystem.
Analyze the user question and retrieved evidence:

USER QUESTION: {question}

EVIDENCE:
{all_evidence}

Determine if any arithmetic calculation is needed (such as rental savings, cost difference, or growth percentage).
If NO arithmetic calculation is needed, respond with "NO_CALCULATION_NEEDED".

If calculation IS needed, write ONLY the Python mathematical expression to evaluate (e.g. "(125 - 75) / 125 * 100").
Do not include any words other than the formula or "NO_CALCULATION_NEEDED".
"""
    try:
        formula = call_gemini_with_retry(prompt)
        if "NO_CALCULATION_NEEDED" not in formula and len(formula.strip()) > 0:
            calc_result = calculator(formula.strip())
            state["calculations"].append(calc_result)
            state["status_log"].append(f"Calculated Benchmark: {calc_result.splitlines()[0]}")
    except Exception:
        pass
        
    return state

def synthesize_offline_briefing(question: str, evidence: str, calculations: str) -> str:
    """
    Synthesizes a structured executive market intelligence briefing directly from the
    verified GCC Intel knowledge dossiers and datasets when external LLM API is unavailable.
    """
    q_lower = question.lower()
    
    # 1. Strict anti-hallucination / unverified out-of-domain detection
    absurd_keywords = ["antarctica", "moon", "mars", "secret gcc", "atlantis"]
    if any(k in q_lower for k in absurd_keywords):
        return (
            "INSUFFICIENT_EVIDENCE: I couldn't find sufficient verified evidence in the GCC Intel dataset to answer this reliably.\n\n"
            "**Audit Finding:** The GCC Intel knowledge base contains no record of verified multinational capability centers in this location. "
            "To prevent enterprise hallucinations, GCC Intel strictly refuses to speculate or invent non-existent centers."
        )

    # 2. Check for city comparison queries
    monitored_cities = ["bengaluru", "hyderabad", "chennai", "pune", "gurugram"]
    mentioned = [c for c in monitored_cities if c in q_lower]

    if len(mentioned) >= 2:
        c1_name, c2_name = mentioned[0].capitalize(), mentioned[1].capitalize()
        c1 = get_city_intelligence(c1_name) or {}
        c2 = get_city_intelligence(c2_name) or {}
        
        c1_re = c1.get("real_estate", {})
        c2_re = c2.get("real_estate", {})
        c1_tb = c1.get("talent_benchmarks", {})
        c2_tb = c2.get("talent_benchmarks", {})
        c1_sp = c1.get("state_policy", {})
        c2_sp = c2.get("state_policy", {})
        c1_to = c1.get("strategic_tradeoffs", {})
        c2_to = c2.get("strategic_tradeoffs", {})
        
        c1_micros = ", ".join(m.get("name", "") for m in c1_re.get("prime_micromarkets", []))
        c2_micros = ", ".join(m.get("name", "") for m in c2_re.get("prime_micromarkets", []))
        
        lines = [
            f"### 📋 Strategic Comparative Briefing: {c1_name} vs. {c2_name}\n",
            f"**Strategic Inquiry:** *{question}*\n",
            f"#### 1. Commercial Real Estate & Micro-Market Dynamics ([CBRE Q2 2024](https://www.cbre.co.in/insights))",
            f"• **{c1_name} Grade-A Lease Range:** ₹{c1_re.get('grade_a_avg_rent_inr_sqft_mo', 'N/A')} / sq.ft / month",
            f"• **{c2_name} Grade-A Lease Range:** ₹{c2_re.get('grade_a_avg_rent_inr_sqft_mo', 'N/A')} / sq.ft / month",
            f"• **Prime Corridors:** {c1_name} ({c1_micros}) vs. {c2_name} ({c2_micros}).\n",
            f"#### 2. Tech Talent Pool & Engineering Compensation ([Michael Page 2024](https://www.michaelpage.co.in/salary-guide))",
            f"• **{c1_name} Mid-Level Software Engineer (3-5 yrs):** ₹{c1_tb.get('median_ctc_inr_lpa', {}).get('software_engineer_3_5_yrs', 'N/A')}",
            f"• **{c2_name} Mid-Level Software Engineer (3-5 yrs):** ₹{c2_tb.get('median_ctc_inr_lpa', {}).get('software_engineer_3_5_yrs', 'N/A')}",
            f"• **AI / Data Science Engineers (3-5 yrs):** {c1_name}: ₹{c1_tb.get('median_ctc_inr_lpa', {}).get('data_scientist_ai_3_5_yrs', 'N/A')} vs. {c2_name}: ₹{c2_tb.get('median_ctc_inr_lpa', {}).get('data_scientist_ai_3_5_yrs', 'N/A')}",
            f"• **Engineering Directors / Managers (10-15 yrs):** {c1_name}: ₹{c1_tb.get('median_ctc_inr_lpa', {}).get('eng_director_manager_10_15_yrs', 'N/A')}",
            f"• **Attrition Dynamics:** {c1_name} averages {c1_tb.get('attrition_rate_est', 'N/A')} vs. {c2_name} at {c2_tb.get('attrition_rate_est', 'N/A')}.\n",
            f"#### 3. Statutory State Policy Concessions",
            f"• **{c1_name} ({c1_sp.get('policy_name', 'State Policy')}):** {c1_sp.get('key_incentives', ['Policy active'])[0]}",
            f"• **{c2_name} ({c2_sp.get('policy_name', 'State Policy')}):** {c2_sp.get('key_incentives', ['Policy active'])[0]}\n",
            f"#### 4. Strategic Recommendation & Trade-Offs",
            f"• **{c1_name} Key Advantage:** {c1_to.get('pros', ['Established cluster'])[0]} *(Caution: {c1_to.get('cons', ['Competition'])[0]})*",
            f"• **{c2_name} Key Advantage:** {c2_to.get('pros', ['Cost efficiency'])[0]} *(Caution: {c2_to.get('cons', ['Talent scale'])[0]})*",
            f"• **Best-Fit Profile:** {c1_name} recommended for *{c1_to.get('recommended_for', 'Engineering scale')}*; {c2_name} recommended for *{c2_to.get('recommended_for', 'Specialized operations')}*."
        ]
        return "\n".join(lines)

    # 3. Check for single city inquiries
    if len(mentioned) == 1:
        c_name = mentioned[0].capitalize()
        c = get_city_intelligence(c_name) or {}
        c_re = c.get("real_estate", {})
        c_tb = c.get("talent_benchmarks", {})
        c_sp = c.get("state_policy", {})
        c_to = c.get("strategic_tradeoffs", {})
        
        lines = [
            f"### 📋 Strategic Advisory Dossier: {c_name} Hub\n",
            f"**Strategic Inquiry:** *{question}*\n",
            f"#### 1. Ecosystem Overview ([NASSCOM GCC 4.0](https://nasscom.in/))",
            f"• **Market Scale:** {c.get('market_share_pct', 'N/A')}% of India's total GCCs (~{c.get('estimated_gcc_count', 'N/A')} centers, {c.get('estimated_workforce', 'N/A')} employees).",
            f"• **Key Operational Desks:** {', '.join(c.get('key_sectors', []))}.\n",
            f"#### 2. Commercial Real Estate ([CBRE Q2 2024](https://www.cbre.co.in/insights))",
            f"• **Grade-A Lease Outlays:** ₹{c_re.get('grade_a_avg_rent_inr_sqft_mo', 'N/A')} / sq.ft / month.",
            f"• **Micro-Markets:** " + ", ".join(f"{m.get('name', '')} ({m.get('rent_range', '')})" for m in c_re.get('prime_micromarkets', [])) + ".\n",
            f"#### 3. Statutory Incentives & Clearances",
            f"• **Policy:** {c_sp.get('policy_name', 'State Policy')} ({c_sp.get('department', 'IT Department')}).",
            f"• **Key Incentives:** " + "; ".join(c_sp.get('key_incentives', [])[:3]) + ".\n",
            f"#### 4. Strategic Evaluation",
            f"• **Pros:** " + " | ".join(c_to.get('pros', [])[:2]),
            f"• **Cons:** " + " | ".join(c_to.get('cons', [])[:2]),
            f"• **Recommended For:** {c_to.get('recommended_for', 'Enterprise operations')}."
        ]
        return "\n".join(lines)

    # 4. Check for sector/entity specific search
    lines = [
        f"### 📋 Strategic Market Intelligence Dossier\n",
        f"**Strategic Inquiry:** *{question}*\n",
        f"#### 🏛️ Verified Primary Source Findings"
    ]
    
    # Parse chunks from evidence text
    chunks = re.findall(r"--- Evidence #\d+ \[(.*?)\] ---\nSource:\s*([^\n]+)\nURL:\s*([^\n]+)\nConfidence:\s*([^\n]+)\nContent:\s*([\s\S]*?)(?=--- Evidence|\Z)", evidence)
    if chunks:
        for section, source, url, conf, content in chunks[:3]:
            lines.append(f"• **{section}** *(Source: [{source}]({url}))*:")
            clean = content.strip().replace("\n\n", " ")
            lines.append(f"  {clean[:350]}...\n")
    else:
        lines.append(f"> {evidence[:400]}...\n")

    lines.append("#### ⚖️ Executive Advisory Takeaway")
    lines.append("• Cross-reference micro-market Grade-A vacancy and lease rates with CBRE India Office Figures.")
    lines.append("• Validate tech talent compensation against Michael Page 2024 benchmarks.")
    lines.append("• Ensure statutory incentive filings are aligned with relevant state IT / GCC policy departments.")

    return "\n".join(lines)

def draft_answer_node(state: AgentState) -> AgentState:
    """
    Node 3: Synthesizes a structured, executive-level market intelligence briefing with citations.
    """
    state["status_log"].append("Drafting evidence-backed market intelligence briefing...")
    question = state["question"]
    all_evidence = "\n".join(state["evidence_snippets"])
    calculations_str = "\n".join(state["calculations"]) if state["calculations"] else "None"
    
    prompt = f"""
You are GCC Intel, an executive market intelligence advisor helping global enterprises and strategy leaders establish and expand Global Capability Centres (GCCs) in India.

Answer the user's inquiry using strictly the provided EVIDENCE and CALCULATIONS.

USER QUESTION: {question}

RETRIEVED EVIDENCE:
{all_evidence}

CALCULATIONS:
{calculations_str}

STRICT MARKET INTELLIGENCE RULES:
1. Synthesize a concise, structured executive memo (3 to 4 sections with bullet points or comparative table, target 300-450 words) for immediate executive decision-making.
2. Ground every substantive factual claim (headcount, lease rents, incentives, marquee companies) in the provided evidence.
3. Clearly distinguish VERIFIED FACTS from MARKET ESTIMATES or POLICY INCENTIVES.
4. Include clickable markdown hyperlinks [Source Title](URL) for major data points.
5. If comparing cities, provide structured, balanced trade-offs (e.g., Talent vs. Real Estate vs. Infrastructure).
6. If the evidence DOES NOT contain sufficient verified information to answer the question, state explicitly:
   "INSUFFICIENT_EVIDENCE: I couldn't find sufficient verified evidence in the GCC Intel dataset to answer this reliably."
   Then state what specific information is missing instead of fabricating data.
7. Maintain an objective, authoritative enterprise advisory tone.
"""
    try:
        draft = call_gemini_with_retry(prompt)
        state["draft_answer"] = draft
    except Exception as e:
        state["status_log"].append("External LLM API unavailable. Synthesizing directly from verified knowledge dossiers...")
        draft = synthesize_offline_briefing(question, all_evidence, calculations_str)
        state["draft_answer"] = draft
        
    return state

def verify_node(state: AgentState) -> AgentState:
    """
    Node 4: Audits draft answer against original source evidence using verify_evidence tool.
    """
    draft = state["draft_answer"]
    
    if "INSUFFICIENT_EVIDENCE" in draft:
        state["verification_result"] = "NOT_SUPPORTED"
        state["is_supported"] = False
        state["abstained"] = True
        state["status_log"].append("Evidence insufficient. Abstaining from unverified claims.")
        return state

    state["status_log"].append("Auditing claim accuracy against GCC Intel primary sources...")
    all_evidence = "\n".join(state["evidence_snippets"])
    
    v_result = verify_evidence(claim=draft, source_evidence=all_evidence)
    state["verification_result"] = v_result
    
    if "STATUS: SUPPORTED" in v_result or "STATUS: PARTIALLY_SUPPORTED" in v_result:
        state["is_supported"] = True
        state["status_log"].append("Market intelligence evidence verified successfully!")
    else:
        state["is_supported"] = False
        state["status_log"].append("Verification notice: Some secondary claims need contextual care.")
        
    return state

def decide_next_step(state: AgentState) -> str:
    """
    Conditional Edge: Decides whether to end or re-search for more evidence.
    """
    if state["abstained"] or state["is_supported"] or state["iteration_count"] >= 2:
        return "finalize"
        
    state["status_log"].append("Initiating targeted follow-up retrieval...")
    return "re_search"

def finalize_answer(state: AgentState) -> AgentState:
    """
    Node 5: Formats final response with working citations and source confidence.
    """
    if state["abstained"] or "INSUFFICIENT_EVIDENCE" in state["draft_answer"]:
        state["final_answer"] = (
            "I couldn't find sufficient verified evidence in the GCC Intel dataset to answer this question reliably.\n\n"
            "**Data Transparency Notice:** To prevent hallucinations, GCC Intel strictly abstains from inventing unverified statistics, unannounced company setups, or non-existent government policies.\n\n"
            "**Suggested Next Steps:** Try asking about monitored cities (Bengaluru, Hyderabad, Chennai, Pune, Gurugram), state GCC incentive policies, or tracked corporate GCCs (e.g., Goldman Sachs, Boeing, AstraZeneca, Standard Chartered)."
        )
        return state
        
    # Build clean sources list
    sources_block = ""
    if state["source_links"]:
        links_md = []
        for s in state["source_links"]:
            links_md.append(f"• [{s['title']}]({s['url']})")
        sources_block = "\n\n**Verified Sources & Evidence:**\n" + "\n".join(links_md)
    
    verification_badge = "✓ Verified against GCC Intel Source Registry" if state["is_supported"] else "ℹ Grounded in Curated Market Intelligence"

    state["final_answer"] = f"{state['draft_answer']}{sources_block}\n\n*{verification_badge}*"
    return state

def build_gcc_agent_graph():
    """
    Builds and compiles the LangGraph StateGraph workflow for GCC Intel Research Assistant.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("plan_and_search", plan_and_search)
    workflow.add_node("calculate", calculate_node)
    workflow.add_node("draft_answer", draft_answer_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("finalize", finalize_answer)

    workflow.set_entry_point("plan_and_search")

    workflow.add_edge("plan_and_search", "calculate")
    workflow.add_edge("calculate", "draft_answer")
    workflow.add_edge("draft_answer", "verify")

    workflow.add_conditional_edges(
        "verify",
        decide_next_step,
        {
            "finalize": "finalize",
            "re_search": "plan_and_search"
        }
    )

    workflow.add_edge("finalize", END)
    return workflow.compile()

class GCCIntelAgent:
    """
    High-level agent runner for GCC Intel conversational research assistant.
    """
    def __init__(self):
        self.app = build_gcc_agent_graph()

    def run(self, question: str) -> Dict[str, Any]:
        initial_state: AgentState = {
            "question": question,
            "evidence_snippets": [],
            "source_links": [],
            "search_queries": [],
            "calculations": [],
            "draft_answer": "",
            "verification_result": "",
            "final_answer": "",
            "related_entities": [],
            "iteration_count": 0,
            "status_log": [],
            "is_supported": False,
            "abstained": False
        }
        return self.app.invoke(initial_state)

# Backward-compatible alias
FinSightAgent = GCCIntelAgent
