# 05_escape_json_quotes.py

import os
import re

input_folder = "../output/split_data_fixed_final"
output_folder = "../output/split_data_final_escaped"
os.makedirs(output_folder, exist_ok=True)

# Matches any JSON-like string inside single quotes
# e.g. '{"source": "Kate O'Brien"}'
json_string_pattern = re.compile(r"'(\{.*\})'")

escaped_fields = 0
processed_files = 0

for filename in os.listdir(input_folder):
    if not filename.endswith(".sql"):
        continue

    infile_path = os.path.join(input_folder, filename)
    outfile_path = os.path.join(output_folder, filename)

    with open(infile_path, "r", encoding="utf-8") as infile, open(outfile_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            def escape_json_quotes(match):
                global escaped_fields
                json_str = match.group(1)
                # Escape single quotes inside the JSON string
                escaped_json = json_str.replace("'", "''")
                escaped_fields += 1
                return f"'{escaped_json}'"

            # Replace all JSON-like strings with escaped versions
            fixed_line = json_string_pattern.sub(escape_json_quotes, line)
            outfile.write(fixed_line)

        processed_files += 1

print(f"✔ Processed {processed_files} files.")
print(f"✔ Escaped {escaped_fields} JSON string(s) containing single quotes.")
print(f"✅ Updated files saved to: {output_folder}")
