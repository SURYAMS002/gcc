import os
import json
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def _load_json(filename: str) -> Any:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_gcc_records(
    search_query: Optional[str] = None,
    city: Optional[str] = None,
    industry: Optional[str] = None,
    function: Optional[str] = None,
    verification_status: Optional[str] = None,
    sort_by: str = "company_name",
    sort_ascending: bool = True
) -> List[Dict[str, Any]]:
    """
    Returns curated, verified GCC records with flexible search, filtering, and sorting.
    """
    records = _load_json("gcc_records.json")
    if not isinstance(records, list):
        return []

    filtered = []
    q = search_query.lower().strip() if search_query else None

    for r in records:
        # Search query across company name, parent, city, industry, functions, and announcements
        if q:
            match_name = q in r.get("company_name", "").lower()
            match_parent = q in r.get("parent_company", "").lower()
            match_city = q in r.get("city", "").lower()
            match_ind = q in r.get("industry", "").lower()
            match_func = any(q in fn.lower() for fn in r.get("business_functions", []))
            match_notes = q in r.get("recent_announcement", "").lower() or q in r.get("headcount_notes", "").lower()
            if not (match_name or match_parent or match_city or match_ind or match_func or match_notes):
                continue

        # Exact / Category Filters
        if city and city != "All Cities" and r.get("city") != city:
            continue
        if industry and industry != "All Industries" and r.get("industry") != industry:
            continue
        if function and function != "All Functions":
            if function not in r.get("business_functions", []):
                continue
        if verification_status and verification_status != "All Statuses" and r.get("verification_status") != verification_status:
            continue

        filtered.append(r)

    # Sorting
    if sort_by in ["company_name", "city", "industry", "verification_status"]:
        filtered.sort(key=lambda x: str(x.get(sort_by, "")).lower(), reverse=not sort_ascending)
    elif sort_by in ["headcount", "establishment_year"]:
        filtered.sort(key=lambda x: x.get(sort_by, 0) or 0, reverse=not sort_ascending)

    return filtered

def get_gcc_by_id(gcc_id: str) -> Optional[Dict[str, Any]]:
    """Returns a single GCC record by ID."""
    records = _load_json("gcc_records.json")
    for r in records:
        if r.get("id") == gcc_id:
            return r
    return None

def get_city_intelligence(city_id: Optional[str] = None) -> Any:
    """Returns all cities intelligence data or a specific city by ID."""
    data = _load_json("city_intelligence.json")
    cities = data.get("cities", []) if isinstance(data, dict) else []
    if city_id:
        for c in cities:
            if c.get("id").lower() == city_id.lower() or c.get("name").lower() == city_id.lower():
                return c
        return None
    return cities

def get_service_providers(
    category: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Returns curated service providers filtered by category and search term."""
    providers = _load_json("service_providers.json")
    if not isinstance(providers, list):
        return []

    filtered = []
    q = search_query.lower().strip() if search_query else None

    for sp in providers:
        if category and category != "All Categories" and sp.get("category") != category:
            continue
        if q:
            match_name = q in sp.get("name", "").lower()
            match_sub = q in sp.get("sub_category", "").lower()
            match_track = q in sp.get("documented_track_record", "").lower()
            match_serv = any(q in s.lower() for s in sp.get("services_offered", []))
            if not (match_name or match_sub or match_track or match_serv):
                continue
        filtered.append(sp)

    return filtered

def get_sources_registry(source_id: Optional[str] = None) -> Any:
    """Returns complete sources registry or a specific source by ID."""
    sources = _load_json("sources_registry.json")
    if source_id:
        for s in sources:
            if s.get("id") == source_id:
                return s
        return None
    return sources

def get_ecosystem_kpis() -> Dict[str, Any]:
    """
    Computes genuine ecosystem metrics with strict source attribution.
    """
    gccs = get_gcc_records()
    cities = get_city_intelligence()
    providers = get_service_providers()
    sources = get_sources_registry()

    # Total verified headcount documented in our curated database
    total_tracked_headcount = sum(g.get("headcount", 0) for g in gccs if isinstance(g.get("headcount"), (int, float)))

    return {
        "curated_gcc_count": len(gccs),
        "total_tracked_headcount": total_tracked_headcount,
        "monitored_tier1_cities": len(cities),
        "service_partners_count": len(providers),
        "verified_sources_count": len(sources),
        # Authoritative macro figures from NASSCOM-Zinnov GCC 4.0 Report
        "macro_india_gccs": "1,580+",
        "macro_talent_pool": "1.66M+",
        "macro_economic_value": "$64B+",
        "macro_source_label": "NASSCOM & Zinnov GCC 4.0 Report (2024)",
        "macro_source_url": "https://nasscom.in/knowledge-center/publications/india-gcc-landscape-2024"
    }
