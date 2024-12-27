import uuid
import time
import os
import random
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from pymongo import MongoClient
from proxy_auth_plugin import create_proxy_auth_extension
import undetected_chromedriver as uc

# Load environment variables
load_dotenv()

# -------------------------------------------
# MongoDB Setup
# -------------------------------------------
def save_to_mongo(record):
    """Save record to MongoDB"""
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["twitter_trends"]
    collection = db["trends"]
    collection.insert_one(record)
    client.close()

# -------------------------------------------
# Setup Driver (with ProxyMesh auth)
# -------------------------------------------
def setup_driver(proxy_address):
    """
    Configure and launch an undetected ChromeDriver instance
    using ProxyMesh authentication via a plugin.
    """
    proxy_username = os.getenv("PROXYMESH_USERNAME")
    proxy_password = os.getenv("PROXYMESH_PASSWORD")

    if not proxy_username or not proxy_password:
        raise ValueError("PROXYMESH_USERNAME or PROXYMESH_PASSWORD missing in .env")

    proxy_host, proxy_port = proxy_address.split(":")
    plugin_file = create_proxy_auth_extension(proxy_host, proxy_port, proxy_username, proxy_password)

    options = uc.ChromeOptions()

    # Add the ProxyMesh authentication plugin
    options.add_extension(plugin_file)

    # Add other driver configurations
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-cache")
    options.add_argument(f"--window-size=1920,1080")

    # Random user agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")

    # Launch ChromeDriver
    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 45)

    return driver, wait


# -------------------------------------------
# Helpers
# -------------------------------------------
def add_random_delay():
    """Add random delay between actions to simulate human behavior."""
    time.sleep(random.uniform(3, 6))

def simulate_human_typing(element, text):
    """Simulate human-like typing with random delays."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.2, 0.4))

# -------------------------------------------
# Login to X
# -------------------------------------------
def login_to_x(driver, wait):
    """
    Automatically logs into X.com using credentials from .env
    with human-like behavior.
    """
    twitter_username = os.getenv("TWITTER_USERNAME")
    twitter_password = os.getenv("TWITTER_PASSWORD")

    if not twitter_username or not twitter_password:
        raise ValueError("Twitter credentials are missing in the .env file.")

    try:
        print("[LOGIN] Navigating to X...")
        driver.get("https://x.com")
        add_random_delay()

        print("[LOGIN] Navigating to login page...")
        driver.get("https://x.com/login")
        add_random_delay()

        # Enter username
        print("[LOGIN] Entering username...")
        username_field = wait.until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        simulate_human_typing(username_field, twitter_username)
        add_random_delay()
        username_field.send_keys(Keys.RETURN)

        # Enter password
        print("[LOGIN] Entering password...")
        password_field = wait.until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        simulate_human_typing(password_field, twitter_password)
        add_random_delay()
        password_field.send_keys(Keys.RETURN)

        # Wait for home page to load fully
        print("[LOGIN] Waiting for home page...")
        home_wait = WebDriverWait(driver, 60)
        home_wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='primaryColumn']"))
        )

        print("[LOGIN] Successfully logged in.")
        return True

    except Exception as e:
        driver.save_screenshot(f"login_error_{time.strftime('%Y%m%d_%H%M%S')}.png")
        print(f"[LOGIN] Error during login: {e}")
        return False

# -------------------------------------------
# Scrape Trending Topics
# -------------------------------------------
def scrape_trending_topics(driver, wait):
    """
    Scrapes the top 5 trending topics from the 'Trending' tab:
    https://x.com/explore/tabs/trending

    Returns a list of dicts:
      [
        {
          "category": "Trending in India",
          "topic": "#ManmohanSingh",
          "post_count": "345K posts"
        },
        ...
      ]
    """
    try:
        print("[SCRAPER] Navigating to 'Trending' tab...")
        driver.get("https://x.com/explore/tabs/trending")
        add_random_delay()

        print("[SCRAPER] Waiting for trending items...")
        # Wait until we see at least one 'trend' div
        trend_items = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '[data-testid="trend"]')
            )
        )

        # Now we have all 'trend' items
        print(f"[SCRAPER] Found {len(trend_items)} items. Extracting top 5...")

        trending_data = []

        # Process only the top 5
        for item in trend_items[:5]:
            lines = item.text.split("\n")

            category = None
            topic = None
            post_count = None

            if len(lines) >= 3:
                category = lines[2]
            if len(lines) >= 4:
                topic = lines[3]
            if len(lines) >= 5:
                post_count = lines[4]

            if not topic or not topic.startswith("#"):
                print(f"[SCRAPER] Unexpected format for lines: {lines}")
                continue

            trending_data.append({
                "category": category,
                "topic": topic,
                "post_count": post_count
            })

        print("[SCRAPER] Extracted Trending Topics (up to 5):")
        for td in trending_data:
            print(f"  - Category: {td['category']}, Topic: {td['topic']}, Posts: {td['post_count']}")

        return trending_data

    except Exception as e:
        driver.save_screenshot(f"scraping_error_{time.strftime('%Y%m%d_%H%M%S')}.png")
        print(f"[SCRAPER] Error during scraping: {e}")
        return []

# -------------------------------------------
# Main Scraping Flow
# -------------------------------------------
def scrape_x():
    """
    Main scraping function that cycles through proxy addresses,
    logs in, scrapes top 5 trends, and stores in MongoDB.
    """
    proxy_addresses = [
        "us-ca.proxymesh.com:31280",
        "us-il.proxymesh.com:31280",
        "us-fl.proxymesh.com:31280"
    ]
    unique_id = str(uuid.uuid4())

    for proxy_address in proxy_addresses:
        driver = None
        try:
            print(f"[SCRAPER] Using Proxy: {proxy_address}")
            driver, wait = setup_driver(proxy_address)

            if login_to_x(driver, wait):
                print("[SCRAPER] Login successful, proceeding with scraping...")

            trending_topics = scrape_trending_topics(driver, wait)
            if trending_topics:
                record = {
                    "_id": unique_id,
                    "trend1": trending_topics[0]["topic"] if len(trending_topics) > 0 else None,
                    "trend2": trending_topics[1]["topic"] if len(trending_topics) > 1 else None,
                    "trend3": trending_topics[2]["topic"] if len(trending_topics) > 2 else None,
                    "trend4": trending_topics[3]["topic"] if len(trending_topics) > 3 else None,
                    "trend5": trending_topics[4]["topic"] if len(trending_topics) > 4 else None,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "ip_address": proxy_address
                }
                save_to_mongo(record)
                print("[SCRAPER] Data saved successfully.")
                break

        except Exception as e:
            print(f"[SCRAPER] Error: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

if __name__ == "__main__":
    scrape_x()
