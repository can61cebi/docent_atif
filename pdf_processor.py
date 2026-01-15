# -*- coding: utf-8 -*-
"""
PDF İŞLEME MODÜLÜ
=================
Tam metinlerden atıf sayfalarını bulma ve çıkarma

İşlevler:
- PDF'den metin çıkarma
- Atıf yapılan sayfayı bulma
- Kaynakça sayfasını bulma
- Belirli sayfaları çıkarma
- PDF birleştirme
"""

import os
import re
import difflib
import io
from typing import List, Optional, Tuple, Dict
from pathlib import Path
from dataclasses import dataclass

# PDF işleme kütüphaneleri
import pdfplumber
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import yellow, red

from config import CitingArticle, SourceArticle, DOWNLOADS_DIR


@dataclass
class PageInfo:
    """Sayfa bilgisi"""
    page_number: int
    text: str
    has_citation: bool = False
    is_reference_page: bool = False
    reference_number: Optional[int] = None

def normalize_text(text: str) -> str:
    """Türkçe karakterleri normalize et (Lowercase + ASCII)"""
    if not text: return ""
    tr_map = str.maketrans("ğĞüÜşŞıİöÖçÇ", "gGuUsSiIoOcC")
    return text.translate(tr_map).lower()



class PDFProcessor:
    """PDF işleme sınıfı"""
    
    def __init__(self):
        self.current_pdf_path: Optional[str] = None
        self.pages: List[PageInfo] = []
    
    def load_pdf(self, pdf_path: str) -> bool:
        """
        PDF dosyasını yükle ve analiz et
        
        Args:
            pdf_path: PDF dosyasının yolu
            
        Returns:
            bool: Başarılı ise True
        """
        if not os.path.exists(pdf_path):
            print(f"❌ Dosya bulunamadı: {pdf_path}")
            return False
        
        self.current_pdf_path = pdf_path
        self.pages = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    
                    page_info = PageInfo(
                        page_number=i,
                        text=text
                    )
                    
                    # Referans sayfası mı kontrol et
                    if self._is_reference_page(text):
                        page_info.is_reference_page = True
                    
                    self.pages.append(page_info)
            
            print(f"✅ PDF yüklendi: {len(self.pages)} sayfa")
            return True
            
        except Exception as e:
            print(f"❌ PDF okuma hatası: {e}")
            return False
    
    def _is_reference_page(self, text: str) -> bool:
        """Metnin referans sayfası olup olmadığını kontrol et"""
        reference_headers = [
            r'\bReferences\b',
            r'\bBibliography\b',
            r'\bLiterature\s+Cited\b',
            r'\bKaynakça\b',
            r'\bKaynaklar\b',
            r'\bWorks\s+Cited\b',
        ]
        
        for pattern in reference_headers:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Referans formatı kontrolü (numaralı referanslar)
        ref_pattern = r'^\s*\[\d+\]|\s+\d+\.\s+[A-Z][a-z]+'
        matches = re.findall(ref_pattern, text, re.MULTILINE)
        if len(matches) > 5:  # En az 5 referans formatı
            return True
        
        return False
    
    def find_citation_page(self, source_article: SourceArticle) -> Optional[Tuple[int, int, Optional[List[float]]]]:
        """
        Kaynak makalenin atıf yapıldığı sayfayı bul (Legacy single-page return).
        Backward compatible wrapper.
        """
        result = self.find_citation_info(source_article)
        if result:
            ref_page, ref_num, citation_pages = result
            # Return first citation page for backward compatibility
            first_citation_page = citation_pages[0][0] if citation_pages else ref_page
            first_citation_bbox = citation_pages[0][1] if citation_pages else None
            return (first_citation_page, ref_num, first_citation_bbox)
        return None
    
    def find_citation_info(self, source_article: SourceArticle) -> Optional[Tuple[int, int, List[Tuple[int, Optional[List[float]]]]]]:
        """
        Kapsamlı atıf arama.
        
        Returns:
            (reference_page_num, ref_num, [(citation_page_num, bbox), ...])
            or None if not found.
        """
        if not self.pages:
            return None
        
        print(f"🔍 Atıf aranıyor: {source_article.authors} ({source_article.year})")
        
        # Hazırlık
        clean_doi = ""
        if source_article.doi:
            clean_doi = re.sub(r'\s+', '', source_article.doi).lower()
        
        first_author = ""
        first_author_norm = ""
        if source_article.authors:
            first_author = source_article.authors[0].split()[-1]
            first_author_norm = normalize_text(first_author)
            
        year_str = str(source_article.year) if source_article.year else ""
        
        # YEAR TOLERANCE
        years_pattern = year_str
        if source_article.year:
            y = source_article.year
            years_pattern = f"({y}|{y-1}|{y+1})"

        # ===== PHASE 1: Find Reference Entry (ONLY in Reference Pages) =====
        ref_pages = [p for p in self.pages if p.is_reference_page]
        if not ref_pages:
            # Fallback: last 3 pages often have references
            ref_pages = self.pages[-3:] if len(self.pages) >= 3 else self.pages
        
        ref_num = None
        ref_page_num = None
        
        # STEP 1A: DOI Match FIRST (scan ALL reference pages for DOI - strongest signal)
        if clean_doi:
            for page in ref_pages:
                page_text_clean = re.sub(r'\s+', '', page.text).lower()
                if clean_doi in page_text_clean:
                    print(f"✅ DOI Eşleşmesi: Sayfa {page.page_number}")
                    ref_num = self._extract_ref_number_smart(page.text, first_author, year_str, clean_doi)
                    if ref_num:
                        ref_page_num = page.page_number
                        page.is_reference_page = True
                        break
        
        # STEP 1B: Author + Year Match (only if DOI not found)
        if not ref_num and first_author_norm and year_str:
            for page in ref_pages:
                page_text_norm = normalize_text(page.text)
                norm_author_esc = re.escape(first_author_norm)
                # Pattern: Must start at line beginning, number then dot, NOT followed by digit
                pattern = rf'(?:^|\n)\s*(\d+)\s*\.\s*(?!\s*\d)(?:(?!\n\d+\s*\.\s).)*?{norm_author_esc}.*?{years_pattern}'
                
                match = re.search(pattern, page_text_norm, re.IGNORECASE | re.DOTALL)
                if match and match.group(0).count('\n') < 15:
                    print(f"✅ Referans Eşleşmesi: Sayfa {page.page_number}")
                    ref_num = int(match.group(1))
                    ref_page_num = page.page_number
                    page.is_reference_page = True
                    break
        
        # Fallback: Proximity search for tricky PDFs (only in reference pages)
        if not ref_num and first_author_norm:
            for page in ref_pages:
                text_norm = normalize_text(page.text)
                for m in re.finditer(re.escape(first_author_norm), text_norm, re.IGNORECASE):
                    start_idx = m.start()
                    window_start = max(0, start_idx - 50)
                    window_text = text_norm[window_start:start_idx]
                    
                    match_back = re.search(r'(\d+)\s*\.\s*$', window_text.strip())
                    if match_back:
                        potential_ref = int(match_back.group(1))
                        window_end = min(len(text_norm), start_idx + 300)
                        after_text = text_norm[start_idx:window_end]
                        if re.search(years_pattern, after_text):
                            print(f"✅ Proximity Match: Sayfa {page.page_number} -> Ref {potential_ref}")
                            ref_num = potential_ref
                            ref_page_num = page.page_number
                            page.is_reference_page = True
                            break
                if ref_num:
                    break
        
        if not ref_num:
            print("❌ Referans girişi bulunamadı.")
            return None
        
        print(f"   -> Referans Numarası: {ref_num}, Referans Sayfası: {ref_page_num}")
        
        # ===== PHASE 2: Find ALL Citation Markers in Body Pages =====
        body_pages = [p for p in self.pages if not p.is_reference_page]
        citation_results: List[Tuple[int, Optional[List[float]]]] = []
        
        for page in body_pages:
            # Search for [ref_num] in various formats:
            # - Isolated: [33]
            # - Start of list: [33, 34...
            # - Middle of list: [..., 33, ...]
            # - End of list: [..., 33]
            # - With ranges: [33-35] or [30–33] (en-dash)
            grouped_pattern = rf'\[(?:[^\]]*[,\s–-])?{ref_num}(?:[,\s–-][^\]]*|\s*)?\]'
            if re.search(grouped_pattern, page.text):
                print(f"   📍 Atıf işareti bulundu: Sayfa {page.page_number} -> [{ref_num}]")
                page.has_citation = True
                
                # Get bbox
                bbox = self._find_citation_marker_bbox(page.page_number, ref_num, first_author, year_str)
                citation_results.append((page.page_number, bbox))
        
        # If no bracketed citations found, try superscript (bare number near punctuation)
        if not citation_results:
            print("   ⚠️ Köşeli parantez atıf bulunamadı, üslü sayı aranıyor...")
            for page in body_pages:
                # Superscript often appears near punctuation: "text.21" or "text,21" or "text21"
                # This is risky but can help
                super_pattern = rf'(?<=[.,;:)\s]){ref_num}(?=[\s.,;:\[]|$)'
                if re.search(super_pattern, page.text):
                    print(f"   📍 Muhtemel üslü atıf: Sayfa {page.page_number}")
                    bbox = self._find_citation_marker_bbox(page.page_number, ref_num, first_author, year_str)
                    citation_results.append((page.page_number, bbox))
        
        if not citation_results:
            print("   ⚠️ Gövde metinde atıf işareti bulunamadı, referans sayfası kullanılıyor.")
            citation_results.append((ref_page_num, None))
        
        return (ref_page_num, ref_num, citation_results)

    def find_reference_bbox(self, page_num: int, ref_num: int, source_article: SourceArticle) -> Optional[List[float]]:
        """Find the bbox of the reference entry in the bibliography"""
        try:
            if not self.current_pdf_path: return None
            
            with pdfplumber.open(self.current_pdf_path) as pdf:
                page = pdf.pages[page_num - 1]
                words = page.extract_words()
                
                if ref_num:
                    target_bracket = f"[{ref_num}]"
                    target_dot = f"{ref_num}."
                    target_str = str(ref_num)
                    
                    for i, w in enumerate(words):
                        txt = w['text']
                        # Only check near left margin for reference list items? (x0 < 100)
                        if w['x0'] > 150: # Heuristic: Ref numbers are usually on the left
                            continue
                            
                        # 1. "[12]"
                        if target_bracket in txt:
                            return [w['x0'], w['top'], w['x1'], w['bottom']]
                        
                        # 2. "12."
                        if target_dot in txt:
                             return [w['x0'], w['top'], w['x1'], w['bottom']]
                             
                        # 3. "12" then "."
                        if txt == target_str:
                             if i + 1 < len(words) and "." in words[i+1]['text']:
                                  return [w['x0'], w['top'], w['x1'], w['bottom']]

                # Fallback: Search for author name in reference page
                if source_article.authors:
                     first_author = source_article.authors[0].split()[-1]
                     for w in words:
                          if first_author.lower() in w['text'].lower():
                               return [w['x0'], w['top'], w['x1'], w['bottom']]
            
            return None
        except:
            return None

    def _find_citation_marker_bbox(self, page_num: int, ref_num: int, author: str, year: str) -> Optional[List[float]]:
        """Find the bbox of [12] or (Author, 2024) on the specific page"""
        try:
            if not self.current_pdf_path: return None
            
            with pdfplumber.open(self.current_pdf_path) as pdf:
                page = pdf.pages[page_num - 1]
                words = page.extract_words()
                
                if ref_num > 0:
                    target_bracket = f"[{ref_num}]"
                    target_dot = f"{ref_num}."
                    target_str = str(ref_num)
                    
                    # PASS 1: High Priority - Exact Bracket Match "[21]"
                    for w in words:
                        if target_bracket in w['text']:
                             return [w['x0'], w['top'], w['x1'], w['bottom']]
                    
                    # PASS 1.5: Bare number match "33" (for grouped brackets like [33, 34])
                    # The word extractor often splits "[33," into multiple tokens
                    for w in words:
                        txt = w['text'].strip(',[]')
                        if txt == target_str:
                            return [w['x0'], w['top'], w['x1'], w['bottom']]

                    # PASS 2: Medium Priority - "21." but NOT "21.269"
                    for i, w in enumerate(words):
                        txt = w['text']
                        
                        # Case: "12." inside text (e.g. "12.Author" or "12.")
                        if target_dot in txt:
                             # Check what comes after "12."
                             # If "12.345", split gives "345"
                             parts = txt.split(target_dot)
                             if len(parts) > 1:
                                 after = parts[1]
                                 # If strictly digits follow, it's likely a float number (p < 0.05 etc)
                                 if after and after[0].isdigit():
                                     continue
                             return [w['x0'], w['top'], w['x1'], w['bottom']]
                             
                        # Case: "12" then "." (broken by space)
                        if txt == target_str:
                            # Check next word for dot
                            if i + 1 < len(words) and "." in words[i+1]['text']:
                                # Ensure the dot is not part of a float in the next word? 
                                # If next word is exactly ".", it's fine.
                                # If next word is ".25", it might be a float 21 .25 (rare but possible)
                                next_txt = words[i+1]['text']
                                if next_txt == ".":
                                    return [w['x0'], w['top'], w['x1'], w['bottom']]
                                elif next_txt.startswith("."):
                                    # Check if digit follows
                                    if len(next_txt) > 1 and not next_txt[1].isdigit():
                                         return [w['x0'], w['top'], w['x1'], w['bottom']]
                
                # If no ref number or not found, try Author
                if author:
                    for w in words:
                        if author.lower() in w['text'].lower():
                            return [w['x0'], w['top'], w['x1'], w['bottom']]
            
            return None
        except Exception as e:
            print(f"DEBUG: Error in bbox search: {e}")
            return None

    def _extract_ref_number_smart(self, text: str, author: str, year: str, clean_doi: str) -> Optional[int]:
        """
        Metin içinde referans numarasını bulmak için çeşitli yöntemler dener.
        """
        # 1. Yöntem: Author isminin olduğu satırın başına bak
        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Author varsa
            if author and author.lower() in line.lower():
                # Satır başı numarası (33. Gul...) NOT (33.5)
                m = re.search(r'^\s*(\d+)\.(?!\s*\d)', line)
                if m: return int(m.group(1))
                
                # Bi önceki satıra bak (Numara\nAuthor...)
                if i > 0:
                    m_prev = re.search(r'^\s*(\d+)\.?\s*(?!\d)$', lines[i-1])
                    if m_prev: return int(m_prev.group(1))

        # 2. Yöntem: DOI'nin olduğu bloğu bul, geriye doğru sayı ara
        # Bu biraz daha karmaşık, şimdilik basit tutalım.
        return None

    def _find_citation_in_text(self, text: str, source: SourceArticle) -> Optional[int]:
        """Metin bloğu içinde kaynak makaleyi bul ve numarasını döndür"""
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # 1. DOI Kontrolü (Kesin Eşleşme)
            if source.doi and source.doi.lower() in line.lower():
                return self._extract_ref_number_from_line(line, i, lines)
                
            # 2. Başlık Benzerliği (Fuzzy Match)
            if source.title:
                # Normalizasyon
                clean_line = re.sub(r'\W+', ' ', line).lower()
                clean_title = re.sub(r'\W+', ' ', source.title).lower()
                
                # Başlık çok kısaysa (örn: "Results") fuzzy match yapma
                if len(clean_title) < 10:
                    continue
                    
                ratio = difflib.SequenceMatcher(None, clean_title, clean_line).ratio()
                
                # Eğer satır sadece başlığın bir parçasıysa (multi-line ref), 
                # önceki/sonraki satırları birleştirip bakmak daha iyi olabilir
                # Şimdilik basit tutalım: %75 üzeri benzerlik kabul
                if ratio > 0.75:
                    return self._extract_ref_number_from_line(line, i, lines)
                    
                # Partial match: Başlık satırın içindeyse
                if clean_title in clean_line:
                     return self._extract_ref_number_from_line(line, i, lines)

        return None

    def _extract_ref_number_from_line(self, line: str, index: int, all_lines: List[str]) -> Optional[int]:
        """Bulunan satırdan veya öncesinden referans numarasını çıkar"""
        # 1. Satırın başında numara var mı? Örn: "12. Gul..." veya "[12] Gul..."
        match = re.search(r'^\s*\[?(\d+)\]?\.?', line)
        if match:
            return int(match.group(1))
            
        # 2. Önceki satıra bak (bazı formatlarda numara üst satırda tek başınadır)
        if index > 0:
            prev_line = all_lines[index-1].strip()
            match = re.search(r'^\s*\[?(\d+)\]?\.?$', prev_line)
            if match:
                return int(match.group(1))
        
        return None

    def _find_citation_marker_page(self, ref_num: int) -> Optional[int]:
        """Metin içinde [X] işaretinin geçtiği ilk sayfayı bul"""
        marker_patterns = [
            rf'\[{ref_num}\]',       # [12]
            rf'\b{ref_num}\b'        # 12 (Superscript genelde düz metin olarak gelir)
        ]
        
        # Atıf sayfalarını (Referans bölümü olmayan) tara
        target_pages = [p for p in self.pages if not p.is_reference_page]
        
        for page in target_pages:
            for pattern in marker_patterns:
                if re.search(pattern, page.text):
                    print(f"   📍 Atıf işareti bulundu: Sayfa {page.page_number} -> {pattern}")
                    page.has_citation = True
                    return page.page_number
        return None
    
    def _find_reference_number(self, text: str, source_article: SourceArticle) -> Optional[int]:
        """Atıfın referans numarasını bul"""
        # [1], [2], [3] formatı
        bracket_refs = re.findall(r'\[(\d+)\]', text)
        
        # Kaynak makale bilgilerini içeren referans numarasını bul
        for ref_num in bracket_refs:
            ref_num = int(ref_num)
            
            # Referans sayfasında bu numarayı kontrol et
            for page in self.pages:
                if page.is_reference_page:
                    # [ref_num] ile başlayan satırı bul
                    pattern = rf'\[{ref_num}\].*'
                    matches = re.findall(pattern, page.text)
                    
                    for match in matches:
                        # Bu referans bizim makaleye mi ait?
                        if source_article.doi and source_article.doi.lower() in match.lower():
                            return ref_num
                        if source_article.authors:
                            first_author = source_article.authors[0].split()[-1]
                            if first_author.lower() in match.lower():
                                return ref_num
        
        return None
    
    def find_reference_pages(self) -> List[int]:
        """Tüm referans sayfalarını bul"""
        return [p.page_number for p in self.pages if p.is_reference_page]
    
    def get_title_page(self) -> int:
        """Başlık sayfasını bul (genelde 1. sayfa)"""
        return 1
    
    def extract_pages(self, page_numbers: List[int], output_path: str) -> bool:
        """
        Belirli sayfaları çıkar ve yeni PDF oluştur
        
        Args:
            page_numbers: Çıkarılacak sayfa numaraları (1'den başlar)
            output_path: Çıktı dosyası yolu
            
        Returns:
            bool: Başarılı ise True
        """
        if not self.current_pdf_path:
            print("❌ Önce PDF yüklenmeli!")
            return False
        
        try:
            reader = PdfReader(self.current_pdf_path)
            writer = PdfWriter()
            
            for page_num in page_numbers:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            print(f"✅ Sayfalar çıkarıldı: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Sayfa çıkarma hatası: {e}")
            return False
    
    def highlight_citations(self, output_path: str, highlights: List[Dict]) -> bool:
        """
        PDF üzerinde belirtilen alanları sarı ile vurgula
        
        Args:
            output_path: Çıktı dosyasının yolu
            highlights: Vurgulanacak alanlar listesi [{'page': 1, 'bbox': [x0, top, x1, bottom]}]
            
        Returns:
            bool: Başarılı ise True
        """
        if not self.current_pdf_path:
            return False
            
        try:
            reader = PdfReader(self.current_pdf_path)
            writer = PdfWriter()
            
            # Sayfa sayfa işle
            for i, page in enumerate(reader.pages):
                page_num = i + 1
                
                # Bu sayfada highlight var mı?
                page_highlights = [h for h in highlights if h['page'] == page_num]
                
                if page_highlights:
                    # Reportlab ile overlay oluştur
                    packet = io.BytesIO()
                    can = canvas.Canvas(packet, pagesize=A4)
                    
                    # Sayfa boyutlarını al
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)
                    
                    # Canvas boyutunu ayarla (önemli!)
                    can.setPageSize((page_width, page_height))
                    
                    # Sarı, yarı saydam renk
                    can.setFillColorRGB(1, 1, 0, 0.4)
                    can.setStrokeColorRGB(1, 1, 0, 0)
                    
                    for h in page_highlights:
                        bbox = h.get('bbox')
                        if bbox:
                            # pdfplumber bbox: [x0, top, x1, bottom] (Top-Left origin)
                            # PDF coords: [x, y, width, height] (Bottom-Left origin)
                            # Convert: y_pdf = page_height - y_plumber
                            
                            x0, top, x1, bottom = bbox
                            width = x1 - x0
                            height = bottom - top
                            
                            # Y koordinatını dönüştür (pdfplumber 'top' değerini verir)
                            # PDF'de y = 0 alt kenardır.
                            # Rect: x, y (bottom-left), w, h
                            y = page_height - bottom 
                            
                            # Draw highlight
                            can.rect(x0, y, width, height, fill=1, stroke=0)
                            
                    can.save()
                    packet.seek(0)
                    
                    # Overlay'i oluştur ve sayfaya birleştir
                    overlay_pdf = PdfReader(packet)
                    page.merge_page(overlay_pdf.pages[0])
                
                writer.add_page(page)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
                
            print(f"✅ Vurgulanan PDF kaydedildi: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Vurgulama hatası: {e}")
            import traceback
            traceback.print_exc()
            return False

    def highlight_citation(self, page_number: int, search_text: str, output_path: str) -> bool:
        """Eski method, geriye uyumluluk için"""
        return self.highlight_citations(output_path, [])
    
    @staticmethod
    def merge_pdfs(pdf_paths: List[str], output_path: str) -> bool:
        """
        Birden fazla PDF'i birleştir
        
        Args:
            pdf_paths: Birleştirilecek PDF dosyalarının yolları
            output_path: Çıktı dosyası yolu
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            writer = PdfWriter()
            
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path):
                    reader = PdfReader(pdf_path)
                    for page in reader.pages:
                        writer.add_page(page)
                else:
                    print(f"⚠️  Dosya bulunamadı, atlanıyor: {pdf_path}")
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            print(f"✅ PDF'ler birleştirildi: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Birleştirme hatası: {e}")
            return False
    
    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """PDF'deki sayfa sayısını döndür"""
        try:
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except:
            return 0


class CitationFinder:
    """
    Atıf bulucu sınıfı
    
    Tam metinden atıf bilgilerini otomatik çıkarır
    """
    
    def __init__(self, source_article: SourceArticle):
        self.source = source_article
        self.processor = PDFProcessor()
    
    def process_pdf(self, pdf_path: str, citing_article: CitingArticle) -> CitingArticle:
        """
        PDF'i işle ve atıf bilgilerini doldur
        
        Args:
            pdf_path: PDF dosyasının yolu
            citing_article: Atıf yapan makale
            
        Returns:
            CitingArticle: Güncellenmiş makale bilgileri
        """
        print(f"\n📄 PDF işleniyor: {os.path.basename(pdf_path)}")
        
        if not self.processor.load_pdf(pdf_path):
            return citing_article
        
        citing_article.pdf_path = pdf_path
        
        # Başlık sayfası (1. sayfa)
        citing_article.title_page = 1
        
        # Atıf bilgilerini bul (yeni çoklu atıf desteği)
        result = self.processor.find_citation_info(self.source)
        if result:
            ref_page_num, ref_num, citation_list = result
            citing_article.reference_number = ref_num
            citing_article.reference_page = ref_page_num
            
            # Tüm atıf sayfalarını kaydet
            citing_article.citation_pages = [cp[0] for cp in citation_list]
            citing_article.citation_bboxes = [cp[1] for cp in citation_list if cp[1]]
            
            # Referans bbox bul
            citing_article.reference_bbox = self.processor.find_reference_bbox(
                ref_page_num, 
                ref_num,
                self.source
            )
        
        return citing_article
    
    def get_required_pages(self, citing_article: CitingArticle) -> List[int]:
        """2025 yeni kriterlerine göre gerekli sayfaları döndür"""
        pages = []
        
        # 1. Başlık sayfası
        if citing_article.title_page:
            pages.append(citing_article.title_page)
        
        # 2. Atıf yapılan sayfaLAR (çoklu)
        for cp in citing_article.citation_pages:
            if cp not in pages:
                pages.append(cp)
        
        # 3. Kaynakça sayfası
        if citing_article.reference_page:
            if citing_article.reference_page not in pages:
                pages.append(citing_article.reference_page)
        
        return sorted(pages)


class PDFDownloadManager:
    """
    PDF indirme yöneticisi
    
    Kullanıcının indirdiği PDF'leri yönetir
    """
    
    def __init__(self, download_dir: str = None):
        self.download_dir = Path(download_dir) if download_dir else DOWNLOADS_DIR
        self.download_dir.mkdir(exist_ok=True)
    
    def get_expected_filename(self, article: CitingArticle) -> str:
        """Beklenen dosya adını oluştur"""
        # DOI varsa DOI'den, yoksa başlıktan
        if article.doi:
            # DOI'yi dosya adına uygun hale getir
            safe_doi = article.doi.replace("/", "_").replace(".", "_")
            return f"{safe_doi}.pdf"
        else:
            # Başlıktan güvenli dosya adı
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', article.title[:50])
            return f"{safe_title}.pdf"
    
    def check_pdf_exists(self, article: CitingArticle) -> Optional[str]:
        """
        PDF'in indirilip indirilmediğini kontrol et
        
        Returns:
            str: Dosya yolu veya None
        """
        expected_name = self.get_expected_filename(article)
        expected_path = self.download_dir / expected_name
        
        if expected_path.exists():
            return str(expected_path)
        
        # DOI ile ara (farklı dosya adı olabilir)
        if article.doi:
            for pdf_file in self.download_dir.glob("*.pdf"):
                try:
                    with pdfplumber.open(pdf_file) as pdf:
                        first_page = pdf.pages[0].extract_text() or ""
                        if article.doi in first_page:
                            return str(pdf_file)
                except:
                    continue
        
        return None
    
    def list_downloaded_pdfs(self) -> List[str]:
        """İndirilen PDF'lerin listesini döndür"""
        return [str(p) for p in self.download_dir.glob("*.pdf")]
    
    def get_missing_pdfs(self, articles: List[CitingArticle]) -> List[CitingArticle]:
        """İndirilmemiş PDF'lerin listesini döndür"""
        missing = []
        for article in articles:
            if not self.check_pdf_exists(article):
                missing.append(article)
        return missing


# ============================================================================
# TEST FONKSİYONU
# ============================================================================

def test_pdf_processor():
    """PDF işleyiciyi test et"""
    processor = PDFProcessor()
    
    # Test PDF'i varsa
    test_pdf = DOWNLOADS_DIR / "test.pdf"
    
    if test_pdf.exists():
        processor.load_pdf(str(test_pdf))
        
        print(f"\nSayfa sayısı: {len(processor.pages)}")
        print(f"Referans sayfaları: {processor.find_reference_pages()}")
        
        # Test kaynak makale
        source = SourceArticle(
            doi="10.1186/s12903-024-05384-2",
            authors=["Buse Cebi Gul"],
            year=2025,
            title="Mechanical analysis of 3D printed dental restorations"
        )
        
        result = processor.find_citation_page(source)
        if result:
            print(f"Atıf bulundu: Sayfa {result[0]}, Ref #{result[1]}")
    else:
        print(f"Test PDF'i bulunamadı: {test_pdf}")
        print("'downloads' klasörüne test PDF'i ekleyin.")


if __name__ == "__main__":
    test_pdf_processor()
