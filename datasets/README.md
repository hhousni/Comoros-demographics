# Population des Comores, projections 2017–2042 / Population of the Comoros, projections 2017–2042

Jeux de données publiés sur [Comores Open Data](https://comoresopendata.org), catégorie Démographie.
Datasets published on [Comores Open Data](https://comoresopendata.org), category Demographics.

Codes du catalogue / catalog codes : category `demographics`, island `all`, organization `Comores Open Data`, license `ccby` (CC BY 4.0), frequency `once`, format `csv`.

**FR.** Ces chiffres sont des **projections** de l'INSEED (hypothèse moyenne), pas des comptages. Seule l'année 2017 vient du recensement général de la population et de l'habitat (RGPH 2017). Les années 2018 à 2042 sont calculées à partir de ce recensement. Pour 2017, le fichier publié donne 758 318 habitants : c'est le total du tableau par commune de l'INSEED, celui que nous publions ; le total national du même classeur est 758 316.

**EN.** These figures are INSEED **projections** (medium hypothesis), not counts. Only 2017 comes from the 2017 general population and housing census (RGPH 2017). The years 2018 to 2042 are computed from that census. For 2017 the published file gives 758,318 inhabitants: the total of INSEED's table by commune, the one we publish; the national total in the same workbook is 758,316.

## Fiche commune aux cinq jeux de population / Shared record for the five population datasets

| | |
|---|---|
| Producteur / Producer | INSEED (Institut national de la statistique et des études économiques et démographiques), Comores ; projections réalisées avec l'appui de l'UNFPA (« Projection-UNFPA » dans le classeur) |
| Document source / Source document | Classeur « Revision_des_Projections_demographiques_hypothese_moyenne » (créé le 23 juin 2021), feuille « Pop îles ajustée » ; copie dans `raw_data/` |
| URL | aucune adresse publique trouvée (recherche du 1er novembre 2026) / no public URL found (search of 1 November 2026) |
| Date de récupération / Retrieved | fichier reçu avant le 17 août 2026 (date du fichier ; ajouté au dépôt le 21 août 2026) |
| Licence | CC BY 4.0 (licence par défaut de Comores Open Data ; l'INSEED ne publie pas de conditions de réutilisation pour ce fichier — à confirmer avec l'INSEED) |
| Couverture / Coverage | 2017–2042, chaque année ; Union des Comores, 3 îles, 16 préfectures, 54 communes, 319 villages et localités |
| Fréquence / Frequency | `once` (publication unique ; mise à jour si l'INSEED publie une nouvelle révision) |
| Unité / Unit | personnes, arrondies à l'unité / persons, rounded to whole persons |
| Organisation | Comores Open Data |
| Version | 31 octobre 2026 (dernière génération ; voir `CHANGELOG.md`) |

Le classeur de l'INSEED donne des chiffres à décimales par village. Chaque village est arrondi à la personne près, puis les communes, préfectures, îles et le pays sont la **somme des villages**. Les totaux peuvent donc différer de quelques personnes de ceux de l'INSEED, et nettement pour Sima et Ngandzalé (voir « Écart avec les totaux de l'INSEED » plus bas).
INSEED's workbook gives decimal figures per village. Each village is rounded to the whole person; communes, prefectures, islands and the country are the **sum of villages**, so totals can differ from INSEED's by a few persons, and clearly for Sima and Ngandzalé (see "Gap with INSEED's totals" below).

## Fichiers publiés / Published files

Le texte français de chaque fiche est celui du champ « Description » du catalogue (`dataset_descriptions.txt` le reprend, prêt à coller). Les titres actuels du site sont entre parenthèses ; les liens existants restent valables si le titre change.
The French text of each record goes in the catalog "Description" field (`dataset_descriptions.txt` holds it, ready to paste). Current site titles are in brackets; existing links keep working if a title changes.

### 1. `population_serie_longue.csv` — pays / country (26 lignes / rows)

- **Titre** : Population des Comores, projections 2017–2042 *(site : « Population nationale en série longue »)*
- **Title**: Population of the Comoros, projections 2017–2042
- **FR** : Population totale de l'Union des Comores pour chaque année de 2017 à 2042, une ligne par année. Ce sont des projections de l'INSEED (hypothèse moyenne) : seule l'année 2017 vient du recensement (RGPH 2017), les années suivantes sont calculées. Le total de chaque année est la somme des 319 villages et localités, arrondis à la personne près ; il peut différer de quelques personnes du total de l'INSEED, de 184 à 2 755 personnes entre 2018 et 2029 à cause d'une incohérence dans la ligne de la commune de Sima du fichier source, et d'environ 100 personnes en 2040–2042 (commune de Ngandzalé).
- **EN**: Total population of the Union of the Comoros for each year from 2017 to 2042, one row per year. These are INSEED projections (medium hypothesis): only 2017 comes from the census (RGPH 2017), later years are computed. Each year's total is the sum of the 319 towns and villages, rounded to whole persons; it can differ from INSEED's total by a few persons, by 184 to 2,755 persons in 2018–2029 because of an inconsistency in the Sima commune row of the source file, and by about 100 persons in 2040–2042 (Ngandzalé commune).

### 2. `population_ile_serie_longue.csv` — îles / islands (78 lignes / rows)

- **Titre** : Population par île, projections 2017–2042 *(site : « Population par île des Comores en série longue »)*
- **Title**: Population by island, projections 2017–2042
- **FR** : Population de chacune des trois îles (Anjouan, Grande Comore, Mohéli) pour chaque année de 2017 à 2042, une ligne par île et par année. Projections de l'INSEED (hypothèse moyenne) : seule l'année 2017 vient du recensement (RGPH 2017). Chaque total est la somme des villages de l'île ; pour Anjouan, il est inférieur à la ligne de l'INSEED de 2018 à 2029 (jusqu'à 2 748 personnes, commune de Sima) et d'environ 100 personnes en 2040–2042 (commune de Ngandzalé).
- **EN**: Population of each of the three islands (Anjouan, Grande Comore, Mohéli) for each year from 2017 to 2042, one row per island and year. INSEED projections (medium hypothesis): only 2017 comes from the census (RGPH 2017). Each total is the sum of the island's villages; for Anjouan it is below INSEED's row in 2018–2029 (up to 2,748 persons, Sima commune) and by about 100 persons in 2040–2042 (Ngandzalé commune).

### 3. `population_prefecture_serie_longue.csv` — préfectures / prefectures (416 lignes / rows)

- **Titre** : Population par préfecture, projections 2017–2042 *(site : « Population par préfecture en série longue »)*
- **Title**: Population by prefecture, projections 2017–2042
- **FR** : Population des 16 préfectures habitées pour chaque année de 2017 à 2042, une ligne par préfecture et par année. Projections de l'INSEED (hypothèse moyenne) : seule l'année 2017 vient du recensement (RGPH 2017). Les préfectures suivent le référentiel administratif de Comores Open Data (OCHA) : la commune de Moya est comptée dans la préfecture de Sima, et Mitsamiouli et Mboudé forment une seule préfecture, alors que l'INSEED les présente séparément. Chaque total est la somme des villages de la préfecture.
- **EN**: Population of the 16 inhabited prefectures for each year from 2017 to 2042, one row per prefecture and year. INSEED projections (medium hypothesis): only 2017 comes from the census (RGPH 2017). Prefectures follow the Comores Open Data administrative reference (OCHA): Moya commune is counted in Sima prefecture, and Mitsamiouli and Mboudé form one prefecture, whereas INSEED shows them separately. Each total is the sum of the prefecture's villages.

### 4. `population_commune_serie_longue.csv` — communes (1 404 lignes / rows)

- **Titre** : Population par commune, projections 2017–2042 *(site : « Population par commune en série longue »)*
- **Title**: Population by commune, projections 2017–2042
- **FR** : Population des 54 communes habitées pour chaque année de 2017 à 2042, une ligne par commune et par année. Projections de l'INSEED (hypothèse moyenne) : seule l'année 2017 vient du recensement (RGPH 2017). Chaque total est la somme des villages de la commune. Deux communes diffèrent de la ligne de l'INSEED : Sima de 2018 à 2029 (jusqu'à 2 744 personnes de moins) et Ngandzalé (NGADZALE chez l'INSEED) de 2040 à 2042 (100 personnes de moins), car dans le fichier source ces lignes ne sont pas égales à la somme de leurs villages.
- **EN**: Population of the 54 inhabited communes for each year from 2017 to 2042, one row per commune and year. INSEED projections (medium hypothesis): only 2017 comes from the census (RGPH 2017). Each total is the sum of the commune's villages. Two communes differ from INSEED's row: Sima in 2018–2029 (up to 2,744 persons fewer) and Ngandzalé (NGADZALE at INSEED) in 2040–2042 (100 fewer), because in the source file these rows are not the sum of their villages.

### 5. `population_village_serie_longue.csv` — villages et localités / towns and villages (8 294 lignes / rows)

- **Titre** : Population par village et localité, projections 2017–2042 *(site : « Population par village / localité en série longue »)*
- **Title**: Population by town and village, projections 2017–2042
- **FR** : Population des 319 villages et localités pour chaque année de 2017 à 2042, une ligne par village et par année, avec sa commune, sa préfecture et son île. Projections de l'INSEED (hypothèse moyenne) : seule l'année 2017 vient du recensement (RGPH 2017). Comores Open Data arrondit les chiffres de l'INSEED, qui ont des décimales, à la personne près. Les identifiants des villages sont ceux du référentiel administratif de Comores Open Data ; les coordonnées GPS sont dans la « Table de référence des villages et localités ».
- **EN**: Population of the 319 towns and villages for each year from 2017 to 2042, one row per village and year, with its commune, prefecture and island. INSEED projections (medium hypothesis): only 2017 comes from the census (RGPH 2017). Comores Open Data rounds INSEED's figures, which have decimals, to whole persons. Village IDs are those of the Comores Open Data administrative reference; GPS coordinates are in the "Reference table of towns and villages".

## Colonnes / Columns

Tous les fichiers sont en UTF-8, séparateur virgule. Colonnes de chaque fichier :
All files are UTF-8, comma-separated. Columns of each file:

| Fichier / File | Colonnes / Columns |
|---|---|
| `population_serie_longue.csv` | `country_id, country_name, year, population` |
| `population_ile_serie_longue.csv` | `country_id, island_id, island_name, year, population` |
| `population_prefecture_serie_longue.csv` | `country_id, island_id, prefecture_id, prefecture_name, year, population` |
| `population_commune_serie_longue.csv` | `country_id, island_id, prefecture_id, prefecture_name, commune_id, commune_name, year, population` |
| `population_village_serie_longue.csv` | `country_id, island_id, prefecture_id, prefecture_name, commune_id, commune_name, town_village_id, town_village_name, year, population` |

| Colonne / Column | Signification / Meaning | Type |
|---|---|---|
| `country_id` | identifiant du pays (`KM`) / country ID | texte / text |
| `country_name` | nom du pays (fichier pays) / country name | texte |
| `island_id` | identifiant de l'île : `KM1` Anjouan, `KM2` Grande Comore, `KM3` Mohéli / island ID | texte |
| `island_name` | nom français de l'île / French island name | texte |
| `prefecture_id`, `prefecture_name` | identifiant et nom de la préfecture (ex. `KM15` Sima) / prefecture ID and name | texte |
| `commune_id`, `commune_name` | identifiant et nom de la commune (ex. `KM152` Sima) / commune ID and name | texte |
| `town_village_id` | identifiant du village (ex. `KM321_0001` Fomboni) / village ID | texte |
| `town_village_name` | nom du village tel qu'écrit par l'INSEED (majuscules) / village name as spelled by INSEED | texte |
| `year` | année, 2017 à 2042 / year | entier / integer |
| `population` | population projetée, en personnes / projected population, persons | entier / integer |

Les identifiants et noms viennent de `comoros-admin-master` (https://github.com/hhousni/comoros-admin-master). / IDs and names come from `comoros-admin-master`.

## Vérifications à la main / Spot-checks

Valeurs comparées à la main avec le classeur de l'INSEED (30 octobre 2026) / values compared by hand with INSEED's workbook:

| Village | Année / Year | INSEED | Publié / Published |
|---|---|---|---|
| Fomboni (`KM321_0001`) | 2017 | 17 290 | 17 290 |
| Fomboni (`KM321_0001`) | 2042 | 31 906,29 | 31 906 |
| Mutsamudu (`KM134_0001`) | 2030 | 36 916,70 | 36 917 |

## Découpage administratif / Administrative boundaries

- **FR.** Les identifiants et noms suivent le référentiel administratif `comoros-admin-master`, qui reprend les codes de l'OCHA (COD-AB Comores, COSEP, v01 de 2019) : 17 préfectures, dont Kartala (`KM29`, cratère du Karthala, inhabité). Les tableaux de l'INSEED présentent 18 préfectures : Moya y figure comme préfecture distincte, et Mitsamiouli et Mboudé sont séparées. Ici :
  - la commune de Moya (`KM151`) est rattachée à la préfecture de Sima (`KM15`), comme dans la loi n°11-006/AU du 2 mai 2011 (art. 7) ;
  - Mitsamiouli et Mboudé sont regroupées dans la préfecture Mitsamiouli-Mboudé (`KM26`).
- **EN.** IDs and names follow the `comoros-admin-master` reference, which uses OCHA's codes (COD-AB Comoros, COSEP, v01, 2019): 17 prefectures, including Kartala (`KM29`, the uninhabited Karthala crater). INSEED's tables show 18 prefectures (Moya separate; Mitsamiouli and Mboudé separate). Here Moya commune (`KM151`) is in Sima prefecture (`KM15`), as in law 11-006/AU of 2 May 2011 (art. 7), and Mitsamiouli and Mboudé form one prefecture, Mitsamiouli-Mboudé (`KM26`).
- Les noms tels qu'ils figurent dans la source INSEED sont conservés dans les colonnes `*_name_local` de `population_fact.csv`. / Names as spelled by INSEED are kept in the `*_name_local` columns of `population_fact.csv`.

## Autres fichiers du dossier (non publiés sur le site) / Other files (not published on the site)

- `population_fact.csv` : table complète au niveau village, avec les noms de l'INSEED (`*_name_local`) ; sert aux contrôles. / full village-level table with INSEED's names; used for checks.
- `population_by_island.csv`, `population_by_prefecture.csv`, `population_by_commune.csv`, `population_by_town_village.csv` : copies identiques des fichiers `*_serie_longue.csv` (anciens noms, voir tâche 5 de `TASKS.md`). / identical copies of the `*_serie_longue.csv` files (old names).
- `master_*.csv` : copies des tables de référence de `comoros-admin-master`. Les tables de référence publiées sur le site, et leurs fiches, viennent de ce dépôt. / copies of the reference tables; the published reference tables and their records come from that repo.
- `population_fact_local.csv` (si présent / if present) : fichier de contrôle local, ignoré par git, jamais publié. / local debug file, ignored by git, never published.

## Écart avec les totaux de l'INSEED / Gap with INSEED's totals

**FR.** Dans ces jeux de données, chaque total (commune, préfecture, île, pays) est la **somme des villages**. Dans le fichier source de l'INSEED (feuille « Pop îles ajustée »), deux lignes de commune ne sont pas égales à la somme de leurs villages :

- **Commune de Sima (KM152), 2018 à 2029** : la ligne de la commune augmente beaucoup plus vite que ses villages, puis redescend en 2030. Nos chiffres sont plus bas que la ligne de l'INSEED ;
- **Commune de Ngandzalé (KM115), 2040 à 2042** : la ligne de la commune dépasse ses villages de 100 personnes.

Nous gardons la somme des villages, pour que tous les niveaux restent cohérents entre eux. Les totaux d'Anjouan et du pays diffèrent donc de ceux de l'INSEED les mêmes années. Ailleurs, les écarts ne dépassent pas l'arrondi des villages à la personne près (quelques personnes). Un test (`tests/test_source_totals.py`) vérifie ces écarts à chaque génération. Le problème a été signalé à l'INSEED.

**EN.** In these datasets every total (commune, prefecture, island, country) is the **sum of villages**. In INSEED's source file (sheet "Pop îles ajustée"), two commune rows are not the sum of their villages: **Sima (KM152), 2018–2029** (the commune row grows much faster than its villages, then drops back in 2030) and **Ngandzalé (KM115), 2040–2042** (100 persons above its villages). We keep the sum of villages so that all levels stay consistent; the Anjouan and national totals therefore differ from INSEED's in those years. Elsewhere gaps stay within the rounding of villages to whole persons. `tests/test_source_totals.py` checks these gaps on every run. The issue was reported to INSEED.

Écart publié − INSEED, en personnes / published − INSEED, persons:

| Année | Sima (KM152) | Ngandzalé (KM115) | Anjouan (KM1) | Comores (KM) |
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
