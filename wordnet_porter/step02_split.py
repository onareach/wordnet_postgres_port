# wordnet_porter/step02_split.py

import os
import re
from collections import defaultdict

def run():
    input_file = "sql/wordnet_data_scrubbed.sql"
    output_folder = "output/split_data_files"
    os.makedirs(output_folder, exist_ok=True)

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Missing input file: {input_file}")

    inserts_by_table = defaultdict(list)
    insert_pattern = re.compile(r'^INSERT INTO (\w+)', re.IGNORECASE)

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            match = insert_pattern.match(line)
            if match:
                table = match.group(1)
                inserts_by_table[table].append(line)

    for table, lines in inserts_by_table.items():
        output_path = os.path.join(output_folder, f"{table}.sql")
        with open(output_path, "w", encoding="utf-8") as out:
            out.writelines(lines)
        print(f"✅ Wrote {len(lines):>5} lines to {output_path}")

    print(f"✅ Step 2 complete: INSERTs split into {len(inserts_by_table)} files in {output_folder}")
