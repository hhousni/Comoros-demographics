# Public datasets for Comoros Open Data

This folder contains publication-ready CSV versions of the demographic and administrative datasets.

Files included:

- population_fact.csv
- population_fact_local.csv
- population_serie_longue.csv
- population_ile_serie_longue.csv
- population_prefecture_serie_longue.csv
- population_commune_serie_longue.csv
- population_village_serie_longue.csv
- population_by_island.csv
- population_by_prefecture.csv
- population_by_commune.csv
- population_by_town_village.csv
- master_country.csv
- master_island.csv
- master_prefecture.csv
- master_commune.csv
- master_town_village.csv

## Notes

- `population_fact.csv` is the main long-format table at the finest geographic level.
- `population_serie_longue.csv` is the national series aggregated to the country level.
- Each row contains one geography unit and one year.
- `population` is reported in persons.
- All IDs follow the administrative master code structure used by the Comoros project.

## Découpage administratif / Administrative boundaries

- Les identifiants et noms suivent le référentiel administratif (comoros-admin-master), aligné sur la loi n°11-006/AU du 2 mai 2011 portant organisation territoriale.
- Les tableaux sources de l'INSEED présentent 18 préfectures : Moya y figure comme préfecture distincte, et Mitsamiouli et Mboudé sont séparées. Dans ces jeux de données, conformément à la loi de 2011 :
  - la commune de Moya est rattachée à la préfecture de Sima (KM15) ;
  - Mitsamiouli et Mboudé sont regroupées dans la préfecture Mitsamiouli-Mboudé (KM26).
- Les noms tels qu'ils figurent dans la source INSEED sont conservés dans les colonnes `*_name_local` de `population_fact.csv`.

## Écart avec les totaux de l'INSEED / Gap with INSEED's totals

**FR.** Dans ces jeux de données, chaque total (commune, préfecture, île, pays) est la **somme des villages**. Dans le fichier source de l'INSEED (feuille « Pop îles ajustée »), deux lignes de commune ne sont pas égales à la somme de leurs villages :

- **Commune de Sima (KM152), 2018 à 2029** : la ligne de la commune augmente beaucoup plus vite que ses villages, puis redescend en 2030. Nos chiffres sont plus bas que la ligne de l'INSEED ;
- **Commune de Ngadzalé (KM115), 2040 à 2042** : la ligne de la commune dépasse ses villages de 100 personnes.

Nous gardons la somme des villages, pour que tous les niveaux restent cohérents entre eux. Les totaux d'Anjouan et du pays diffèrent donc de ceux de l'INSEED les mêmes années. Ailleurs, les écarts ne dépassent pas l'arrondi des villages à la personne près (quelques personnes). Un test (`tests/test_source_totals.py`) vérifie ces écarts à chaque génération. Le problème a été signalé à l'INSEED.

**EN.** In these datasets every total (commune, prefecture, island, country) is the **sum of villages**. In INSEED's source file (sheet "Pop îles ajustée"), two commune rows are not the sum of their villages: **Sima (KM152), 2018–2029** (the commune row grows much faster than its villages, then drops back in 2030) and **Ngadzalé (KM115), 2040–2042** (100 persons above its villages). We keep the sum of villages so that all levels stay consistent; the Anjouan and national totals therefore differ from INSEED's in those years. Elsewhere gaps stay within the rounding of villages to whole persons. `tests/test_source_totals.py` checks these gaps on every run. The issue was reported to INSEED.

Écart publié − INSEED, en personnes / published − INSEED, persons:

| Année | Sima (KM152) | Ngadzalé (KM115) | Anjouan (KM1) | Comores (KM) |
|---|---|---|---|---|
| 2018 | −186 | | −187 | −184 |
| 2019 | −383 | | −383 | −394 |
| 2020 | −588 | | −589 | −590 |
| 2021 | −802 | | −801 | −804 |
| 2022 | −1 024 | | −1 021 | −1 015 |
| 2023 | −1 250 | | −1 250 | −1 249 |
| 2024 | −1 484 | | −1 488 | −1 482 |
| 2025 | −1 725 | | −1 725 | −1 724 |
| 2026 | −1 972 | | −1 971 | −1 970 |
| 2027 | −2 224 | | −2 227 | −2 228 |
| 2028 | −2 481 | | −2 481 | −2 484 |
| 2029 | −2 744 | | −2 748 | −2 755 |
| 2040 | | −100 | −103 | −103 |
| 2041 | | −100 | −99 | −98 |
| 2042 | | −100 | −98 | −97 |

Exemple / example — Sima 2029 : INSEED 24 644, publié / published 21 900.
