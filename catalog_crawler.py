import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

CHROMEDRIVER_PATH = r'c:\Users\PC-12\Documents\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
WAIT_TIME = 20
MAX_PAGES = 100
RETRY_LIMIT = 2
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

categories = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
wait = WebDriverWait(driver, WAIT_TIME)

all_results = {}

for cat in categories:
    print(f"\n=== CATEGORY: {cat} ===")
    results = []
    current_page = 0

    base_url = (
        'ENTER YOUR URL'
    )

    driver.get(base_url + str(current_page))

    while current_page < MAX_PAGES:
        try:
            print(f"\n[{cat}] Page {current_page} — loading...")
            retry_count = 0
            while retry_count < RETRY_LIMIT:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.view-content')))
                    print(f"[{cat}] Page {current_page}: Loaded")
                    results.append((current_page, "Loaded"))
                    break
                except TimeoutException:
                    retry_count += 1
                    print(f"[{cat}] Page {current_page}: Timeout/Error - retry {retry_count}/{RETRY_LIMIT}")
                    screenshot = os.path.join(SCREENSHOT_DIR, f"{cat}_page_{current_page}_fail_retry{retry_count}.png")
                    driver.save_screenshot(screenshot)
                    print(f"  Screenshot saved: {screenshot}")
                    if retry_count < RETRY_LIMIT:
                        print(f"  Retrying page {current_page}...")
                        driver.get(base_url + str(current_page))
                        time.sleep(3)
                    else:
                        results.append((current_page, "Timeout/Error"))
                        break

            if retry_count == RETRY_LIMIT:
                current_page += 1
                driver.get(base_url + str(current_page))
                time.sleep(3)
                continue

            if current_page == MAX_PAGES - 1:
                print(f"[{cat}] Reached max page limit ({MAX_PAGES}).")
                break

            try:
                nxt = driver.find_element(By.CSS_SELECTOR, 'a[rel="next"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", nxt)
                time.sleep(0.5)
                nxt.click()
                current_page += 1
                time.sleep(1.5)

            except NoSuchElementException:
                nxtp = current_page + 1
                print(f"[{cat}] No Next link — manually opening page {nxtp}")
                driver.get(base_url + str(nxtp))
                time.sleep(2)

                retry_empty = 0
                while retry_empty < RETRY_LIMIT:
                    results_exist = driver.find_elements(By.CSS_SELECTOR, 'div.view-content > div.views-row')
                    if results_exist:
                        break  
                    else:
                        retry_empty += 1
                        if retry_empty < RETRY_LIMIT:
                            print(f"[{cat}] Page {nxtp} appears empty, retry {retry_empty}/{RETRY_LIMIT} after refresh.")
                            driver.refresh()
                            time.sleep(3)
                        else:
                            print(f"[{cat}] Page {nxtp} has NO journal entries after retries — end of category.")
                            break
                if retry_empty == RETRY_LIMIT and not results_exist:
                    break

                current_page = nxtp

        except Exception as e:
            print(f"[{cat}] Unexpected error on page {current_page}: {e}")
            traceback.print_exc()
            results.append((current_page, f"Error: {e}"))

            current_page += 1
            nxt_url = base_url + str(current_page)
            print(f"[{cat}] Redirecting to page {current_page} manually.")
            try:
                driver.get(nxt_url)
                time.sleep(2)
            except Exception as e2:
                print(f"[{cat}] Failed to load manual page {current_page}: {e2}")
                traceback.print_exc()
                break

    all_results[cat] = results

driver.quit()

print("\nSUMMARY")
for category, pages in all_results.items():
    print(f"\nCategory '{category}':")
    for pg, status in pages:
        print(f"  Page {pg}: {status}")
