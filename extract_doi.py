# -*- coding: utf-8 -*-
"""
PDF DOI Extractor
=================
PDF dosyasının ilk sayfasından DOI çıkarır
"""

import sys
import json
import re
import os

def extract_doi_from_pdf(pdf_path):
    """
    PDF dosyasından DOI çıkar
    
    Args:
        pdf_path: PDF dosyasının yolu
        
    Returns:
        dict: {doi: str or None, source: str}
    """
    try:
        import pdfplumber
        
        with pdfplumber.open(pdf_path) as pdf:
            # İlk 3 sayfayı kontrol et (DOI genelde ilk sayfada olur)
            for page_num in range(min(3, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # DOI pattern'leri
                # Standard: 10.xxxx/xxxxx
                doi_patterns = [
                    r'(?:doi\s*[:.]?\s*)(10\.\d{4,}/[^\s\]>\)]+)',  # doi: 10.xxx/xxx
                    r'(?:https?://doi\.org/)(10\.\d{4,}/[^\s\]>\)]+)',  # https://doi.org/10.xxx
                    r'(?:https?://dx\.doi\.org/)(10\.\d{4,}/[^\s\]>\)]+)',  # https://dx.doi.org/10.xxx
                    r'\b(10\.\d{4,}/[^\s\]>\),]+)',  # Bare DOI: 10.xxx/xxx
                ]
                
                for pattern in doi_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        # En uzun DOI'yi seç (daha complete olma ihtimali)
                        doi = max(matches, key=len)
                        # Temizlik: sondaki noktalama işaretlerini kaldır
                        doi = re.sub(r'[.,;:\s]+$', '', doi)
                        return {
                            "doi": doi.lower(),
                            "source": f"page_{page_num + 1}",
                            "found": True
                        }
        
        return {"doi": None, "source": "not_found", "found": False}
        
    except Exception as e:
        return {"doi": None, "source": "error", "error": str(e), "found": False}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"found": False, "error": "Missing PDF path argument"}))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(json.dumps({"found": False, "error": f"File not found: {pdf_path}"}))
        sys.exit(1)
    
    result = extract_doi_from_pdf(pdf_path)
    print(json.dumps(result))
