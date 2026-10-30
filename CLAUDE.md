# CLAUDE.md — Comoros Demographics

Context and rules for Claude Code working in this repository. Read this first, then check `TASKS.md` for the current backlog.
Workspace map and shared rules: `../CLAUDE.md`; dataset rules: `../docs/DATA_CONTRACT.md` (this repo is its reference implementation).

## What this repo does

Turns the INSEED population projections workbook (medium hypothesis, 2017–2042) into publication-ready CSVs for Comoros Open Data, keyed by the official administrative IDs.

- Input: `raw_data/Revision_des_Projections_demographiques_hypothese_moyenne_3a125e5b6c.xlsx`, sheet `Pop îles ajustée` (data starts at row 67; hierarchy is encoded by row labels: `Comores` → island (`MWALI`/`NDZUWANI`/`NGAZIDJA`) → `Préfecture de …` → `Commune de …` → village rows).
- Admin reference (source of truth for IDs and names): git submodule `external/comoros-admin-master/masters/*.csv` (repo: https://github.com/hhousni/comoros-admin-master). Fallback: `masters/` (normally absent).
- Pipeline: `script/generate_public_datasets.py` (single script, pandas).
- Output: `datasets/*.csv` (+ `datasets/README.md`, `datasets/dataset_descriptions.txt` in French).

## Commands (run from repo root)

```bash
git submodule update --init --recursive      # or: bash script/sync_admin_master.sh
python3 script/generate_public_datasets.py   # regenerates everything in datasets/
python3 -m pytest -q                          # tests read datasets/ with relative paths
```

Always regenerate datasets and run tests after changing the script. Commit the script change and regenerated CSVs together.

## ID scheme (must hold for every row)

| Level | Example | Rule |
|---|---|---|
| country | `KM` | |
| island | `KM1` Anjouan, `KM2` Grande Comore, `KM3` Mohéli | starts with country_id |
| prefecture | `KM32` | starts with island_id |
| commune | `KM321` | starts with prefecture_id |
| town_village | `KM321_0001` | starts with `commune_id + "_"` |

Invariants:
- Every ID in outputs exists in the corresponding master table.
- `(town_village_id, year)` is unique in `population_fact.csv`.
- Each year has the same set of villages; years are 2017–2042 (26).
- Sum of villages = commune = prefecture = island = country totals for each year.

## Rules for changes

- Never edit the admin master files here. Name/ID fixes belong in `comoros-admin-master`; note them in `TASKS.md` instead.
- Never edit `raw_data/`.
- Matching must be explicit: exact normalized match within the parent unit, then a documented alias table. No silent fuzzy matching — if something doesn't match, fail loudly with the list of unmatched names.
- Keep aliases in one clearly named place (dict or CSV), each with a comment explaining it.
- Keep output column names and file names stable (they are published). Changes to published schemas need a note in `datasets/README.md`.
- `datasets/population_fact_local.csv` is gitignored (debug only).
- User-facing dataset docs are in French; code and comments in English.
