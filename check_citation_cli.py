
import sys
import json
import os
import io
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config import SourceArticle, CitingArticle
from pdf_processor import CitationFinder

def check_citation(pdf_path, article_data):
    """
    Checks for citation in the given PDF for the source article
    """
    # Redirect stdout to stderr to prevent pollution of the final JSON output
    original_stdout = sys.stdout
    sys.stdout = sys.stderr
    
    try:
        # Create source article object from metadata
        source_article = SourceArticle(
            title=article_data.get('source_title', ''),
            doi=article_data.get('source_doi', ''),
            authors=article_data.get('source_authors', []),
            year=article_data.get('source_year', 0)
        )
        
        # Create citing article object (target)
        citing_article = CitingArticle(
            title=article_data.get('title', ''),
            doi=article_data.get('doi', '')
        )
        
        finder = CitationFinder(source_article)
        result_article = finder.process_pdf(pdf_path, citing_article)
        
        # Restore stdout before returning result
        sys.stdout = original_stdout
        
        return {
            "status": "success",
            "found": bool(result_article.citation_pages),
            "citation_pages": result_article.citation_pages,  # Array of page numbers
            "citation_bboxes": result_article.citation_bboxes or [],  # Bounding boxes for highlights
            "reference_page": result_article.reference_page,
            "reference_number": result_article.reference_number,
            "reference_bbox": result_article.reference_bbox  # Bounding box for reference highlight
        }
    except Exception as e:
        sys.stdout = original_stdout
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Missing arguments"}))
        sys.exit(1)
        
    try:
        arg = sys.argv[1]
        if os.path.exists(arg):
            with open(arg, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        else:
            input_data = json.loads(arg)
            
        pdf_path = input_data.get('pdf_path')
        article_data = input_data.get('article_data')
        
        if not os.path.exists(pdf_path):
             print(json.dumps({"status": "error", "message": f"File not found: {pdf_path}"}))
             sys.exit(1)

        result = check_citation(pdf_path, article_data)
        # Ensure only JSON is printed to stdout
        sys.stdout.write(json.dumps(result))
        sys.stdout.flush()
        
    except Exception as e:
        sys.stdout.write(json.dumps({"status": "error", "message": str(e)}))
        sys.stdout.flush()
