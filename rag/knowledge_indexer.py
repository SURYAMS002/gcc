import os
import re
import json
from typing import List, Dict, Any, Optional
from rag.vector_store import FAISSVectorStore
from rag.data_loader import get_gcc_records, get_city_intelligence, get_service_providers, get_sources_registry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_INDEX_DIR = os.path.join(BASE_DIR, "faiss_gcc_store")

def generate_knowledge_chunks() -> List[Dict[str, Any]]:
    """
    Constructs high-density chunks with rich metadata from:
    1. gcc_knowledge_dossiers.md
    2. city_intelligence.json
    3. gcc_records.json
    4. service_providers.json
    """
    chunks = []
    chunk_counter = 1

    # 1. Ingest Dossiers from markdown
    dossier_path = os.path.join(DATA_DIR, "gcc_knowledge_dossiers.md")
    if os.path.exists(dossier_path):
        with open(dossier_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by "## Dossier"
        sections = re.split(r"(?=## Dossier)", content)
        for sec in sections:
            sec_clean = sec.strip()
            # Ignore tiny headers or empty preamble
            if len(sec_clean) < 80 or not sec_clean.startswith("## Dossier"):
                continue

            # Extract title and source info
            lines = sec_clean.split("\n")
            title = lines[0].replace("##", "").strip()
            
            # Find source URL if present
            url_match = re.search(r"URL:\s*([^\s\]]+)", sec_clean)
            source_url = url_match.group(1) if url_match else "https://nasscom.in/"
            
            source_label_match = re.search(r"\[Source:\s*([^|\]]+)", sec_clean)
            source_label = source_label_match.group(1).strip() if source_label_match else "GCC Intel Research Dossier"

            chunks.append({
                "chunk_id": f"DOSSIER-{chunk_counter:03d}",
                "page": chunk_counter,
                "source": source_label,
                "source_url": source_url,
                "section": title,
                "category": "Market Dossier",
                "verification_status": "Verified Benchmark",
                "text": sec_clean
            })
            chunk_counter += 1

    # 2. Ingest City Intelligence profiles
    cities = get_city_intelligence()
    for c in cities:
        city_name = c["name"]
        state = c["state"]
        rent_range = c["real_estate"]["grade_a_avg_rent_inr_sqft_mo"]
        micros = ", ".join([f"{m['name']} ({m['rent_range']})" for m in c["real_estate"]["prime_micromarkets"]])
        salaries = ", ".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in c["talent_benchmarks"]["median_ctc_inr_lpa"].items()])
        incentives = " | ".join(c["state_policy"]["key_incentives"])
        pros = "; ".join(c["strategic_tradeoffs"]["pros"])
        cons = "; ".join(c["strategic_tradeoffs"]["cons"])
        rec = c["strategic_tradeoffs"]["recommended_for"]

        text_block = f"""
CITY PROFILE & GCC BENCHMARK: {city_name}, {state} ({c['tier']})
- Ecosystem Tagline: {c['tagline']}
- Market Share: {c['market_share_pct']}% of India's GCCs | Estimated GCC Count: {c['estimated_gcc_count']} | Tech Workforce: {c['estimated_workforce']}
- Dominant Sectors: {', '.join(c['key_sectors'])}
- Marquee GCCs: {', '.join(c['marquee_gccs'])}
- Commercial Grade-A Lease Rentals: INR {rent_range}/sq.ft/month. Key micro-markets: {micros}
- Talent Salary Benchmarks: {salaries} (Attrition: {c['talent_benchmarks']['attrition_rate_est']})
- Premier Academic Institutes: {', '.join(c['talent_benchmarks']['premier_institutions'])}
- State Policy: {c['state_policy']['policy_name']} ({c['state_policy']['department']})
- Key Policy Incentives: {incentives}
- Infrastructure: Airport: {c['infrastructure']['airport']}. Metro: {c['infrastructure']['metro']}. Power: {c['infrastructure']['power_reliability']}.
- Strategic Advantages (Pros): {pros}
- Strategic Trade-offs (Cons): {cons}
- Recommended For: {rec}
Source: {c['real_estate']['source_label']} & {c['state_policy']['policy_name']}
        """.strip()

        chunks.append({
            "chunk_id": f"CITY-{c['id'].upper()}",
            "page": chunk_counter,
            "source": f"{city_name} City Intelligence Brief",
            "source_url": c.get("state_policy", {}).get("source_id", "https://nasscom.in/"),
            "section": f"{city_name} GCC Ecosystem & Benchmarks",
            "category": "City Intelligence",
            "verification_status": "Verified Policy & Market Range",
            "text": text_block
        })
        chunk_counter += 1

    # 3. Ingest GCC Company Records (grouped by city & sector for high-density context)
    gcc_records = get_gcc_records()
    # Group by city
    city_gcc_map = {}
    for g in gcc_records:
        city = g["city"]
        city_gcc_map.setdefault(city, []).append(g)

    for city, records in city_gcc_map.items():
        gcc_summaries = []
        for r in records:
            gcc_summaries.append(
                f"• {r['company_name']} (HQ: {r['global_headquarters']}) | Industry: {r['industry']} | Est: {r['establishment_year']} | "
                f"Headcount: {r['headcount']} ({r['headcount_type']}) | Functions: {', '.join(r['business_functions'])} | "
                f"Recent Expansion: {r['recent_announcement']} [Source: {r['source_title']} ({r['source_url']})]"
            )

        text_block = f"MAJOR GCCs IN {city.upper()} ({len(records)} verified centres):\n" + "\n".join(gcc_summaries)

        chunks.append({
            "chunk_id": f"GCCS-{city.upper()}",
            "page": chunk_counter,
            "source": f"Curated GCC Directory - {city}",
            "source_url": records[0]["source_url"] if records else "https://nasscom.in/",
            "section": f"GCCs Operating in {city}",
            "category": "GCC Profiles",
            "verification_status": "Verified Corporate Disclosure",
            "text": text_block
        })
        chunk_counter += 1

    # 4. Ingest Service Providers
    providers = get_service_providers()
    provider_lines = []
    for sp in providers:
        provider_lines.append(
            f"• {sp['name']} ({sp['category']} - {sp['sub_category']}): HQ: {sp['headquarters']}, Serving: {', '.join(sp['locations_served'])}. "
            f"Services: {', '.join(sp['services_offered'])}. Track Record: {sp['documented_track_record']} [URL: {sp['source_url']}]"
        )

    text_block = "GCC ENABLEMENT SERVICE PROVIDERS & ADVISORY DIRECTORY:\n" + "\n".join(provider_lines)
    chunks.append({
        "chunk_id": "SERVICE-PROVIDERS-ALL",
        "page": chunk_counter,
        "source": "GCC Intel Ecosystem Partners Directory",
        "source_url": "https://ansr.com/",
        "section": "Service Providers, EOR & Advisory Partners",
        "category": "Service Providers",
        "verification_status": "Verified Partner Profile",
        "text": text_block
    })

    return chunks

def build_or_load_gcc_index(
    index_dir: str = DEFAULT_INDEX_DIR,
    force_rebuild: bool = False
) -> FAISSVectorStore:
    """
    Builds or loads the FAISS vector index for GCC Intel.
    """
    store = FAISSVectorStore()

    if not force_rebuild and store.load(index_dir):
        return store

    print("[Building GCC Intel Vector Index] Generating knowledge chunks...")
    chunks = generate_knowledge_chunks()
    print(f"[OK] Prepared {len(chunks)} high-density knowledge chunks.")

    print("Generating vector embeddings via Gemini embedding-2...")
    store.build_from_chunks(chunks, batch_size=20)
    store.save(index_dir)
    print(f"[OK] GCC Intel FAISS index successfully built and saved to '{index_dir}'.")

    return store
