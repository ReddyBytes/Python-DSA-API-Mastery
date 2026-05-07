# Web Scraping — Practice

## Quick Index

| # | Chapter | Topic | Difficulty |
|---|---------|-------|------------|
| Q1 | Ch1 requests + BS4 | Basic GET request with headers | 🟢 Basic |
| Q2 | Ch1 requests + BS4 | Parse HTML — find and find_all | 🟢 Basic |
| Q3 | Ch1 requests + BS4 | CSS selectors | 🟢 Basic |
| Q4 | Ch1 requests + BS4 | Extract text vs attributes | 🟢 Basic |
| Q5 | Ch1 requests + BS4 | raise_for_status and response properties | 🟢 Basic |
| Q6 | Ch2 Multiple Pages | Pagination loop with query params | 🟡 Intermediate |
| Q7 | Ch2 Multiple Pages | Relative URL construction | 🟡 Intermediate |
| Q8 | Ch2 Multiple Pages | Rate limiting with time.sleep | 🟢 Basic |
| Q9 | Ch2 Multiple Pages | Error handling 404 and 500 | 🟡 Intermediate |
| Q10 | Ch2 Multiple Pages | Retry with exponential backoff | 🟠 Advanced |
| Q11 | Ch3 JavaScript Pages | Why requests fails on JS pages | 🟢 Basic |
| Q12 | Ch3 JavaScript Pages | Selenium headless Chrome setup | 🟡 Intermediate |
| Q13 | Ch3 JavaScript Pages | WebDriverWait — wait for selector | 🟡 Intermediate |
| Q14 | Ch3 JavaScript Pages | Playwright async basics | 🟠 Advanced |
| Q15 | Ch3 JavaScript Pages | Extract rendered page via BS4 | 🟡 Intermediate |
| Q16 | Ch4 Ethical & Legal | robots.txt parsing | 🟢 Basic |
| Q17 | Ch4 Ethical & Legal | User-Agent etiquette | 🟢 Basic |
| Q18 | Ch4 Ethical & Legal | When scraping is and isn't legal | 🟢 Basic |
| Q19 | Ch5 requests.Session | Session for cookie persistence | 🟡 Intermediate |
| Q20 | Ch5 requests.Session | Shared headers on a Session | 🟢 Basic |
| Q21 | Ch5 requests.Session | Connection pooling benefit | 🟡 Intermediate |
| Q22 | Ch6 Structured Data | Scrape to list of dicts | 🟡 Intermediate |
| Q23 | Ch6 Structured Data | pandas DataFrame from scraped data | 🟡 Intermediate |
| Q24 | Ch6 Structured Data | Save to CSV and JSON | 🟢 Basic |
| Q25 | Ch6 Structured Data | Deduplication of scraped records | 🟡 Intermediate |

---

## Ch1 — requests + BeautifulSoup

### Q1 · Ch1 — Basic GET Request with Headers 🟢

Write a function `fetch_page(url)` that sends a GET request with a browser-like User-Agent header, a 10-second timeout, and returns the response text. Raise an exception for any HTTP error status.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>Use requests.get() with headers={"User-Agent": "..."} and call raise_for_status() before returning response.text</details>
<details><summary>✅ Answer</summary>

```python
import requests

def fetch_page(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)  # ← 10s timeout
    response.raise_for_status()   # ← raises HTTPError for 4xx/5xx
    return response.text
```

**Why:** Setting a real browser User-Agent prevents many sites from blocking you; raise_for_status() catches errors early before you try to parse bad HTML.
</details>

---

### Q2 · Ch1 — Parse HTML with find and find_all 🟢

Given the HTML string below, use BeautifulSoup to (a) find the first `<h1>` tag text, and (b) collect a list of all `<a>` href values.

```html
<html><body>
  <h1>Products</h1>
  <a href="/item/1">Laptop</a>
  <a href="/item/2">Mouse</a>
</body></html>
```

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>soup.find("h1").get_text() and [a["href"] for a in soup.find_all("a")]</details>
<details><summary>✅ Answer</summary>

```python
from bs4 import BeautifulSoup

html = """<html><body>
  <h1>Products</h1>
  <a href="/item/1">Laptop</a>
  <a href="/item/2">Mouse</a>
</body></html>"""

soup = BeautifulSoup(html, "html.parser")

title = soup.find("h1").get_text(strip=True)          # ← first <h1>
links = [a["href"] for a in soup.find_all("a")]        # ← all href values
print(title)   # "Products"
print(links)   # ["/item/1", "/item/2"]
```

**Why:** `find()` returns the first match; `find_all()` returns a list of all matches — these are the two core BS4 methods you use 90% of the time.
</details>

---

### Q3 · Ch1 — CSS Selectors 🟢

Using the product HTML below, use `soup.select()` to extract all product names and prices into a list of dicts.

```html
<div class="product-card">
  <h2 class="product-name">Laptop Pro</h2>
  <span class="price">$999.99</span>
</div>
<div class="product-card">
  <h2 class="product-name">Wireless Mouse</h2>
  <span class="price">$29.99</span>
</div>
```

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>soup.select("div.product-card") then select_one("h2.product-name") inside each card</details>
<details><summary>✅ Answer</summary>

```python
from bs4 import BeautifulSoup

html = """
<div class="product-card">
  <h2 class="product-name">Laptop Pro</h2>
  <span class="price">$999.99</span>
</div>
<div class="product-card">
  <h2 class="product-name">Wireless Mouse</h2>
  <span class="price">$29.99</span>
</div>"""

soup = BeautifulSoup(html, "html.parser")
products = []
for card in soup.select("div.product-card"):         # ← all cards
    name  = card.select_one("h2.product-name").get_text(strip=True)
    price = card.select_one("span.price").get_text(strip=True)
    products.append({"name": name, "price": price})

print(products)
# [{"name": "Laptop Pro", "price": "$999.99"}, ...]
```

**Why:** CSS selectors handle complex nested patterns in a single expression — more powerful than chaining find() calls.
</details>

---

### Q4 · Ch1 — Extract Text vs Attributes 🟢

Given this HTML, extract (a) the image `src` attribute, (b) the link `href`, and (c) the `data-id` from the div — all using BeautifulSoup.

```html
<div data-id="42">
  <img class="product-image" src="/images/laptop.jpg" alt="Laptop">
  <a class="product-link" href="/products/42">View Product</a>
</div>
```

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>Use el["attr"] for attribute access or el.get("attr", default) for safe access</details>
<details><summary>✅ Answer</summary>

```python
from bs4 import BeautifulSoup

html = """<div data-id="42">
  <img class="product-image" src="/images/laptop.jpg" alt="Laptop">
  <a class="product-link" href="/products/42">View Product</a>
</div>"""

soup = BeautifulSoup(html, "html.parser")

img_url  = soup.select_one("img.product-image")["src"]       # ← bracket access
link     = soup.select_one("a.product-link")["href"]
data_id  = soup.select_one("div[data-id]").get("data-id")    # ← .get() is safe

print(img_url)   # "/images/laptop.jpg"
print(link)      # "/products/42"
print(data_id)   # "42"
```

**Why:** `el["attr"]` raises KeyError if missing; `el.get("attr", default)` is safer when the attribute might not exist.
</details>

---

### Q5 · Ch1 — raise_for_status and Response Properties 🟢

Write code that fetches a URL and prints the status code, content type, and first 100 characters of the response body. Handle HTTP errors explicitly and print a friendly message.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>response.status_code, response.headers["Content-Type"], response.text[:100], catch requests.HTTPError</details>
<details><summary>✅ Answer</summary>

```python
import requests

def inspect_response(url: str) -> None:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()                         # ← raises for 4xx/5xx
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type', 'unknown')}")
        print(f"Preview: {r.text[:100]}")
    except requests.HTTPError as e:
        print(f"HTTP Error {e.response.status_code}: {url}")
    except requests.ConnectionError:
        print(f"Could not connect to {url}")
    except requests.Timeout:
        print(f"Timed out waiting for {url}")
```

**Why:** Separating HTTPError, ConnectionError, and Timeout lets you handle each failure mode differently — retry on timeout, skip on 404, alert on 500.
</details>

---

## Ch2 — Scraping Multiple Pages

### Q6 · Ch2 — Pagination Loop with Query Params 🟡

Write a `scrape_all_pages(base_url, max_pages)` function that loops through pages using `?page=N` query params, collects items from each page, and stops early if a page returns no items.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>Use base_url.format(page) or f-string, check len(items) == 0 to break, always time.sleep(1)</details>
<details><summary>✅ Answer</summary>

```python
import requests
from bs4 import BeautifulSoup
import time

def scrape_all_pages(base_url: str, max_pages: int = 50) -> list[dict]:
    headers = {"User-Agent": "Mozilla/5.0"}
    all_items = []

    for page_num in range(1, max_pages + 1):
        url = f"{base_url}?page={page_num}"           # ← build page URL
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            items = soup.select("div.item")
            if not items:                              # ← stop if empty page
                print(f"No items on page {page_num}, stopping")
                break

            for item in items:
                all_items.append({"text": item.get_text(strip=True)})
            print(f"Page {page_num}: {len(items)} items")

        except requests.RequestException as e:
            print(f"Error on page {page_num}: {e}")

        time.sleep(1)   # ← be respectful

    return all_items
```

**Why:** Always have a stopping condition — either an empty-page check or a next-page button check — to avoid infinite loops on sites that don't 404 on over-range pages.
</details>

---

### Q7 · Ch2 — Relative URL Construction 🟡

A scraper finds product links like `/products/42` on `https://shop.example.com`. Write a function that takes a base URL and a relative href and returns the full absolute URL. Handle both relative paths (starting with `/`) and already-absolute URLs.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>Use urllib.parse.urljoin — it handles both relative and absolute URLs correctly</details>
<details><summary>✅ Answer</summary>

```python
from urllib.parse import urljoin

def make_absolute(base_url: str, href: str) -> str:
    return urljoin(base_url, href)   # ← handles all cases correctly

# Examples:
base = "https://shop.example.com/products"
print(make_absolute(base, "/products/42"))         # https://shop.example.com/products/42
print(make_absolute(base, "page2"))                # https://shop.example.com/page2
print(make_absolute(base, "https://other.com/x")) # https://other.com/x (absolute unchanged)
```

**Why:** `urljoin` is the correct tool — hand-rolling string concatenation breaks on edge cases like URLs without trailing slashes.
</details>

---

### Q8 · Ch2 — Rate Limiting with time.sleep 🟢

You're scraping 100 pages. Show two patterns: (a) a fixed 1-second delay after every request, and (b) a randomized delay between 1 and 3 seconds to appear more human-like.

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>time.sleep(1) for fixed; random.uniform(1, 3) for randomized</details>
<details><summary>✅ Answer</summary>

```python
import time
import random

# Pattern A: fixed delay
for page in range(1, 101):
    # ... fetch page ...
    time.sleep(1)   # ← exactly 1 second every time

# Pattern B: randomized delay (looks more human)
for page in range(1, 101):
    # ... fetch page ...
    delay = random.uniform(1.0, 3.0)   # ← random between 1 and 3 seconds
    time.sleep(delay)
```

**Why:** Random delays are harder for anti-bot systems to fingerprint — perfectly regular request intervals are a giveaway that it's a bot.
</details>

---

### Q9 · Ch2 — Error Handling for 404 and 500 🟡

Write a `safe_fetch(url)` function that handles HTTP 404 (return None and log), HTTP 500 (raise a custom exception), and connection errors (return None and log).

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>Catch requests.HTTPError and check e.response.status_code to differentiate 404 from 500</details>
<details><summary>✅ Answer</summary>

```python
import requests
import logging

logger = logging.getLogger(__name__)

class ServerError(Exception):
    pass

def safe_fetch(url: str) -> str | None:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.text

    except requests.HTTPError as e:
        code = e.response.status_code
        if code == 404:
            logger.warning("Not found (404): %s", url)
            return None                   # ← skip missing pages
        elif code == 500:
            raise ServerError(f"Server error on {url}") from e   # ← escalate
        else:
            logger.error("HTTP %s: %s", code, url)
            return None

    except requests.ConnectionError:
        logger.error("Connection failed: %s", url)
        return None
```

**Why:** 404 means the resource doesn't exist (skip it); 500 may mean the server is down and you should stop — treating them the same hides important information.
</details>

---

### Q10 · Ch2 — Retry with Exponential Backoff 🟠

Configure a `requests.Session` with automatic retry logic that retries up to 3 times on status codes 429, 500, 502, 503, 504 with exponential backoff (1s, 2s, 4s delays).

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>Use requests.adapters.HTTPAdapter and urllib3.util.retry.Retry with backoff_factor</details>
<details><summary>✅ Answer</summary>

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def build_retry_session() -> requests.Session:
    session = requests.Session()

    retry = Retry(
        total=3,                                      # ← max 3 attempts
        backoff_factor=1,                             # ← 1s, 2s, 4s delays
        status_forcelist=[429, 500, 502, 503, 504],   # ← retry on these codes
        allowed_methods=["GET", "HEAD"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)   # ← apply to all https requests
    session.mount("http://", adapter)

    return session

session = build_retry_session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
# r = session.get("https://example.com")  — now auto-retries on failures
```

**Why:** `backoff_factor=1` means delay = backoff_factor * (2^(retry_number - 1)): 1s, 2s, 4s — this avoids hammering a struggling server and allows it to recover.
</details>

---

## Ch3 — Handling JavaScript-Rendered Pages

### Q11 · Ch3 — Why requests Fails on JS Pages 🟢

Explain why `requests.get()` returns incomplete data for JavaScript-rendered pages. What does `requests` actually receive, and what would you see if you used `View Page Source` vs the browser DevTools inspector?

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details><summary>💡 Hint</summary>requests gets the raw HTML the server sends before any JavaScript executes</details>
<details><summary>✅ Answer</summary>

```python
# requests only downloads the initial HTML response from the server.
# JavaScript runs in the browser AFTER that HTML is received.
#
# View Page Source  → shows what requests.get() receives (raw HTML)
# Browser Inspector → shows the final DOM after JS has run
#
# Example: a React app might send this initial HTML:
#   <div id="root"></div>
# Then JavaScript renders the actual content inside that div.
# requests.get() sees the empty <div id="root"></div>.
#
# Solution: use Selenium or Playwright, which launch a real browser
# that executes the JavaScript before you extract the HTML.

import requests
from bs4 import BeautifulSoup

r = requests.get("https://example.com")   # ← only gets server-sent HTML
soup = BeautifulSoup(r.text, "html.parser")

# If the site uses React/Vue/Angular, soup may contain no product data —
# it's all loaded by JS after the initial page load.
```

**Why:** Always check "View Page Source" (not DevTools Elements) to see what `requests` will actually receive. If your target data isn't there, you need a browser automation tool.
</details>

---

### Q12 · Ch3 — Selenium Headless Chrome Setup 🟡

Write the setup code to launch Chrome in headless mode using Selenium, navigate to a URL, and safely close the browser even if an exception occurs.

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details><summary>💡 Hint</summary>Use Options() with --headless, wrap driver.get() in try/finally with driver.quit()</details>
<details><summary>✅ Answer</summary>

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")             # ← no visible window
options.add_argument("--no-sandbox")           # ← required in Docker/Linux
options.add_argument("--disable-dev-shm-usage")  # ← prevents shared memory crash

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://example.com/dynamic-page")
    print(driver.title)                        # ← page title after JS renders
    html = driver.page_source                  # ← fully rendered HTML
finally:
    driver.quit()   # ← always close the browser
```

**Why:** `driver.quit()` in `finally` ensures the browser process is killed even if your code crashes — otherwise you leak browser processes and eat RAM.
</details>

---

### Q13 · Ch3 — WebDriverWait — Wait for Selector 🟡

A product page loads its price via JavaScript 2–3 seconds after page load. Write code using `WebDriverWait` to wait up to 10 seconds for an element with class `price` to appear, then extract its text.

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

<details><summary>💡 Hint</summary>WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "price")))</details>
<details><summary>✅ Answer</summary>

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument("--headless")
driver = webdriver.Chrome(options=opts)

try:
    driver.get("https://example.com/product")

    wait = WebDriverWait(driver, 10)           # ← wait up to 10 seconds
    price_el = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "price"))  # ← wait for this
    )
    print(price_el.text)                       # ← safe to read now

finally:
    driver.quit()
```

**Why:** Never use `time.sleep(3)` to wait for JS — use `WebDriverWait`. Sleep always wastes time (waits full duration even when ready) and is fragile (fails on slow networks).
</details>

---

### Q14 · Ch3 — Playwright Async Basics 🟠

Rewrite the Selenium example from Q12 using async Playwright. Launch Chromium headlessly, navigate to a URL, wait for a `.price` selector, extract its text, and close the browser.

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

<details><summary>💡 Hint</summary>async with async_playwright() as p, await p.chromium.launch(headless=True), await page.wait_for_selector(".price")</details>
<details><summary>✅ Answer</summary>

```python
import asyncio
from playwright.async_api import async_playwright

async def scrape_with_playwright(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)   # ← headless Chromium
        page = await browser.new_page()

        await page.goto(url)
        await page.wait_for_selector(".price")             # ← waits for JS render

        price_text = await page.text_content(".price")
        await browser.close()                              # ← always close
        return price_text

# price = asyncio.run(scrape_with_playwright("https://example.com/product"))
```

**Why:** Playwright's async API lets you scrape multiple pages concurrently with asyncio — you can run 10 pages in parallel instead of waiting for them sequentially.
</details>

---

### Q15 · Ch3 — Extract After Render via BeautifulSoup 🟡

After using Selenium to load a JavaScript page, extract the rendered HTML and parse it with BeautifulSoup. Show the pattern that combines both tools.

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

<details><summary>💡 Hint</summary>driver.page_source gives you the fully rendered HTML — pass it to BeautifulSoup as usual</details>
<details><summary>✅ Answer</summary>

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

opts = Options()
opts.add_argument("--headless")
driver = webdriver.Chrome(options=opts)

try:
    driver.get("https://example.com/products")

    # Wait until JS has rendered the product cards
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-card"))
    )

    # Hand the rendered HTML to BeautifulSoup for easy parsing
    soup = BeautifulSoup(driver.page_source, "html.parser")  # ← key line
    products = soup.select("div.product-card")
    for p in products:
        print(p.select_one("h2").get_text(strip=True))

finally:
    driver.quit()
```

**Why:** `driver.page_source` returns the DOM after JavaScript has executed — this is the standard Selenium + BeautifulSoup combination for JS-rendered sites.
</details>

---

## Ch4 — Ethical and Legal Guidelines

### Q16 · Ch4 — robots.txt Parsing 🟢

Write code using `urllib.robotparser` to check whether your scraper is allowed to access `/products` and `/private/data` on a given website.

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

<details><summary>💡 Hint</summary>RobotFileParser.set_url(), .read(), then .can_fetch("*", url)</details>
<details><summary>✅ Answer</summary>

```python
from urllib.robotparser import RobotFileParser

def check_robots(domain: str, paths: list[str]) -> dict[str, bool]:
    rp = RobotFileParser()
    rp.set_url(f"{domain}/robots.txt")   # ← point to robots.txt
    rp.read()                            # ← fetch and parse it

    results = {}
    for path in paths:
        full_url = f"{domain}{path}"
        allowed = rp.can_fetch("*", full_url)   # ← "*" = any bot
        results[path] = allowed
        status = "ALLOWED" if allowed else "DISALLOWED"
        print(f"{path}: {status}")
    return results

check_robots("https://example.com", ["/products", "/private/data"])
```

**Why:** `can_fetch("*", url)` checks the wildcard rule that applies to all bots — always check this before scraping, and skip any Disallowed paths entirely.
</details>

---

### Q17 · Ch4 — User-Agent Etiquette 🟢

What is the difference between these two User-Agent headers, and which is more ethical for a research scraper? Write the better one and explain why.

```python
# Option A
headers = {}

# Option B
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/120.0"}

# Option C
headers = {"User-Agent": "ResearchBot/1.0 (university project; contact@uni.edu)"}
```

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

<details><summary>💡 Hint</summary>Think about transparency vs disguise — which option lets the server owner identify and contact you?</details>
<details><summary>✅ Answer</summary>

```python
# Option A — worst: sends default "python-requests/2.x" which gets auto-blocked
# Option B — deceptive: pretends to be a real Chrome browser
# Option C — most ethical: identifies the bot AND provides contact info

headers = {
    "User-Agent": "ResearchBot/1.0 (university project; contact@uni.edu)"
}

# Option B is common practice for avoiding blocks, but Option C is more ethical
# because the server operator can:
#   1. Identify your scraper in their logs
#   2. Contact you if there's an issue
#   3. Whitelist your bot if they want
#
# In practice: use B for basic scraping, use C for any formal or published work
```

**Why:** A descriptive User-Agent with contact info shows good faith to site operators — it's the equivalent of knocking on the door instead of sneaking through a window.
</details>

---

### Q18 · Ch4 — When Scraping Is and Isn't Legal 🟢

List the key factors that determine whether scraping a site is legal/ethical, and identify which of these scenarios would be a red flag.

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

<details><summary>💡 Hint</summary>Think: robots.txt, Terms of Service, public vs private data, bypassing authentication, data use</details>
<details><summary>✅ Answer</summary>

```python
"""
LEGAL / ETHICAL CHECKLIST for web scraping:

GENERALLY OK:
  - Publicly available data (no login required)
  - robots.txt allows your paths
  - ToS does not explicitly prohibit scraping
  - Data is used for research / personal use, not resold
  - Respectful rate limiting (no server strain)

RED FLAGS — likely problematic:
  - Site ToS explicitly bans scraping (LinkedIn, Twitter/X, Facebook)
  - Requires login to view data → scraping may violate CFAA (Computer Fraud law)
  - Bypassing CAPTCHA or anti-bot measures
  - Scraping personal / PII data (names, emails, phone numbers)
  - Using scraped data commercially without permission
  - robots.txt blocks your paths but you scrape anyway

KEY CASE: hiQ vs LinkedIn (2022) — US 9th Circuit ruled scraping
publicly available data is NOT a violation of CFAA. But ToS violations
can still result in civil lawsuits.
"""
```

**Why:** The legality of scraping is a gray area — when in doubt, prefer official APIs, and always get legal review before any commercial or large-scale scraping project.
</details>

---

## Ch5 — requests.Session

### Q19 · Ch5 — Session for Cookie Persistence 🟡

Write code that uses a `requests.Session` to log in to a site and then fetch a protected page, showing that the session automatically carries the authentication cookie.

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

<details><summary>💡 Hint</summary>session.post() to login, then session.get() to protected page — cookies are stored automatically</details>
<details><summary>✅ Answer</summary>

```python
import requests
from bs4 import BeautifulSoup

session = requests.Session()   # ← cookie jar is shared across all requests
session.headers.update({"User-Agent": "Mozilla/5.0"})

# Step 1: Login — session stores the auth cookie automatically
login_response = session.post(
    "https://example.com/login",
    data={"username": "myuser", "password": "mypass"}
)
login_response.raise_for_status()
print("Logged in:", login_response.status_code)

# Step 2: Access protected page — session sends the cookie automatically
protected = session.get("https://example.com/my-account")
soup = BeautifulSoup(protected.text, "html.parser")
# No need to manually pass cookies — Session handles it
```

**Why:** Without a Session, each request is stateless — you would have to manually extract and re-send the auth cookie on every request, which is error-prone.
</details>

---

### Q20 · Ch5 — Shared Headers on a Session 🟢

Create a `requests.Session` with shared headers (User-Agent, Accept, Accept-Language) that apply to every request made through the session — without repeating them on each call.

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

<details><summary>💡 Hint</summary>session.headers.update({...}) sets defaults; individual requests can still override them</details>
<details><summary>✅ Answer</summary>

```python
import requests

session = requests.Session()

# Set once — applies to every request in this session
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
})

# All these requests automatically include the headers above
r1 = session.get("https://example.com/page1")
r2 = session.get("https://example.com/page2")
r3 = session.get("https://example.com/page3")

# Individual override is still possible:
r4 = session.get("https://example.com/api", headers={"Accept": "application/json"})
```

**Why:** Setting headers on the session once is DRY and ensures consistency — you can't accidentally forget headers on a specific request.
</details>

---

### Q21 · Ch5 — Connection Pooling Benefit 🟡

Explain what connection pooling is in `requests.Session` and write a benchmark comparison showing why Session is faster than plain `requests.get()` for scraping the same domain 10 times.

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

<details><summary>💡 Hint</summary>TCP handshake + TLS handshake cost ~100ms per connection — Session reuses established connections</details>
<details><summary>✅ Answer</summary>

```python
import requests
import time

urls = [f"https://httpbin.org/delay/0?n={i}" for i in range(5)]

# Without Session — new TCP+TLS handshake for every request
start = time.time()
for url in urls:
    requests.get(url, timeout=10)
without_session = time.time() - start

# With Session — reuses the same TCP connection (HTTP keep-alive)
session = requests.Session()
start = time.time()
for url in urls:
    session.get(url, timeout=10)
with_session = time.time() - start

print(f"Without Session: {without_session:.2f}s")
print(f"With Session:    {with_session:.2f}s")
# Session is typically 20-40% faster for same-domain requests

# Why? TCP+TLS handshake = ~100-300ms overhead per new connection
# Session uses HTTP keep-alive to reuse the connection across requests
```

**Why:** For scraping 100+ pages from the same domain, Session typically saves 10–30 seconds compared to plain `requests.get()` — the handshake cost adds up fast.
</details>

---

## Ch6 — Scraping Data into Structured Format

### Q22 · Ch6 — Scrape to List of Dicts 🟡

Using the HTML below, scrape all products into a list of dicts with keys `name`, `price`, `rating`. Handle missing ratings gracefully (use `None`).

```html
<div class="product" data-id="1">
  <h2 class="name">Laptop Pro</h2>
  <span class="price">$999.99</span>
  <span class="rating">4.5 stars</span>
</div>
<div class="product" data-id="2">
  <h2 class="name">USB Hub</h2>
  <span class="price">$49.99</span>
</div>
```

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

<details><summary>💡 Hint</summary>rating_el = card.select_one("span.rating"); rating = rating_el.get_text() if rating_el else None</details>
<details><summary>✅ Answer</summary>

```python
from bs4 import BeautifulSoup

html = """
<div class="product" data-id="1">
  <h2 class="name">Laptop Pro</h2>
  <span class="price">$999.99</span>
  <span class="rating">4.5 stars</span>
</div>
<div class="product" data-id="2">
  <h2 class="name">USB Hub</h2>
  <span class="price">$49.99</span>
</div>"""

soup = BeautifulSoup(html, "html.parser")
products = []

for card in soup.select("div.product"):
    rating_el = card.select_one("span.rating")
    products.append({
        "name":   card.select_one("h2.name").get_text(strip=True),
        "price":  card.select_one("span.price").get_text(strip=True),
        "rating": rating_el.get_text(strip=True) if rating_el else None,  # ← safe
    })

print(products)
# [{"name": "Laptop Pro", "price": "$999.99", "rating": "4.5 stars"},
#  {"name": "USB Hub", "price": "$49.99", "rating": None}]
```

**Why:** Always handle optional elements with a None check — `select_one()` returns None when the element doesn't exist, and calling `.get_text()` on None raises AttributeError.
</details>

---

### Q23 · Ch6 — pandas DataFrame from Scraped Data 🟡

Take the list of product dicts from Q22 and convert it to a pandas DataFrame. Then clean the `price` column by stripping the `$` sign and converting to float.

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

<details><summary>💡 Hint</summary>pd.DataFrame(list_of_dicts), then df["price"].str.replace("$", "", regex=False).astype(float)</details>
<details><summary>✅ Answer</summary>

```python
import pandas as pd

products = [
    {"name": "Laptop Pro",  "price": "$999.99", "rating": "4.5 stars"},
    {"name": "Wireless Mouse", "price": "$29.99", "rating": "4.2 stars"},
    {"name": "USB Hub",     "price": "$49.99",  "rating": None},
]

df = pd.DataFrame(products)   # ← list of dicts → DataFrame instantly

# Clean the price column
df["price_usd"] = (
    df["price"]
    .str.replace(r"[$,]", "", regex=True)   # ← strip $ and commas
    .astype(float)
)

print(df[["name", "price_usd"]])
#         name  price_usd
# 0  Laptop Pro     999.99
# 1  Wireless Mouse   29.99
# 2     USB Hub      49.99

print(f"Most expensive: {df.loc[df['price_usd'].idxmax(), 'name']}")
```

**Why:** `str.replace(r"[$,]", "", regex=True)` handles prices like `$1,234.56` in one step — the regex strips both `$` and `,` before the float conversion.
</details>

---

### Q24 · Ch6 — Save to CSV and JSON 🟢

Given a pandas DataFrame of scraped products, save it to both `products.csv` and `products.json`. Show the correct pandas methods for each and explain one gotcha for each format.

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

<details><summary>💡 Hint</summary>df.to_csv(index=False) and df.to_json(orient="records", indent=2)</details>
<details><summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame([
    {"name": "Laptop Pro",     "price_usd": 999.99, "rating": "4.5 stars"},
    {"name": "Wireless Mouse", "price_usd":  29.99, "rating": "4.2 stars"},
])

# Save to CSV
df.to_csv("products.csv", index=False)   # ← index=False: don't write row numbers
# Gotcha: special characters (commas, newlines in data) need quoting — pandas handles
# this automatically, but always open the file and verify the first few rows.

# Save to JSON
df.to_json("products.json", orient="records", indent=2)
# orient="records" → list of dicts format (most readable)
# Gotcha: NaN values become null in JSON — that's correct, but verify your nulls
# are intentional and not scraping errors before saving.

print("Saved to products.csv and products.json")
```

**Why:** Always use `index=False` for CSV — the default index column (0, 1, 2...) is meaningless for scraped data and confuses anyone who opens the file.
</details>

---

### Q25 · Ch6 — Deduplication of Scraped Records 🟡

You've scraped 500 products across 10 pages and suspect some products appear on multiple pages. Write code to deduplicate the list of product dicts by product `name`, keeping the first occurrence.

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

<details><summary>💡 Hint</summary>Use df.drop_duplicates(subset=["name"]) or a seen set for in-memory dedup during scraping</details>
<details><summary>✅ Answer</summary>

```python
import pandas as pd

# Method 1: pandas dedup after scraping (simple, works on any dict list)
all_products = [
    {"name": "Laptop Pro",  "price": "$999.99"},
    {"name": "USB Hub",     "price": "$49.99"},
    {"name": "Laptop Pro",  "price": "$999.99"},   # ← duplicate
    {"name": "Wireless Mouse", "price": "$29.99"},
]

df = pd.DataFrame(all_products)
df_deduped = df.drop_duplicates(subset=["name"], keep="first")   # ← keep first
print(f"Before: {len(df)} rows, After: {len(df_deduped)} rows")

# Method 2: in-memory dedup during scraping (more efficient for huge datasets)
seen_names = set()
unique_products = []

for product in all_products:
    if product["name"] not in seen_names:
        seen_names.add(product["name"])
        unique_products.append(product)
```

**Why:** Method 2 (seen set) uses O(n) memory and avoids storing duplicates at all — preferred when scraping millions of records where loading everything into a DataFrame first is too memory-intensive.
</details>

---

## Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| ⬅️ Prev Module | [../28_eda_workflow/theory.md](../28_eda_workflow/theory.md) |
| ➡️ Next Module | [../30_sql_with_python/theory.md](../30_sql_with_python/theory.md) |

---

**[Back to README](../README.md)**
