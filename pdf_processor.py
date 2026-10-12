import io
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> dict:
    """
    Extracts text from a PDF file buffer.
    Returns a dictionary with:
      - 'full_text': Combined text of all pages
      - 'pages': List of text per page
      - 'total_pages': Number of pages
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_text.append({
                "page_num": idx + 1,
                "text": text.strip()
            })
            
        full_text = "\n\n".join([p["text"] for p in pages_text if p["text"]])
        
        return {
            "success": True,
            "full_text": full_text,
            "pages": pages_text,
            "total_pages": len(reader.pages)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "full_text": "",
            "pages": [],
            "total_pages": 0
        }


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> list:
    """
    Simple sliding-window text chunker for context window management.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start += chunk_size - overlap
        
    return chunks
