from pathlib import Path
import re
import unicodedata

import pandas as pd


COMMUNE_NAME_ALIASES = {
    "bambao mstanga": "bambao mtsanga",
    "bambao ya djou": "bambao yadjou",
    "bandrani ya mitsangani": "bandrani ya mtsangani",
    "moinbassa": "moimbassa",
    "ngadzale": "ngandzale",
    "oichili yaboini": "oichili yamboini",
    "shaweni": "chaweni",
}

PREFECTURE_NAME_ALIASES = {
    "mboude": "mitsamiouli mboude",
    "mitsamiouli": "mitsamiouli mboude",
    "moya": "sima",
    "nioumachoua": "nioumachioi",
}

PREFECTURE_PREFIXES = ("prefecture",)
COMMUNE_PREFIXES = ("commune",)


def normalize_name(value):
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.strip().lower()
    text = text.replace("-", " ")
    text = text.replace("/", " ")
    text = text.replace(".", " ")
    text = text.replace("'", " ")
    text = text.replace("(", " ")
    text = text.replace(")", " ")
    text = text.replace("_", " ")
    text = " ".join(text.split())
    return text


def strip_admin_prefix(value, prefixes):
    if pd.isna(value):
        return ""
    text = normalize_name(value)
    for prefix in prefixes:
        normalized_prefix = normalize_name(prefix)
        pattern = rf"^(?:{re.escape(normalized_prefix)})\s+(?:de\s+)?"
        stripped = re.sub(pattern, "", text, count=1, flags=re.IGNORECASE).strip()
        if stripped != text:
            return stripped
    return text


def split_localized_name(value):
    if pd.isna(value):
        return "", ""
    text = str(value).strip()
    if "(" in text and text.endswith(")"):
        main, local = text.split("(", 1)
        local = local.rsplit(")", 1)[0].strip()
        return main.strip(), local.strip()
    return text, text


project_root = Path(__file__).resolve().parent.parent
input_file = project_root / "raw_data" / "com_admin_boundaries.xlsx"
output_dir = project_root / "masters"

output_dir.mkdir(parents=True, exist_ok=True)

if input_file.exists():
    # Country master: official code from the raw workbook
    country_df = pd.read_excel(input_file, sheet_name="com_admin0")[
        ["adm0_name", "adm0_pcode"]
    ].drop_duplicates().reset_index(drop=True)
    country_df.columns = ["country_name", "country_id"]

    # Island master: keep French and local names, plus official island code
    island_df = pd.read_excel(input_file, sheet_name="com_admin1")[
        ["adm1_name", "adm1_pcode", "adm0_pcode"]
    ].drop_duplicates().reset_index(drop=True)
    parsed = island_df["adm1_name"].apply(split_localized_name)
    island_df[["island_name_fr", "island_name_local"]] = pd.DataFrame(
        parsed.tolist(), index=island_df.index
    )
    island_df = island_df[
        ["adm0_pcode", "adm1_pcode", "island_name_fr", "island_name_local"]
    ]
    island_df.columns = [
        "country_id",
        "island_id",
        "island_name_fr",
        "island_name_local",
    ]

    # Prefecture and commune masters follow the official administrative standard.
    prefecture_df = pd.read_excel(input_file, sheet_name="com_admin2")[
        ["adm2_name", "adm2_pcode", "adm1_pcode", "adm0_pcode"]
    ].drop_duplicates().reset_index(drop=True)
    prefecture_df.columns = [
        "prefecture_name",
        "prefecture_id",
        "island_id",
        "country_id",
    ]

    commune_df = pd.read_excel(input_file, sheet_name="com_admin3")[
        ["adm3_name", "adm3_pcode", "adm2_pcode", "adm1_pcode", "adm0_pcode"]
    ].drop_duplicates().reset_index(drop=True)
    commune_df.columns = [
        "commune_name",
        "commune_id",
        "prefecture_id",
        "island_id",
        "country_id",
    ]
else:
    country_df = pd.read_excel(output_dir / "master_country.xlsx")
    island_df = pd.read_excel(output_dir / "master_island.xlsx")
    prefecture_df = pd.read_excel(output_dir / "master_prefecture.xlsx")
    commune_df = pd.read_excel(output_dir / "master_commune.xlsx")

country_df.to_excel(output_dir / "master_country.xlsx", index=False)
island_df.to_excel(output_dir / "master_island.xlsx", index=False)
prefecture_df.to_excel(output_dir / "master_prefecture.xlsx", index=False)
commune_df.to_excel(output_dir / "master_commune.xlsx", index=False)

# Town/village detail master limited to identifiers, names and coordinates.
clean_input = project_root / "clean_data" / "comoros_administrative_clean.xlsx"
if clean_input.exists():
    local_df = pd.read_excel(clean_input)
    local_df = local_df[
        [
            "country",
            "island",
            "prefecture",
            "commune",
            "town_village",
            "Latitude_final",
            "Longitude_final",
        ]
    ].copy()
    local_df = local_df.rename(columns={"town_village": "town_village_name"})

    island_code_map = {
        "MWALI": "KM3",
        "NDZUWANI": "KM1",
        "NGAZIDJA": "KM2",
    }
    local_df["country_id"] = "KM"
    local_df["island_id"] = local_df["island"].map(island_code_map)

    pref_map = dict(
        zip(
            prefecture_df["prefecture_name"].apply(normalize_name),
            prefecture_df["prefecture_id"],
        )
    )

    commune_lookup = commune_df.merge(
        prefecture_df[["prefecture_id", "prefecture_name"]],
        on="prefecture_id",
        how="left",
    )
    commune_map = dict(
        zip(
            zip(
                commune_lookup["prefecture_name"].apply(normalize_name),
                commune_lookup["commune_name"].apply(normalize_name),
            ),
            commune_lookup["commune_id"],
        )
    )

    local_df["prefecture_name"] = local_df["prefecture"].apply(
        lambda value: strip_admin_prefix(value, PREFECTURE_PREFIXES)
    )
    local_df["commune_name"] = local_df["commune"].apply(
        lambda value: strip_admin_prefix(value, COMMUNE_PREFIXES)
    )
    local_df["prefecture_key"] = local_df["prefecture_name"].apply(
        lambda value: PREFECTURE_NAME_ALIASES.get(value, value)
    )
    local_df["commune_key"] = local_df["commune_name"].apply(
        lambda value: COMMUNE_NAME_ALIASES.get(value, value)
    )
    local_df["commune_lookup_key"] = list(
        zip(local_df["prefecture_key"], local_df["commune_key"])
    )
    local_df["commune_id"] = local_df["commune_lookup_key"].map(commune_map)
    local_df["prefecture_id"] = local_df["prefecture_key"].apply(pref_map.get)

    local_df["town_village_id"] = ""
    for commune_id, group in local_df.groupby("commune_id", dropna=False):
        if pd.isna(commune_id):
            local_df.loc[group.index, "town_village_id"] = ""
            continue
        ids = [f"{commune_id}_{idx:04d}" for idx in range(1, len(group) + 1)]
        local_df.loc[group.index, "town_village_id"] = ids

    town_master = local_df[
        [
            "country_id",
            "island_id",
            "prefecture_id",
            "commune_id",
            "town_village_id",
            "town_village_name",
            "Latitude_final",
            "Longitude_final",
        ]
    ].copy()
    town_master.columns = [
        "country_id",
        "island_id",
        "prefecture_id",
        "commune_id",
        "town_village_id",
        "town_village_name",
        "latitude",
        "longitude",
    ]
    town_master.to_excel(output_dir / "master_town_village.xlsx", index=False)

print("Official admin masters created successfully in 'masters/' :")
print("1. master_country.xlsx")
print("2. master_island.xlsx")
print("3. master_prefecture.xlsx")
print("4. master_commune.xlsx")
print("5. master_town_village.xlsx")
