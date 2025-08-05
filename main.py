import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urljoin, urlparse
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from migration.page import Page  # asumsi model SQLAlchemy ada di sini
from embedding import get_embedding  # fungsi dari sebelumnya
from estimate_token import count_tokens
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from playwright.sync_api import sync_playwright
import re

engine = create_engine("postgresql://mukhtada:password@localhost:5432/chatbot")
Session = sessionmaker(bind=engine)
session = Session()

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com",
}


visited = set()


def fetch_dynamic_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com",
            }
        )

        try:
            page.goto(url, timeout=30000, wait_until="networkidle")
            # page.wait_for_load_state("networkidle", timeout=30000)
            html = page.content()
        except Exception as e:
            print(f"❌ Gagal render {url}: {e}")
            html = ""
        finally:
            browser.close()
        return html


# Setup headless Chrome
def get_headless_driver():
    options = Options()
    options.headless = True
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def wait_for_page_load(url, driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except TimeoutException:
        print(f"⚠️ Timeout while loading {url}")
        return None
    except Exception as e:
        print(f"❌ Error loading {url}: {e}")
        return None


def extract_clean_text_with_images(soup):
    try:
        # print(soup)
        # Hapus elemen yang tidak dibutuhkan
        for tag in soup.find_all(["script", "style", "noscript", "svg"]):
            tag.decompose()

        # Ambil body atau seluruh dokumen
        main = soup.body or soup
        output_parts = []

        for element in main.descendants:
            if isinstance(element, NavigableString):
                text = element.strip()
                if text:
                    output_parts.append(text)
            elif isinstance(element, Tag) and element.name == "img":
                output_parts.append(str(element))

        return " ".join(output_parts)

    except Exception as e:
        print("[ERROR EXTRACTING HTML]", e)
        return ""


def is_valid_url(href, base=None):
    parsed = urlparse(href)
    return parsed.scheme in ["http", "https"] and (base is None or base in href)


EXCLUDE_PATTERNS = [
    # r"/browse",
    r"/policies",
    r"/contact",
    r"/for-authors",
    r"/for-reviewers",
    # r"/about",
    # r"per_page",
]


def should_skip_url(url: str):
    if "neliti.com/journals" in url:
        for pattern in EXCLUDE_PATTERNS:
            if re.search(pattern, url):
                return True
    return False


def crawl_static(url: str, depth: int = 0, max_depth: int = 2):
    if depth > max_depth:  # or url in visited or should_skip_url(url):
        return

    visited.add(url)
    print(f"[{depth}] Crawling: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Gagal fetch {url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Cek apakah URL sudah ada di database
    content = extract_clean_text_with_images(soup)
    if len(content) < 100:
        return  # skip konten kosong

    if not session.query(Page).filter_by(url=url).first():
        embedding = get_embedding(content.lower())

        # The line `token_count = count_tokens(content)` is
        # calculating the number of tokens in the content extracted
        # from a webpage. This function likely tokenizes the content
        # (splitting it into individual words or tokens) and then
        # counts the total number of tokens present in the content.
        # This count can be useful for various purposes such as
        # analyzing the text complexity, determining the length of
        # the content, or for any other text processing tasks that
        # require token-level analysis.

        token_count = count_tokens(content)
        page = Page(
            url=url,
            content=content,
            embedding=embedding,
            fetched_at=datetime.utcnow(),
            title=soup.title.string if soup.title else None,
            token=token_count,
            status=200,
        )
        session.add(page)
        session.commit()
        print(f"✅ Simpan: {url} ({token_count} tokens)")

    # Rekursif ke link lain
    for link in soup.find_all("a", href=True):
        href = link["href"]
        next_url = urljoin(url, href)

        if is_valid_url(next_url, base=url):
            crawl(next_url, depth + 1, max_depth)


def crawl(url: str, depth: int = 0, max_depth: int = 2):
    if (
        depth > max_depth
        or url in visited
        or session.query(Page).filter_by(url=url).first()
        # or should_skip_url(url)
    ):
        return

    visited.add(url)
    print(f"[{depth}] Crawling (JS): {url}")

    try:
        soup = BeautifulSoup(fetch_dynamic_page(url), "html.parser")
    except Exception as e:
        print("[ERROR]: ", e)

    # Cek apakah URL sudah ada di database
    if not session.query(Page).filter_by(url=url).first():
        # print(soup)
        content = extract_clean_text_with_images(soup)
        if len(content) < 100:
            return  # skip konten kosong

        embedding = get_embedding(content)
        token_count = count_tokens(content)
        page = Page(
            url=url,
            content=content,
            embedding=embedding,
            fetched_at=datetime.utcnow(),
            title=soup.title.string if soup.title else None,
            token=token_count,
            status=200,
        )
        session.add(page)
        session.commit()
        print(f"✅ Simpan: {url} ({token_count} tokens)")

    # Rekursif ke link lain
    for link in soup.find_all("a", href=True):
        href = link["href"]
        next_url = urljoin(url, href)

        if is_valid_url(next_url, base=url):
            # if url not in visited:
            crawl(next_url, depth + 1, max_depth)
