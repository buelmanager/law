"""Data processing utilities."""

import logging
from typing import List, Dict, Tuple
import re

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunk documents into smaller pieces."""
    
    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 100,
        separator: str = "\n\n",
    ):
        """Initialize chunker.
        
        Args:
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
            separator: Separator for splitting
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separator = separator
    
    def chunk_by_law_articles(self, text: str, law_name: str = "") -> List[Dict]:
        """Chunk document by law articles (법령을 조문 단위로 청킹).
        
        Args:
            text: Document text
            law_name: Name of the law
            
        Returns:
            List of chunks with metadata
        """
        logger.debug(f"Chunking document by articles (law: {law_name})")
        
        # 조문 패턴: 제1조, 제2조, 등
        article_pattern = r"(?:제\d+조)"
        
        chunks = []
        current_chunk = ""
        current_article = ""
        
        lines = text.split("\n")
        for line in lines:
            if re.match(article_pattern, line.strip()):
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "article": current_article,
                        "law": law_name,
                        "type": "article",
                    })
                current_article = line.strip()
                current_chunk = line
            else:
                current_chunk += "\n" + line
        
        if current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "article": current_article,
                "law": law_name,
                "type": "article",
            })
        
        logger.debug(f"Created {len(chunks)} article chunks")
        return chunks
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Chunk text by size with overlap.
        
        Args:
            text: Text to chunk
            metadata: Metadata for chunks
            
        Returns:
            List of chunks with metadata
        """
        logger.debug(f"Chunking text (size: {len(text)})")
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to find separator near the end
            if end < len(text):
                sep_idx = text.rfind(self.separator, start, end)
                if sep_idx > start:
                    end = sep_idx + len(self.separator)
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "content": chunk_text,
                    **metadata,
                    "type": "text",
                })
            
            start = end - self.overlap
        
        logger.debug(f"Created {len(chunks)} text chunks")
        return chunks


def clean_text(text: str) -> str:
    """Clean and normalize text.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Remove multiple spaces
    text = re.sub(r" +", " ", text)
    
    # Remove multiple newlines
    text = re.sub(r"\n\n+", "\n\n", text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_metadata(document: Dict) -> Dict:
    """Extract metadata from document.
    
    Args:
        document: Document dictionary
        
    Returns:
        Metadata dictionary
    """
    return {
        "law": document.get("law", ""),
        "article": document.get("article", ""),
        "date": document.get("date", ""),
        "source": document.get("source", ""),
        "type": document.get("type", ""),
    }
