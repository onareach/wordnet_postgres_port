# wordnet_porter/step05_json_escape.py

import os
import re

def run():
    input_folder = "output/split_data_fixed_final"
    output_folder = "output/split_data_final_escaped"
    os.makedirs(output_folder, exist_ok=True)

    # Matches lines like:
    # INSERT INTO table VALUES(..., '{...}', ...);
    json_pattern = re.compile(
        r"(?P<pre>VALUES\(.+?,\s*)(?P<json>'\{.*\}')(?P<post>\s*\);)",
        re.DOTALL
    )

    fixed_files = 0
    escaped_fields = 0

    for filename in os.listdir(input_folder):
        if not filename.endswith(".sql"):
            continue

        infile_path = os.path.join(input_folder, filename)
        outfile_path = os.path.join(output_folder, filename)

        with open(infile_path, "r", encoding="utf-8") as infile, open(outfile_path, "w", encoding="utf-8") as outfile:
            for line in infile:
                if "VALUES" in line and "{" in line and "'" in line:
                    match = json_pattern.search(line)
                    if match:
                        pre = match.group("pre")
                        json_str = match.group("json")
                        post = match.group("post")

                        inner = json_str[1:-1]  # Remove outer single quotes
                        escaped = inner.replace("'", "''")  # Escape single quotes

                        new_line = f"{pre}'{escaped}'{post}\n"
                        outfile.write(new_line)
                        escaped_fields += 1
                        continue  # Skip writing original line
                outfile.write(line)

        fixed_files += 1

    print(f"✅ Step 5 complete:")
    print(f"   • Files processed : {fixed_files}")
    print(f"   • Fields escaped  : {escaped_fields}")
    print(f"   • Output saved to: {output_folder}")
