# -*- coding: utf-8 -*-
"""
DOÇENTLİK ATIF DOSYASI OLUŞTURMA ARACI
======================================
2025 Mart Dönemi Yeni Kriterlerine Uygun

KURULUM (Windows 11):
    pip install playwright playwright-stealth pypdf reportlab openpyxl pdfplumber
    playwright install chromium

KULLANIM:
    python main.py

PROJE YAPISI:
    docentlik_atif/
    ├── config.py           # Ayarlar
    ├── wos_scraper.py      # Web of Science scraper (Playwright stealth)
    ├── pdf_processor.py    # PDF işleme (tam metinlerden sayfa çıkarma)
    ├── document_builder.py # Atıf dosyası oluşturma
    ├── main.py             # Ana program
    └── downloads/          # İndirilen PDF'ler buraya konacak

YENİ KRİTERLER (2025 Mart):
    Her atıf için aşağıdaki belgeler gerekli:
    1. Atıf Listesi - Künye bilgileri (otomatik oluşturulacak)
    2. Ünvan/Kapak Sayfası - Atıf yapan derginin kapağı
    3. Başlık Sayfası - Atıf yapan makalenin ilk sayfası
    4. İlk Atıf Sayfası - Sizin makalenizin referans verildiği sayfa (vurgulanmış)
    5. Kaynakça Sayfası - References bölümü (atıf işaretlenmiş)
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

# ============================================================================
# AYARLAR
# ============================================================================

# Proje dizini
BASE_DIR = Path(__file__).parent.absolute()
DOWNLOADS_DIR = BASE_DIR / "downloads"
OUTPUT_DIR = BASE_DIR / "output"

# Dizinleri oluştur
DOWNLOADS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Web of Science URL'leri
WOS_BASE_URL = "https://www.webofscience.com"
WOS_LOGIN_URL = "https://www.webofscience.com/wos/woscc/basic-search"


# ============================================================================
# VERİ SINIFLARI
# ============================================================================

@dataclass
class WoSCredentials:
    """Web of Science giriş bilgileri"""
    email: str = ""
    password: str = ""
    institution: str = ""  # Kurum seçimi için (opsiyonel)


@dataclass
class CitingArticle:
    """Atıf yapan makale bilgileri"""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    journal: str = ""
    year: int = 0
    volume: str = ""
    issue: str = ""
    pages: str = ""
    doi: str = ""
    wos_id: str = ""
    
    # PDF işleme sonrası doldurulacak
    pdf_path: Optional[str] = None
    cover_page: Optional[int] = None      # Kapak sayfası numarası
    title_page: Optional[int] = None      # Başlık sayfası (genelde 1)
    citation_pages: List[int] = field(default_factory=list)   # Atıfın yapıldığı SAYFALAR (çoklu)
    reference_page: Optional[int] = None  # Kaynakça sayfası
    reference_number: Optional[int] = None  # Kaynakçadaki sıra numarası
    citation_bboxes: List[List[float]] = field(default_factory=list) # Atıfların koordinatları
    reference_bbox: Optional[List[float]] = None # Kaynakça referansının koordinatları
    cover_page_path: Optional[str] = None # Dergi kapak/ünvan sayfası dosyası (ana kapak)
    cover_pages_all: List[str] = field(default_factory=list)  # Tüm kapak sayfası dosya yolları
    
    def get_citation_string(self, style: str = "academic") -> str:
        """Künye oluştur - Akademik format"""
        # Format authors
        if self.authors and len(self.authors) > 0:
            authors_str = ", ".join(self.authors[:3])
            if len(self.authors) > 3:
                authors_str += ", et al."
        else:
            authors_str = "Unknown Author"
        
        # Academic format: Author, et al. "Title" Journal (Year). DOI
        citation = f'{authors_str}. "{self.title}" {self.journal} ({self.year}).'
        if self.doi:
            citation += f" https://doi.org/{self.doi}"
        return citation


@dataclass
class SourceArticle:
    """Atıf yapılan (sizin) makale bilgileri"""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    journal: str = ""
    year: int = 0
    volume: str = ""
    issue: str = ""
    pages: str = ""
    doi: str = ""
    wos_id: str = ""
    total_citations: int = 0
    
    # Atıf yapan makaleler
    citing_articles: List[CitingArticle] = field(default_factory=list)


@dataclass  
class CandidateInfo:
    """Doçentlik adayı bilgileri"""
    name: str = ""
    institution: str = ""
    department: str = ""
    application_period: str = "2025 Mart"


# ============================================================================
# YARDIMCI FONKSİYONLAR
# ============================================================================

def sanitize_filename(filename: str) -> str:
    """Dosya adını güvenli hale getir"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:200]  # Max 200 karakter


def print_banner():
    """Program başlığını yazdır"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║       DOÇENTLİK ATIF DOSYASI OLUŞTURMA ARACI                    ║
║       2025 Mart Dönemi Yeni Kriterlerine Uygun                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def print_step(step_num: int, message: str):
    """Adım mesajı yazdır"""
    print(f"\n{'='*60}")
    print(f"  ADIM {step_num}: {message}")
    print(f"{'='*60}\n")
