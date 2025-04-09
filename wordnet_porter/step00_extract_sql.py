import os

def run():
    input_file = "data/wordnet_raw.sql"
    schema_file = "sql/wordnet_schema_only.sql"
    data_file = "sql/wordnet_data_only.sql"

    os.makedirs("sql", exist_ok=True)

    schema_lines = []
    data_lines = []

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            if line.startswith("INSERT INTO"):
                data_lines.append(line)
            else:
                schema_lines.append(line)

    with open(schema_file, "w", encoding="utf-8") as f:
        f.writelines(schema_lines)
    print(f"✅ Extracted schema to: {schema_file} ({len(schema_lines)} lines)")

    with open(data_file, "w", encoding="utf-8") as f:
        f.writelines(data_lines)
    print(f"✅ Extracted data to:   {data_file} ({len(data_lines)} lines)")
