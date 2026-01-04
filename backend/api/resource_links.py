from backend.utils.llm_client import call_llm
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
import re

def get_resource_sources(topic: str, level: str) -> list[str]:
    prompt = f"""
    List 5-7 authoritative learning sources (website or organization names only)
    to learn {level} architecture of {topic}.
    Return one source per line.
    No URLs.
    No extra text.
    """

    try:
        response = call_llm(prompt)
        sources = [line.strip() for line in response.split("\n") if line.strip()]
        return sources if sources else get_fallback_sources()
    except Exception as e:
        print(f"Error getting sources from LLM: {e}")
        return get_fallback_sources()


def get_fallback_sources() -> list[str]:
    """Fallback sources when LLM fails"""
    return [
        "Medium",
        "Dev.to",
        "GitHub",
        "Stack Overflow",
        "ArchiWiki",
        "YouTube"
    ]


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid and from a content source (not ads/tracking).
    """
    if not url or len(url) < 10:
        return False
    
    blocked_domains = ['google.', 'facebook.', 'ads.', 'doubleclick.', 'amazon-adsystem.', 'pagead2.', 'twitter.com/i/']
    
    # Check blocked domains
    for domain in blocked_domains:
        if domain in url.lower():
            return False
    
    # Check if it's a valid URL format
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc, len(result.netloc) > 3])
    except:
        return False


def fetch_direct_links(query: str, max_results: int = 5) -> list[str]:
    """
    Fetch direct content links from Google search results.
    Returns actual resource URLs, not search result pages.
    """
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = set()
        
        # Extract direct links from Google search results
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Extract URL from Google's redirect format
            if href.startswith('/url?q='):
                try:
                    # Decode the URL and extract the actual link
                    actual_url = unquote(href.split('/url?q=')[1].split('&')[0])
                    if is_valid_url(actual_url):
                        links.add(actual_url)
                except:
                    continue
            
            # Also capture direct http/https links
            elif href.startswith('http') and 'google' not in href:
                if is_valid_url(href):
                    links.add(href)
        
        result = list(links)[:max_results]
        print(f"✓ Found {len(result)} links for: {query}")
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching links for '{query}': {e}")
        return []
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return []


def generate_fallback_links(topic: str, level: str) -> list[str]:
    """
    Generate direct links to well-known documentation and resources
    when search fails.
    """
    topic_lower = topic.lower()
    fallback_urls = []
    
    # Popular documentation sources
    docs = {
        'messaging': [
            'https://www.whatsapp.com/business/guide/',
            'https://www.twilio.com/docs/messaging',
            'https://firebase.google.com/docs/cloud-messaging'
        ],
        'app': [
            'https://developer.android.com/guide/topics/manifest',
            'https://developer.apple.com/documentation/',
            'https://web.dev/'
        ],
        'system': [
            'https://en.wikipedia.org/wiki/Scalable_system',
            'https://www.nginx.com/blog/',
            'https://aws.amazon.com/architecture/'
        ],
        'architecture': [
            'https://microservices.io/',
            'https://www.nginx.com/blog/introduction-to-microservices/',
            'https://martinfowler.com/articles/microservices.html'
        ]
    }
    
    # Match keywords
    for key, urls in docs.items():
        if key in topic_lower:
            fallback_urls.extend(urls)
    
    # Add generic resources
    fallback_urls.extend([
        f'https://medium.com/search?q={topic_lower} {level} architecture',
        f'https://dev.to/search?q={topic_lower} architecture',
        'https://github.com/search?type=repositories',
    ])
    
    return fallback_urls[:7]


def get_resource_links(topic: str, level: str) -> list[str]:
    """
    Get direct content links that contain actual information about the topic.
    Uses multiple strategies with fallback mechanisms.
    """
    print(f"\n🔍 Searching for links on: {topic} ({level})...")
    
    sources = get_resource_sources(topic, level)
    print(f"📚 Sources: {', '.join(sources[:3])}...")
    
    all_links = {}
    
    # Try different search strategies to find best links
    search_queries = [
        (sources, f"{{source}} {topic} architecture {level}"),
        (sources, f"{{source}} {topic} {level} tutorial"),
        (sources, f"{{source}} {topic} documentation"),
        ([], f"{topic} {level} architecture guide"),
        ([], f"{topic} architecture design patterns"),
    ]
    
    for sources_list, query_template in search_queries:
        if sources_list:
            # Search for each source
            for source in sources_list[:3]:  # Limit to top 3 sources
                query = query_template.replace("{source}", source)
                direct_links = fetch_direct_links(query, max_results=2)
                for link in direct_links:
                    if link not in all_links:
                        all_links[link] = True
        else:
            # Generic search
            direct_links = fetch_direct_links(query_template, max_results=3)
            for link in direct_links:
                if link not in all_links:
                    all_links[link] = True
        
        if len(all_links) >= 5:
            break
    
    # If we got results, return them
    if all_links:
        result = list(all_links.keys())[:7]
        print(f"✅ Got {len(result)} valid links\n")
        return result
    
    # Fallback: Generate direct links to known resources
    print("⚠️ No links found from search, using fallback links...")
    fallback = generate_fallback_links(topic, level)
    print(f"✅ Using {len(fallback)} fallback links\n")
    return fallback[:7]
