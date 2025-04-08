# 03_fix_end_booleans.py

import os
import re

input_folder = "../output/split_data_files"
output_folder = "../output/split_data_fixed"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Regex to match ", 0);" or ",1);" at end of VALUES clauses
false_pattern = re.compile(r',\s*0\s*\);')
true_pattern = re.compile(r',\s*1\s*\);')

processed_files = 0
converted_lines = 0

for filename in os.listdir(input_folder):
    if not filename.endswith(".sql"):
        continue

    infile_path = os.path.join(input_folder, filename)
    outfile_path = os.path.join(output_folder, filename)

    with open(infile_path, "r", encoding="utf-8") as infile, open(outfile_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            original_line = line
            # Convert boolean-looking integers to actual booleans
            line = false_pattern.sub(', FALSE);', line)
            line = true_pattern.sub(', TRUE);', line)

            if line != original_line:
                converted_lines += 1

            outfile.write(line)
        processed_files += 1

print(f"✔ Processed {processed_files} files.")
print(f"✔ Converted {converted_lines} boolean values.")
print(f"✅ Fixed files saved in: {output_folder}")
