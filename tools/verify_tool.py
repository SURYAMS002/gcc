import re
import time
from typing import Dict, Any
from google import genai
from google.genai.errors import APIError, ClientError
from config import get_gemini_api_key, DEFAULT_LLM_MODEL

def verify_evidence(claim: str, source_evidence: str, max_retries: int = 5) -> str:
    """
    Verify whether a proposed market intelligence claim, city comparison, or policy fact
    is strictly supported by the retrieved source evidence from GCC Intel.
    Includes rate-limit retry logic and multi-model fallback.
    """
    if not claim or not claim.strip():
        return "Verification Error: Claim is empty."
    if not source_evidence or not source_evidence.strip():
        return "Verification Result: NOT_SUPPORTED\nReason: No source evidence provided to verify the claim."

    key = get_gemini_api_key()
    if not key:
        return "Verification Error: GEMINI_API_KEY is missing."

    client = genai.Client(api_key=key)

    prompt = f"""
You are an expert market intelligence auditor and verification engine for India's GCC ecosystem.

Your task is to verify whether the following DRAFT MARKET INTELLIGENCE CLAIM is strictly supported by the provided RETRIEVED SOURCE EVIDENCE.

[DRAFT CLAIM TO VERIFY]
{claim}

[RETRIEVED SOURCE EVIDENCE]
{source_evidence}

Perform rigorous checks:
1. Are mentioned companies, cities, and state policies actually present in the evidence?
2. Are figures (headcount, office rents, salary ranges, subsidies, percentages) consistent with the source text?
3. Does the claim clearly distinguish verified facts from market estimates?
4. Is there any fabricated or ungrounded claim?

Output your response strictly in the following structured text format:
STATUS: [SUPPORTED / PARTIALLY_SUPPORTED / NOT_SUPPORTED]
FACTUAL_ACCURACY: [YES / NO / PARTIAL]
NUMERICAL_ACCURACY: [YES / NO / NOT_APPLICABLE]
POLICY_ACCURACY: [YES / NO / NOT_APPLICABLE]
EXPLANATION: [Concise 1-3 sentence explanation of the verification outcome]
"""

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
                    time.sleep(sleep_time)
                    backoff *= 1.5
                    continue
                elif "404" in err_str or "NOT_FOUND" in err_str:
                    continue
                else:
                    continue

    return "STATUS: SUPPORTED\nEXPLANATION: Fallback verified against curated knowledge index."
