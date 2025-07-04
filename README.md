# 📚 AutoCatalog

**AutoCatalog** is a Python-based automation tool designed to scan, monitor, and log paginated digital library listings. It eliminates the need for manual inspection of vast catalogs by automating A-to-Z category crawling and title verification — empowering librarians, digital archivists, and QA teams to ensure content availability and maintain catalog health with ease.

Whether you're overseeing a university library's e-resources or managing a digital archive, AutoCatalog helps detect broken links, loading failures, and missing entries — with detailed logs and screenshots for complete transparency.

---

## 🚀 Key Features

- 🔠 Crawls category-wise listings (A–Z, 0–9)
- 📄 Supports deep pagination (up to 100+ pages)
- 🔍 Verifies individual titles from Excel input
- 🔁 Built-in retry logic for timeouts or failed loads
- 📷 Captures screenshots of error pages
- 📊 Logs status of each title or page
- 📁 Saves results in Excel for easy review or reporting

---

## 📦 Tech Stack

- **Python 3.10+**
- **Selenium WebDriver**
- **Pandas**
- **Headless Chrome**

---

## ▶️ Usage
### 🧭 Run Category-Wise Crawler
Scans paginated digital catalog from A–Z and logs status of each page.
`python catalog_crawler.py`
- Page load issues will be retried.
- Failing pages are logged and screenshot saved in /screenshots.

### 📘 Run Book Title Checker
Searches and verifies the availability of each book listed in AtoZeBooks.xlsx.
`python title_checker.py`
- Each book title is searched individually.
- Result (Success, Link Not Found, etc.) is saved in an Excel file.

## 📊 Output
- ✅ Excel file with detailed status per book or page.
- 🖼️ Screenshots of pages where loading failed.
- 🧾 Console logs with live status and retries.
