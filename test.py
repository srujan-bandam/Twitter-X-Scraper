from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import uuid
from pymongo import MongoClient
import time
from config import Config

# MongoDB Configuration
mongo_uri = Config.MONGODB_URI
db_name = Config.DB_NAME
collection_name =Config.COLLECTION_NAME

options = webdriver.ChromeOptions()
        # Enabling headless mode 
        # options.add_argument("--headless=new")  

options.add_argument("--disable-gpu")  
options.add_argument("--no-sandbox")  
options.add_argument("--disable-dev-shm-usage")  
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
PROXY_USERNAME = Config.PROXY_USERNAME
PROXY_PASSWORD = Config.PROXY_PASSWORD
PROXY_HOST = Config.PROXY_HOST
PROXY_PORT = Config.PROXY_PORT

    
options.add_argument(f'--proxy-server=http://{PROXY_HOST}:{PROXY_PORT}')
options.add_argument(f'--proxy-auth={PROXY_USERNAME}:{PROXY_PASSWORD}')
options.add_argument(f'--proxy-bypass-list=<-loopback>')

chrome_options = Options()
service = Service('chromedriver.exe')
#driver = webdriver.Chrome(options=options)
driver = webdriver.Chrome(service=service, options=chrome_options)

def fetch_trending_topics():
    try:
        # Login
        driver.get("https://x.com/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text"))).send_keys(Config.TWITTER_USERNAME, Keys.RETURN)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(Config.TWITTER_PASSWORD, Keys.RETURN)
        
        # Optional email step
        try:
            email_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
            email_field.send_keys(Config.TWITTER_EMAIL, Keys.RETURN)
        except Exception:
            print("Email step skipped.")
        
        # Fetch trends
        driver.get("https://x.com/explore/tabs/trending")
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='trend']")))
        trending_elements = driver.find_elements(By.XPATH, "//div[@data-testid='trend']")[:5]
        trends = [element.text for element in trending_elements]
        return trends
    except Exception as e:
        print("Error fetching trends:", e)
        return []

def store_in_mongodb(unique_id, trends, end_time, ip_address):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    data = {
        "unique_id": unique_id,
        "trend1": trends[0] if len(trends) > 0 else None,
        "trend2": trends[1] if len(trends) > 1 else None,
        "trend3": trends[2] if len(trends) > 2 else None,
        "trend4": trends[3] if len(trends) > 3 else None,
        "trend5": trends[4] if len(trends) > 4 else None,
        "end_time": end_time,
        "ip_address": ip_address,
    }
    collection.insert_one(data)
    print("Data stored in MongoDB.")
    

def get_current_ip():
    driver.get("http://httpbin.org/ip")
    time.sleep(3)
    return driver.find_element(By.TAG_NAME, "body").text


# Main Execution
try:
    unique_id = str(uuid.uuid4())
    trends = fetch_trending_topics()
    ip_address = get_current_ip()
    end_time = datetime.now()
    store_in_mongodb(unique_id, trends, end_time, ip_address)
finally:
    driver.quit()
