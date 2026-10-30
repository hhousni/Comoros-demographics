# TASKS.md — backlog for Claude Code

Work top to bottom. For each task: make the change, regenerate datasets, run tests, tick the box, add a one-line note under "Log" at the bottom. Tasks marked **[NEEDS DECISION]** must not be implemented until the owner records a decision in the task.

Audit date: 2026-10-22. Numbers below are from that audit.

---

## 1. [x] Fix village ID lookup (critical — published data is wrong)

**Problem.** `town_map` in `get_population_fact()` is keyed by normalized village name only. Villages sharing a name across communes all get the same ID.
- 319 villages in raw data → only 308 distinct `town_village_id`s.
- 546 rows have a duplicated `(town_village_id, year)`; 442 rows have a village ID whose prefix doesn't match their commune.
- Affected names: DOMONI (×4, all `KM252_0007`), KANGANI, BARAKANI, SALAMANI, MAWENI, SIMA, MILEMBENI, PIDJANI, KOUA, DZAHANI.
- Commune/prefecture/island/country totals are unaffected; village-level files are wrong.

**Do.**
- Look up villages by `(commune_id, normalized name)` using the master's `commune_id` column.
- If a village has no match in its commune, collect all misses and raise an error listing them (commune name, village name). Do not fall back to a global name lookup.
- If legitimate spelling differences exist, add them to a per-commune alias table, e.g. `{("KM311", "kangani"): "KM311_00xx"}`.

**Done when.** 319 distinct village IDs; no duplicated `(town_village_id, year)`; every `town_village_id` starts with its `commune_id + "_"`.

## 2. [ ] Make all matching explicit and logged

**Problem.** Prefecture and commune IDs use `difflib` fuzzy matching (cutoff 0.82) with no record of what was matched. Also `prefecture_id` is computed twice (second pass overwrites the first) and `load_master_tables()` is called twice.

**Do.**
- Match prefectures within island, communes within prefecture (exact normalized name → alias table → error).
- Remove fuzzy matching, or keep it only to *suggest* candidates in the error message.
- Write a mapping report `datasets/_mapping_report.csv` (gitignored) listing raw name → ID → method (`exact`/`alias`).
- Remove the duplicate computations.

**Done when.** Script fails loudly on any unmatched unit; report generated; outputs identical to after Task 1 (or differences explained in the Log).

## 3. [x] Prefecture list inconsistency (Moya, Mboudé, Kartala)

**Problem.** Raw data has a "Préfecture de Moya"; the script aliases it to `KM16`. The admin master has no `KM16` and places commune Moya (`KM151`) under Sima (`KM15`). Output rows point to a prefecture ID not in `master_prefecture.csv`.

**Options.**
- A. Moya is its own prefecture → add `KM16` to `comoros-admin-master` (and re-ID its communes there), then update the submodule.
- B. Moya belongs to Sima → remove the `moya → KM16` alias so rows map to `KM15`.

**Research (2026-10-22).**
- Loi n°11-006/AU du 2 mai 2011 (organisation territoriale), art. 7: Ndzuwani has 5 prefectures — Mutsamudu, Ouani, Domoni, Mrémani, Sima — and "Sima (Communes de Sima, Vouani, Moya)". Art. 10: "Moya 6 villes ou villages" (matches the 6 Moya villages in the raw file). Source: https://justice.gouv.km/wp-content/uploads/2025/03/loi-n-11-006au-du-02-mai-2011-portant-organisation-territoriale-de-lunion-des-comores-promulguee-par-decret-n-11-148pr.pdf
- citypopulation.de (based on the 2017 census) lists Moya as a separate prefecture containing one commune, Moya (24,140 in 2017). So INSEED's statistical breakdown separates Moya, while the law puts it under Sima. Source: https://www.citypopulation.de/de/comoros/admin/16__moya/
- Broader picture: three prefecture lists disagree.
  - 2011 law: 16 prefectures (Anjouan 5, Ngazidja 8, Mohéli 3).
  - INSEED raw file: 18 — adds MOYA (split from Sima) and splits MITSAMIOULI / MBOUDE (both currently forced to KM26).
  - Admin master: 17 — the law's 16 + KARTALA (KM29), which has no population rows and isn't in the 2011 law.
  - Mboudé was raised to prefecture on 5 March 2017 (inaugurated by the President; legal basis reported as disputed). Source: https://www.comoresinfos.net/region-de-mboude-une-prefecture-sans-prefet/
- So this task is really "which prefecture list is official today", and that decision belongs in comoros-admin-master, not here.
- Recommendation: until the master is updated, follow the master (option B for Moya; keep Mboudé + Mitsamiouli under KM26) and document in datasets/README.md that INSEED publishes 18 prefectures. If a post-2011 text officially creates Moya / Mboudé / Kartala, update the master first, then re-run here.

**Decision:** B, confirmed by owner 2026-10-22. Follow the admin master: Moya → Sima (KM15); Mitsamiouli + Mboudé stay under KM26. Open follow-up in comoros-admin-master: confirm the official current prefecture list (is any post-2011 text creating Moya / Mboudé / Kartala?) and why Kartala (KM29) is in the master. → Answered 2026-10-22: the admin master uses the OCHA/COSEP COD-AB p-codes (same as the comorosmaps R package). KM29 = "Kartala", whose only commune is KM291 "Cratère du Karthala" — the uninhabited volcano crater zone. So zero population is expected; keep it.

**Done when.** Every `prefecture_id` in outputs exists in `master_prefecture.csv`.

## 4. [ ] Add data-integrity tests

Add to `tests/` (pytest, read from `datasets/`):
- All IDs exist in the respective `master_*.csv`.
- Hierarchy prefixes hold (see ID scheme in `CLAUDE.md`).
- `(town_village_id, year)` unique; years = 2017–2042; same village count every year.
- Aggregates are consistent: village sums = commune = prefecture = island = country, per year.
- No null IDs or populations; populations are non-negative integers.

**Done when.** Tests fail on the pre-Task-1 data and pass after.

## 5. [ ] Duplicate output files **[NEEDS DECISION]**

`population_by_{island,prefecture,commune,town_village}.csv` are byte-identical to `population_{ile,prefecture,commune,village}_serie_longue.csv`.

**Options.** Keep one naming scheme (recommended: the `_serie_longue` names, which match `dataset_descriptions.txt`) or keep both and state in `datasets/README.md` that they are aliases.

**Decision:** _(owner to fill in)_

## 6. [ ] Master coverage gaps (report only — fix belongs in admin-master repo)

- **Duplicate village rows in the master (root cause of Task 1).** Each village name shared by several communes was copied into every one of those communes, with coordinates copied too: 19 (commune, name) pairs have two rows. After Task 1 the 19 unused master villages are exactly these phantom rows. The script picks the right one via `AMBIGUOUS_TOWN_VILLAGE_IDS`; once the master is fixed, delete that dict (the script will fail loudly if an entry no longer exists). Pairs: Domoni (KM112, KM252, KM323), Salamani (KM115, KM153), Kangani (KM121, KM311), Maweni (KM131, KM151), Barakani (KM143, KM332), Milembeni (KM152, KM234), Pidjani (KM241, KM264), Koua (KM262, KM265), Dzahani (KM271, KM283).
- (Before Task 1 the audit counted 30 unused master villages; that number was inflated by the bug.)
- Many master villages have empty latitude/longitude, and some coordinates are on the wrong island (e.g. Barakani KM332_0003 in Mohéli has Anjouan coordinates).

**Do.** Generate a list of both (village ID, name, commune) into `TASKS.md` under this task so they can be raised in `comoros-admin-master`. 

### Follow-up: harmonise villages with comorosmaps (cross-repo, later)

- comorosmaps (CRAN 1.6.1) uses the same COD-AB p-codes as the admin master for country → commune, so prefecture/commune population joins directly.
- Its city layer (268 localities, from `data-raw/shp_files/km.xlsx`) only carries an island code (`KM1c`/`KM2c`/`KM3c`), not `town_village_id`.
- Plan: once the admin-master village table is cleaned (duplicates removed, coordinates checked), give each comorosmaps city its `town_village_id` and use the master as the single village list (and source of coordinates) for both projects.

## 7. [ ] Small cleanups

- Make tests independent of working directory (build paths from `Path(__file__)`).
- Add `requirements.txt` (pandas, openpyxl, pytest).
- Update `README.md`: remove references to `clean_data/` and `masters/` if they stay absent, document the commands from `CLAUDE.md`.

---

## Log

- 2026-10-22 — Backlog created from audit.
- 2026-10-22 — Task 3: added legal research on Moya (2011 law puts it under Sima).
- 2026-10-22 — Task 3 done: alias moya → KM15 in script; datasets regenerated (Sima 2017 = 59,313 = 35,173 + Moya 24,140; national totals unchanged; no orphan prefecture IDs); note added to datasets/README.md. Village-ID bug (Task 1) still present in regenerated files.
- 2026-10-22 — Task 1 done: villages now matched by (commune_id, normalized name) in `assign_town_village_ids()`; unmatched or ambiguous villages raise an error; 19 master duplicates resolved explicitly in `AMBIGUOUS_TOWN_VILLAGE_IDS`. Result: 319 distinct village IDs (was 308), no duplicate (village, year), all IDs inside their commune. Totals unchanged (2017: 758,318). Added `tests/test_village_ids.py` (part of Task 4). Published village IDs changed for the previously mis-assigned villages.
