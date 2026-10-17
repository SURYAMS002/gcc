import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.data_loader import (
    get_gcc_records, 
    get_city_intelligence, 
    get_service_providers, 
    get_sources_registry, 
    get_ecosystem_kpis
)
from rag.knowledge_indexer import build_or_load_gcc_index
from tools.calculator_tool import safe_eval_expr, calculator
from tools.search_tool import search_gcc_intelligence
from agent import GCCIntelAgent

class TestGCCIntelPlatform(unittest.TestCase):
    """
    Automated test suite verifying the integrity of GCC Intel data, retrieval, tools, and agent.
    """

    def test_gcc_records_integrity(self):
        records = get_gcc_records()
        self.assertGreaterEqual(len(records), 25, "Should have at least 25 curated GCC records")
        
        required_fields = [
            "id", "company_name", "parent_company", "global_headquarters",
            "city", "state", "industry", "business_functions",
            "establishment_year", "headcount", "headcount_type",
            "recent_announcement", "source_url", "verification_status"
        ]

        cities_found = set()
        for r in records:
            for field in required_fields:
                self.assertIn(field, r, f"Record {r.get('id')} missing field {field}")
            self.assertTrue(r["source_url"].startswith("http"), f"Invalid source URL in {r['id']}")
            self.assertIn(r["verification_status"], ["Verified Fact", "Company Announcement", "Industry Estimate"])
            cities_found.add(r["city"])

        self.assertTrue({"Bengaluru", "Hyderabad", "Chennai", "Pune", "Gurugram"}.issubset(cities_found),
                        "Dataset should cover all 5 monitored tech hubs")

    def test_city_intelligence_integrity(self):
        cities = get_city_intelligence()
        self.assertEqual(len(cities), 5, "Should monitor exactly 5 Tier-1 cities")
        city_names = [c["name"] for c in cities]
        self.assertIn("Bengaluru", city_names)
        self.assertIn("Hyderabad", city_names)
        self.assertIn("Chennai", city_names)
        self.assertIn("Pune", city_names)
        self.assertIn("Gurugram", city_names)

        for c in cities:
            self.assertIn("real_estate", c)
            self.assertIn("grade_a_avg_rent_inr_sqft_mo", c["real_estate"])
            self.assertIn("talent_benchmarks", c)
            self.assertIn("state_policy", c)
            self.assertIn("strategic_tradeoffs", c)

    def test_service_providers_integrity(self):
        providers = get_service_providers()
        self.assertGreaterEqual(len(providers), 5, "Should have at least 5 vetted service providers")
        categories = {p["category"] for p in providers}
        self.assertIn("Strategy & Market-Entry Consulting", categories)
        self.assertIn("Commercial Real Estate", categories)
        self.assertIn("Legal & Regulatory Services", categories)

    def test_sources_registry(self):
        sources = get_sources_registry()
        self.assertGreaterEqual(len(sources), 10, "Should have at least 10 canonical sources")
        for s in sources:
            self.assertTrue(s["url"].startswith("http"))
            self.assertIn("publisher", s)

    def test_calculator_tool(self):
        # Test safe AST evaluation
        res = safe_eval_expr("(125 - 75) / 125 * 100")
        self.assertAlmostEqual(res, 40.0, places=1)
        
        # Test calculator formatting
        out = calculator("(125 - 75) / 125 * 100")
        self.assertIn("40", out)

    def test_vector_search_retrieval(self):
        store = build_or_load_gcc_index()
        self.assertGreater(store.index.ntotal, 10, "Index should contain at least 10 embeddings")
        
        results = store.search("Tamil Nadu state incentives", top_k=2)
        self.assertGreater(len(results), 0)
        top_text = results[0]["text"].lower()
        self.assertTrue("tamil nadu" in top_text or "incentive" in top_text)

    def test_agent_abstention_on_unsupported_query(self):
        agent = GCCIntelAgent()
        # Query asking for completely fictitious or unsupported claim
        res = agent.run("What is the top secret Martian GCC established by Acme Rockets?")
        self.assertTrue(res["abstained"] or "INSUFFICIENT_EVIDENCE" in res["draft_answer"] or "couldn't find sufficient verified evidence" in res["final_answer"],
                        "Agent must strictly abstain from hallucinating unverified facts")

if __name__ == "__main__":
    unittest.main()
