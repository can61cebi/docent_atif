# -*- coding: utf-8 -*-
"""
Web of Science Dosya İçe Aktarma Modülü
========================================
WoS 'Plain Text' (tab-delimited veya tagged) formatındaki dosyaları okur.
"""

import os
from typing import List, Tuple, Optional
from config import CitingArticle, SourceArticle

class WoSFileImporter:
    """Web of Science .txt export dosyası okuyucu (Field Tagged format)"""
    
    @staticmethod
    def parse_file(file_path: str) -> List[CitingArticle]:
        """
        WoS Plain Text export dosyasını okur ve CitingArticle listesi döner.
        Beklenen format: Field Tagged (örn: PT J, AU ..., TI ..., ER)
        """
        articles = []
        
        if not os.path.exists(file_path):
            print(f"❌ Dosya bulunamadı: {file_path}")
            return []
            
        current_article = {}
        current_tag = ""
        
        try:
            # Önce farklı encodingleri dene
            content = ""
            for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1254']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    print(f"📄 Dosya okundu (encoding: {encoding})")
                    break
                except UnicodeDecodeError:
                    continue
            
            if not content:
                print("❌ Dosya hiçbir encoding ile okunamadı!")
                return []

            lines = content.splitlines()
                
            for line in lines:
                # Satır sonu karakterlerini temizle ama baştaki boşlukları koru (devam satırları için)
                line_stripped = line.rstrip()
                if not line_stripped:
                    continue
                
                # Tag kontrolü
                # 1. ER veya EF gibi 2 karakterlik özel tagler (boşluksuz olabilir)
                # 2. Standart tagler: "TI Title" (TI + boşluk)
                
                is_tag_line = False
                tag = ""
                value = ""
                
                if line_stripped == "ER":
                    tag = "ER"
                    is_tag_line = True
                elif line_stripped == "EF":
                    tag = "EF"
                    is_tag_line = True
                elif len(line) >= 3 and line[0:2].isupper() and line[2] == " ":
                    tag = line[:2]
                    value = line[3:].strip()
                    is_tag_line = True
                
                if is_tag_line:
                    current_tag = tag
                    
                    if tag == "ER": # End of Record
                        if current_article:
                            # Nesneye dönüştür
                            article = WoSFileImporter._dict_to_article(current_article)
                            if article:
                                articles.append(article)
                        current_article = {}
                        current_tag = ""
                    elif tag == "EF": # End of File
                        break
                    elif tag == "FN": # File Name (Header) - Yoksay
                        pass
                    elif tag == "VR": # Version (Header) - Yoksay
                        pass
                    elif tag in ["AU", "AF", "CR", "C1"]: # Liste olması gereken alanlar
                        if tag not in current_article:
                            current_article[tag] = []
                        current_article[tag].append(value)
                    else:
                        current_article[tag] = value
                
                elif current_tag: # Devam eden satır (Tag yok veya girintili)
                    # Genelde 3 boşlukla başlar ama garanti değil, tag yoksa devamdır
                    value = line.strip()
                    if not value: continue
                    
                    if current_tag in ["AU", "AF", "CR", "C1"]:
                        current_article[current_tag].append(value)
                    else:
                        # Metin alanları için boşlukla ekle
                        current_article[current_tag] += " " + value
                        
            print(f"✅ {len(articles)} makale başarıyla okundu.")
            return articles
            
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            return []

    @staticmethod
    def _dict_to_article(data: dict) -> Optional[CitingArticle]:
        """Dictionary verisini CitingArticle nesnesine çevir"""
        try:
            # Temel kontroller
            if "TI" not in data and "AF" not in data:
                return None
                
            title = data.get("TI", "")
            if not title: # Bazen başlık yoksa atla
                 return None
                 
            # Yazarlar: AF (Author Full) tercih edilir, yoksa AU
            authors = data.get("AF", data.get("AU", []))
            
            # Dergi
            journal = data.get("SO", "")  # Source Code
            if not journal:
                 journal = data.get("SE", "") # Book series
            
            # Yıl
            year_str = data.get("PY", "0")
            try:
                year = int(year_str)
            except:
                year = 0
                
            # Cilt/Sayı
            volume = data.get("VL", "")
            issue = data.get("IS", "")
            
            # Sayfalar
            pages = ""
            if "BP" in data and "EP" in data:
                pages = f"{data['BP']}-{data['EP']}"
            elif "AR" in data: # Article Number
                pages = data["AR"]
                
            # DOI
            doi = data.get("DI", "")
            wos_id = data.get("UT", "").replace("WOS:", "")
            
            return CitingArticle(
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                volume=volume,
                issue=issue,
                pages=pages,
                doi=doi,
                wos_id=wos_id
            )
            
        except Exception as e:
            print(f"⚠️ Makale dönüştürme hatası: {e}")
            return None
