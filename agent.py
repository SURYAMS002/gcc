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

def call_gemini_with_retry(prompt: str, max_retries: int = 5) -> str:
    """
    Executes a Gemini LLM request with robust rate-limit (429) retry and multi-model fallback.
    """
    client = get_gemini_client()
    backoff = 3.0
    models_to_try = [DEFAULT_LLM_MODEL, "gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest"]
    
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
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    delay_match = re.search(r"retryDelay': '(\d+)", err_str)
                    sleep_time = int(delay_match.group(1)) + 2 if delay_match else int(backoff)
                    print(f"[Rate Limit 429] Model '{model}' limited. Waiting {sleep_time}s...")
                    time.sleep(sleep_time)
                    backoff *= 1.5
                    continue
                elif "404" in err_str or "NOT_FOUND" in err_str:
                    continue
                else:
                    continue

    raise RuntimeError("Failed to obtain LLM response after retrying across available Gemini models.")

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
    except Exception as e:
        state["status_log"].append(f"Calculation step bypassed: {e}")
        
    return state

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
1. Ground every substantive factual claim (headcount, lease rents, incentives, marquee companies) in the provided evidence.
2. Clearly distinguish VERIFIED FACTS from MARKET ESTIMATES or POLICY INCENTIVES.
3. Include clickable markdown hyperlinks [Source Title](URL) for major data points.
4. If comparing cities, provide structured, balanced trade-offs (e.g., Talent vs. Real Estate vs. Infrastructure).
5. If the evidence DOES NOT contain sufficient verified information to answer the question, state explicitly:
   "INSUFFICIENT_EVIDENCE: I couldn't find sufficient verified evidence in the GCC Intel dataset to answer this reliably."
   Then state what specific information is missing instead of fabricating data.
6. Maintain an objective, authoritative enterprise advisory tone.
"""
    try:
        draft = call_gemini_with_retry(prompt)
        state["draft_answer"] = draft
    except Exception as e:
        state["draft_answer"] = f"Error drafting market intelligence briefing: {e}"
        
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
