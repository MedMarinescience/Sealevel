#!/usr/bin/env python3
"""
TUDES Data Downloader - Simple Interactive Script
Downloads sea level data from Erdemli station
Updated to match actual website structure
"""

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta
import time
import os
import json
import re
import warnings

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Configuration based on HTML analysis
USER_INFO = {
    'AdSoyad': 'serhat ertugrul',
    'Eposta': 'serhatertugrul@gmail.com',  
    'Kurum': 'METU-IMS',
    'LisansSozlesmesi': 'on'
}

STATION_NAME = 'Erdemli'
STATION_ID = 3  # From HTML: <option value="3">Erdemli</option>
DATA_TYPE = 'DenizSeviyesi'  # Sea level in meters
DATA_TYPE_DISPLAY = 'Seviye (m)'

def create_session():
    """Create a session with proper headers and SSL bypass"""
    session = requests.Session()
    session.verify = False  # Disable SSL verification
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://tudes.harita.gov.tr',
        'Referer': 'https://tudes.harita.gov.tr/Portal/VeriSorgula'
    })
    return session

def get_verification_token(session):
    """Get the __RequestVerificationToken from the page"""
    try:
        response = session.get('https://tudes.harita.gov.tr/Portal/VeriSorgula')
        token_match = re.search(r'name="__RequestVerificationToken".*?value="([^"]+)"', response.text)
        if token_match:
            return token_match.group(1)
    except:
        pass
    return None

def query_data(session, start_date, end_date):
    """Query data from TUDES"""
    
    token = get_verification_token(session)
    
    # Prepare form data matching exact structure from HTML
    form_data = {
        'IstasyonId': STATION_ID,
        'VeriCesit': DATA_TYPE,
        'BaslamaTarihi': start_date.strftime('%d.%m.%Y'),
        'BitisTarihi': end_date.strftime('%d.%m.%Y')
    }
    
    if token:
        form_data['__RequestVerificationToken'] = token
    
    print(f"Querying: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    
    try:
        response = session.post(
            'https://tudes.harita.gov.tr/Portal/VeriSorgula',
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('Durum', 0) > 0 and result.get('Data'):
                print(f"✓ Found {len(result['Data'])} data points")
                return result['Data']
            else:
                print(f"✗ No data found: {result.get('Mesaj', 'Unknown error')}")
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return None

def download_and_save(session, data, start_date, end_date, output_dir):
    """Log download and save data"""
    
    if not data:
        return False
    
    # Create filename
    filename = f"erdemli_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Save data
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'station': STATION_NAME,
            'station_id': STATION_ID,
            'data_type': DATA_TYPE,
            'data_type_display': DATA_TYPE_DISPLAY,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'download_info': USER_INFO,
            'data_points': len(data),
            'data': data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved to: {filename}")
    
    # Log download request (as per website requirement)
    try:
        token = get_verification_token(session)
        
        parametreler = {
            'BaslangicTarih': start_date.strftime('%d.%m.%Y'),
            'BitisTarihi': end_date.strftime('%d.%m.%Y'),
            DATA_TYPE_DISPLAY: f"{STATION_NAME},"
        }
        
        log_data = {
            'AdSoyad': USER_INFO['AdSoyad'],
            'Eposta': USER_INFO['Eposta'],
            'Kurum': USER_INFO['Kurum'],
            'LisansSozlesmesi': USER_INFO['LisansSozlesmesi'],
            'parametreler': json.dumps(parametreler),
            'tip': 'json'
        }
        
        if token:
            log_data['__RequestVerificationToken'] = token
        
        session.post(
            'https://tudes.harita.gov.tr/Portal/VeriIndirLog',
            data=log_data
        )
    except:
        pass  # Logging is optional
    
    return True

def main():
    print("="*60)
    print("TUDES Data Downloader for Erdemli Station")
    print("="*60)
    print(f"Station: {STATION_NAME} (ID: {STATION_ID})")
    print(f"Data type: {DATA_TYPE_DISPLAY}")
    print(f"User: {USER_INFO['AdSoyad']}")
    print(f"Email: {USER_INFO['Eposta']}")
    print(f"Institution: {USER_INFO['Kurum']}")
    print("="*60)
    
    # Get date range
    print("\nEnter date range (leave empty for defaults)")
    print("Format: DD.MM.YYYY")
    
    # Start date
    start_input = input("Start date (default: 01.01.2024): ").strip()
    if start_input:
        try:
            start_date = datetime.strptime(start_input, '%d.%m.%Y')
        except:
            print("Invalid format, using default")
            start_date = datetime(2024, 1, 1)
    else:
        start_date = datetime(2024, 1, 1)
    
    # End date
    end_input = input("End date (default: today): ").strip()
    if end_input:
        try:
            end_date = datetime.strptime(end_input, '%d.%m.%Y')
        except:
            print("Invalid format, using today")
            end_date = datetime.now()
    else:
        end_date = datetime.now()
    
    # Calculate chunks
    total_days = (end_date - start_date).days
    num_chunks = (total_days // 60) + (1 if total_days % 60 else 0)
    
    print(f"\nDate range: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    print(f"Total days: {total_days}")
    print(f"Number of 60-day chunks: {num_chunks}")
    
    # Confirm
    confirm = input("\nProceed with download? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Create output directory
    output_dir = f"tudes_data/erdemli_{DATA_TYPE}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create session
    session = create_session()
    
    # Download in chunks
    current_date = start_date
    chunk_num = 0
    successful = 0
    total_points = 0
    
    print(f"\nStarting download to: {output_dir}/")
    print("-"*60)
    
    while current_date < end_date:
        chunk_end = min(current_date + timedelta(days=59), end_date)
        chunk_num += 1
        
        print(f"\nChunk {chunk_num}/{num_chunks}:")
        
        # Query data
        data = query_data(session, current_date, chunk_end)
        
        if data:
            # Save data
            if download_and_save(session, data, current_date, chunk_end, output_dir):
                successful += 1
                total_points += len(data)
                time.sleep(2)  # Be nice to the server
        
        current_date = chunk_end + timedelta(days=1)
    
    # Summary
    print("\n" + "="*60)
    print(f"Download complete!")
    print(f"Successful chunks: {successful}/{num_chunks}")
    print(f"Total data points: {total_points}")
    print(f"Data saved in: {output_dir}/")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
