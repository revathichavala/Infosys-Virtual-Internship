"""
Utility functions for file handling and text extraction
"""

import io
from typing import Optional

# Import logger
try:
    from logger import get_utils_logger
    logger = get_utils_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def extract_text_from_file(uploaded_file) -> Optional[str]:
    """Extract text from uploaded file (PDF or TXT)."""
    
    file_type = uploaded_file.type
    file_name = uploaded_file.name.lower()
    logger.info(f"Extracting text from file: {file_name} (type: {file_type})")
    
    try:
        if file_type == 'text/plain' or file_name.endswith('.txt'):
            # Handle text files
            logger.debug("Processing as text file")
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            logger.info(f"Successfully extracted {len(content)} characters from text file")
            return content
        
        elif file_type == 'application/pdf' or file_name.endswith('.pdf'):
            # Handle PDF files
            logger.debug("Processing as PDF file")
            try:
                import pdfplumber
                
                pdf_bytes = io.BytesIO(uploaded_file.read())
                text_content = []
                
                with pdfplumber.open(pdf_bytes) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                
                return '\n\n'.join(text_content)
            
            except ImportError:
                # Fallback to PyPDF2 if pdfplumber not available
                try:
                    import PyPDF2
                    
                    pdf_bytes = io.BytesIO(uploaded_file.read())
                    pdf_reader = PyPDF2.PdfReader(pdf_bytes)
                    
                    text_content = []
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
                    
                    return '\n\n'.join(text_content)
                
                except ImportError:
                    return "PDF extraction requires pdfplumber or PyPDF2. Please install: pip install pdfplumber"
        
        else:
            return f"Unsupported file type: {file_type}"
    
    except Exception as e:
        return f"Error extracting text: {str(e)}"


def clean_text(text: str) -> str:
    """Clean and preprocess text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    import re
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = text.replace('\x00', '')
    
    return text.strip()


def chunk_text(text: str, max_chunk_size: int = 4000) -> list:
    """Split text into chunks for processing."""
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    words = text.split()
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1  # +1 for space
        if current_size + word_size > max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def fetch_article_content(url: str) -> Optional[str]:
    """Fetch and extract text content from a URL."""
    logger.info(f"Fetching article content from: {url}")
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.debug("Sending HTTP request...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logger.debug(f"Response received: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # Try to find main content areas
        content = None
        
        # Look for common article containers
        for selector in ['article', 'main', '.content', '.post-content', '.article-body', '#content']:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(separator='\n', strip=True)
                logger.debug(f"Found content using selector: {selector}")
                break
        
        # Fallback to body if no specific container found
        if not content:
            body = soup.find('body')
            if body:
                content = body.get_text(separator='\n', strip=True)
                logger.debug("Using body fallback for content extraction")
        
        if content:
            # Clean up the text
            lines = content.split('\n')
            cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 20]
            result = '\n\n'.join(cleaned_lines)
            logger.info(f"Successfully extracted {len(result)} characters from URL")
            return result
        
        logger.warning(f"No content found at URL: {url}")
        return "Error: Oops! We couldn't find any readable content on this page. Try a different URL with more text content."
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return "Error: Missing packages! Please run: pip install requests beautifulsoup4"
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching URL: {url}")
        return "Error: The website took too long to respond. Please check your internet connection and try again."
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error for URL {url}: {e}")
        return "Error: Couldn't connect to the website. Please check the URL and your internet connection."
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return "Error: Page not found (404). Please check if the URL is correct."
        elif e.response.status_code == 403:
            return "Error: Access denied. This website doesn't allow content fetching."
        else:
            return f"Error: Website returned an error (Code: {e.response.status_code}). Try a different URL."
    except requests.exceptions.RequestException as e:
        return f"Error: Couldn't fetch the article. Please check the URL and try again."
    except Exception as e:
        return f"Error: Something went wrong. Please try a different URL."
