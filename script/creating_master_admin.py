from pathlib import Path
import re
import unicodedata

import pandas as pd


def normalize_name(value):
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.replace("-", " ")
    text = text.replace("/", " ")
    text = text.replace(".", " ")
    text = text.replace("'", " ")
    text = text.replace("(", " ")
    text = text.replace(")", " ")
    text = text.replace("_", " ")
    text = " ".join(text.split())
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


def clean_admin_name(value, level):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if level == "prefecture":
        return re.sub(r"(?i)^pr[eé]fecture de\s+", "", text, count=1).strip()
    if level == "commune":
        return re.sub(r"(?i)^commune(?: de)?\s+", "", text, count=1).strip()
    return text


def apply_aliases(series, aliases):
    def apply_alias(value):
        cleaned_value = "" if pd.isna(value) else str(value).strip()
        return aliases.get(normalize_name(cleaned_value), cleaned_value)

    return series.apply(apply_alias)


def unique_lookup(df, key, columns):
    lookup = df[[key] + columns].dropna(subset=[key]).drop_duplicates().copy()
    if lookup.duplicated(subset=[key]).any():
        raise ValueError(f"Duplicate values found for {key} in admin lookup data")
    return lookup


def load_lookup_frames(project_root, input_file):
    if input_file.exists():
        prefecture_lookup = pd.read_excel(input_file, sheet_name="com_admin2")[
            ["adm2_name", "adm2_pcode", "adm1_pcode", "adm0_pcode"]
        ].drop_duplicates().reset_index(drop=True)
        prefecture_lookup.columns = [
            "prefecture_name",
            "prefecture_id",
            "island_id",
            "country_id",
        ]

        commune_lookup = pd.read_excel(input_file, sheet_name="com_admin3")[
            ["adm3_name", "adm3_pcode", "adm2_pcode", "adm1_pcode", "adm0_pcode"]
        ].drop_duplicates().reset_index(drop=True)
        commune_lookup.columns = [
            "commune_name",
            "commune_id",
            "prefecture_id",
            "island_id",
            "country_id",
        ]
        return prefecture_lookup, commune_lookup

    prefecture_path = project_root / "masters" / "master_prefecture.xlsx"
    commune_path = project_root / "masters" / "master_commune.xlsx"
    missing_files = [str(path) for path in [prefecture_path, commune_path] if not path.exists()]
    if missing_files:
        raise FileNotFoundError(
            "Missing admin lookup workbook(s): " + ", ".join(missing_files)
        )

    prefecture_lookup = pd.read_excel(prefecture_path)
    commune_lookup = pd.read_excel(commune_path)
    return prefecture_lookup, commune_lookup


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
    country_df.to_excel(output_dir / "master_country.xlsx", index=False)

    # Island master: keep French and local names, plus official island code
    island_df = pd.read_excel(input_file, sheet_name="com_admin1")[
        ["adm1_name", "adm1_pcode", "adm0_pcode"]
    ].drop_duplicates().reset_index(drop=True)
    parsed = island_df["adm1_name"].apply(split_localized_name)
    island_df[["island_name_fr", "island_name_local"]] = pd.DataFrame(
        parsed.tolist(), index=island_df.index
    )
    island_df = island_df[["adm0_pcode", "adm1_pcode", "island_name_fr", "island_name_local"]]
    island_df.columns = ["country_id", "island_id", "island_name_fr", "island_name_local"]
    island_df.to_excel(output_dir / "master_island.xlsx", index=False)

    # Prefecture and commune masters follow the official administrative standard.
    prefecture_df, commune_df = load_lookup_frames(project_root, input_file)
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
    local_df = local_df.drop_duplicates().reset_index(drop=True)

    island_code_map = {
        "MWALI": "KM3",
        "NDZUWANI": "KM1",
        "NGAZIDJA": "KM2",
    }
    local_df["country_id"] = "KM"
    local_df["island_id"] = local_df["island"].map(island_code_map)

    prefecture_lookup, commune_lookup = load_lookup_frames(project_root, input_file)
    prefecture_lookup = prefecture_lookup.copy()
    commune_lookup = commune_lookup.copy()
    prefecture_lookup["norm"] = prefecture_lookup["prefecture_name"].apply(normalize_name)
    commune_lookup["norm"] = commune_lookup["commune_name"].apply(normalize_name)
    pref_map = dict(zip(prefecture_lookup["norm"], prefecture_lookup["prefecture_id"]))
    commune_map = dict(zip(commune_lookup["norm"], commune_lookup["commune_id"]))

    prefecture_aliases = {
        "mboude": "Mitsamiouli-Mboudé",
        "mitsamiouli": "Mitsamiouli-Mboudé",
        "moya": "Sima",
        "nioumachoua": "Nioumachioi",
    }
    commune_aliases = {
        "bambao mstanga": "Bambao Mtsanga",
        "bandrani ya mitsangani": "Bandrani Ya Mtsangani",
        "bambao ya djou": "Bambao Yadjou",
        "moinbassa": "Moimbassa",
        "ngadzale": "Ngandzalé",
        "oichili yaboini": "Oichili Yamboini",
        "shaweni": "Chaweni",
    }

    local_df["prefecture_name"] = local_df["prefecture"].apply(
        lambda value: clean_admin_name(value, "prefecture")
    )
    local_df["commune_name"] = local_df["commune"].apply(
        lambda value: clean_admin_name(value, "commune")
    )
    local_df["prefecture_name"] = apply_aliases(local_df["prefecture_name"], prefecture_aliases)
    local_df["commune_name"] = apply_aliases(local_df["commune_name"], commune_aliases)
    local_df["prefecture_id"] = local_df["prefecture_name"].apply(
        lambda x: pref_map.get(normalize_name(x))
    )
    local_df["commune_id"] = local_df["commune_name"].apply(
        lambda x: commune_map.get(normalize_name(x))
    )

    commune_id_lookup = unique_lookup(
        commune_lookup,
        "commune_id",
        ["prefecture_id", "island_id", "country_id"],
    )
    local_df = local_df.merge(
        commune_id_lookup,
        on="commune_id",
        how="left",
        suffixes=("", "_from_commune"),
    )
    local_df["prefecture_id"] = local_df["prefecture_id_from_commune"].combine_first(
        local_df["prefecture_id"]
    )
    local_df["island_id"] = local_df["island_id_from_commune"].combine_first(
        local_df["island_id"]
    )
    local_df["country_id"] = local_df["country_id_from_commune"].combine_first(
        local_df["country_id"]
    )
    local_df = local_df.drop(
        columns=["prefecture_id_from_commune", "island_id_from_commune", "country_id_from_commune"]
    )

    prefecture_id_lookup = unique_lookup(
        prefecture_lookup,
        "prefecture_id",
        ["island_id", "country_id"],
    )
    local_df = local_df.merge(
        prefecture_id_lookup,
        on="prefecture_id",
        how="left",
        suffixes=("", "_from_prefecture"),
    )
    local_df["island_id"] = local_df["island_id_from_prefecture"].combine_first(
        local_df["island_id"]
    )
    local_df["country_id"] = local_df["country_id_from_prefecture"].combine_first(
        local_df["country_id"]
    )
    local_df = local_df.drop(columns=["island_id_from_prefecture", "country_id_from_prefecture"])

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
