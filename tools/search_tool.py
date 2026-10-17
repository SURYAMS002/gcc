import os
import re
from typing import List, Dict, Any, Optional
from rag.vector_store import FAISSVectorStore
from rag.knowledge_indexer import build_or_load_gcc_index

_GLOBAL_VECTOR_STORE: Optional[FAISSVectorStore] = None

def get_vector_store() -> FAISSVectorStore:
    """Gets or initializes the global FAISS vector store reference for GCC Intel."""
    global _GLOBAL_VECTOR_STORE
    if _GLOBAL_VECTOR_STORE is None:
        _GLOBAL_VECTOR_STORE = build_or_load_gcc_index()
    return _GLOBAL_VECTOR_STORE

def set_vector_store(store: FAISSVectorStore):
    """Sets the global FAISS vector store reference."""
    global _GLOBAL_VECTOR_STORE
    _GLOBAL_VECTOR_STORE = store

def search_gcc_intelligence(query: str, top_k: int = 4) -> str:
    """
    Search GCC Intel knowledge base for verified ecosystem data, city benchmarks,
    state policies, company records, and service providers.
    
    Args:
        query: Natural language research query (e.g. 'Compare Bengaluru and Chennai for fintech GCC')
        top_k: Number of relevant knowledge chunks to retrieve (default: 4)
        
    Returns:
        Formatted evidence string containing section headers, source citations, URLs, and snippet text.
    """
    store = get_vector_store()
    if store is None or store.index is None or store.index.ntotal == 0:
        return "Error: GCC Intel vector store is not initialized."

    results = store.search(query, top_k=top_k)
    if not results:
        return f"No relevant evidence found in the GCC Intel knowledge base for query: '{query}'"

    formatted_outputs = []
    for idx, item in enumerate(results, start=1):
        source_title = item.get("source", "GCC Intel Knowledge Base")
        source_url = item.get("source_url", "https://nasscom.in/")
        section = item.get("section", "General Overview")
        status = item.get("verification_status", "Verified Fact")
        score = item.get("score", 0.0)

        formatted_outputs.append(
            f"--- Evidence #{idx} [{section}] ---\n"
            f"Source: {source_title}\n"
            f"URL: {source_url}\n"
            f"Confidence: {status} (Similarity: {score:.2f})\n"
            f"Content:\n{item['text']}\n"
        )

    return "\n".join(formatted_outputs)

# Legacy alias for backward compatibility
def search_report(query: str, top_k: int = 4) -> str:
    return search_gcc_intelligence(query, top_k=top_k)
