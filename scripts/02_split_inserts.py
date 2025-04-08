# 02_split_inserts.py

import re
from collections import defaultdict

input_file = "../sql/wordnet_data_scrubbed.sql"
output_folder = "../output/split_data_files/"

import os
os.makedirs(output_folder, exist_ok=True)

# Prepare buffers to store inserts by table
inserts_by_table = defaultdict(list)

# Match INSERT INTO tablename
pattern = re.compile(r'^INSERT INTO (\w+)', re.IGNORECASE)

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        match = pattern.match(line)
        if match:
            table = match.group(1)
            inserts_by_table[table].append(line)

# Write one file per table
for table, lines in inserts_by_table.items():
    output_path = os.path.join(output_folder, f"{table}.sql")
    with open(output_path, "w", encoding="utf-8") as out:
        out.writelines(lines)
        print(f"✔ Wrote {len(lines):>5} lines to {output_path}")
