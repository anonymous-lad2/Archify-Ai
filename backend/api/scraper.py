import requests
from bs4 import BeautifulSoup
from readability import Document
import time

def scrape_page(url: str) -> str:
    """
    Scrape and extract main content from a page.
    Uses readability to get the core content, removes noise.
    Handles 403 errors and other common blocks gracefully.
    """
    try:
        # Add delay to avoid rate limiting
        time.sleep(0.5)
        
        # Better headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1'
        }
        
        response = requests.get(url, timeout=15, allow_redirects=True, headers=headers)
        
        # Skip if forbidden or too restricted
        if response.status_code == 403:
            print(f"  ⚠️ Access forbidden (403): {url[:50]}...")
            return ""
        
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
            # Fallback if readability fails - use raw HTML
            html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts/styles and other noise
        for tag in soup(["script", "style", "noscript", "meta", "link", "img", "iframe", "nav"]):
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
        print(f"  ✗ Timeout: {url[:50]}...")
        return ""
    except requests.exceptions.HTTPError as e:
        print(f"  ✗ HTTP error {e.response.status_code}: {url[:50]}...")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Request error: {str(e)[:50]}...")
        return ""
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:50]}...")
        return ""

    
def scrape_multiple(links: list[str]) -> str:
    """
    Scrape multiple links and combine their content.
    Filters out empty results and provides status updates.
    """
    if not links:
        print("⚠️ No links to scrape")
        return ""
    
    print(f"\n📄 Scraping {len(links)} links...")
    content = []
    successful = 0

    for i, link in enumerate(links, 1):
        try:
            page_text = scrape_page(link)
            if page_text:  # Only add if we got valid content
                content.append(f"[Source {i}]\n{page_text}")
                successful += 1
            
        except Exception as e:
            print(f"  ✗ Error processing link: {e}")
            continue

    if not content:
        print("⚠️ No content extracted from any links")
        print("💡 Tip: Using fallback architecture for response\n")
        return ""
    
    combined = "\n\n---\n\n".join(content)
    print(f"✅ Successfully scraped {successful}/{len(links)} pages, total {len(combined)} chars\n")
    return combined