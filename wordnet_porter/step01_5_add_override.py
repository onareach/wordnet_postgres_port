import os
import re

def run():
    print("\n" + "=" * 60)
    print("Step 01.5: Add column names + OVERRIDING SYSTEM VALUE")
    print("=" * 60)

    input_file = "sql/wordnet_data_only.sql"
    output_file = "sql/wordnet_data_scrubbed.sql"

    if not os.path.exists(input_file):
        print(f"❌ Missing input file: {input_file}")
        return

    # Define column lists for tables where rowid needs to be explicitly overridden
    columns_by_table = {
        "ilis": "(rowid, id, status_rowid, definition, metadata)",
        "proposed_ilis": "(rowid, synset_rowid, definition, metadata)",
        "lexicons": "(rowid, id, label, language, email, license, version, url, citation, logo, metadata, modified)",
        "entries": "(rowid, id, lexicon_rowid, pos, metadata)",
        "forms": "(rowid, id, lexicon_rowid, entry_rowid, form, normalized_form, script, rank)",
        "synsets": "(rowid, id, lexicon_rowid, ili_rowid, pos, lexicalized, lexfile_rowid, metadata)",
        "definitions": "(rowid, lexicon_rowid, synset_rowid, definition, language, sense_rowid, metadata)",
        "senses": "(rowid, id, lexicon_rowid, entry_rowid, entry_rank, synset_rowid, synset_rank, lexicalized, metadata)",
        "synset_relations": "(rowid, lexicon_rowid, source_rowid, target_rowid, type_rowid, metadata)",
        "sense_relations": "(rowid, lexicon_rowid, source_rowid, target_rowid, type_rowid, metadata)",
        "sense_synset_relations": "(rowid, lexicon_rowid, source_rowid, target_rowid, type_rowid, metadata)",
        "synset_examples": "(rowid, lexicon_rowid, synset_rowid, example, language, metadata)",
        "sense_examples": "(rowid, lexicon_rowid, sense_rowid, example, language, metadata)",
        "counts": "(rowid, lexicon_rowid, sense_rowid, count, metadata)",
        "syntactic_behaviours": "(rowid, id, lexicon_rowid, frame)",
        "relation_types": "(rowid, type)",
        "ili_statuses": "(rowid, status)",
        "lexfiles": "(rowid, name)"
    }

    updates = 0

    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            match = re.match(r'^INSERT INTO (\w+)\s+VALUES', line)
            if match:
                table = match.group(1)
                if table in columns_by_table:
                    line = line.replace(
                        f"INSERT INTO {table} VALUES",
                        f"INSERT INTO {table} {columns_by_table[table]} OVERRIDING SYSTEM VALUE VALUES"
                    )
                    updates += 1
            outfile.write(line)

    print(f"✅ Added column list + OVERRIDING SYSTEM VALUE to {updates} insert blocks")
    print(f"✅ Output written to: {output_file}")
