# 04_fix_booleans_and_hex_metadata.py

import os
import binascii

input_folder = "../output/split_data_fixed"
output_folder = "../output/split_data_fixed_final"
os.makedirs(output_folder, exist_ok=True)

boolean_columns = {
    "lexicons": [11],
    "synsets": [5],
    "senses": [7],
    "pronunciations": [4],
}

def decode_sqlite_blob(value):
    if value.startswith("X'") and value.endswith("'"):
        hex_str = value[2:-1]
        try:
            return "'" + binascii.unhexlify(hex_str).decode('utf-8') + "'"
        except Exception as e:
            print(f"⚠️ Failed to decode blob: {value} → {e}")
            return "NULL"
    return value

processed_files = 0
fixed_lines = 0
fixed_blobs = 0

for filename in os.listdir(input_folder):
    if not filename.endswith(".sql"):
        continue

    table = filename.replace(".sql", "")
    infile_path = os.path.join(input_folder, filename)
    outfile_path = os.path.join(output_folder, filename)

    with open(infile_path, "r", encoding="utf-8") as infile, open(outfile_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            if line.startswith("INSERT INTO") and "VALUES" in line:
                try:
                    prefix, values = line.split("VALUES", 1)
                    values = values.strip().rstrip(";\n")

                    if values.startswith("(") and values.endswith(")"):
                        values = values[1:-1]
                        fields = [v.strip() for v in values.split(",")]

                        # Boolean replacements
                        if table in boolean_columns:
                            for i in boolean_columns[table]:
                                if fields[i] == "1":
                                    fields[i] = "TRUE"
                                    fixed_lines += 1
                                elif fields[i] == "0":
                                    fields[i] = "FALSE"
                                    fixed_lines += 1

                        # Metadata fix: try last column
                        for i in reversed(range(len(fields))):
                            if fields[i].startswith("X'"):
                                decoded = decode_sqlite_blob(fields[i])
                                if decoded != fields[i]:
                                    fields[i] = decoded
                                    fixed_blobs += 1
                                break

                        new_line = f"{prefix}VALUES({', '.join(fields)});\n"
                        outfile.write(new_line)
                        continue
                except Exception as e:
                    print(f"⚠️ Error parsing line: {e}")
            outfile.write(line)
        processed_files += 1

print(f"✔ Processed {processed_files} files.")
print(f"✔ Fixed {fixed_lines} boolean values.")
print(f"✔ Decoded {fixed_blobs} SQLite blob → JSON values.")
print(f"✅ Clean files saved in: {output_folder}")
