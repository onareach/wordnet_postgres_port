# wordnet_porter/main.py

import sys
from wordnet_porter import (
    bootstrap,
    step00_extract_sql,
    step01_generate_schema_files,
    step01_5_add_override,
    step02_split,
    step03_booleans,
    step04_metadata,
    step05_json_escape,
)

def run_all_steps():
    print("🔧 Bootstrapping project...")
    bootstrap.setup()

    bootstrap.print_header("Step 00: Extract schema and data from raw SQL")
    step00_extract_sql.run()

    bootstrap.print_header("Step 01: Generate schema + index files")
    step01_generate_schema_files.run()

    bootstrap.print_header("Step 01.5: Add override columns to inserts")
    step01_5_add_override.run()

    bootstrap.print_header("Step 02: Split INSERTs into per-table files")
    step02_split.run()

    bootstrap.print_header("Step 03: Fix booleans (trailing and inline)")
    step03_booleans.run()

    bootstrap.print_header("Step 04: Convert SQLite metadata blobs to JSON")
    step04_metadata.run()

    bootstrap.print_header("Step 05: Escape single quotes in JSON")
    step05_json_escape.run()

    bootstrap.print_header("✅ All steps complete!")


if __name__ == "__main__":
    try:
        run_all_steps()
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        sys.exit(1)

