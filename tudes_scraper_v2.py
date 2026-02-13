#!/usr/bin/env python3
"""
TUDES Data Scraper - Updated Version
Based on actual website structure from HTML analysis
"""

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta
import time
import os
import json
import re
import html as html_lib
from tudes_json_to_excel import convert_json_folder

import warnings

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class TudesDataScraperV2:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification
        self.base_url = "https://tudes.harita.gov.tr"
        self.query_url = f"{self.base_url}/Portal/VeriSorgula"
        self.download_log_url = f"{self.base_url}/Portal/VeriIndirLog"
        
        # Station mapping (fallback if live parsing fails)
        self.stations = {
            'Amasra': 13,
            'Antalya': 20,
            'Arsuz': 2,
            'Bodrum': 15,
            'Bozyazı': 11,
            'Erdek': 17,
            'Erdemli': 3,
            'Gazımagusa': 18,
            'Girne': 19,
            'Gokceada': 4,
            'Igneada': 14,
            'Istanbul': 21,
            'Marmara Ereglisi': 9,
            'Marmaris': 8,
            'Mentes': 16,
            'Sıle': 5,
            'Sinop': 10,
            'Tasucu': 12,
            'Trabzon': 6,
            'Yalova': 7
        }
        
        # Data types (fallback if live parsing fails)
        self.data_types = {
            'Seviye (m)': 'DenizSeviyesi',
            'Ruzgar1 (WVc)': 'Ruzgar1',
            'Ruzgar2 (WVc)': 'Ruzgar2',
            'Ruzgar3 (WVc)': 'Ruzgar3',
            'Ruzgar4 (WVc)': 'Ruzgar4',
            'Sıcaklık (°C)': 'Sicaklik',
            'Basınç (mbar)': 'Basinc',
            'Nem (%)': 'Nem'
        }
        
        # User information (can be overridden from environment variables)
        self.user_info = {
            'AdSoyad': os.getenv('TUDES_USER_NAME', 'YOUR NAME'),
            'Eposta': os.getenv('TUDES_USER_EMAIL', 'your.email@example.com'),
            'Kurum': os.getenv('TUDES_USER_INSTITUTION', 'YOUR INSTITUTION')
        }
        
        self.setup_session()
        self.refresh_metadata()
    
    def setup_session(self):
        """Setup session with proper headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/Portal/VeriSorgula'
        })

    def refresh_metadata(self):
        """Fetch live station and data type lists from the page"""
        page_html = self._fetch_page_html()
        if not page_html:
            return

        stations = self._parse_select_options(page_html, 'IstasyonId')
        data_types = self._parse_select_options(page_html, 'VeriCesit')
        form_action = self._extract_form_action(page_html)

        if stations:
            self.stations = stations
        if data_types:
            self.data_types = data_types
        if form_action:
            self.query_url = f"{self.base_url}{form_action}"

    def _fetch_page_html(self):
        try:
            response = self.session.get(self.query_url, timeout=30)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"Warning: Could not load page HTML: {e}")
        return None

    def _parse_select_options(self, page_html, select_id):
        select_match = re.search(
            rf'<select[^>]*id="{select_id}"[^>]*>(.*?)</select>',
            page_html,
            re.IGNORECASE | re.DOTALL
        )
        if not select_match:
            return None

        select_html = select_match.group(1)
        options = re.findall(
            r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>',
            select_html,
            re.IGNORECASE | re.DOTALL
        )
        parsed = {}
        for value, label in options:
            clean_label = html_lib.unescape(re.sub(r'<.*?>', '', label)).strip()
            if value and clean_label:
                parsed[clean_label] = value
        return parsed or None

    def _extract_form_action(self, page_html):
        form_match = re.search(
            r'<form[^>]*id="frmVeriSorgula"[^>]*action="([^"]+)"',
            page_html,
            re.IGNORECASE
        )
        if form_match:
            return form_match.group(1)
        return None

    def _data_type_label(self, data_type_code):
        for label, code in self.data_types.items():
            if code == data_type_code:
                return label
        return None

    def _save_debug_response(self, response_text, station_name, data_type, start_date, end_date):
        debug_dir = os.path.join("tudes_data", "_debug")
        os.makedirs(debug_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"debug_{station_name}_{data_type}_{timestamp}.html"
        filepath = os.path.join(debug_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response_text)
        print(f"Saved debug response to: {filepath}")
    
    def get_request_token(self):
        """Get the request verification token from the page"""
        try:
            response = self.session.get(self.query_url, timeout=30)
            
            # Extract __RequestVerificationToken
            token_match = re.search(r'name="__RequestVerificationToken".*?value="([^"]+)"', response.text)
            if token_match:
                return token_match.group(1)
            
            print("Warning: Could not find request verification token")
            return None
        except Exception as e:
            print(f"Error getting request token: {e}")
            return None
    
    def query_data(self, station_id, data_type, start_date, end_date):
        """Query data from TUDES API"""
        
        # Format dates
        start_date_str = start_date.strftime('%d.%m.%Y')
        end_date_str = end_date.strftime('%d.%m.%Y')
        
        # Get request token
        token = self.get_request_token()
        
        # Prepare form data matching the HTML structure
        form_data = {
            'IstasyonId': station_id,
            'VeriCesit': data_type,
            'BaslamaTarihi': start_date_str,
            'BitisTarihi': end_date_str
        }
        
        if token:
            form_data['__RequestVerificationToken'] = token
        
        # Make the request
        try:
            response = self.session.post(
                self.query_url,
                data=form_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    print("Error: Server did not return JSON. Saving debug response.")
                    self._save_debug_response(response.text, str(station_id), data_type, start_date, end_date)
                    return None
            else:
                print(f"Error: Server returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error querying data: {e}")
            return None
    
    def download_data(self, station_name, station_id, data_type, data_to_download, start_date, end_date):
        """Download data with user information"""
        
        # Get request token
        token = self.get_request_token()
        
        # Prepare download parameters
        display_label = self._data_type_label(data_type)
        parametreler = {
            'BaslangicTarih': start_date.strftime('%d.%m.%Y'),
            'BitisTarihi': end_date.strftime('%d.%m.%Y')
        }
        if display_label:
            parametreler[display_label] = f"{station_name},"
        else:
            parametreler[data_type] = f"{station_name},"
        
        # Prepare form data for download
        form_data = {
            'AdSoyad': self.user_info['AdSoyad'],
            'Eposta': self.user_info['Eposta'],
            'Kurum': self.user_info['Kurum'],
            'LisansSozlesmesi': 'on',
            'parametreler': json.dumps(parametreler),
            'tip': 'json'
        }
        
        if token:
            form_data['__RequestVerificationToken'] = token
        
        # Log the download request
        try:
            response = self.session.post(
                self.download_log_url,
                data=form_data,
                timeout=30
            )
            print(f"Download logged: {response.status_code}")
        except Exception as e:
            print(f"Error logging download: {e}")
        
        return data_to_download
    
    def process_station(self, station_name, start_date, end_date, data_type='DenizSeviyesi'):
        """Process data download for a specific station"""
        
        # Get station ID
        station_id = self.stations.get(station_name)
        if not station_id:
            print(f"Station '{station_name}' not found!")
            print(f"Available stations: {', '.join(self.stations.keys())}")
            return False
        
        print(f"\nProcessing: {station_name} (ID: {station_id})")
        print(f"Date range: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
        print(f"Data type: {data_type}")
        
        # Query the data
        result = self.query_data(station_id, data_type, start_date, end_date)
        
        if result and result.get('Durum', 0) > 0:
            data = result.get('Data', [])
            if data:
                print(f"Found {len(data)} data points")
                
                # Download and save
                downloaded_data = self.download_data(station_name, station_id, data_type, data, start_date, end_date)
                
                # Save to file
                output_dir = f"tudes_data/{station_name}_{data_type}"
                os.makedirs(output_dir, exist_ok=True)
                
                filename = f"{output_dir}/{station_name}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'station': station_name,
                        'station_id': station_id,
                        'data_type': data_type,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'data': downloaded_data
                    }, f, ensure_ascii=False, indent=2)
                
                print(f"✓ Data saved to: {filename}")
                return True
            else:
                print("No data found for this period")
                return False
        else:
            error_msg = result.get('Mesaj', 'Unknown error') if result else 'No response'
            print(f"Error: {error_msg}")
            return False
    
    def download_in_chunks(self, station_name, total_start_date, total_end_date, data_type='DenizSeviyesi'):
        """Download data in 60-day chunks"""
        output_dir = f"tudes_data/{station_name}_{data_type}"
        os.makedirs(output_dir, exist_ok=True)

        current_date = total_start_date
        chunk_count = 0
        successful_chunks = 0
        
        print(f"\n{'='*60}")
        print(f"Downloading data for: {station_name}")
        print(f"Total period: {total_start_date.strftime('%d.%m.%Y')} - {total_end_date.strftime('%d.%m.%Y')}")
        print(f"{'='*60}")
        
        while current_date < total_end_date:
            chunk_end_date = min(current_date + timedelta(days=59), total_end_date)
            
            chunk_count += 1
            print(f"\n--- Chunk {chunk_count} ---")
            
            success = self.process_station(station_name, current_date, chunk_end_date, data_type)
            
            if success:
                successful_chunks += 1
                # Wait between requests
                time.sleep(2)
            
            current_date = chunk_end_date + timedelta(days=1)
        
        print(f"\n{'='*60}")
        print(f"Download complete: {successful_chunks}/{chunk_count} chunks successful")
        print(f"{'='*60}")
        return {
            'output_dir': output_dir,
            'successful_chunks': successful_chunks,
            'chunk_count': chunk_count
        }

def main():
    print("TUDES Data Scraper V2 - Based on Actual Website Structure")
    print("="*60)
    
    # Initialize scraper
    scraper = TudesDataScraperV2()
    
    # Show available stations
    print("\nAvailable stations:")
    for i, (name, id) in enumerate(scraper.stations.items(), 1):
        print(f"{i:2}. {name} (ID: {id})")
    
    # Get station choice
    print("\nEnter station name (default: Erdemli): ", end='')
    station_input = input().strip()
    station_name = station_input if station_input else 'Erdemli'
    
    # Validate station
    if station_name not in scraper.stations:
        print(f"Station '{station_name}' not found. Using 'Erdemli'")
        station_name = 'Erdemli'
    
    # Show available data types
    print("\nAvailable data types:")
    for i, (display_name, code) in enumerate(scraper.data_types.items(), 1):
        print(f"{i}. {display_name} ({code})")
    
    print("\nSelect data type (1-8, default: 1 for sea level): ", end='')
    type_input = input().strip()
    
    try:
        type_idx = int(type_input) - 1 if type_input else 0
        data_type_code = list(scraper.data_types.values())[type_idx]
    except:
        print("Invalid selection. Using sea level data.")
        data_type_code = 'DenizSeviyesi'
    
    # Get date range
    print("\nEnter start date (DD.MM.YYYY, default: 01.01.2024): ", end='')
    start_input = input().strip()
    
    if start_input:
        try:
            start_date = datetime.strptime(start_input, '%d.%m.%Y')
        except:
            print("Invalid date format. Using default.")
            start_date = datetime(2014, 1, 1)
    else:
        start_date = datetime(2024, 1, 1)
    
    print("Enter end date (DD.MM.YYYY, default: today): ", end='')
    end_input = input().strip()
    
    if end_input:
        try:
            end_date = datetime.strptime(end_input, '%d.%m.%Y')
        except:
            print("Invalid date format. Using today.")
            end_date = datetime.now()
    else:
        end_date = datetime.now()
    
    # Summary
    print(f"\n{'='*60}")
    print("Download Configuration:")
    print(f"Station: {station_name}")
    print(f"Data Type: {data_type_code}")
    print(f"Period: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    print(f"User: {scraper.user_info['AdSoyad']}")
    print(f"Email: {scraper.user_info['Eposta']}")
    print(f"Institution: {scraper.user_info['Kurum']}")
    print(f"{'='*60}")
    
    # Confirm
    print("\nProceed? (y/n): ", end='')
    if input().strip().lower() != 'y':
        print("Cancelled.")
        return
    
    # Download data
    result = scraper.download_in_chunks(station_name, start_date, end_date, data_type_code)
    if result and result.get('successful_chunks', 0) > 0:
        print("\nCompiling JSON files to Excel/CSV...")
        try:
            convert_json_folder(
                result['output_dir'],
                output_dir=result['output_dir'],
                output_prefix=f"{station_name}_{data_type_code}"
            )
        except Exception as e:
            print(f"Warning: Could not compile JSON to Excel/CSV: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
