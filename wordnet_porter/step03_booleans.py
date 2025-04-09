# wordnet_porter/step03_booleans.py

import os
import re

def run():
    input_folder = "output/split_data_files"
    output_folder = "output/split_data_fixed"
    os.makedirs(output_folder, exist_ok=True)

    # Regex for trailing boolean values
    trailing_false_pattern = re.compile(r',\s*0\s*\);')
    trailing_true_pattern = re.compile(r',\s*1\s*\);')

    # Boolean column indexes for specific tables
    boolean_columns = {
        "lexicons": [11],       # modified
        "synsets": [5],         # lexicalized
        "senses": [7],          # lexicalized
        "pronunciations": [4],  # phonemic
    }

    processed_files = 0
    trailing_fixes = 0
    mid_column_fixes = 0

    for filename in os.listdir(input_folder):
        if not filename.endswith(".sql"):
            continue

        table = filename.replace(".sql", "")
        infile_path = os.path.join(input_folder, filename)
        outfile_path = os.path.join(output_folder, filename)

        with open(infile_path, "r", encoding="utf-8") as infile, open(outfile_path, "w", encoding="utf-8") as outfile:
            for line in infile:
                original_line = line

                # Fix trailing boolean values
                line = trailing_false_pattern.sub(', FALSE);', line)
                line = trailing_true_pattern.sub(', TRUE);', line)

                if line != original_line:
                    trailing_fixes += 1
                    original_line = line  # update reference

                # Fix mid-column boolean values
                if table in boolean_columns and line.startswith("INSERT INTO") and "VALUES" in line:
                    try:
                        prefix, values = line.split("VALUES", 1)
                        values = values.strip().rstrip(";\n")
                        if values.startswith("(") and values.endswith(")"):
                            values = values[1:-1]
                            fields = [v.strip() for v in values.split(",")]

                            changed = False
                            for i in boolean_columns[table]:
                                if fields[i] == "1":
                                    fields[i] = "TRUE"
                                    changed = True
                                elif fields[i] == "0":
                                    fields[i] = "FALSE"
                                    changed = True

                            if changed:
                                new_line = f"{prefix}VALUES({', '.join(fields)});\n"
                                outfile.write(new_line)
                                mid_column_fixes += 1
                                continue  # skip default write

                    except Exception as e:
                        print(f"⚠️  Failed parsing mid-column booleans in {filename}: {e}")

                # Default write
                outfile.write(line)

        processed_files += 1

    print(f"✅ Step 3 complete:")
    print(f"   • Files processed        : {processed_files}")
    print(f"   • Trailing booleans fixed: {trailing_fixes}")
    print(f"   • Mid-column booleans fixed: {mid_column_fixes}")
    print(f"   • Output saved to: {output_folder}")
