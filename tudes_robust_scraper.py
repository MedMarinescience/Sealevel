#!/usr/bin/env python3
"""
TUDES Robust Data Scraper - Simplified SSL Version
Handles SSL issues automatically
"""

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta
import time
import os
import json
import warnings
import sys

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
warnings.filterwarnings('ignore')

class TudesRobustScraper:
    def __init__(self):
        self.session = self.create_session()
        self.base_url = "https://tudes.harita.gov.tr"
        
        # User configuration
        self.user_info = {
            'AdSoyad': 'serhat ertugrul',
            'Eposta': 'serhatertugrul@gmail.com',
            'Kurum': 'METU-IMS'
        }
        
        # Default parameters
        self.default_station = 'Erdemli'
        self.default_station_id = 3
        self.default_data_type = 'DenizSeviyesi'
        
    def create_session(self):
        """Create a session with SSL bypass"""
        session = requests.Session()
        session.verify = False  # Disable SSL verification
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/Portal/VeriSorgula'
        })
        
        return session
    
    def query_and_save(self, start_date, end_date, output_dir):
        """Query data and save to file"""
        
        form_data = {
            'IstasyonId': self.default_station_id,
            'VeriCesit': self.default_data_type,
            'BaslamaTarihi': start_date.strftime('%d.%m.%Y'),
            'BitisTarihi': end_date.strftime('%d.%m.%Y')
        }
        
        print(f"Querying: {form_data['BaslamaTarihi']} - {form_data['BitisTarihi']}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/Portal/VeriSorgula",
                data=form_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('Durum', 0) > 0 and result.get('Data'):
                    data = result['Data']
                    print(f"✓ Found {len(data)} data points")
                    
                    # Save to file
                    filename = f"{output_dir}/erdemli_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump({
                            'station': self.default_station,
                            'start_date': start_date.isoformat(),
                            'end_date': end_date.isoformat(),
                            'data_points': len(data),
                            'data': data
                        }, f, ensure_ascii=False, indent=2)
                    
                    print(f"✓ Saved to: {filename}")
                    return True
                else:
                    print(f"✗ No data: {result.get('Mesaj', 'Unknown error')}")
            else:
                print(f"✗ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Error: {type(e).__name__}: {str(e)}")
        
        return False
    
    def download_all(self, start_date, end_date):
        """Download data in 60-day chunks"""
        
        output_dir = f"tudes_data/erdemli_{self.default_data_type}"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nDownloading data for {self.default_station}")
        print(f"Period: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
        print("-" * 60)
        
        current = start_date
        chunk_num = 0
        successful = 0
        
        while current < end_date:
            chunk_end = min(current + timedelta(days=59), end_date)
            chunk_num += 1
            
            print(f"\nChunk {chunk_num}:")
            
            if self.query_and_save(current, chunk_end, output_dir):
                successful += 1
                time.sleep(2)
            
            current = chunk_end + timedelta(days=1)
        
        print("\n" + "="*60)
        print(f"Complete: {successful}/{chunk_num} chunks successful")
        if successful > 0:
            print(f"Data saved in: {output_dir}/")
        print("="*60)

def main():
    print("="*60)
    print("TUDES Robust Data Scraper (SSL Safe)")
    print("="*60)
    print("SSL verification is automatically disabled")
    print("="*60)
    
    scraper = TudesRobustScraper()
    
    # Simple date input
    print("\nDate range (DD.MM.YYYY format):")
    
    start_input = input("Start date (default: 01.01.2024): ").strip()
    if start_input:
        try:
            start_date = datetime.strptime(start_input, '%d.%m.%Y')
        except:
            print("Invalid format, using default")
            start_date = datetime(2024, 1, 1)
    else:
        start_date = datetime(2024, 1, 1)
    
    end_input = input("End date (default: today): ").strip()
    if end_input:
        try:
            end_date = datetime.strptime(end_input, '%d.%m.%Y')
        except:
            print("Invalid format, using today")
            end_date = datetime.now()
    else:
        end_date = datetime.now()
    
    # Download
    scraper.download_all(start_date, end_date)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\n\nError: {e}")
