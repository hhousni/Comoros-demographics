# Journal des modifications

## 2026-10-22 — Corrections des identifiants

Les chiffres de population ne changent pas : les totaux national, par île et par commune sont identiques à la version précédente. Seuls certains identifiants et rattachements ont été corrigés.

### 1. Préfecture de Moya rattachée à Sima

Conformément à la loi n°11-006/AU du 2 mai 2011 portant organisation territoriale (art. 7), la commune de Moya fait partie de la préfecture de Sima.

- L'identifiant `KM16` (Moya), qui n'existe pas dans le référentiel administratif, est supprimé.
- La population de Moya est désormais incluse dans Sima (`KM15`). En 2017, Sima passe de 35 173 à 59 313 habitants (35 173 + 24 140).
- Fichiers concernés : `population_prefecture_serie_longue.csv` et les fichiers au niveau commune et village (colonne `prefecture_id`).

### 2. Identifiants de villages corrigés

Les villages portant le même nom dans plusieurs communes recevaient par erreur le même identifiant. Chaque village a désormais un identifiant unique, rattaché à sa propre commune : 319 villages, contre 308 identifiants auparavant.

| Commune | Village | Ancien ID | Nouvel ID |
|---|---|---|---|
| Domoni | DOMONI | KM252_0007 | KM112_0001 |
| Ngandzalé | SALAMANI | KM153_0014 | KM115_0003 |
| Adda | KANGANI | KM121_0005 | KM121_0004 |
| Bandrani Ya Chironkamba | MAWENI | KM151_0007 | KM131_0004 |
| Moya | MAWENI | KM151_0007 | KM151_0006 |
| Sima | SIMA | KM232_0003 | KM152_0001 |
| Sima | MILEMBENI | KM234_0004 | KM152_0007 |
| Isahari | MILEMBENI | KM234_0004 | KM234_0003 |
| Domba | PIDJANI | KM264_0004 | KM241_0005 |
| Nioumagama | DOMONI | KM252_0007 | KM252_0006 |
| Cembenoi Sada Djoulamlima | KOUA | KM265_0009 | KM262_0002 |
| Nyumamro Kiblani | KOUA | KM265_0009 | KM265_0008 |
| Bambao Ya Hari | DZAHANI | KM283_0003 | KM271_0008 |
| Djando | KANGANI | KM121_0005 | KM311_0005 |
| Moimbassa | DOMONI | KM252_0007 | KM323_0003 |
| Moimbao | BARAKANI | KM143_0003 | KM332_0002 |

Fichier concerné : `population_village_serie_longue.csv`. La population de chaque village est inchangée.
