# Porting WordNet from SQLite to PostgreSQL

**Step 1:  Open the SQLite WordNet database:**

These instruction assume that WordNet, SQLite, PostgreSQL, and Python are installed on the machine.

```
sqlite3 ~/.wn_data/wn.db 
SQLite version 3.49.1 2025-02-18 13:38:58
Enter ".help" for usage hints.
```

**Step 2:  Inspect the tables:**

```
sqlite> .tables
adjpositions                proposed_ilis             
counts                      relation_types            
definitions                 sense_examples            
entries                     sense_relations           
forms                       sense_synset_relations    
ili_statuses                senses                    
ilis                        synset_examples           
lexfiles                    synset_relations          
lexicon_dependencies        synsets                   
lexicon_extensions          syntactic_behaviour_senses
lexicons                    syntactic_behaviours      
pronunciations              tags                      
sqlite> .schema
CREATE TABLE ilis (
    rowid INTEGER PRIMARY KEY,
    id TEXT NOT NULL,
    status_rowid INTEGER NOT NULL REFERENCES ili_statuses (rowid),
    definition TEXT,
    metadata META,
    UNIQUE (id)
);
CREATE INDEX ili_id_index ON ilis (id);
CREATE TABLE proposed_ilis (
    rowid INTEGER PRIMARY KEY,
    synset_rowid INTEGER REFERENCES synsets (rowid) ON DELETE CASCADE,
    definition TEXT,
    metadata META,
    UNIQUE (synset_rowid)
);
CREATE INDEX proposed_ili_synset_rowid_index ON proposed_ilis (synset_rowid);
CREATE TABLE lexicons (
    rowid INTEGER PRIMARY KEY,  -- unique database-internal id
    id TEXT NOT NULL,           -- user-facing id
    label TEXT NOT NULL,
    language TEXT NOT NULL,     -- bcp-47 language tag
    email TEXT NOT NULL,
    license TEXT NOT NULL,
    version TEXT NOT NULL,
    url TEXT,
    citation TEXT,
    logo TEXT,
    metadata META,
    modified BOOLEAN CHECK( modified IN (0, 1) ) DEFAULT 0 NOT NULL,
    UNIQUE (id, version)
);
CREATE TABLE lexicon_dependencies (
    dependent_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    provider_id TEXT NOT NULL,
    provider_version TEXT NOT NULL,
    provider_url TEXT,
    provider_rowid INTEGER REFERENCES lexicons (rowid) ON DELETE SET NULL
);
CREATE INDEX lexicon_dependent_index ON lexicon_dependencies(dependent_rowid);
CREATE TABLE lexicon_extensions (
    extension_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    base_id TEXT NOT NULL,
    base_version TEXT NOT NULL,
    base_url TEXT,
    base_rowid INTEGER REFERENCES lexicons (rowid),
    UNIQUE (extension_rowid, base_rowid)
);
CREATE INDEX lexicon_extension_index ON lexicon_extensions(extension_rowid);
CREATE TABLE entries (
    rowid INTEGER PRIMARY KEY,
    id TEXT NOT NULL,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    pos TEXT NOT NULL,
    metadata META,
    UNIQUE (id, lexicon_rowid)
);
CREATE INDEX entry_id_index ON entries (id);
CREATE TABLE forms (
    rowid INTEGER PRIMARY KEY,
    id TEXT,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons(rowid) ON DELETE CASCADE,
    entry_rowid INTEGER NOT NULL REFERENCES entries(rowid) ON DELETE CASCADE,
    form TEXT NOT NULL,
    normalized_form TEXT,
    script TEXT,
    rank INTEGER DEFAULT 1,  -- rank 0 is the preferred lemma
    UNIQUE (entry_rowid, form, script)
);
CREATE INDEX form_entry_index ON forms (entry_rowid);
CREATE INDEX form_index ON forms (form);
CREATE INDEX form_norm_index ON forms (normalized_form);
CREATE TABLE pronunciations (
    form_rowid INTEGER NOT NULL REFERENCES forms (rowid) ON DELETE CASCADE,
    value TEXT,
    variety TEXT,
    notation TEXT,
    phonemic BOOLEAN CHECK( phonemic IN (0, 1) ) DEFAULT 1 NOT NULL,
    audio TEXT
);
CREATE INDEX pronunciation_form_index ON pronunciations (form_rowid);
CREATE TABLE tags (
    form_rowid INTEGER NOT NULL REFERENCES forms (rowid) ON DELETE CASCADE,
    tag TEXT,
    category TEXT
);
CREATE INDEX tag_form_index ON tags (form_rowid);
CREATE TABLE synsets (
    rowid INTEGER PRIMARY KEY,
    id TEXT NOT NULL,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    ili_rowid INTEGER REFERENCES ilis (rowid),
    pos TEXT,
    lexicalized BOOLEAN CHECK( lexicalized IN (0, 1) ) DEFAULT 1 NOT NULL,
    lexfile_rowid INTEGER REFERENCES lexfiles (rowid),
    metadata META
);
CREATE INDEX synset_id_index ON synsets (id);
CREATE INDEX synset_ili_rowid_index ON synsets (ili_rowid);
CREATE TABLE synset_relations (
    rowid INTEGER PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    source_rowid INTEGER NOT NULL REFERENCES synsets(rowid) ON DELETE CASCADE,
    target_rowid INTEGER NOT NULL REFERENCES synsets(rowid) ON DELETE CASCADE,
    type_rowid INTEGER NOT NULL REFERENCES relation_types(rowid),
    metadata META
);
CREATE INDEX synset_relation_source_index ON synset_relations (source_rowid);
CREATE INDEX synset_relation_target_index ON synset_relations (target_rowid);
CREATE TABLE definitions (
    rowid INTEGER PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons(rowid) ON DELETE CASCADE,
    synset_rowid INTEGER NOT NULL REFERENCES synsets(rowid) ON DELETE CASCADE,
    definition TEXT,
    language TEXT,  -- bcp-47 language tag
    sense_rowid INTEGER REFERENCES senses(rowid) ON DELETE SET NULL,
    metadata META
);
CREATE INDEX definition_rowid_index ON definitions (synset_rowid);
CREATE INDEX definition_sense_index ON definitions (sense_rowid);
CREATE TABLE synset_examples (
    rowid INTEGER PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons(rowid) ON DELETE CASCADE,
    synset_rowid INTEGER NOT NULL REFERENCES synsets(rowid) ON DELETE CASCADE,
    example TEXT,
    language TEXT,  -- bcp-47 language tag
    metadata META
);
CREATE INDEX synset_example_rowid_index ON synset_examples(synset_rowid);
CREATE TABLE senses (
    rowid INTEGER PRIMARY KEY,
    id TEXT NOT NULL,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons(rowid) ON DELETE CASCADE,
    entry_rowid INTEGER NOT NULL REFERENCES entries(rowid) ON DELETE CASCADE,
    entry_rank INTEGER DEFAULT 1,
    synset_rowid INTEGER NOT NULL REFERENCES synsets(rowid) ON DELETE CASCADE,
    synset_rank INTEGER DEFAULT 1,
    lexicalized BOOLEAN CHECK( lexicalized IN (0, 1) ) DEFAULT 1 NOT NULL,
    metadata META
);
CREATE INDEX sense_id_index ON senses(id);
CREATE INDEX sense_entry_rowid_index ON senses (entry_rowid);
CREATE INDEX sense_synset_rowid_index ON senses (synset_rowid);
CREATE TABLE sense_relations (
    rowid INTEGER PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    source_rowid INTEGER NOT NULL REFERENCES senses(rowid) ON DELETE CASCADE,
    target_rowid INTEGER NOT NULL REFERENCES senses(rowid) ON DELETE CASCADE,
    type_rowid INTEGER NOT NULL REFERENCES relation_types(rowid),
    metadata META
);
CREATE INDEX sense_relation_source_index ON sense_relations (source_rowid);
CREATE INDEX sense_relation_target_index ON sense_relations (target_rowid);
CREATE TABLE sense_synset_relations (
    rowid INTEGER PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    source_rowid INTEGER NOT NULL REFERENCES senses(rowid) ON DELETE CASCADE,
    target_rowid INTEGER NOT NULL REFERENCES synsets(rowid) ON DELETE CASCADE,
    type_rowid INTEGER NOT NULL REFERENCES relation_types(rowid),
    metadata META
);
CREATE INDEX sense_synset_relation_source_index ON sense_synset_relations (source_rowid);
CREATE INDEX sense_synset_relation_target_index ON sense_synset_relations (target_rowid);
CREATE TABLE adjpositions (
    sense_rowid INTEGER NOT NULL REFERENCES senses(rowid) ON DELETE CASCADE,
    adjposition TEXT NOT NULL
);
CREATE INDEX adjposition_sense_index ON adjpositions (sense_rowid);
CREATE TABLE sense_examples (
    rowid INTEGER PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons(rowid) ON DELETE CASCADE,
    sense_rowid INTEGER NOT NULL REFERENCES senses(rowid) ON DELETE CASCADE,
    example TEXT,
    language TEXT,  -- bcp-47 language tag
    metadata META
);
CREATE INDEX sense_example_index ON sense_examples (sense_rowid);
CREATE TABLE counts (
    rowid INTEGER PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons(rowid) ON DELETE CASCADE,
    sense_rowid INTEGER NOT NULL REFERENCES senses(rowid) ON DELETE CASCADE,
    count INTEGER NOT NULL,
    metadata META
);
CREATE INDEX count_index ON counts(sense_rowid);
CREATE TABLE syntactic_behaviours (
    rowid INTEGER PRIMARY KEY,
    id TEXT,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    frame TEXT NOT NULL,
    UNIQUE (lexicon_rowid, id),
    UNIQUE (lexicon_rowid, frame)
);
CREATE INDEX syntactic_behaviour_id_index ON syntactic_behaviours (id);
CREATE TABLE syntactic_behaviour_senses (
    syntactic_behaviour_rowid INTEGER NOT NULL REFERENCES syntactic_behaviours (rowid) ON DELETE CASCADE,
    sense_rowid INTEGER NOT NULL REFERENCES senses (rowid) ON DELETE CASCADE
);
CREATE INDEX syntactic_behaviour_sense_sb_index
    ON syntactic_behaviour_senses (syntactic_behaviour_rowid);
CREATE INDEX syntactic_behaviour_sense_sense_index
    ON syntactic_behaviour_senses (sense_rowid);
CREATE TABLE relation_types (
    rowid INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    UNIQUE (type)
);
CREATE INDEX relation_type_index ON relation_types (type);
CREATE TABLE ili_statuses (
    rowid INTEGER PRIMARY KEY,
    status TEXT NOT NULL,
    UNIQUE (status)
);
CREATE INDEX ili_status_index ON ili_statuses (status);
CREATE TABLE lexfiles (
    rowid INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    UNIQUE (name)
);
CREATE INDEX lexfile_index ON lexfiles (name);
```



**Step 3:  Export SQLite Data and Place in Project Directory:**

1. Run the following command to generate a full SQL dump including schema and inserts:

```
sqlite3 ~/.wn_data/wn.db .dump > wordnet_raw.sql
```

2. Create a directory tree as follows:

```
wordnet_postgres_port
├── README.md
├── data
├── output
├── scripts
└── sql
```

3. Move the `wordnet_raw.sql` file into the `data` directory.



**Step 4:  Clean the SQL for PostgreSQL:**

Open `wordnet_raw.sql` in an editor. (I used VS Code).

1. Remove these SQLite-specific lines:

   - `PRAGMA foreign_keys=OFF;`
   - `BEGIN TRANSACTION;`
   - `COMMIT;`

2. Replace `INTEGER PRIMARY KEY` → `INTEGER GENERATED ALWAYS AS PRIMARY KEY`

3. Using Find/Replace in RegEx (.*) mode (assuming the use of VS Code), replace

   `BOOLEAN CHECK\( \w+ IN \(0, 1\) \) DEFAULT 0 NOT NULL` 

   with

   `BOOLEAN DEFAULT FALSE NOT NULL` 

   

   Replace

   `BOOLEAN CHECK\( \w+ IN \(0, 1\) \) DEFAULT 1 NOT NULL` 

   with

   `BOOLEAN DEFAULT TRUE NOT NULL` 

   

4. Replace a SQLite META datatype with the JSONB datatype, which is compatible with PostgreSQL. Replace:

   `metadata META` 

   with

   `metadata JSONB` 

   

**Step 5:  Create a Schema-Only Test File:**

Given that the `wordnet_raw.sql` is more than 1.5 million lines long, it is wise separate the DDL (data definition language) elements from the data insertion. 

While in the `data` directory, run the following command to create a SQL script with only schema DDL:

```
grep -v '^INSERT INTO' wordnet_raw.sql > wordnet_schema_only.sql
```

Move the new `wordnet_schema_only.sql` file to the `sql` folder.  

Note: After creating the schema-only file, which was about 200 lines long, I uploaded the file to ChatGPT to verify the syntax. ChatGPT gave some optional modifications, but confirmed the script was correctly formatted with good syntax.



**Step 6:  Create a Database:**

These instruction assume the use of the PostgreSQL superuser account.

1. Login to PostgreSQL with the following command:

```
psql -U postgres
```

You will be prompted for a password each time you enter a  `psql -U` command. Enter your password.

```
Password for user postgres: 
```

After entering the password, the following appears:

```
WARNING: psql major version 14, server major version 16.
         Some psql features might not work.
Type "help" for help.

postgres=#
```

(Later, to exit postgres, use the `\q` command.)



2. Run the following command:

```
CREATE DATABASE wordnet_test;
```



3. Switch to the new wordnet_test database to confirm the test database was created:

```
postgres=# \c wordnet_test
psql (14.17 (Homebrew), server 16.2)
WARNING: psql major version 14, server major version 16.
         Some psql features might not work.
You are now connected to database "wordnet_test" as user "postgres".
wordnet_test=#
```



4. Exit psql:

```
\q
```



**Interlude:  REVERSING Any Missteps:**

1. If the scripts in the following steps do not execute properly and encounter errors, you can start over by deleting all of the tables and re-running the repaired scripts. To keep the database, but delete all of the tables, login to PostgreSQL, go to the `wordnet_test=#` prompt, and run the following block of code:

```
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END
$$;
```



2. Verify that all of the tables were dropped with the command:

```
\dt
```

If all of the tables have been dropped, you will receive the following output:

```
Did not find any relations.
```

Alternatively, if you just want delete the records in a table, use the following command:

```
TRUNCATE TABLE [table_name] RESTART IDENTITY CASCADE;
```

Then run a `SELECT *` query to verify the records were deleted.



**Step 7:  Separate and Re-order the CREATE TABLE and CREATE INDEX Scripts:**

If you run the schema-creation script in its current state, portions of the script will fail. Some of the tables and indices depend on the existence of other tables, so the tables need to be created in a certain order.  

1. Create the following CREATE TABLE Script (`wordnet_tables.sql`) in the `sql` folder.

```
-- Basic lookup tables first
CREATE TABLE ili_statuses (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status TEXT NOT NULL,
    UNIQUE (status)
);

CREATE TABLE relation_types (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type TEXT NOT NULL,
    UNIQUE (type)
);

CREATE TABLE lexfiles (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    UNIQUE (name)
);

CREATE TABLE lexicons (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id TEXT NOT NULL,
    label TEXT NOT NULL,
    language TEXT NOT NULL,
    email TEXT NOT NULL,
    license TEXT NOT NULL,
    version TEXT NOT NULL,
    url TEXT,
    citation TEXT,
    logo TEXT,
    metadata JSONB,
    modified BOOLEAN DEFAULT FALSE NOT NULL,
    UNIQUE (id, version)
);

-- These depend on previous tables
CREATE TABLE ilis (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id TEXT NOT NULL,
    status_rowid INTEGER NOT NULL REFERENCES ili_statuses (rowid),
    definition TEXT,
    metadata JSONB,
    UNIQUE (id)
);

CREATE TABLE synsets (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id TEXT NOT NULL,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    ili_rowid INTEGER REFERENCES ilis (rowid),
    pos TEXT,
    lexicalized BOOLEAN DEFAULT TRUE NOT NULL,
    lexfile_rowid INTEGER REFERENCES lexfiles (rowid),
    metadata JSONB
);

CREATE TABLE proposed_ilis (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    synset_rowid INTEGER REFERENCES synsets (rowid) ON DELETE CASCADE,
    definition TEXT,
    metadata JSONB,
    UNIQUE (synset_rowid)
);

CREATE TABLE entries (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id TEXT NOT NULL,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    pos TEXT NOT NULL,
    metadata JSONB,
    UNIQUE (id, lexicon_rowid)
);

CREATE TABLE forms (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id TEXT,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    entry_rowid INTEGER NOT NULL REFERENCES entries (rowid) ON DELETE CASCADE,
    form TEXT NOT NULL,
    normalized_form TEXT,
    script TEXT,
    rank INTEGER DEFAULT 1,
    UNIQUE (entry_rowid, form, script)
);

CREATE TABLE pronunciations (
    form_rowid INTEGER NOT NULL REFERENCES forms (rowid) ON DELETE CASCADE,
    value TEXT,
    variety TEXT,
    notation TEXT,
    phonemic BOOLEAN DEFAULT TRUE NOT NULL,
    audio TEXT
);

CREATE TABLE tags (
    form_rowid INTEGER NOT NULL REFERENCES forms (rowid) ON DELETE CASCADE,
    tag TEXT,
    category TEXT
);

CREATE TABLE synset_relations (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    source_rowid INTEGER NOT NULL REFERENCES synsets (rowid) ON DELETE CASCADE,
    target_rowid INTEGER NOT NULL REFERENCES synsets (rowid) ON DELETE CASCADE,
    type_rowid INTEGER NOT NULL REFERENCES relation_types (rowid),
    metadata JSONB
);

CREATE TABLE senses (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id TEXT NOT NULL,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    entry_rowid INTEGER NOT NULL REFERENCES entries (rowid) ON DELETE CASCADE,
    entry_rank INTEGER DEFAULT 1,
    synset_rowid INTEGER NOT NULL REFERENCES synsets (rowid) ON DELETE CASCADE,
    synset_rank INTEGER DEFAULT 1,
    lexicalized BOOLEAN DEFAULT TRUE NOT NULL,
    metadata JSONB
);

CREATE TABLE definitions (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    synset_rowid INTEGER NOT NULL REFERENCES synsets (rowid) ON DELETE CASCADE,
    definition TEXT,
    language TEXT,
    sense_rowid INTEGER REFERENCES senses (rowid) ON DELETE SET NULL,
    metadata JSONB
);

CREATE TABLE synset_examples (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    synset_rowid INTEGER NOT NULL REFERENCES synsets (rowid) ON DELETE CASCADE,
    example TEXT,
    language TEXT,
    metadata JSONB
);

CREATE TABLE sense_relations (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    source_rowid INTEGER NOT NULL REFERENCES senses (rowid) ON DELETE CASCADE,
    target_rowid INTEGER NOT NULL REFERENCES senses (rowid) ON DELETE CASCADE,
    type_rowid INTEGER NOT NULL REFERENCES relation_types (rowid),
    metadata JSONB
);

CREATE TABLE sense_synset_relations (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    source_rowid INTEGER NOT NULL REFERENCES senses (rowid) ON DELETE CASCADE,
    target_rowid INTEGER NOT NULL REFERENCES synsets (rowid) ON DELETE CASCADE,
    type_rowid INTEGER NOT NULL REFERENCES relation_types (rowid),
    metadata JSONB
);

CREATE TABLE adjpositions (
    sense_rowid INTEGER NOT NULL REFERENCES senses (rowid) ON DELETE CASCADE,
    adjposition TEXT NOT NULL
);

CREATE TABLE sense_examples (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    sense_rowid INTEGER NOT NULL REFERENCES senses (rowid) ON DELETE CASCADE,
    example TEXT,
    language TEXT,
    metadata JSONB
);

CREATE TABLE counts (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    sense_rowid INTEGER NOT NULL REFERENCES senses (rowid) ON DELETE CASCADE,
    count INTEGER NOT NULL,
    metadata JSONB
);

CREATE TABLE syntactic_behaviours (
    rowid INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id TEXT,
    lexicon_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    frame TEXT NOT NULL,
    UNIQUE (lexicon_rowid, id),
    UNIQUE (lexicon_rowid, frame)
);

CREATE TABLE syntactic_behaviour_senses (
    syntactic_behaviour_rowid INTEGER NOT NULL REFERENCES syntactic_behaviours (rowid) ON DELETE CASCADE,
    sense_rowid INTEGER NOT NULL REFERENCES senses (rowid) ON DELETE CASCADE
);

CREATE TABLE lexicon_dependencies (
    dependent_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    provider_id TEXT NOT NULL,
    provider_version TEXT NOT NULL,
    provider_url TEXT,
    provider_rowid INTEGER REFERENCES lexicons (rowid) ON DELETE SET NULL
);

CREATE TABLE lexicon_extensions (
    extension_rowid INTEGER NOT NULL REFERENCES lexicons (rowid) ON DELETE CASCADE,
    base_id TEXT NOT NULL,
    base_version TEXT NOT NULL,
    base_url TEXT,
    base_rowid INTEGER REFERENCES lexicons (rowid),
    UNIQUE (extension_rowid, base_rowid)
);
```



2. Create a CREATE INDEX Script (`wordnet_indexes.sql`) in the `sql` folder.

```
CREATE INDEX ili_id_index ON ilis (id);
CREATE INDEX proposed_ili_synset_rowid_index ON proposed_ilis (synset_rowid);
CREATE INDEX lexicon_dependent_index ON lexicon_dependencies(dependent_rowid);
CREATE INDEX lexicon_extension_index ON lexicon_extensions(extension_rowid);
CREATE INDEX entry_id_index ON entries (id);
CREATE INDEX form_entry_index ON forms (entry_rowid);
CREATE INDEX form_index ON forms (form);
CREATE INDEX form_norm_index ON forms (normalized_form);
CREATE INDEX pronunciation_form_index ON pronunciations (form_rowid);
CREATE INDEX tag_form_index ON tags (form_rowid);
CREATE INDEX synset_id_index ON synsets (id);
CREATE INDEX synset_ili_rowid_index ON synsets (ili_rowid);
CREATE INDEX synset_relation_source_index ON synset_relations (source_rowid);
CREATE INDEX synset_relation_target_index ON synset_relations (target_rowid);
CREATE INDEX definition_rowid_index ON definitions (synset_rowid);
CREATE INDEX definition_sense_index ON definitions (sense_rowid);
CREATE INDEX synset_example_rowid_index ON synset_examples (synset_rowid);
CREATE INDEX sense_id_index ON senses (id);
CREATE INDEX sense_entry_rowid_index ON senses (entry_rowid);
CREATE INDEX sense_synset_rowid_index ON senses (synset_rowid);
CREATE INDEX sense_relation_source_index ON sense_relations (source_rowid);
CREATE INDEX sense_relation_target_index ON sense_relations (target_rowid);
CREATE INDEX sense_synset_relation_source_index ON sense_synset_relations (source_rowid);
CREATE INDEX sense_synset_relation_target_index ON sense_synset_relations (target_rowid);
CREATE INDEX adjposition_sense_index ON adjpositions (sense_rowid);
CREATE INDEX sense_example_index ON sense_examples (sense_rowid);
CREATE INDEX count_index ON counts (sense_rowid);
CREATE INDEX syntactic_behaviour_id_index ON syntactic_behaviours (id);
CREATE INDEX syntactic_behaviour_sense_sb_index ON syntactic_behaviour_senses (syntactic_behaviour_rowid);
CREATE INDEX syntactic_behaviour_sense_sense_index ON syntactic_behaviour_senses (sense_rowid);
CREATE INDEX relation_type_index ON relation_types (type);
CREATE INDEX ili_status_index ON ili_statuses (status);
CREATE INDEX lexfile_index ON lexfiles (name);
```



**Step 8:  Run the Scripts:**

1. Run the table creation script:

```
psql -U postgres -d wordnet_test -f wordnet_tables.sql
```

2. Run the index creation script:

```
psql -U postgres -d wordnet_test -f wordnet_indexes.sql
```



**Step 9:  Modify the INSERT Data Scripts:**

1. In a Terminal window in the `data` directory, execute the following command:

```
grep '^INSERT INTO' wordnet_raw.sql > wordnet_data_only.sql
```



In Steps 2 through 11 below, several Python scripts will be created and executed to modify the `.sql` scripts. Here is a summary of the Python scripts, the input and output directories of the `.sql` scripts, and the purpose of each step:

| Script                                | Input                            | Output                             | Purpose                                        |
| ------------------------------------- | -------------------------------- | ---------------------------------- | ---------------------------------------------- |
| `01_add_override_and_columns.py`      | `sql/wordnet_data_only.sql`      | `sql/wordnet_data_scrubbed.sql`    | Add `OVERRIDING SYSTEM VALUE` and column names |
| `02_split_inserts.py`                 | `sql/wordnet_data_scrubbed.sql`  | `output/split_data_files/`         | Split INSERTs by table                         |
| `03_fix_end_booleans.py`              | `output/split_data_files/`       | `output/split_data_fixed/`         | Fix trailing boolean values                    |
| `04_fix_booleans_and_hex_metadata.py` | `output/split_data_fixed/`       | `output/split_data_fixed_final/`   | Fix booleans in middle + decode hex blobs      |
| `05_escape_json_quotes.py`            | `output/split_data_fixed_final/` | `output/split_data_final_escaped/` | Escape quotes in JSON                          |



2. Create the following Python script in the `scripts` directory. Its purpose is to add `OVERRIDING SYSTEM VALUE` to INSERTs. This causes the new PostgreSQL tables to accept the `rowids` from the original SQLite tables when available, and create new `rowids` if they are missing.

```
# 01_add_override_and_columns.py

import re

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

input_file = "../sql/wordnet_data_only.sql"
output_file = "../sql/wordnet_data_scrubbed.sql"

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

print(f"✔ Successfully wrote updated INSERTs to: {output_file}")

```



3. While in the `scripts` directory, run the Python script with the following command:

```
python3 01_add_override_and_columns.py
```



4. Create the following Python script to split the data into multiple files so the data can be loaded in the correct order to honor foreign key relation constraints:

```
# 02_split_inserts.py

import re
from collections import defaultdict

input_file = "../sql/wordnet_data_scrubbed.sql"
output_folder = "../output/split_data_files/"

import os
os.makedirs(output_folder, exist_ok=True)

# Prepare buffers to store inserts by table
inserts_by_table = defaultdict(list)

# Match INSERT INTO tablename
pattern = re.compile(r'^INSERT INTO (\w+)', re.IGNORECASE)

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        match = pattern.match(line)
        if match:
            table = match.group(1)
            inserts_by_table[table].append(line)

# Write one file per table
for table, lines in inserts_by_table.items():
    output_path = os.path.join(output_folder, f"{table}.sql")
    with open(output_path, "w", encoding="utf-8") as out:
        out.writelines(lines)
        print(f"✔ Wrote {len(lines):>5} lines to {output_path}")

```



5. Run the new Python script:

```
python3 02_split_inserts.py
```



6. Create the following Python script to change 1 and 0 to True and False for boolean columns at the end of the column list in some tables:

```
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
```



7. Run the new Python script:

```
python3 03_fix_end_booleans.py
```



8. Create the following Python script to change 1 and 0 to True and False for boolean columns in the middle of column list of some table, and to replace SQLite blobs with JSON strings:

```
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

```



9. Run the new Python script:

```
python3 04_fix_booleans_and_hex_metadata.py
```



10. Create the replace single quotes inside of JSON strings with two single quotes, which is the PostgreSQL method of escaping single quotes::

```
# 05_escape_json_quotes.py

import os
import re

input_folder = "../output/split_data_fixed_final"
output_folder = "../output/split_data_final_escaped"
os.makedirs(output_folder, exist_ok=True)

# This pattern tries to find the last quoted JSON string (usually metadata)
json_pattern = re.compile(r"(?P<pre>VALUES\(.+?,.+?,.+?,.+?,.+?,.+?,)(?P<json>'\{.*\}')(?P<post>\);)", re.DOTALL)

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
                # Find the JSON-ish field at the end
                match = json_pattern.search(line)
                if match:
                    pre = match.group("pre")
                    json_str = match.group("json")
                    post = match.group("post")

                    # Escape single quotes inside the JSON (but not the outer quotes)
                    inner_json = json_str[1:-1]  # remove outer quotes
                    escaped_json = inner_json.replace("'", "''")
                    fixed_line = f"{pre}'{escaped_json}'{post}\n"
                    outfile.write(fixed_line)
                    escaped_fields += 1
                    continue  # skip default write
            outfile.write(line)
        fixed_files += 1

print(f"✔ Processed {fixed_files} files.")
print(f"✔ Escaped single quotes in {escaped_fields} JSON string fields.")
print(f"✅ Escaped files saved to: {output_folder}")
```



11. Run the new Python script:

```
python3 05_escape_json_quotes.py
```

At this point, the folder/file tree should appear as follows:

```
wordnet_postgres_port
├── README.md
├── data
│   └── wordnet_raw.sql
├── output
│   ├── split_data_files
│   ├── split_data_final_escaped
│   ├── split_data_fixed
│   └── split_data_fixed_final
├── scripts
│   ├── 01_add_override_and_columns.py
│   ├── 02_split_inserts.py
│   ├── 03_fix_end_booleans.py
│   ├── 04_fix_booleans_and_hex_metadata.py
│   └── 05_escape_json_quotes.py
└── sql
    ├── wordnet_data_only.sql
    ├── wordnet_data_scrubbed.sql
    ├── wordnet_indexes.sql
    ├── wordnet_schema_only.sql
    └── wordnet_tables.sql
```



12. Move to the `split_data_final_escaped` directory. Some of the following `.sql` scripts will not run because there is no data to insert. (They were extracted from empty SQLite tables. Run the data load scripts in following order:

```
psql -U postgres -d wordnet_test -f ili_statuses.sql
psql -U postgres -d wordnet_test -f relation_types.sql
psql -U postgres -d wordnet_test -f lexfiles.sql
psql -U postgres -d wordnet_test -f lexicons.sql
psql -U postgres -d wordnet_test -f ilis.sql
psql -U postgres -d wordnet_test -f synsets.sql
psql -U postgres -d wordnet_test -f proposed_ilis.sql
psql -U postgres -d wordnet_test -f entries.sql
psql -U postgres -d wordnet_test -f forms.sql
psql -U postgres -d wordnet_test -f pronunciations.sql
psql -U postgres -d wordnet_test -f tags.sql
psql -U postgres -d wordnet_test -f senses.sql
psql -U postgres -d wordnet_test -f definitions.sql
psql -U postgres -d wordnet_test -f synset_examples.sql
psql -U postgres -d wordnet_test -f synset_relations.sql
psql -U postgres -d wordnet_test -f sense_relations.sql
psql -U postgres -d wordnet_test -f sense_synset_relations.sql
psql -U postgres -d wordnet_test -f adjpositions.sql
psql -U postgres -d wordnet_test -f sense_examples.sql
psql -U postgres -d wordnet_test -f counts.sql
psql -U postgres -d wordnet_test -f syntactic_behaviours.sql
psql -U postgres -d wordnet_test -f syntactic_behaviour_senses.sql
psql -U postgres -d wordnet_test -f lexicon_dependencies.sql
psql -U postgres -d wordnet_test -f lexicon_extensions.sql
```



The migration of WordNet from the native SQLite database to PostgreSQL is complete.
