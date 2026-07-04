import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

def normalize_url(url: str) -> str:
    try:
        url_obj = urlparse(url)
        path = url_obj.path
        if path.endswith("/"):
            path = path[:-1]
        href = f"{url_obj.scheme}://{url_obj.netloc}{path}"
        return href.lower()
    except Exception:
        return url.lower()

def extract_links(html: str, origin: str, homepage_url: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    
    keyword_regex = re.compile(r"about|product|service|solution|pricing|contact|faq|feature", re.IGNORECASE)
    skip_regex = re.compile(r"login|signin|signup|register|logout|privacy|terms|cookie|cart|checkout|wp-admin|blog", re.IGNORECASE)
    
    for a in soup.find_all("a", href=True):
        href = a["href"].split("#")[0].strip()
        if not href:
            continue
            
        absolute_url = ""
        if href.startswith("/"):
            absolute_url = f"{origin}{href}"
        elif href.startswith("http://") or href.startswith("https://"):
            absolute_url = href
        else:
            base = homepage_url if homepage_url.endswith("/") else f"{homepage_url}/"
            absolute_url = urljoin(base, href)
            
        try:
            url_obj = urlparse(absolute_url)
            if url_obj.scheme + "://" + url_obj.netloc == origin:
                normalized = normalize_url(absolute_url)
                path = url_obj.path
                link_text = a.get_text()
                
                matches_keywords = bool(keyword_regex.search(path) or keyword_regex.search(link_text))
                should_skip = bool(skip_regex.search(path) or skip_regex.search(link_text) or "?" in href)
                
                if matches_keywords and not should_skip and normalized != normalize_url(homepage_url):
                    if normalized not in links:
                        links.append(normalized)
        except Exception:
            pass
            
    return links[:8]

def crawl_single_page(url: str) -> dict:
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timeout=8
        )
        if response.status_code != 200:
            return None
            
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return None
            
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove noise
        for tag in soup(["script", "style", "iframe", "noscript", "nav", "footer", "header", "svg"]):
            tag.decompose()
            
        title = soup.title.string.strip() if soup.title else ""
        
        headings = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            text = h.get_text().strip()
            if text and 3 < len(text) < 150:
                headings.append(text)
                
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text().strip()
            if text and 20 < len(text) < 1000:
                paragraphs.append(text)
                
        raw_text = " ".join(paragraphs)
        content_excerpt = raw_text[:3000] + "..." if len(raw_text) > 3000 else raw_text
        
        return {
            "url": url,
            "title": title,
            "headings": headings[:15],
            "paragraphs": paragraphs[:15],
            "contentExcerpt": content_excerpt,
            "rawHtml": html
        }
    except Exception as e:
        print(f"Error crawling single page {url}: {e}")
        return None

def crawl_website(start_url: str) -> list:
    crawled_pages = []
    visited_urls = set()
    urls_to_visit = [normalize_url(start_url)]
    
    try:
        url_obj = urlparse(start_url)
        origin = f"{url_obj.scheme}://{url_obj.netloc}"
    except Exception:
        print(f"Invalid start URL: {start_url}")
        return []
        
    max_pages = 7
    page_count = 0
    
    while urls_to_visit and page_count < max_pages:
        current_url = urls_to_visit.pop(0)
        if current_url in visited_urls:
            continue
            
        visited_urls.add(current_url)
        print(f"Crawling: {current_url}")
        
        page_data = crawl_single_page(current_url)
        if page_data:
            raw_html = page_data.pop("rawHtml", None) # remove rawHtml from output
            crawled_pages.append(page_data)
            page_count += 1
            
            # If we are at the homepage, discover sub-links
            if normalize_url(current_url) == normalize_url(start_url) and raw_html:
                links = extract_links(raw_html, origin, start_url)
                for link in links:
                    if link not in visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)
                        
    return crawled_pages
