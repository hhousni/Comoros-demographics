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
