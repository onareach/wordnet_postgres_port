# wordnet_porter/step01_override.py

import re
import os

def run():
    input_file = "sql/wordnet_data_only.sql"
    output_file = "sql/wordnet_data_scrubbed.sql"

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

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Missing input file: {input_file}")

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
            outfile.write(line)

    print(f"✅ Step 1 complete: {output_file} written.")
