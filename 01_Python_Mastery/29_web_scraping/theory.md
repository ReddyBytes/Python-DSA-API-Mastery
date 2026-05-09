<a id="top"></a>
# 🕷️ Web Scraping with Python

## 📖 Table of Contents

- [Learning Priority](#-learning-priority)
- [1. The Foundation: requests + BeautifulSoup](#1-the-foundation-requests--beautifulsoup)
- [2. Scraping Multiple Pages](#2-scraping-multiple-pages)
- [3. Handling JavaScript-Rendered Pages](#3-handling-javascript-rendered-pages)
- [4. Ethical and Legal Guidelines](#4-ethical-and-legal-guidelines)
- [5. requests.Session for Efficiency](#5-requestssession-for-efficiency)
- [6. Scraping Data into Structured Format](#6-scraping-data-into-structured-format)
- [Summary](#-summary)
- [Navigation](#-navigation)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`requests` library · `BeautifulSoup` parsing · CSS selectors · `find()` / `find_all()` · Handling HTTP errors · Robots.txt and ethics

**Should Learn** — Important for real projects, comes up regularly:
`requests.Session` · Headers / User-Agent · Rate limiting and `time.sleep()` · Selenium for JavaScript-rendered pages · `httpx` for async scraping

**Good to Know** — Useful in specific situations:
`Scrapy` framework · `Playwright` · `lxml` parser · Handling pagination · Proxy rotation

**Reference** — Know it exists, look up when needed:
CAPTCHA solving services · `curl_cffi` · Antibot bypass techniques

---

You need pricing data from 50 e-commerce websites. The sites don't have APIs. The data is right there in the HTML — product names, prices, ratings — but to get it into a spreadsheet, someone would have to manually copy and paste 10,000 rows. Web scraping automates this: instead of a human reading a web page and copying text, a Python script reads the same HTML and extracts the same data, 1000 pages per minute, without stopping for coffee.

---

<a id="1-the-foundation-requests--beautifulsoup"></a>
# 1. The Foundation: requests + BeautifulSoup

```python
import requests
from bs4 import BeautifulSoup
import time

# 1. Fetch the HTML
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

response = requests.get("https://example.com/products", headers=headers, timeout=10)
response.raise_for_status()   # ← raises HTTPError for 4xx/5xx status codes

# 2. Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# 3. Extract data
# By tag
title = soup.find("h1").get_text(strip=True)        # first <h1>
all_links = soup.find_all("a")                       # all <a> tags

# By class
prices = soup.find_all("span", class_="price")      # all elements with class="price"
for p in prices:
    print(p.get_text(strip=True))

# By CSS selector (most flexible)
items = soup.select("div.product-card")             # all divs with class product-card
for item in items:
    name  = item.select_one("h2.product-name").get_text(strip=True)
    price = item.select_one("span.price").get_text(strip=True)
    print(f"{name}: {price}")

# Get an attribute
img_url = soup.select_one("img.product-image")["src"]
link    = soup.select_one("a.product-link")["href"]
```

📝 **Practice:** [Q1–Q5 — requests + BeautifulSoup](./practice.md#q1)

[↑ Back to Top](#top)

---

<a id="2-scraping-multiple-pages"></a>
# 2. Scraping Multiple Pages

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_page(url: str, headers: dict) -> list[dict]:
    """Scrape a single product listing page."""
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    products = []
    for card in soup.select("div.product-card"):
        products.append({
            "name":   card.select_one("h2").get_text(strip=True),
            "price":  card.select_one(".price").get_text(strip=True),
            "rating": card.select_one(".rating").get_text(strip=True) if card.select_one(".rating") else None,
        })
    return products

headers = {"User-Agent": "Mozilla/5.0"}
base_url = "https://example.com/products?page={}"

all_products = []
for page_num in range(1, 11):   # pages 1-10
    url = base_url.format(page_num)
    try:
        products = scrape_page(url, headers)
        all_products.extend(products)
        print(f"Page {page_num}: {len(products)} products")
    except requests.RequestException as e:
        print(f"Error on page {page_num}: {e}")
    finally:
        time.sleep(1)   # ← be respectful — 1 second between requests

df = pd.DataFrame(all_products)
df.to_csv("products.csv", index=False)
print(f"Saved {len(df)} products")
```

📝 **Practice:** [Q6–Q10 — Scraping Multiple Pages](./practice.md#q6)

[↑ Back to Top](#top)

---

<a id="3-handling-javascript-rendered-pages"></a>
# 3. Handling JavaScript-Rendered Pages

Some websites render content with JavaScript after page load. `requests` only gets the initial HTML — it cannot execute JavaScript. Use **Selenium** or **Playwright** for these.

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Headless Chrome (no visible browser window)
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://example.com/dynamic-page")

    # Wait until a specific element appears (up to 10 seconds)
    wait = WebDriverWait(driver, 10)
    price_el = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "price")))
    print(price_el.text)

    # Click a button
    button = driver.find_element(By.ID, "load-more")
    button.click()

    # Now get the updated page source
    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = soup.select("div.product-card")

finally:
    driver.quit()   # always close the browser
```

📝 **Practice:** [Q11–Q15 — JavaScript-Rendered Pages](./practice.md#q11)

[↑ Back to Top](#top)

---

<a id="4-ethical-and-legal-guidelines"></a>
# 4. Ethical and Legal Guidelines

```
Before scraping, always:
1. Read robots.txt: https://example.com/robots.txt
   - Disallow rules specify what you cannot scrape
   - Respect them — violating robots.txt can have legal consequences

2. Check Terms of Service — some sites explicitly prohibit scraping

3. Add delays between requests (time.sleep(1-3))
   - Don't flood servers with requests

4. Use a descriptive User-Agent identifying your scraper
   - "MyResearchBot/1.0 (contact@example.com)"

5. Cache responses — don't re-fetch pages you already have

6. Prefer official APIs when available
```

📝 **Practice:** [Q16–Q18 — Ethical & Legal Guidelines](./practice.md#q16)

[↑ Back to Top](#top)

---

<a id="5-requestssession-for-efficiency"></a>
# 5. requests.Session for Efficiency

```python
import requests
from bs4 import BeautifulSoup

session = requests.Session()   # ← reuses TCP connections, cookies persist
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml",
})

# Login first (for sites requiring authentication)
login_response = session.post("https://example.com/login", data={
    "username": "user",
    "password": "pass"
})

# Now all requests in this session are authenticated
page = session.get("https://example.com/protected-page")
soup = BeautifulSoup(page.text, "html.parser")
```

📝 **Practice:** [Q19–Q21 — requests.Session](./practice.md#q19)

[↑ Back to Top](#top)

---

<a id="6-scraping-data-into-structured-format"></a>
# 6. Scraping Data into Structured Format

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

response = requests.get("https://example.com/table", headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(response.text, "html.parser")

# Parse HTML table directly with pandas
tables = pd.read_html(str(soup.find("table")))   # returns list of DataFrames
df = tables[0]

# Or extract manually
rows = []
for tr in soup.select("table tbody tr"):
    cells = [td.get_text(strip=True) for td in tr.find_all("td")]
    if cells:
        rows.append(cells)

df = pd.DataFrame(rows, columns=["Column1", "Column2", "Column3"])

# Clean price strings: "$1,234.56" → 1234.56
df["price"] = df["price"].str.replace(r"[$,]", "", regex=True).astype(float)
```

📝 **Practice:** [Q22–Q25 — Scraping Data into Structured Format](./practice.md#q22)

[↑ Back to Top](#top)

---

## 🔥 Summary

Web scraping turns publicly visible data into structured, queryable datasets — without waiting for someone to build an API. The core skill is understanding HTML structure well enough to write selectors that find the right elements reliably.

**Common mistakes to avoid:**

- **Not setting User-Agent**: many sites block the default Python/requests user agent. Always set a browser-like User-Agent.
- **No error handling**: networks fail. Always wrap requests in try/except and handle HTTP errors with `raise_for_status()`.
- **No rate limiting**: hammering a server with hundreds of requests/second is rude, may get your IP banned, and can harm the server. Always `time.sleep(1-2)` between requests.
- **Scraping JavaScript-rendered pages with requests**: if the product list isn't in the raw HTML source, you need Selenium or Playwright.
- **Ignoring pagination**: many scraping bugs come from only getting the first page and missing the "next page" button.

| Tool | When to use |
|---|---|
| `requests` + `BeautifulSoup` | Static HTML pages — the default choice |
| `requests.Session` | Multiple pages, authenticated scraping |
| `Selenium` | JavaScript-rendered pages, clicking buttons |
| `Playwright` | Modern alternative to Selenium, async support |
| `Scrapy` | Large-scale crawling projects with pipelines |
| `httpx` | Async scraping of many pages concurrently |

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Module | [← EDA Workflow](../28_eda_workflow/theory.md) |
| ➡️ | [🏠 Back to README](../README.md) |

**[🏠 Back to README](../README.md)**

**Prev:** [← EDA Workflow](../28_eda_workflow/theory.md) &nbsp;|&nbsp; **[🏠 Back to Python Mastery README](../README.md)**

**Related Topics:** [Cheatsheet](./cheetsheet.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)

[↑ Back to Top](#top)
