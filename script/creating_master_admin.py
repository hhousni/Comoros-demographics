import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


def normalize_name(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    for char in ["-", "/", ".", "'", "(", ")", "_", ",", ";", ":", "’", "\""]:
        text = text.replace(char, " ")
    text = re.sub(r"\b(prefecture|commune)\b", " ", text)
    text = re.sub(r"\bde\b", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def strip_admin_prefix(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"^(préfecture|prefecture|commune)\s*(de)?\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


def build_name_lookup(df, name_col, code_col):
    lookup = {}
    for _, row in df[[name_col, code_col]].dropna().iterrows():
        raw_name = str(row[name_col]).strip()
        for candidate in {normalize_name(raw_name), normalize_name(strip_admin_prefix(raw_name))}:
            if candidate:
                lookup[candidate] = row[code_col]
    return lookup


def find_best_match(name, lookup):
    if pd.isna(name):
        return None
    normalized = normalize_name(name)
    if not normalized:
        return None
    if normalized in lookup:
        return lookup[normalized]

    best_match = None
    best_score = 0.0
    for candidate, code in lookup.items():
        score = SequenceMatcher(None, normalized, candidate).ratio()
        if score > best_score and score >= 0.82:
            best_score = score
            best_match = code
    return best_match


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
    prefecture_df = pd.read_excel(input_file, sheet_name="com_admin2")[
        ["adm2_name", "adm2_pcode", "adm1_pcode", "adm0_pcode"]
    ].drop_duplicates().reset_index(drop=True)
    prefecture_df.columns = [
        "prefecture_name",
        "prefecture_id",
        "island_id",
        "country_id",
    ]
    prefecture_df.to_excel(output_dir / "master_prefecture.xlsx", index=False)

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
    commune_df.to_excel(output_dir / "master_commune.xlsx", index=False)
else:
    missing_master_files = [
        output_dir / "master_country.xlsx",
        output_dir / "master_island.xlsx",
        output_dir / "master_prefecture.xlsx",
        output_dir / "master_commune.xlsx",
    ]
    if not all(path.exists() for path in missing_master_files):
        raise FileNotFoundError(
            f"No admin workbook found at {input_file} and some master files are missing in '{output_dir}'."
        )

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

    prefecture_source = pd.read_excel(input_file, sheet_name="com_admin2") if input_file.exists() else pd.read_excel(output_dir / "master_prefecture.xlsx")
    prefecture_source["norm"] = prefecture_source["adm2_name"].apply(normalize_name) if "adm2_name" in prefecture_source.columns else prefecture_source["prefecture_name"].apply(normalize_name)
    pref_map = dict(zip(prefecture_source["norm"], prefecture_source["adm2_pcode"])) if "adm2_pcode" in prefecture_source.columns else dict(zip(prefecture_source["norm"], prefecture_source["prefecture_id"]))

    commune_source = pd.read_excel(input_file, sheet_name="com_admin3") if input_file.exists() else pd.read_excel(output_dir / "master_commune.xlsx")
    commune_source["norm"] = commune_source["adm3_name"].apply(normalize_name) if "adm3_name" in commune_source.columns else commune_source["commune_name"].apply(normalize_name)
    commune_map = dict(zip(commune_source["norm"], commune_source["adm3_pcode"])) if "adm3_pcode" in commune_source.columns else dict(zip(commune_source["norm"], commune_source["commune_id"]))

    local_df["prefecture_name"] = local_df["prefecture"].apply(strip_admin_prefix)
    local_df["commune_name"] = local_df["commune"].apply(strip_admin_prefix)

    prefecture_aliases = {
        "nioumachoua": "KM33",
        "mitsamouli": "KM26",
        "mitsamiouli": "KM26",
        "mboude": "KM26",
        "moya": "KM16",
    }
    local_df["prefecture_id"] = local_df["prefecture_name"].apply(
        lambda x: find_best_match(x, pref_map) or prefecture_aliases.get(normalize_name(x))
    )
    local_df["commune_id"] = local_df["commune_name"].apply(lambda x: find_best_match(x, commune_map))

    local_df["town_village_id"] = ""
    for group_key, group in local_df.groupby(["commune_id", "prefecture_id"], dropna=False):
        base_id = group_key[0] if pd.notna(group_key[0]) else (group_key[1] if pd.notna(group_key[1]) else group["island_id"].iloc[0])
        if pd.isna(base_id):
            local_df.loc[group.index, "town_village_id"] = ""
            continue
        ids = [f"{base_id}_{idx:04d}" for idx in range(1, len(group) + 1)]
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
