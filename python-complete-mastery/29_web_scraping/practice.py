"""
Web Scraping — Practice Problems
Uses httpbin.org (public test API) and Wikipedia to practice safely.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json


# ─────────────────────────────────────────────
# PROBLEM 1: Basic GET Request
# ─────────────────────────────────────────────
print("PROBLEM 1: Basic GET Request")

headers = {"User-Agent": "PythonLearner/1.0"}
r = requests.get("https://httpbin.org/json", headers=headers, timeout=10)
r.raise_for_status()
data = r.json()
print(f"Status: {r.status_code}")
print(f"Response: {json.dumps(data, indent=2)}")


# ─────────────────────────────────────────────
# PROBLEM 2: Parse HTML with BeautifulSoup
# ─────────────────────────────────────────────
print("\nPROBLEM 2: HTML Parsing")

# Use Wikipedia's Python page (stable public HTML)
try:
    r = requests.get(
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        headers=headers,
        timeout=10
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Extract title
    title = soup.find("h1", {"id": "firstHeading"}).get_text(strip=True)
    print(f"Page title: {title}")

    # Extract first paragraph
    first_para = soup.select_one("div.mw-parser-output > p:not(.mw-empty-elt)")
    if first_para:
        text = first_para.get_text(strip=True)[:200]
        print(f"First paragraph (200 chars): {text}...")

    # Count all links
    all_links = soup.find_all("a", href=True)
    internal = [a for a in all_links if a["href"].startswith("/wiki/")]
    print(f"Total links: {len(all_links)}, Internal wiki links: {len(internal)}")

except requests.RequestException as e:
    print(f"Network error: {e}")


# ─────────────────────────────────────────────
# PROBLEM 3: CSS Selectors
# ─────────────────────────────────────────────
print("\nPROBLEM 3: CSS Selectors")

html = """
<html>
<body>
    <div class="product" data-id="1">
        <h2 class="name">Laptop Pro</h2>
        <span class="price">$999.99</span>
        <span class="rating">4.5 stars</span>
    </div>
    <div class="product" data-id="2">
        <h2 class="name">Wireless Mouse</h2>
        <span class="price">$29.99</span>
        <span class="rating">4.2 stars</span>
    </div>
    <div class="product" data-id="3">
        <h2 class="name">USB-C Hub</h2>
        <span class="price">$49.99</span>
    </div>
</html>
"""

soup = BeautifulSoup(html, "html.parser")

# Extract all products using CSS selectors
products = []
for card in soup.select("div.product"):
    name     = card.select_one("h2.name").get_text(strip=True)
    price    = card.select_one("span.price").get_text(strip=True)
    rating_el = card.select_one("span.rating")
    rating   = rating_el.get_text(strip=True) if rating_el else "N/A"
    prod_id  = card.get("data-id")

    products.append({"id": prod_id, "name": name, "price": price, "rating": rating})
    print(f"  {name}: {price} ({rating})")

df = pd.DataFrame(products)
df["price_num"] = df["price"].str.replace("$", "").astype(float)
print(f"\nMost expensive: {df.loc[df['price_num'].idxmax(), 'name']} at {df['price_num'].max()}")


# ─────────────────────────────────────────────
# PROBLEM 4: Error Handling
# ─────────────────────────────────────────────
print("\nPROBLEM 4: Error Handling")

test_urls = [
    "https://httpbin.org/status/200",   # success
    "https://httpbin.org/status/404",   # not found
    "https://httpbin.org/status/500",   # server error
    "https://nonexistent-domain-xyz123.com/",  # connection error
]

for url in test_urls:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
        print(f"  ✓ {url} → {r.status_code}")
    except requests.HTTPError as e:
        print(f"  ✗ HTTP error {e.response.status_code}: {url}")
    except requests.ConnectionError:
        print(f"  ✗ Connection failed: {url}")
    except requests.Timeout:
        print(f"  ✗ Timeout: {url}")
    time.sleep(0.3)   # rate limiting


# ─────────────────────────────────────────────
# PROBLEM 5: HTML Table Parsing
# ─────────────────────────────────────────────
print("\nPROBLEM 5: HTML Table Parsing")

table_html = """
<table>
    <thead><tr><th>Country</th><th>Population</th><th>GDP (T)</th></tr></thead>
    <tbody>
        <tr><td>USA</td><td>335M</td><td>$27T</td></tr>
        <tr><td>China</td><td>1.4B</td><td>$18T</td></tr>
        <tr><td>Japan</td><td>125M</td><td>$4.2T</td></tr>
        <tr><td>Germany</td><td>84M</td><td>$4.1T</td></tr>
    </tbody>
</table>
"""

# Method 1: pandas read_html
df_table = pd.read_html(table_html)[0]
print("Table from pd.read_html:")
print(df_table)

# Method 2: BeautifulSoup manual
soup = BeautifulSoup(table_html, "html.parser")
rows = []
headers_row = [th.get_text() for th in soup.select("thead th")]
for tr in soup.select("tbody tr"):
    cells = [td.get_text() for td in tr.find_all("td")]
    rows.append(dict(zip(headers_row, cells)))

df_manual = pd.DataFrame(rows)
print("\nTable from manual parsing:")
print(df_manual)


print("\n✅ Web scraping practice complete!")
