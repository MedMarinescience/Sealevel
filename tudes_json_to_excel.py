#!/usr/bin/env python3
"""
TUDES JSON to Excel Converter
Combines multiple JSON chunks into a single Excel file
"""

import os
import json
import pandas as pd
from datetime import datetime
import glob

def convert_json_folder(folder_path, output_dir=None, output_prefix=None):
    """Convert all JSON files in a folder into a combined Excel/CSV file."""
    if not os.path.exists(folder_path):
        print(f"Error: folder not found: {folder_path}")
        return None

    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    if not json_files:
        print(f"No JSON files found in {folder_path}")
        return None

    folder_name = os.path.basename(folder_path.rstrip("\\/"))
    print(f"\nReading {len(json_files)} JSON files from {folder_name}...")

    all_data = []
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if 'data' in content and isinstance(content['data'], list):
                    all_data.extend(content['data'])
                elif isinstance(content, list):
                    all_data.extend(content)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    if not all_data:
        print("No data points found in JSON files.")
        return None

    print(f"Total data points found: {len(all_data)}")

    df = pd.DataFrame(all_data)

    if 'Tarih' in df.columns:
        print("Converting timestamps...")
        df['Datetime'] = pd.to_datetime(df['Tarih'], unit='ms')
        cols = ['Datetime'] + [c for c in df.columns if c != 'Datetime']
        df = df[cols]

    if 'Datetime' in df.columns:
        df = df.sort_values('Datetime')

    initial_len = len(df)
    df = df.drop_duplicates()
    if len(df) < initial_len:
        print(f"Removed {initial_len - len(df)} duplicate records.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not output_dir:
        output_dir = os.getcwd()
    if not output_prefix:
        output_prefix = folder_name

    output_filename = os.path.join(output_dir, f"{output_prefix}_combined_{timestamp}.xlsx")
    csv_filename = os.path.join(output_dir, f"{output_prefix}_combined_{timestamp}.csv")

    print("\nSaving data...")
    try:
        df.to_excel(output_filename, index=False)
        print(f"✓ Excel file created: {output_filename}")
        return output_filename
    except Exception as e:
        print(f"✗ Could not save Excel file: {e}")
        print("Trying to save as CSV instead...")
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"✓ CSV file created: {csv_filename}")
        print("Tip: Install openpyxl (pip install openpyxl) to enable Excel export.")
        return csv_filename

def convert_json_to_excel():
    print("="*60)
    print("TUDES JSON to Excel Converter")
    print("="*60)

    data_root = "tudes_data"
    if not os.path.exists(data_root):
        print(f"Error: {data_root} directory not found.")
        return

    subdirs = [d for d in os.listdir(data_root) if os.path.isdir(os.path.join(data_root, d))]
    if not subdirs:
        print("No data folders found in tudes_data/")
        return

    print("\nAvailable data folders:")
    for i, subdir in enumerate(subdirs, 1):
        print(f"{i}. {subdir}")

    choice = input(f"\nSelect a folder (1-{len(subdirs)}, default: 1): ").strip()
    try:
        idx = int(choice) - 1 if choice else 0
        selected_subdir = subdirs[idx]
    except:
        selected_subdir = subdirs[0]

    folder_path = os.path.join(data_root, selected_subdir)
    convert_json_folder(folder_path)

    print("\n" + "="*60)
    print("Process complete!")
    print("="*60)

if __name__ == "__main__":
    try:
        convert_json_to_excel()
    except KeyboardInterrupt:
        print("\nProcess cancelled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")



