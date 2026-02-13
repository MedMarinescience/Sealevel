from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import time
import os
import json
import pandas as pd

class TudesSeleniumScraper:
    def __init__(self, headless=False):
        self.setup_driver(headless)
        self.base_url = "https://tudes.harita.gov.tr/Portal/VeriSorgula"
        
        # User information (can be overridden from environment variables)
        self.user_info = {
            'ad_soyad': os.getenv('TUDES_USER_NAME', 'YOUR NAME'),
            'e_posta': os.getenv('TUDES_USER_EMAIL', 'your.email@example.com'),
            'kurum': os.getenv('TUDES_USER_INSTITUTION', 'YOUR INSTITUTION')
        }
        
    def setup_driver(self, headless):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Download settings
        prefs = {
            "download.default_directory": os.path.abspath("./downloads"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except:
            print("Chrome driver not found. Please install ChromeDriver.")
            print("You can download it from: https://chromedriver.chromium.org/")
            raise
    
    def wait_and_find(self, by, value, timeout=10):
        """Wait for element and return it"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_and_click(self, by, value, timeout=10):
        """Wait for element to be clickable and click it"""
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()
        return element
    
    def fill_user_info(self):
        """Fill in user information fields"""
        print("Filling user information...")
        
        # Fill Ad Soyad
        ad_soyad = self.wait_and_find(By.ID, "adSoyad")
        ad_soyad.clear()
        ad_soyad.send_keys(self.user_info['ad_soyad'])
        
        # Fill E-posta
        e_posta = self.wait_and_find(By.ID, "ePosta")
        e_posta.clear()
        e_posta.send_keys(self.user_info['e_posta'])
        
        # Fill Kurum
        kurum = self.wait_and_find(By.ID, "kurum")
        kurum.clear()
        kurum.send_keys(self.user_info['kurum'])
        
        # Check license agreement
        try:
            lisans = self.driver.find_element(By.ID, "lisansOnay")
            if not lisans.is_selected():
                lisans.click()
        except:
            print("License checkbox not found or already checked")
    
    def select_station(self, station_name="erdemli"):
        """Select station from the dropdown"""
        print(f"Selecting station: {station_name}")
        
        # Find and click station input
        station_input = self.wait_and_find(By.ID, "istasyon")
        station_input.clear()
        station_input.send_keys(station_name)
        
        # Wait for dropdown to appear
        time.sleep(2)
        
        # Try to select first option from dropdown
        try:
            first_option = self.wait_and_find(By.CSS_SELECTOR, ".ui-menu-item", timeout=5)
            first_option.click()
        except:
            print("No dropdown appeared, continuing with typed value")
    
    def set_date_range(self, start_date, end_date):
        """Set date range for data download"""
        print(f"Setting date range: {start_date} to {end_date}")
        
        # Set start date
        start_input = self.wait_and_find(By.ID, "tarihBaslangic")
        start_input.clear()
        start_input.send_keys(start_date.strftime('%d.%m.%Y'))
        
        # Set end date
        end_input = self.wait_and_find(By.ID, "tarihBitis")
        end_input.clear()
        end_input.send_keys(end_date.strftime('%d.%m.%Y'))
    
    def select_data_type(self, data_type="seviye"):
        """Select data type (seviye for sea level)"""
        print(f"Selecting data type: {data_type}")
        
        try:
            # Find the select element
            data_select = self.wait_and_find(By.ID, "veriTuru")
            
            # Use JavaScript to set value
            self.driver.execute_script(f"document.getElementById('veriTuru').value = '{data_type}';")
        except:
            print("Could not find data type selector")
    
    def submit_form(self):
        """Submit the data request form"""
        print("Submitting form...")
        
        try:
            # Find and click submit button
            submit_button = self.wait_and_click(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .btn-primary")
            time.sleep(3)
            
            # Check for any response or download
            return True
        except Exception as e:
            print(f"Error submitting form: {e}")
            return False
    
    def download_data_chunk(self, station_name, start_date, end_date):
        """Download data for a specific date range"""
        try:
            # Navigate to the page
            self.driver.get(self.base_url)
            time.sleep(2)
            
            # Fill form
            self.fill_user_info()
            self.select_station(station_name)
            self.set_date_range(start_date, end_date)
            self.select_data_type("seviye")
            
            # Submit
            success = self.submit_form()
            
            if success:
                print(f"Successfully submitted request for {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
                
                # Wait for any download or response
                time.sleep(5)
                
                # Save page source as backup
                output_dir = f"tudes_data/{station_name}"
                os.makedirs(output_dir, exist_ok=True)
                
                filename = f"{output_dir}/response_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error in download_data_chunk: {e}")
            return False
    
    def download_all_data(self, station_name, total_start_date, total_end_date):
        """Download data in 60-day chunks"""
        current_date = total_start_date
        chunk_count = 0
        successful_chunks = 0
        
        while current_date < total_end_date:
            chunk_end_date = min(current_date + timedelta(days=59), total_end_date)
            
            chunk_count += 1
            print(f"\n{'='*50}")
            print(f"Processing chunk {chunk_count}")
            print(f"{'='*50}")
            
            success = self.download_data_chunk(station_name, current_date, chunk_end_date)
            
            if success:
                successful_chunks += 1
                # Wait between requests
                time.sleep(3)
            else:
                print(f"Failed to download chunk {chunk_count}")
            
            current_date = chunk_end_date + timedelta(days=1)
        
        print(f"\nCompleted: {successful_chunks}/{chunk_count} chunks downloaded successfully")
    
    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    # Create downloads directory
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("tudes_data", exist_ok=True)
    
    print("TUDES Data Scraper with Selenium")
    print("="*50)
    
    # Ask if user wants headless mode
    headless_input = input("Run in headless mode? (y/n, default: n): ").strip().lower()
    headless = headless_input == 'y'
    
    # Initialize scraper
    try:
        scraper = TudesSeleniumScraper(headless=headless)
    except Exception as e:
        print(f"Failed to initialize scraper: {e}")
        return
    
    try:
        # Get station name
        station_name = input("Enter station name (default: erdemli): ").strip()
        if not station_name:
            station_name = "erdemli"
        
        # Get date range
        print("\nDate range (max 60 days per request)")
        start_date_str = input("Start date (DD.MM.YYYY, default: 01.01.2023): ").strip()
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
            except:
                print("Invalid date format. Using default.")
                start_date = datetime(2023, 1, 1)
        else:
            start_date = datetime(2023, 1, 1)
        
        end_date_str = input("End date (DD.MM.YYYY, default: today): ").strip()
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%d.%m.%Y')
            except:
                print("Invalid date format. Using today.")
                end_date = datetime.now()
        else:
            end_date = datetime.now()
        
        # Download data
        scraper.download_all_data(station_name, start_date, end_date)
        
    finally:
        # Always close the browser
        scraper.close()
        print("\nScraper closed.")

if __name__ == "__main__":
    main()
