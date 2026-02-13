#!/usr/bin/env python3
"""
TUDES Connection Test Script
Tests the connection and data retrieval from TUDES
"""

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import re
import warnings
from datetime import datetime, timedelta

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def test_connection():
    """Test basic connection to TUDES"""
    print("1. Testing connection to TUDES...")
    
    try:
        response = requests.get('https://tudes.harita.gov.tr', timeout=10, verify=False)
        if response.status_code == 200:
            print("✓ Connection successful")
            return True
        else:
            print(f"✗ Connection failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def test_data_page():
    """Test access to data query page"""
    print("\n2. Testing data query page...")
    
    try:
        response = requests.get('https://tudes.harita.gov.tr/Portal/VeriSorgula', timeout=10, verify=False)
        if response.status_code == 200:
            print("✓ Data page accessible")
            
            # Extract token
            token_match = re.search(r'name="__RequestVerificationToken".*?value="([^"]+)"', response.text)
            if token_match:
                token = token_match.group(1)
                print(f"✓ Found verification token: {token[:20]}...")
                return True, token
            else:
                print("✗ Verification token not found")
                return True, None
        else:
            print(f"✗ Page not accessible: Status {response.status_code}")
            return False, None
    except Exception as e:
        print(f"✗ Error accessing page: {e}")
        return False, None

def test_data_query(token=None):
    """Test data query for Erdemli station"""
    print("\n3. Testing data query for Erdemli station...")
    
    session = requests.Session()
    session.verify = False  # Disable SSL verification
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://tudes.harita.gov.tr',
        'Referer': 'https://tudes.harita.gov.tr/Portal/VeriSorgula',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    })
    
    # Test with a 7-day period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    form_data = {
        'IstasyonId': '3',  # Erdemli
        'VeriCesit': 'DenizSeviyesi',
        'BaslamaTarihi': start_date.strftime('%d.%m.%Y'),
        'BitisTarihi': end_date.strftime('%d.%m.%Y')
    }
    
    if token:
        form_data['__RequestVerificationToken'] = token
    
    print(f"Query period: {form_data['BaslamaTarihi']} - {form_data['BitisTarihi']}")
    
    try:
        response = session.post(
            'https://tudes.harita.gov.tr/Portal/VeriSorgula',
            data=form_data,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✓ Got JSON response")
                
                # Pretty print the response structure
                print("\nResponse structure:")
                print(json.dumps(result, indent=2, ensure_ascii=False)[:500] + "...")
                
                if result.get('Durum', 0) > 0:
                    data = result.get('Data', [])
                    print(f"\n✓ Query successful! Found {len(data)} data points")
                    
                    if data:
                        print(f"First data point: {data[0]}")
                        print(f"Last data point: {data[-1]}")
                else:
                    print(f"✗ Query failed: {result.get('Mesaj', 'Unknown error')}")
                
                return True
                
            except json.JSONDecodeError:
                print("✗ Response is not JSON")
                print(f"Response content: {response.text[:200]}...")
                return False
        else:
            print(f"✗ Query failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Query error: {e}")
        return False

def test_download_log():
    """Test download logging endpoint"""
    print("\n4. Testing download log endpoint...")
    
    session = requests.Session()
    session.verify = False  # Disable SSL verification
    
    form_data = {
        'AdSoyad': 'Test User',
        'Eposta': 'test@example.com',
        'Kurum': 'Test Institution',
        'LisansSozlesmesi': 'on',
        'parametreler': '{"BaslangicTarih":"01.01.2024","BitisTarihi":"31.01.2024"}',
        'tip': 'json'
    }
    
    try:
        response = session.post(
            'https://tudes.harita.gov.tr/Portal/VeriIndirLog',
            data=form_data,
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Log endpoint accessible")
        else:
            print("✗ Log endpoint returned error")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    print("TUDES API Test Script")
    print("="*60)
    
    # Test 1: Basic connection
    if not test_connection():
        print("\nConnection failed. Check your internet connection.")
        return
    
    # Test 2: Data page access
    page_ok, token = test_data_page()
    if not page_ok:
        print("\nCannot access data page.")
        return
    
    # Test 3: Data query
    test_data_query(token)
    
    # Test 4: Download log
    test_download_log()
    
    print("\n" + "="*60)
    print("Test complete!")
    print("\nRecommendations:")
    print("- If data query works: Use 'download_erdemli_data.py'")
    print("- If SSL errors: Use 'tudes_robust_scraper.py --no-verify-ssl'")
    print("- For debugging: Use 'tudes_scraper_v2.py' with verbose output")

if __name__ == "__main__":
    main()
