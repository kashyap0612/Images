from playwright.sync_api import sync_playwright
from urllib.parse import quote, urlparse

def filter_urls(links: list, limit: int) -> list:
    ignored_domains = [
        "google.", "youtube.com", "facebook.com", "twitter.com", 
        "instagram.com", "linkedin.com", "pinterest.com", "github.com", 
        "wikipedia.org", "w3schools.com", "reddit.com", "quora.com",
        "stackoverflow.com", "schema.org", "gravatar.com"
    ]
    ignored_extensions = (".pdf", ".zip", ".exe", ".png", ".jpg", ".jpeg", ".svg", ".gif", ".json", ".txt")
    
    filtered = []
    seen_domains = set()
    
    for link in links:
        parsed = urlparse(link)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # Filter domains
        if any(ignored in domain for ignored in ignored_domains):
            continue
            
        # Filter files/extensions
        if path.endswith(ignored_extensions):
            continue
            
        # Prevent domain duplicates in the same run to maximize diversity of sources
        if domain not in seen_domains:
            seen_domains.add(domain)
            filtered.append(link)
            
        if len(filtered) >= limit:
            break
            
    return filtered

def search_google_links(query: str, limit: int = 10) -> list:
    """
    Searches Google for the target query and uses heuristic filters
    to extract a set of high-quality website URLs.
    """
    search_url = f"https://www.google.com/search?q={quote(query)}"
    links = []
    
    with sync_playwright() as p:
        # Launch browser headlessly for server/background environment
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        try:
            print(f"Searching Google for: '{query}'")
            page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
            
            # Extract all anchor links
            hrefs = page.evaluate("""
            () => {
                return [...document.querySelectorAll("a")]
                    .map(a => a.href)
                    .filter(href => href.startsWith("http"));
            }
            """)
            links = list(dict.fromkeys(hrefs))
        except Exception as e:
            print(f"Error during Google search automation: {e}")
        finally:
            browser.close()
            
    return filter_urls(links, limit)
