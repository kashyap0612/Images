from ddgs import DDGS
from urllib.parse import urlparse

def filter_urls(links: list, limit: int) -> list:
    ignored_domains = [
        "google.", "youtube.com", "facebook.com", "twitter.com", 
        "instagram.com", "linkedin.com", "pinterest.com", "github.com", 
        "wikipedia.org", "w3schools.com", "reddit.com", "quora.com",
        "stackoverflow.com", "schema.org", "gravatar.com", "duckduckgo.com"
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
    Searches DuckDuckGo using the robust ddgs API.
    Bypasses automated browser checks and blocks entirely.
    """
    links = []
    try:
        print(f"Searching DuckDuckGo API for: '{query}'")
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=limit * 2)
            if results:
                for r in results:
                    href = r.get("href")
                    if href:
                        links.append(href)
                        
        print(f"DuckDuckGo API extracted links: {links}")
    except Exception as e:
        print(f"Error during DuckDuckGo API search: {e}")
        
    return filter_urls(links, limit)
