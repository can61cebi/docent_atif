# -*- coding: utf-8 -*-
"""
ANA PROGRAM
===========
Doçentlik Atıf Dosyası Oluşturma - Kullanıcı Arayüzü

Kullanım:
    python main.py

İş Akışı:
    1. Kullanıcı bilgilerini al
    2. WoS export dosyasını yükle (savedrecs.txt)
    3. Kullanıcıdan PDF'leri ve kapak dosyalarını indirmesini iste
    4. PDF'leri işle
    5. Final dokümanı oluştur
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from config import (
    CandidateInfo, SourceArticle, CitingArticle,
    DOWNLOADS_DIR, OUTPUT_DIR, print_banner, print_step
)
from import_utils import WoSFileImporter
from pdf_processor import PDFProcessor, CitationFinder, PDFDownloadManager
from document_builder import CitationDocumentBuilder, FinalDocumentAssembler


class CitationApp:
    """Ana uygulama sınıfı"""
    
    def __init__(self):
        self.candidate: Optional[CandidateInfo] = None
        self.source_article: Optional[SourceArticle] = None
        self.download_manager = PDFDownloadManager()
        
        # Veri dosyası (devam etmek için)
        self.data_file = OUTPUT_DIR / "session_data.json"
    
    def save_session(self):
        """Oturum verilerini kaydet"""
        if not self.source_article:
            return
        
        data = {
            "candidate": {
                "name": self.candidate.name if self.candidate else "",
                "institution": self.candidate.institution if self.candidate else "",
                "department": self.candidate.department if self.candidate else "",
                "application_period": self.candidate.application_period if self.candidate else "",
            },
            "source_article": {
                "title": self.source_article.title,
                "authors": self.source_article.authors,
                "journal": self.source_article.journal,
                "year": self.source_article.year,
                "volume": self.source_article.volume,
                "issue": self.source_article.issue,
                "pages": self.source_article.pages,
                "doi": self.source_article.doi,
                "wos_id": self.source_article.wos_id,
            },
            "citing_articles": [
                {
                    "title": a.title,
                    "authors": a.authors,
                    "journal": a.journal,
                    "year": a.year,
                    "volume": a.volume,
                    "issue": a.issue,
                    "pages": a.pages,
                    "doi": a.doi,
                    "wos_id": a.wos_id,
                    "pdf_path": a.pdf_path,
                    "title_page": a.title_page,
                    "citation_page": a.citation_page,
                    "reference_page": a.reference_page,
                    "reference_number": a.reference_number,
                    "cover_page_path": getattr(a, 'cover_page_path', None),
                }
                for a in self.source_article.citing_articles
            ],
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Oturum kaydedildi: {self.data_file}")
    
    def load_session(self) -> bool:
        """Önceki oturumu yükle"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Aday bilgisi
            if data.get("candidate"):
                c = data["candidate"]
                self.candidate = CandidateInfo(
                    name=c.get("name", ""),
                    institution=c.get("institution", ""),
                    department=c.get("department", ""),
                    application_period=c.get("application_period", "")
                )
            
            # Kaynak makale
            if data.get("source_article"):
                s = data["source_article"]
                self.source_article = SourceArticle(
                    title=s.get("title", ""),
                    authors=s.get("authors", []),
                    journal=s.get("journal", ""),
                    year=s.get("year", 0),
                    volume=s.get("volume", ""),
                    issue=s.get("issue", ""),
                    pages=s.get("pages", ""),
                    doi=s.get("doi", ""),
                    wos_id=s.get("wos_id", ""),
                )
            
            # Atıf yapan makaleler
            for a in data.get("citing_articles", []):
                article = CitingArticle(
                    title=a.get("title", ""),
                    authors=a.get("authors", []),
                    journal=a.get("journal", ""),
                    year=a.get("year", 0),
                    volume=a.get("volume", ""),
                    issue=a.get("issue", ""),
                    pages=a.get("pages", ""),
                    doi=a.get("doi", ""),
                    wos_id=a.get("wos_id", ""),
                    pdf_path=a.get("pdf_path"),
                    title_page=a.get("title_page"),
                    citation_page=a.get("citation_page"),
                    reference_page=a.get("reference_page"),
                    reference_number=a.get("reference_number"),
                )
                self.source_article.citing_articles.append(article)
            
            print(f"📂 Önceki oturum yüklendi ({data.get('saved_at', '')})")
            return True
            
        except Exception as e:
            print(f"⚠️  Oturum yükleme hatası: {e}")
            return False
    
    def get_candidate_info(self):
        """Kullanıcı bilgilerini al"""
        print_step(1, "ADAY BİLGİLERİ")
        
        self.candidate = CandidateInfo()
        
        self.candidate.name = input("Adınız Soyadınız: ").strip()
        self.candidate.institution = input("Kurumunuz: ").strip()
        self.candidate.department = input("Bölümünüz: ").strip()
        self.candidate.application_period = input("Başvuru Dönemi (örn: 2025 Mart): ").strip() or "2025 Mart"
        
        print(f"\n✅ Aday bilgileri alındı: {self.candidate.name}")
    
    def import_wos_file(self):
        """WoS export dosyasını yükle"""
        print_step(2, "WOS DOSYA YÜKLEME")
        
        print("Lütfen Web of Science'dan 'Export > Plain Text File' seçeneği ile")
        print("indirdiğiniz dosyanın tam yolunu girin. (Content: Full Record)")
        print("Varsayılan: savedrecs.txt")
        
        path = input("\nDosya yolu [savedrecs.txt]: ").strip() or "savedrecs.txt"
        
        if not os.path.exists(path):
            print(f"❌ Dosya bulunamadı: {path}")
            return False
            
        # Kaynak makale bilgilerini al (eğer yoksa)
        if not self.source_article:
            print("\n⚠️ Kaynak makale bilgilerinizi girin.")
            print("   (Bu bilgiler PDF içinde atıf ararken kullanılacaktır)")
            
            title = input("Makale Başlığı: ").strip()
            doi = input("DOI (örn: 10.xxx/...): ").strip()
            author = input("İlk Yazar Soyadı (örn: Gul): ").strip()
            year_str = input("Yıl (örn: 2024): ").strip()
            
            try:
                year = int(year_str)
            except:
                year = 0
                
            if title:
                self.source_article = SourceArticle(
                    title=title, 
                    doi=doi,
                    authors=[author] if author else [],
                    year=year
                )
                print("✅ Kaynak makale tanımlandı.")
            else:
                print("❌ Başlık girilmedi, işlem iptal.")
                return False
        
        print(f"\n📂 '{path}' dosyası okunuyor...")
        articles = WoSFileImporter.parse_file(path)
        
        if articles:
            self.source_article.citing_articles = articles
            self.source_article.total_citations = len(articles)
            print(f"✅ {len(articles)} atıf başarıyla yüklendi!")
            self.save_session()
            return True
        else:
            print("⚠️ Dosyadan hiç makale okunamadı.")
            return False
    
    def show_download_instructions(self):
        """PDF indirme talimatlarını göster"""
        print_step(3, "PDF İNDİRME TALİMATLARI")
        
        if not self.source_article or not self.source_article.citing_articles:
            print("❌ Önce atıflar yüklenmeli!")
            return
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  PDF VE KAPAK DOSYASI İNDİRME TALİMATLARI                       ║
╚══════════════════════════════════════════════════════════════════╝

Her atıf için 2 dosya indirmeniz gerekmektedir:

1. TAM METİN PDF
   - Makalemin tam metni
   - Dosya adı önerisi: DOI bazlı (örn: 10.1111_adj.70022.pdf)
   
2. KAPAK/ÜNVAN SAYFASI (A.1)
   - Derginin kapağı veya makalenin yayınlandığı sayının görseli
   - Web sitesinde göründüğü hali de olabilir
   - Dosya adı: kapak_1.pdf, kapak_2.pdf ... şeklinde

İndirme kaynakları:
  • Dergi web sitesi (DOI linki ile)
  • Sci-Hub (https://sci-hub.se)
  • Google Scholar
  • ResearchGate
  • Üniversite kütüphanesi
""")
        print(f"📁 Dosyaları şu klasöre koyun: {DOWNLOADS_DIR}")
        
        print("\n" + "="*70)
        print("İNDİRİLMESİ GEREKEN MAKALELER:")
        print("="*70)
        
        for i, article in enumerate(self.source_article.citing_articles, 1):
            pdf_exists = self.download_manager.check_pdf_exists(article)
            status = "✓ PDF VAR" if pdf_exists else "✗ PDF BEKLİYOR"
            
            print(f"\n{i}. [{status}]")
            print(f"   Başlık: {article.title[:50]}...")
            print(f"   DOI: {article.doi}")
            print(f"   Tam metin: {article.doi.replace('/', '_')}.pdf")
            print(f"   Kapak: kapak_{i}.pdf")
            if article.doi:
                print(f"   Link: https://doi.org/{article.doi}")
        
        print("\n" + "="*70)
        input("\nPDF'leri indirdikten sonra Enter'a basın...")
    
    def check_pdfs(self):
        """İndirilen PDF'leri kontrol et"""
        print("\n🔍 PDF'ler kontrol ediliyor...")
        
        if not self.source_article:
            print("❌ Önce atıflar yüklenmeli!")
            return False
            
        all_found = True
        for article in self.source_article.citing_articles:
            pdf_path = self.download_manager.find_pdf_for_article(article)
            if pdf_path:
                article.pdf_path = pdf_path
                print(f"   ✓ {article.title[:40]}... -> {os.path.basename(pdf_path)}")
            else:
                all_found = False
                print(f"   ✗ {article.title[:40]}... -> BULUNAMADI")
        
        return all_found
    
    def process_pdfs(self):
        """PDF'leri işle ve atıf sayfalarını bul"""
        print_step(4, "PDF İŞLEME")
        
        if not self.source_article:
            print("❌ Önce atıflar yüklenmeli!")
            return
        
        finder = CitationFinder(self.source_article)
        
        processed = 0
        for i, article in enumerate(self.source_article.citing_articles, 1):
            if article.pdf_path:
                print(f"\n[{i}/{len(self.source_article.citing_articles)}] İşleniyor...")
                article = finder.process_pdf(article.pdf_path, article)
                
                if article.citation_page:
                    print(f"   ✓ Atıf sayfası: {article.citation_page}")
                    processed += 1
                else:
                    print(f"   ⚠️  Atıf sayfası otomatik bulunamadı")
        
        print(f"\n📊 İşleme Sonucu: {processed}/{len(self.source_article.citing_articles)} başarılı")
        
        # Oturumu güncelle
        self.save_session()
    
    def generate_documents(self):
        """Final dokümanları oluştur"""
        print_step(5, "DOKÜMAN OLUŞTURMA")
        
        if not self.source_article or not self.candidate:
            print("❌ Eksik veriler!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # PDF builder
        builder = CitationDocumentBuilder(self.candidate, self.source_article)
        
        # Atıf listesi PDF'i
        list_pdf_path = OUTPUT_DIR / f"atif_listesi_{timestamp}.pdf"
        builder.build_pdf(str(list_pdf_path))
        
        # Excel raporu
        excel_path = OUTPUT_DIR / f"atif_raporu_{timestamp}.xlsx"
        builder.build_excel(str(excel_path))
        
        # Final doküman (PDF + tam metin sayfaları)
        final_pdf_path = OUTPUT_DIR / f"docentlik_atif_dosyasi_{timestamp}.pdf"
        
        assembler = FinalDocumentAssembler(self.source_article)
        assembler.assemble(str(list_pdf_path), str(final_pdf_path))
        
        print("\n" + "="*70)
        print("✅ OLUŞTURULAN DOSYALAR:")
        print("="*70)
        print(f"  📄 Atıf Listesi: {list_pdf_path}")
        print(f"  📊 Excel Rapor: {excel_path}")
        print(f"  📋 Final Doküman: {final_pdf_path}")
        print("="*70)
    
    def run(self):
        """Ana program döngüsü"""
        print_banner()
        
        # Önceki oturum var mı kontrol et
        if self.data_file.exists():
            choice = input("\n📂 Önceki oturum bulundu. Devam etmek ister misiniz? (E/H): ").strip().upper()
            if choice == 'E':
                if self.load_session():
                    print(f"   Makale: {self.source_article.title[:50]}...")
                    print(f"   Atıf sayısı: {len(self.source_article.citing_articles)}")
        
        while True:
            print("\n" + "="*60)
            print("ANA MENÜ")
            print("="*60)
            print("""
1. Aday bilgilerini gir
2. WoS export dosyasını yükle (savedrecs.txt)
3. PDF indirme talimatlarını göster
4. İndirilen PDF'leri kontrol et
5. PDF'leri işle (atıf sayfalarını bul)
6. Final dokümanları oluştur

0. Çıkış
            """)
            
            choice = input("Seçiminiz: ").strip()
            
            if choice == '1':
                self.get_candidate_info()
                
            elif choice == '2':
                self.import_wos_file()
                    
            elif choice == '3':
                self.show_download_instructions()
                
            elif choice == '4':
                self.check_pdfs()
                
            elif choice == '5':
                self.process_pdfs()
                
            elif choice == '6':
                self.generate_documents()

            elif choice == '0':
                print("\n👋 Güle güle!")
                break
            
            else:
                print("⚠️  Geçersiz seçim!")


def main():
    """Ana fonksiyon"""
    app = CitationApp()
    app.run()


if __name__ == "__main__":
    main()
