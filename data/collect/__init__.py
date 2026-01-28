"""Data collection utilities for law documents."""

import requests
import logging
from typing import List, Dict, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class LawAPIClient:
    """Client for Korean law API."""
    
    BASE_URL = "https://www.law.go.kr/api"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize law API client.
        
        Args:
            api_key: Optional API key for authentication
        """
        self.api_key = api_key
        self.session = requests.Session()
    
    def search_laws(
        self,
        query: str,
        law_type: str = "법령",
        page: int = 1,
        page_size: int = 100,
    ) -> Dict:
        """Search for laws.
        
        Args:
            query: Search query
            law_type: Type of law ("법령", "판례", etc.)
            page: Page number
            page_size: Results per page
            
        Returns:
            API response
        """
        logger.info(f"Searching laws: {query}")
        
        # TODO: Implement actual API call
        # This is a placeholder that returns empty results
        return {"results": [], "total": 0}
    
    def get_law_details(self, law_id: str) -> Dict:
        """Get detailed information about a law.
        
        Args:
            law_id: Law ID
            
        Returns:
            Law details
        """
        logger.info(f"Fetching law details: {law_id}")
        
        # TODO: Implement actual API call
        return {}


def save_documents(
    documents: List[Dict],
    output_path: str,
    format: str = "jsonl",
) -> None:
    """Save documents to file.
    
    Args:
        documents: List of documents
        output_path: Output file path
        format: Output format ("json" or "jsonl")
    """
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving {len(documents)} documents to {output_path}")
    
    if format == "jsonl":
        with open(output_path, "w", encoding="utf-8") as f:
            for doc in documents:
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    elif format == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved {len(documents)} documents")


def load_documents(input_path: str) -> List[Dict]:
    """Load documents from file.
    
    Args:
        input_path: Input file path
        
    Returns:
        List of documents
    """
    logger.info(f"Loading documents from {input_path}")
    
    documents = []
    
    if input_path.endswith(".jsonl"):
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    documents.append(json.loads(line))
    elif input_path.endswith(".json"):
        with open(input_path, "r", encoding="utf-8") as f:
            documents = json.load(f)
    
    logger.info(f"Loaded {len(documents)} documents")
    return documents
