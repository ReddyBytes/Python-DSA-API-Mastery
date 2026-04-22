# 🕷️ Web Scraping with Python

---

You need pricing data from 50 e-commerce websites. The sites don't have APIs. The data is right there in the HTML — product names, prices, ratings — but to get it into a spreadsheet, someone would have to manually copy and paste 10,000 rows.

That's exactly what web scraping automates. Instead of a human reading a web page and copying text, a Python script reads the same HTML and extracts the same data, 1000 pages per minute, without stopping for coffee.

**Web scraping** is the automated extraction of data from websites by parsing their HTML structure.

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

## 1️⃣ The Foundation: requests + BeautifulSoup

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

---

## 2️⃣ Scraping Multiple Pages

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

---

## 3️⃣ Handling JavaScript-Rendered Pages

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

---

## 4️⃣ Ethical and Legal Guidelines

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

---

## 5️⃣ requests.Session for Efficiency

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

---

## 6️⃣ Scraping Data into Structured Format

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

---

## Common Mistakes to Avoid ⚠️

- **Not setting User-Agent**: many sites block the default Python/requests user agent. Always set a browser-like User-Agent.
- **No error handling**: networks fail. Always wrap requests in try/except and handle HTTP errors with `raise_for_status()`.
- **No rate limiting**: hammering a server with hundreds of requests/second is rude, may get your IP banned, and can harm the server. Always `time.sleep(1-2)` between requests.
- **Scraping JavaScript-rendered pages with requests**: if the product list isn't in the raw HTML source, you need Selenium or Playwright.
- **Ignoring pagination**: many scraping bugs come from only getting the first page and missing the "next page" button.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Prev Module | [../28_eda_workflow/theory.md](../28_eda_workflow/theory.md) |
| ➡️ Next Module | [../30_sql_with_python/theory.md](../30_sql_with_python/theory.md) |

---

**[🏠 Back to README](../README.md)**
