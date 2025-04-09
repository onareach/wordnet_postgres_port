import os
import re

def run():
    input_file = "sql/wordnet_schema_only.sql"
    tables_output = "sql/wordnet_tables.sql"
    indexes_output = "sql/wordnet_indexes.sql"

    if not os.path.exists(input_file):
        print(f"❌ Cannot find input schema: {input_file}")
        return

    os.makedirs("sql", exist_ok=True)

    table_blocks = []
    index_lines = []

    with open(input_file, "r", encoding="utf-8") as f:
        current_block = []
        in_table = False

        for line in f:
            if line.startswith("CREATE TABLE"):
                in_table = True
                current_block = [line]
            elif in_table:
                current_block.append(line)
                if line.strip().endswith(");"):
                    table_blocks.append("".join(current_block))
                    in_table = False
            elif line.startswith("CREATE INDEX"):
                index_lines.append(line)

    # Save CREATE TABLE block (manual order preferred, but here we keep as-is)
    with open(tables_output, "w", encoding="utf-8") as f:
        for block in table_blocks:
            f.write(block + "\n")
    print(f"✅ Extracted {len(table_blocks)} CREATE TABLE blocks → {tables_output}")

    # Save CREATE INDEX statements
    with open(indexes_output, "w", encoding="utf-8") as f:
        for line in index_lines:
            f.write(line)
    print(f"✅ Extracted {len(index_lines)} CREATE INDEX statements → {indexes_output}")
