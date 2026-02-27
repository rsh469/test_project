"""
Tea flavor descriptor scrapers from multiple sources.
"""

import re
import time
import random
import logging
from dataclasses import dataclass, field
from typing import Optional
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@dataclass
class ReviewEntry:
    source: str
    tea_name: str
    text: str
    url: str = ""
    rating: Optional[float] = None


def _get(url: str, params: dict = None, timeout: int = 15) -> Optional[requests.Response]:
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
        resp.raise_for_status()
        time.sleep(random.uniform(0.8, 1.8))
        return resp
    except Exception as e:
        logger.warning("GET %s failed: %s", url, e)
        return None


# ---------------------------------------------------------------------------
# Steepster
# ---------------------------------------------------------------------------

def scrape_steepster(tea_name: str, max_pages: int = 3) -> list[ReviewEntry]:
    """Search Steepster.com for tea reviews."""
    results = []
    search_url = "https://steepster.com/teas"
    resp = _get(search_url, params={"q": tea_name})
    if not resp:
        return results

    soup = BeautifulSoup(resp.text, "lxml")
    tea_links = []
    for a in soup.select("a.name"):
        href = a.get("href", "")
        if href:
            tea_links.append(("https://steepster.com" + href, a.get_text(strip=True)))
        if len(tea_links) >= 5:
            break

    for tea_url, tea_title in tea_links:
        for page in range(1, max_pages + 1):
            page_url = tea_url + f"?page={page}"
            r = _get(page_url)
            if not r:
                break
            s = BeautifulSoup(r.text, "lxml")
            for entry in s.select("div.entry-body"):
                text = entry.get_text(separator=" ", strip=True)
                if len(text) > 40:
                    results.append(ReviewEntry(
                        source="Steepster",
                        tea_name=tea_title,
                        text=text,
                        url=page_url,
                    ))

    logger.info("Steepster: %d reviews for '%s'", len(results), tea_name)
    return results


# ---------------------------------------------------------------------------
# RateTea
# ---------------------------------------------------------------------------

def scrape_ratetea(tea_name: str) -> list[ReviewEntry]:
    """Search RateTea.net for tea reviews."""
    results = []
    resp = _get("https://ratetea.com/search/", params={"query": tea_name, "searchtype": "tea"})
    if not resp:
        return results

    soup = BeautifulSoup(resp.text, "lxml")
    tea_links = []
    for a in soup.select("a[href*='/tea/']"):
        href = a.get("href", "")
        if re.match(r"/tea/[\w-]+/\d+/", href):
            tea_links.append(("https://ratetea.com" + href, a.get_text(strip=True)))
        if len(tea_links) >= 4:
            break

    for tea_url, tea_title in tea_links:
        r = _get(tea_url)
        if not r:
            continue
        s = BeautifulSoup(r.text, "lxml")
        # Grab description paragraphs
        for p in s.select("div#description p, div.review p, div.reviewtext"):
            text = p.get_text(separator=" ", strip=True)
            if len(text) > 40:
                results.append(ReviewEntry(
                    source="RateTea",
                    tea_name=tea_title,
                    text=text,
                    url=tea_url,
                ))

    logger.info("RateTea: %d entries for '%s'", len(results), tea_name)
    return results


# ---------------------------------------------------------------------------
# Reddit (r/tea) via public JSON API
# ---------------------------------------------------------------------------

def scrape_reddit(tea_name: str, limit: int = 25) -> list[ReviewEntry]:
    """Search Reddit r/tea for posts mentioning the tea."""
    results = []
    url = "https://www.reddit.com/r/tea/search.json"
    params = {
        "q": tea_name,
        "restrict_sr": "1",
        "sort": "relevance",
        "limit": limit,
        "t": "all",
    }
    headers = {**HEADERS, "User-Agent": "TeaFlavorBot/1.0 (educational project)"}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning("Reddit search failed: %s", e)
        return results

    for post in data.get("data", {}).get("children", []):
        p = post.get("data", {})
        title = p.get("title", "")
        selftext = p.get("selftext", "")
        combined = f"{title}. {selftext}".strip()
        if len(combined) > 40:
            results.append(ReviewEntry(
                source="Reddit r/tea",
                tea_name=title,
                text=combined,
                url="https://reddit.com" + p.get("permalink", ""),
            ))

    logger.info("Reddit: %d posts for '%s'", len(results), tea_name)
    return results


# ---------------------------------------------------------------------------
# TeaVivre (English product descriptions)
# ---------------------------------------------------------------------------

def scrape_teavivre(tea_name: str) -> list[ReviewEntry]:
    """Scrape TeaVivre product descriptions."""
    results = []
    resp = _get("https://www.teavivre.com/catalog/search/", params={"q": tea_name})
    if not resp:
        return results

    soup = BeautifulSoup(resp.text, "lxml")
    product_links = []
    for a in soup.select("a.product-item-link, h2.product-name a, a[href*='teavivre.com']"):
        href = a.get("href", "")
        if "teavivre.com" in href and href not in product_links:
            product_links.append(href)
        if len(product_links) >= 3:
            break

    for link in product_links:
        r = _get(link)
        if not r:
            continue
        s = BeautifulSoup(r.text, "lxml")
        for div in s.select("div.product.attribute.description, div#description, div.std"):
            text = div.get_text(separator=" ", strip=True)
            if len(text) > 40:
                results.append(ReviewEntry(
                    source="TeaVivre",
                    tea_name=tea_name,
                    text=text,
                    url=link,
                ))

    logger.info("TeaVivre: %d entries for '%s'", len(results), tea_name)
    return results


# ---------------------------------------------------------------------------
# Yunnan Sourcing (English product descriptions)
# ---------------------------------------------------------------------------

def scrape_yunnansourcing(tea_name: str) -> list[ReviewEntry]:
    """Scrape Yunnan Sourcing product descriptions."""
    results = []
    resp = _get(
        "https://yunnansourcing.com/search",
        params={"type": "product", "q": tea_name},
    )
    if not resp:
        return results

    soup = BeautifulSoup(resp.text, "lxml")
    product_links = []
    for a in soup.select("a.product-grid-item, a[href*='/products/']"):
        href = a.get("href", "")
        if href and "/products/" in href:
            full = href if href.startswith("http") else "https://yunnansourcing.com" + href
            if full not in product_links:
                product_links.append(full)
        if len(product_links) >= 3:
            break

    for link in product_links:
        r = _get(link)
        if not r:
            continue
        s = BeautifulSoup(r.text, "lxml")
        for div in s.select("div.product-single__description, div#description, div.rte"):
            text = div.get_text(separator=" ", strip=True)
            if len(text) > 40:
                results.append(ReviewEntry(
                    source="Yunnan Sourcing",
                    tea_name=tea_name,
                    text=text,
                    url=link,
                ))

    logger.info("YunnanSourcing: %d entries for '%s'", len(results), tea_name)
    return results


# ---------------------------------------------------------------------------
# Tea blog / article search via DuckDuckGo HTML
# ---------------------------------------------------------------------------

def scrape_web_search(tea_name: str, max_results: int = 5) -> list[ReviewEntry]:
    """
    Lightweight web search via DuckDuckGo HTML for tea flavor descriptions.
    Fetches top pages and extracts relevant paragraphs.
    """
    results = []
    query = f"{tea_name} tea flavor aroma tasting notes"
    resp = _get("https://html.duckduckgo.com/html/", params={"q": query})
    if not resp:
        return results

    soup = BeautifulSoup(resp.text, "lxml")
    links = []
    for a in soup.select("a.result__url, a.result__a"):
        href = a.get("href", "")
        if href.startswith("http") and "duckduckgo" not in href:
            links.append(href)
        if len(links) >= max_results:
            break

    for link in links:
        r = _get(link, timeout=12)
        if not r:
            continue
        try:
            s = BeautifulSoup(r.text, "lxml")
            # Remove nav/footer/ads
            for tag in s.select("nav, footer, header, script, style, aside"):
                tag.decompose()
            paragraphs = s.find_all("p")
            text_chunks = [p.get_text(separator=" ", strip=True) for p in paragraphs]
            combined = " ".join(c for c in text_chunks if len(c) > 60)
            if combined:
                results.append(ReviewEntry(
                    source="Web Article",
                    tea_name=tea_name,
                    text=combined[:3000],
                    url=link,
                ))
        except Exception as e:
            logger.debug("Failed parsing %s: %s", link, e)

    logger.info("Web search: %d pages for '%s'", len(results), tea_name)
    return results


# ---------------------------------------------------------------------------
# Main aggregation entry point
# ---------------------------------------------------------------------------

def collect_all(tea_name: str, progress_callback=None) -> list[ReviewEntry]:
    """Run all scrapers and return combined results."""
    all_reviews: list[ReviewEntry] = []

    scrapers = [
        ("Reddit r/tea", lambda: scrape_reddit(tea_name)),
        ("Steepster", lambda: scrape_steepster(tea_name)),
        ("RateTea", lambda: scrape_ratetea(tea_name)),
        ("TeaVivre", lambda: scrape_teavivre(tea_name)),
        ("Yunnan Sourcing", lambda: scrape_yunnansourcing(tea_name)),
        ("Web Search", lambda: scrape_web_search(tea_name)),
    ]

    for name, fn in scrapers:
        if progress_callback:
            progress_callback(f"Сканирую {name}...")
        try:
            entries = fn()
            all_reviews.extend(entries)
        except Exception as e:
            logger.error("Scraper %s crashed: %s", name, e)

    return all_reviews
