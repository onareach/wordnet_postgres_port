# **Writing WordNet Porter**

Writing WordNet Porter involved the assembly into a self-contained package a series of Python and SQL scripts that I used to port the native SQLite database to a Postgres database. The original motivation for migrating WordNet from SQLite to Postgres was to make it easier to use WordNet on a web application with a Heroku back-end. Postgres is the default database on Heroku and I had used it before. 

The WordNet Porter application was scaffolded, built, tested, and documented with the help of ChatGPT.

### **Development Steps**

#### **1. Finish Initial `bootstrap.py`**

- This script should:
  - Create the project folder structure (if not present).
  - Set up a virtual environment (e.g., `venv/`) using `venv` or `virtualenv`.
  - Optionally install required packages using `pip` from a `requirements.txt` or `pyproject.toml`.

#### **2. Implement `main.py` as the Orchestrator**

- Import and sequentially call the `step01_...`, `step02_...` modules, etc.
- Add CLI flags or config options to control:
  - Which steps to run
  - Verbosity
  - Input/output overrides
  - Dry run vs. actual execution

#### **3. Finalize Each Step Module**

- Move the logic from the existing `scripts/` into corresponding `wordnet_porter/step*.py` files.
- Modularize each step with a `run()` function or similar interface.
- Add meaningful progress output and optional logging.

#### **4. Add Logging and Error Handling**

- Create a logging config in `wordnet_porter/utils.py` or similar.
- Support log levels (info, warning, error) and optionally write to a file.

#### **5. Package Setup for Installation**

- Finalize your `pyproject.toml` with:
  - Dependencies (e.g., `click`, `rich`, etc.)
  - A `[project.scripts]` entry for `wordnet-porter = wordnet_porter.main:main`
- Add a `requirements.txt` if you want quick pip installs outside build tools.

#### **6. Optional Enhancements**

- Add a config system (like `config.yaml` or `.env`)
- Add a CLI interface using `argparse` or `click`
- Integrate unit tests under `tests/` using `pytest`
- Add metadata and badges to `README.md` (e.g., GitHub Actions, License)

#### **7. Push to GitHub**

- Exclude large files with `.gitignore`
- Include a clean README with usage instructions
- Add MIT License or similar

