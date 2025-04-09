# wordnet_porter/step04_metadata.py

import os
import binascii

def decode_sqlite_blob(value):
    """Decode a SQLite X'...' blob into a UTF-8 string for PostgreSQL JSONB fields."""
    if value.startswith("X'") and value.endswith("'"):
        hex_str = value[2:-1]
        try:
            decoded = binascii.unhexlify(hex_str).decode("utf-8")
            return f"'{decoded}'"
        except Exception as e:
            print(f"⚠️  Failed to decode blob: {value} → {e}")
            return "NULL"
    return value

def run():
    input_folder = "output/split_data_fixed"
    output_folder = "output/split_data_fixed_final"
    os.makedirs(output_folder, exist_ok=True)

    processed_files = 0
    fixed_blobs = 0

    for filename in os.listdir(input_folder):
        if not filename.endswith(".sql"):
            continue

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

                            # Try to decode the last field (likely metadata)
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
                        print(f"⚠️  Error decoding hex in {filename}: {e}")

                # Default write
                outfile.write(line)

        processed_files += 1

    print(f"✅ Step 4 complete:")
    print(f"   • Files processed : {processed_files}")
    print(f"   • Hex blobs fixed : {fixed_blobs}")
    print(f"   • Output saved to: {output_folder}")
