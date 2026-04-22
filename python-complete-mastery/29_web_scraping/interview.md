# 🕷️ Web Scraping — Interview Questions

---

**Q: What is the difference between requests+BeautifulSoup and Selenium for web scraping?**

`requests` + `BeautifulSoup` fetches raw HTML from the server and parses it. It's fast (no browser overhead), simple, and works for any site that returns its content in the initial HTML response. Selenium launches a real browser (Chrome/Firefox), loads the page, executes JavaScript, and waits for dynamic content to render. It's 10-100x slower than requests but handles JavaScript-rendered content. Use requests first. Switch to Selenium only if the data you need is not in the raw HTML source (check by viewing page source, not the browser inspector which shows the JS-rendered DOM).

---

**Q: How do you avoid getting blocked while scraping?**

Multiple strategies: (1) **User-Agent**: always set a realistic browser User-Agent — default Python/requests UA is blocked by most serious sites; (2) **Rate limiting**: `time.sleep(1-3)` between requests — aggressive scraping triggers rate limiting and IP bans; (3) **Session**: use `requests.Session()` to reuse connections and persist cookies like a real browser; (4) **Robots.txt**: read and respect `robots.txt` — blocked paths should not be scraped; (5) **Request headers**: add Accept, Accept-Language, Referer headers to look like a real browser; (6) **Rotation**: for large-scale scraping, rotate User-Agents and consider proxy rotation; (7) **Error handling**: handle 429 (Too Many Requests) with exponential backoff rather than retrying immediately.

---

**Q: What is CSS selector syntax and how do you use it in BeautifulSoup?**

CSS selectors are patterns for matching HTML elements. Key patterns: `tag` matches all elements of that type (`div`); `.class` matches elements with that class (`.product`); `#id` matches by ID (`#header`); `parent > child` matches direct children; `ancestor descendant` matches nested elements; `[attribute=value]` matches by attribute. In BeautifulSoup: `soup.select("div.product-card")` returns all divs with class `product-card`; `soup.select_one("span.price")` returns the first match. CSS selectors are more powerful than `find_all(tag, class_=...)` because they handle complex nested patterns in a single expression.

---

**Q: How would you handle scraping a paginated website?**

Standard pagination patterns: (1) **Query parameter**: `?page=1`, `?page=2` — loop through page numbers until empty result or no next-page button; (2) **Next-page link**: extract the `href` of the "Next" button and follow it; (3) **API pagination**: some sites load content via JSON API calls (check browser Network tab) — scrape the API directly with requests. The stopping condition is key: detect an empty page (no items found) or the absence of a next-page element. Always handle the last page gracefully — don't assume a fixed number of pages.

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
