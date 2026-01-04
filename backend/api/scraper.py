import requests
from bs4 import BeautifulSoup
from readability import Document
import time

def scrape_page(url: str) -> str:
    """
    Scrape and extract main content from a page.
    Uses readability to get the core content, removes noise.
    """
    try:
        # Add delay to avoid rate limiting
        time.sleep(0.3)
        
        response = requests.get(url, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # Check if response has content
        if not response.text or len(response.text) < 100:
            print(f"  ✗ No content from {url}")
            return ""
        
        # Use readability to extract main article content
        try:
            doc = Document(response.text)
            html = doc.summary()
        except:
            # Fallback if readability fails
            html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts/styles and other noise
        for tag in soup(["script", "style", "noscript", "meta", "link", "img"]):
            tag.decompose()

        # Extract text with proper spacing
        text = soup.get_text(separator=" ", strip=True)
        
        # Clean up whitespace
        cleaned = " ".join(text.split())
        
        # Return if content is substantial, else return empty
        if len(cleaned) > 150:
            print(f"  ✓ Extracted {len(cleaned)} chars from {url[:50]}...")
            return cleaned[:6000]  # limit to avoid overload
        else:
            print(f"  ✗ Insufficient content ({len(cleaned)} chars) from {url}")
            return ""

    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout: {url}")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Request error: {e}")
        return ""
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return ""

    
def scrape_multiple(links: list[str]) -> str:
    """
    Scrape multiple links and combine their content.
    Filters out empty results.
    """
    if not links:
        print("⚠️ No links to scrape")
        return ""
    
    print(f"\n📄 Scraping {len(links)} links...")
    content = []

    for i, link in enumerate(links, 1):
        try:
            page_text = scrape_page(link)
            if page_text:  # Only add if we got valid content
                content.append(f"[Source {i}]\n{page_text}")
            
        except Exception as e:
            print(f"  ✗ Error processing link: {e}")
            continue

    if not content:
        print("⚠️ No content extracted from any links")
        return ""
    
    combined = "\n\n---\n\n".join(content)
    print(f"✅ Successfully scraped {len(content)} pages, total {len(combined)} chars\n")
    return combined