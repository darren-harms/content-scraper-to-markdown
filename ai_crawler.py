from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import markdownify
import time
import datetime
import random
import json
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import os

class WebCrawler:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        # Performance optimizations
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-setuid-sandbox")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument("--disable-save-password-bubble")
        self.options.add_argument("--disable-translate")
        self.options.add_argument("--disable-web-security")
        self.options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        self.options.add_argument("--disable-site-isolation-trials")
        
        # Add random user agent
        ua = UserAgent()
        self.options.add_argument(f'user-agent={ua.random}')
        
        # Add additional anti-detection arguments
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # Improved ChromeDriver initialization
        self.service = ChromeService(ChromeDriverManager().install())
        self.all_content = {}
        
    def random_delay(self):
        """Add random delay between actions to avoid detection"""
        time.sleep(random.uniform(0.5, 1.5))  # Reduced delay range
        
    def create_driver(self):
        """Create a new Chrome driver instance with proper error handling"""
        try:
            driver = webdriver.Chrome(service=self.service, options=self.options)
            # Modify navigator.webdriver to avoid detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"❌ Error creating Chrome driver: {e}")
            return None
        
    def wait_for_element(self, driver, by, value, timeout=10):
        """Wait for an element to be present and return it"""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            print(f"⚠️ Timeout waiting for element {value}: {e}")
            return None

    def fetch_and_save(self, url):
        driver = None
        try:
            driver = self.create_driver()
            if not driver:
                return
                
            driver.get(url)
            
            page_content = ""
            page_number = 1
            print(f"📄 Scraping {url} - page {page_number}...")
            
            while True:
                try:
                    # Wait for main content with reduced timeout
                    main_section = self.wait_for_element(driver, By.TAG_NAME, "main", timeout=5)
                    if not main_section:
                        print(f"⚠️ No main content found on page {page_number} for {url}")
                        break
                        
                    page_content += markdownify.markdownify(main_section.get_attribute("innerHTML"), heading_style="ATX")
                    
                    # Check for next button with reduced timeout
                    next_button = self.wait_for_element(driver, By.XPATH, "//a[@aria-label='Next Page']", timeout=3)
                    if not next_button:
                        print(f"✅ No more pages to scrape for {url}")
                        break
                        
                    # Scroll and click in one action
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", next_button)
                    
                    page_number += 1
                    print(f"📄 Scraping {url} - page {page_number}...")
                    
                    # Reduced delay between pages
                    time.sleep(random.uniform(0.3, 0.7))
                    
                except Exception as e:
                    print(f"❌ Error on page {page_number}: {e}")
                    break
            
            self.all_content[url] = page_content
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    print(f"⚠️ Error closing driver for {url}: {e}")

    def save_all_content(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/output_{timestamp}.md"
        
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as file:
            for url, content in self.all_content.items():
                file.write(f"# Content from {url}\n\n")
                file.write(content)
                file.write("\n\n---\n\n")
        
        print(f"✅ Saved all content to: {output_file}")

def main():
    urls = [
        "https://www.healthgrades.com/art-therapy-directory",
        # Add more URLs here
    ]
    
    crawler = WebCrawler()
    
    # Use ThreadPoolExecutor for parallel crawling with increased workers
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(crawler.fetch_and_save, urls)
    
    crawler.save_all_content()

if __name__ == "__main__":
    main()
