# 🕷️ Web Scraping — Cheatsheet

## Core Libraries

```bash
pip install requests beautifulsoup4 lxml selenium playwright httpx
playwright install chromium   # download browser binary
```

---

## requests — HTTP Requests

```python
import requests

# GET request
r = requests.get(url, headers=headers, params={"page": 2}, timeout=10)
r.raise_for_status()          # raise HTTPError for 4xx/5xx
r.status_code                 # 200, 404, etc.
r.text                        # response as string
r.content                     # response as bytes
r.json()                      # parse JSON response

# POST request
r = requests.post(url, data={"key": "val"}, json={"key": "val"})

# Session (reuse connections, persist cookies)
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
r = session.get(url)

# Standard headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://google.com",
}
```

---

## BeautifulSoup — HTML Parsing

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_string, "html.parser")  # or "lxml" (faster)

# Find elements
soup.find("h1")                           # first <h1>
soup.find("div", class_="product")        # first div with class product
soup.find("a", {"data-id": "123"})        # by attribute
soup.find_all("a")                        # all <a> tags
soup.find_all("p", limit=5)              # first 5

# CSS selectors (most flexible)
soup.select("div.card")                   # all divs with class card
soup.select("ul > li")                    # li directly inside ul
soup.select("a[href^='https']")          # a with href starting with https
soup.select_one(".price")                 # first match

# Extract text and attributes
el.get_text(strip=True)                   # text content, whitespace stripped
el.get_text(separator="\n")              # with newlines
el["href"]                                # get attribute value
el.get("href", "")                        # safe get with default
el.attrs                                  # dict of all attributes

# Navigate tree
el.parent                                 # parent element
el.children                               # direct children (generator)
el.next_sibling                           # next sibling element
el.find_next("p")                         # next <p> anywhere in doc
```

---

## Pagination Pattern

```python
import requests
from bs4 import BeautifulSoup
import time

def scrape_all_pages(base_url, max_pages=50):
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0"
    results = []

    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        try:
            r = session.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            items = soup.select("div.item")
            if not items:       # ← stop when no more items
                print(f"No items on page {page}, stopping")
                break

            for item in items:
                results.append({"text": item.get_text(strip=True)})

            # Check for next page button
            next_btn = soup.select_one("a.next-page")
            if not next_btn:
                break

        except requests.RequestException as e:
            print(f"Error page {page}: {e}")

        time.sleep(1)   # rate limiting

    return results
```

---

## Selenium — JavaScript Pages

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup headless Chrome
opts = Options()
opts.add_argument("--headless"); opts.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=opts)

try:
    driver.get(url)

    # Wait for element
    el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.product"))
    )

    # Find elements
    driver.find_element(By.ID, "search-input").send_keys("laptop")
    driver.find_element(By.CSS_SELECTOR, "button.submit").click()

    # Scroll to bottom (load more items)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Get page source for BeautifulSoup
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

finally:
    driver.quit()
```

---

## Data Cleaning Patterns

```python
import re

# Remove currency symbols and commas: "$1,234.56" → 1234.56
price = float(re.sub(r"[^\d.]", "", "$1,234.56"))

# Parse pandas HTML tables
import pandas as pd
tables = pd.read_html(html_string)   # list of DataFrames

# Clean text
text = soup.get_text(separator="\n", strip=True)
text = re.sub(r"\s+", " ", text).strip()
```

---

## Error Handling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Automatic retry with backoff
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Per-request error handling
try:
    r = session.get(url, timeout=10)
    r.raise_for_status()
except requests.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
except requests.ConnectionError:
    print("Connection failed")
except requests.Timeout:
    print("Request timed out")
```

---

## robots.txt Quick Check

```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://example.com/robots.txt")
rp.read()

allowed = rp.can_fetch("*", "https://example.com/products")
print(f"Can scrape /products: {allowed}")
```

---

## Golden Rules

1. Always set a browser-like User-Agent — default requests UA is blocked by many sites
2. Always rate-limit: `time.sleep(1)` minimum between requests
3. Check robots.txt and ToS before scraping
4. Use `raise_for_status()` to catch HTTP errors immediately
5. Use Selenium/Playwright only when necessary — static HTML scraping is 100x faster
