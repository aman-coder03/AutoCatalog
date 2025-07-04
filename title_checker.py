import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, InvalidSelectorException
from urllib.parse import quote_plus

excel_path = r'YOUR INPUT FILE PATH'
column_name = 'Title'
base_url = "ENTER YOUR URL"
output_path = r'YOUR OUTPUT FILE PATH'

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

df = pd.read_excel(excel_path)
results = []

def escape_xpath_text(text):
    if "'" not in text:
        return f"'{text}'"
    elif '"' not in text:
        return f'"{text}"'
    else:
        parts = text.split("'")
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"

def search_with_retry(search_url, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            driver.get(search_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.view-content"))
            )
            return True
        except TimeoutException:
            retries += 1
            print(f"Timeout while searching {search_url}. Retrying... ({retries}/{max_retries})")
            time.sleep(2)
    return False

def find_book_link_with_retry(title, max_retries=3):
    retries = 0
    safe_title = escape_xpath_text(title)
    while retries < max_retries:
        try:
            book_link = driver.find_element(By.XPATH, f"//a[contains(normalize-space(.), {safe_title})]")
            return book_link
        except NoSuchElementException:
            retries += 1
            print(f"Book link not found for {title}. Retrying... ({retries}/{max_retries})")
            time.sleep(2)
    return None

def load_detail_page_with_retry(detail_url, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            driver.get(detail_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return True
        except TimeoutException:
            retries += 1
            print(f"Timeout while loading detail page {detail_url}. Retrying... ({retries}/{max_retries})")
            time.sleep(2)
    return False

for index, row in df.iterrows():
    title = str(row[column_name]).strip()
    encoded_title = quote_plus(title)
    search_url = base_url.format(encoded_title)

    print(f"\n[{index + 1}/{len(df)}] Searching URL: {search_url}")

    try:
        # Search the page with retries
        if not search_with_retry(search_url):
            results.append((title, "Search failed after retries"))
            continue

        # Try to find the book link with retries
        book_link = find_book_link_with_retry(title)
        if not book_link:
            results.append((title, "Link not found after retries"))
            continue

        detail_url = book_link.get_attribute("href")
        print(f"Found link: {detail_url}")

        # Try to load the detail page with retries
        if not load_detail_page_with_retry(detail_url):
            results.append((title, "Detail page failed to load after retries"))
            continue

        page_source = driver.page_source.lower()
        page_title = driver.title.lower()

        if "page not found" in page_source or "404" in page_title:
            print(f"Detail page error: {title}")
            results.append((title, "Detail page error"))
        else:
            print(f"Detail page loaded: {title}")
            results.append((title, "Success"))

    except Exception as e:
        print(f"Error occurred for {title}: {e}")
        results.append((title, f"Error: {str(e)}"))

driver.quit()
pd.DataFrame(results, columns=["Title", "Status"]).to_excel(output_path, index=False)
print(f"\n Results saved to: {output_path}")
