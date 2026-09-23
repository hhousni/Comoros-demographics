# Comoros Demographics

This repository is the analysis and publication layer for the Comoros demographic project.

## Purpose

The goal of this project is to prepare and publish demographic datasets for open data use, following a clean administrative hierarchy.

## Source-of-truth split

The administrative reference tables are maintained in a separate reusable repository:

- https://github.com/hhousni/comoros-admin-master.git

This repository consumes that admin master as the canonical source for:

- country
- island
- prefecture
- commune
- town_village

This project is responsible for:

- reading raw demographic inputs
- joining them to official administrative IDs
- building publication-ready datasets
- exporting CSV outputs for open data use

## Dependency setup

The demographics project is intentionally separate from the admin master repo, but it can depend on that repo in a clean way.

### Recommended setup

Clone the admin repo as a local dependency under the external folder:

- git submodule add https://github.com/hhousni/comoros-admin-master.git external/comoros-admin-master
- git submodule update --init --recursive

After that, the project will resolve the master files from:

- external/comoros-admin-master/masters

If that dependency is not present, the repo falls back to the local masters folder for compatibility.

## Repository structure

- raw_data/ : original source files
- clean_data/ : cleaned intermediate data if needed
- script/ : ETL, cleaning, and dataset generation scripts
- external/ : external project dependencies, including the admin master repo
- masters/ : local fallback copies if needed
- datasets/ : final publication datasets

## Recommended workflow

1. Maintain the admin master in the dedicated admin repo when official administrative data changes.
2. Update the remote dependency or pull the master repo.
3. Generate demographic outputs here using the canonical IDs.
4. Publish the final CSV datasets from this repo.

## Notes

- The admin master repo is the authoritative layer for IDs and names.
- This repo is the analysis/publication layer for demographic results.
- Administrative maintenance stays separate from demographic analysis and publication work.
