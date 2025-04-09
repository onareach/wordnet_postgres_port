# wordnet_porter/bootstrap.py

import os

def setup():
    folders = [
        "data",
        "output/split_data_files",
        "output/split_data_fixed",
        "output/split_data_fixed_final",
        "output/split_data_final_escaped",
        "sql",
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"📁 Ensured folder exists: {folder}")

def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"{title}")
    print("=" * 60)
