#!/usr/bin/env python3
"""
TUDES Data Scraper - Main Menu
Choose your preferred scraping method
This code is compatible with Python 3.10
This script is used to scrape data from the TUDES website for the all stations.
Key Features:
* Multi-Method Scraping: Supports Simple Requests, Advanced API v2 logic, 
  and Selenium-based browser automation.
* SSL Resilience: Automatically bypasses local issuer certificate verification 
  issues common in institutional networks.
* All-Station Support: Configured for all 20+ TUDES stations including 
  Erdemli, Antalya, Istanbul, and Trabzon.
* Data Processing: Built-in utility to merge chronological JSON data chunks 
  into research-ready Excel (.xlsx) or CSV formats.
* Multi-Parameter: Capable of retrieving Sea Level (m), Temperature, 
  Pressure, Humidity, and Wind data.

Compatibility: Python 3.10+
Developed for: Aquatic Ecology Lab, METU-IMS
Author: Serhat Ertugrul

"""

import os
import sys
import subprocess

def print_header():
    print("="*60)
    print("TUDES DATA SCRAPER FOR SEA LEVEL DATA")
    print("="*60)
    print("Pre-configured with:")
    print("  - Name: xxxx") # TODO: change to your name
    print("  - Email: xxx") # TODO: change to your email
    print("  - Institution: xxx") # TODO: change to your institution
    print("  - Station: xxx") # TODO: change to your station
    print("  - Data Type: Sea Level (meters)") # TODO: change to your data type unfournately only sea level is available until now
    print("="*60)

def print_menu():
    print("\nChoose a scraping method:")
    print("1. Simple Download (Erdemli)")#our harbor station
    print("2. Advanced Scraper V2 (All Stations - Recommended)")#all stations in system 
    print("3. Selenium Browser Automation")#selenium browser automation
    print("4. Robust Scraper (Legacy SSL Safe)")#robust scraper
    print("5. Connection Test")#connection test
    print("6. Combine JSON files to Excel")#combine json files to excel
    print("7. Exit")#exit
    print()

def run_script(script_name):
    """Run a Python script"""
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except subprocess.CalledProcessError:
        print(f"\nError running {script_name}")
    except FileNotFoundError:
        print(f"\nScript not found: {script_name}")

def main():
    print_header()
    print("Note: All scrapers now include automatic SSL bypass.")
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            print("\nStarting simple downloader...")
            run_script('download_erdemli_data.py')
        
        elif choice == '2':
            print("\nStarting Advanced Scraper V2...")
            run_script('tudes_scraper_v2.py')
        
        elif choice == '3':
            print("\nStarting Selenium scraper...")
            print("Note: This requires ChromeDriver to be installed")
            run_script('tudes_selenium_scraper.py')
        
        elif choice == '4':
            print("\nStarting robust scraper...")
            run_script('tudes_robust_scraper.py')
            
        elif choice == '5':
            print("\nStarting connection test...")
            run_script('test_tudes_connection.py')
            
        elif choice == '6':
            print("\nStarting JSON to Excel converter...")
            run_script('tudes_json_to_excel.py')
        
        elif choice == '7':
            print("\nExiting...")
            break
        
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
