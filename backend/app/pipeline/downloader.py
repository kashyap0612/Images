import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

def get_page_html(url: str) -> str:
    """
    Launches a headless browser to retrieve HTML content.
    Uses 'domcontentloaded' to yield results quickly.
    """
    html = ""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        try:
            print(f"Opening webpage: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            html = page.content()
        except Exception as e:
            print(f"Failed to load webpage {url}: {e}")
        finally:
            browser.close()
    return html

def extract_image_urls(page_url: str, html: str) -> list:
    """
    Parses HTML to find absolute and relative image urls.
    """
    if not html:
        return []
        
    soup = BeautifulSoup(html, "html.parser")
    raw_urls = set()
    
    # 1. Inspect image tag attributes
    for img in soup.find_all("img"):
        for attr in ["src", "data-src", "data-lazy-src", "data-original"]:
            val = img.get(attr)
            if val:
                raw_urls.add(val.strip())
                
    # 2. Inspect preloaded links
    for link in soup.find_all("link"):
        if link.get("as") == "image":
            href = link.get("href")
            if href:
                raw_urls.add(href.strip())
                
    # 3. Inspect OpenGraph meta images
    for meta in soup.find_all("meta"):
        if meta.get("property") == "og:image":
            content = meta.get("content")
            if content:
                raw_urls.add(content.strip())
                
    # 4. Regex fallback for inline image files
    pattern = r'https?://[^\s"\']+\.(?:jpg|jpeg|png|webp)'
    for match in re.finditer(pattern, html, re.IGNORECASE):
        raw_urls.add(match.group(0))
        
    # Resolve relative paths
    resolved_urls = []
    for raw in raw_urls:
        if raw.startswith("data:image"): # Skip base64 strings
            continue
        # Convert relative to absolute URL using base page url
        abs_url = urljoin(page_url, raw)
        resolved_urls.append(abs_url)
        
    return list(dict.fromkeys(resolved_urls))

def download_images(urls: list, output_dir: str, limit_per_run: int = 50) -> list:
    """
    Downloads list of image urls into output_dir. 
    Filters out SVGs, tracking pixels (<2KB), and obvious UI icons.
    """
    os.makedirs(output_dir, exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    downloaded_paths = []
    count = 0
    
    # Skip standard UI terms to focus on rich datasets
    ignored_keywords = [
        "profile-", "favicon", "apple-touch-icon", "opengraph",
        "adzerk", "logo", "icon", "banner", "button", "avatar"
    ]
    
    for url in urls:
        if count >= limit_per_run:
            break
            
        url_lower = url.lower()
        if any(keyword in url_lower for keyword in ignored_keywords):
            continue
            
        ext = ".jpg"
        if ".webp" in url_lower:
            ext = ".webp"
        elif ".png" in url_lower:
            ext = ".png"
        elif ".jpeg" in url_lower:
            ext = ".jpeg"
            
        try:
            response = requests.get(url, headers=headers, timeout=8, stream=True)
            if response.status_code == 200:
                filename = f"image_{count+1}{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Verify downloaded file size is > 2KB to filter tracking pixels
                if os.path.exists(filepath) and os.path.getsize(filepath) > 2048:
                    downloaded_paths.append((filepath, url))
                    count += 1
                else:
                    if os.path.exists(filepath):
                        os.remove(filepath)
        except Exception as e:
            print(f"Failed download for {url}: {e}")
            
    return downloaded_paths
