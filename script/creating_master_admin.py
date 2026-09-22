from pathlib import Path
import re
import unicodedata

import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


ISLAND_CODE_MAP = {
    "MWALI": "KM3",
    "NDZUWANI": "KM1",
    "NGAZIDJA": "KM2",
}

PREFECTURE_ALIASES = {
    "mboude": "Mitsamiouli-Mboudé",
    "mitsamiouli": "Mitsamiouli-Mboudé",
    "moya": "Sima",
    "nioumachoua": "Nioumachioi",
}

COMMUNE_ALIASES = {
    "bambao mstanga": "Bambao Mtsanga",
    "bandrani ya mitsangani": "Bandrani Ya Mtsangani",
    "bambao ya djou": "Bambao Yadjou",
    "moinbassa": "Moimbassa",
    "ngadzale": "Ngandzalé",
    "oichili yaboini": "Oichili Yamboini",
    "shaweni": "Chaweni",
}


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
    lookup = df[[key] + columns].dropna(subset=[key]).copy()
    conflicting_keys = lookup.groupby(key, dropna=False).apply(
        lambda group: len(group[columns].drop_duplicates()) > 1
    )
    if conflicting_keys.any():
        raise ValueError(f"Duplicate values found for {key} in admin lookup data")
    return lookup.drop_duplicates(subset=[key]).copy()


def format_master_workbook(path):
    workbook = load_workbook(path)
    worksheet = workbook.active
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for column_index, column_cells in enumerate(worksheet.iter_cols(), start=1):
        values = [cell.value for cell in column_cells if cell.value is not None]
        if not values:
            continue
        max_length = max(len(str(value)) for value in values)
        worksheet.column_dimensions[get_column_letter(column_index)].width = min(
            max_length + 2, 40
        )

    workbook.save(path)


def format_existing_master_workbooks(output_dir):
    for workbook_path in sorted(output_dir.glob("master_*.xlsx")):
        format_master_workbook(workbook_path)


def load_admin_frames(project_root, input_file):
    if input_file.exists():
        country_df = pd.read_excel(input_file, sheet_name="com_admin0")[
            ["adm0_name", "adm0_pcode"]
        ].drop_duplicates().reset_index(drop=True)
        country_df.columns = ["country_name", "country_id"]

        island_df = pd.read_excel(input_file, sheet_name="com_admin1")[
            ["adm1_name", "adm1_pcode", "adm0_pcode"]
        ].drop_duplicates().reset_index(drop=True)
        parsed = island_df["adm1_name"].apply(split_localized_name)
        island_df[["island_name_fr", "island_name_local"]] = pd.DataFrame(
            parsed.tolist(), index=island_df.index
        )
        island_df = island_df[["adm0_pcode", "adm1_pcode", "island_name_fr", "island_name_local"]]
        island_df.columns = ["country_id", "island_id", "island_name_fr", "island_name_local"]

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
        return country_df, island_df, prefecture_df, commune_df

    country_path = project_root / "masters" / "master_country.xlsx"
    island_path = project_root / "masters" / "master_island.xlsx"
    prefecture_path = project_root / "masters" / "master_prefecture.xlsx"
    commune_path = project_root / "masters" / "master_commune.xlsx"
    missing_files = [
        str(path)
        for path in [country_path, island_path, prefecture_path, commune_path]
        if not path.exists()
    ]
    if missing_files:
        raise FileNotFoundError(
            "Missing admin lookup workbook(s): " + ", ".join(missing_files)
        )

    return (
        pd.read_excel(country_path),
        pd.read_excel(island_path),
        pd.read_excel(prefecture_path),
        pd.read_excel(commune_path),
    )


def load_clean_localities(clean_input):
    if not clean_input.exists():
        return None

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
    return local_df.rename(columns={"town_village": "town_village_name"})


def add_lookup_normalization(prefecture_df, commune_df):
    prefecture_lookup = prefecture_df.copy()
    commune_lookup = commune_df.copy()
    prefecture_lookup["norm"] = prefecture_lookup["prefecture_name"].apply(normalize_name)
    commune_lookup["norm"] = commune_lookup["commune_name"].apply(normalize_name)
    return prefecture_lookup, commune_lookup


def normalize_locality_admin_names(local_df):
    normalized_df = local_df.copy()
    normalized_df["country_id"] = "KM"
    normalized_df["island_id"] = normalized_df["island"].map(ISLAND_CODE_MAP)
    normalized_df["prefecture_name"] = normalized_df["prefecture"].apply(
        lambda value: clean_admin_name(value, "prefecture")
    )
    normalized_df["commune_name"] = normalized_df["commune"].apply(
        lambda value: clean_admin_name(value, "commune")
    )
    normalized_df["prefecture_name"] = apply_aliases(
        normalized_df["prefecture_name"], PREFECTURE_ALIASES
    )
    normalized_df["commune_name"] = apply_aliases(
        normalized_df["commune_name"], COMMUNE_ALIASES
    )
    return normalized_df


def reconcile_admin_ids(local_df, prefecture_df, commune_df):
    reconciled_df = normalize_locality_admin_names(local_df)
    prefecture_lookup, commune_lookup = add_lookup_normalization(prefecture_df, commune_df)
    pref_map = dict(zip(prefecture_lookup["norm"], prefecture_lookup["prefecture_id"]))
    commune_map = dict(zip(commune_lookup["norm"], commune_lookup["commune_id"]))

    reconciled_df["prefecture_id"] = reconciled_df["prefecture_name"].apply(
        lambda value: pref_map.get(normalize_name(value))
    )
    reconciled_df["commune_id"] = reconciled_df["commune_name"].apply(
        lambda value: commune_map.get(normalize_name(value))
    )

    commune_id_lookup = unique_lookup(
        commune_lookup,
        "commune_id",
        ["prefecture_id", "island_id", "country_id"],
    )
    reconciled_df = reconciled_df.merge(
        commune_id_lookup,
        on="commune_id",
        how="left",
        suffixes=("", "_from_commune"),
    )
    reconciled_df["prefecture_id"] = reconciled_df["prefecture_id_from_commune"].combine_first(
        reconciled_df["prefecture_id"]
    )
    reconciled_df["island_id"] = reconciled_df["island_id_from_commune"].combine_first(
        reconciled_df["island_id"]
    )
    reconciled_df["country_id"] = reconciled_df["country_id_from_commune"].combine_first(
        reconciled_df["country_id"]
    )
    reconciled_df = reconciled_df.drop(
        columns=["prefecture_id_from_commune", "island_id_from_commune", "country_id_from_commune"]
    )

    prefecture_id_lookup = unique_lookup(
        prefecture_lookup,
        "prefecture_id",
        ["island_id", "country_id"],
    )
    reconciled_df = reconciled_df.merge(
        prefecture_id_lookup,
        on="prefecture_id",
        how="left",
        suffixes=("", "_from_prefecture"),
    )
    reconciled_df["island_id"] = reconciled_df["island_id_from_prefecture"].combine_first(
        reconciled_df["island_id"]
    )
    reconciled_df["country_id"] = reconciled_df["country_id_from_prefecture"].combine_first(
        reconciled_df["country_id"]
    )
    return reconciled_df.drop(columns=["island_id_from_prefecture", "country_id_from_prefecture"])


def build_town_master(local_df):
    deduplicated_df = local_df.drop_duplicates(
        subset=[
            "country_id",
            "island_id",
            "prefecture_id",
            "commune_id",
            "town_village_name",
            "Latitude_final",
            "Longitude_final",
        ]
    ).reset_index(drop=True)

    deduplicated_df["town_village_id"] = ""
    for commune_id, group in deduplicated_df.groupby("commune_id", dropna=False):
        if pd.isna(commune_id):
            deduplicated_df.loc[group.index, "town_village_id"] = ""
            continue
        ids = [f"{commune_id}_{idx:04d}" for idx in range(1, len(group) + 1)]
        deduplicated_df.loc[group.index, "town_village_id"] = ids

    town_master = deduplicated_df[
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
    return town_master


def filter_admin_frames_to_used_ids(country_df, island_df, prefecture_df, commune_df, town_master):
    used_country_ids = set(town_master["country_id"].dropna())
    used_island_ids = set(town_master["island_id"].dropna())
    used_prefecture_ids = set(town_master["prefecture_id"].dropna())
    used_commune_ids = set(town_master["commune_id"].dropna())

    return (
        country_df[country_df["country_id"].isin(used_country_ids)].reset_index(drop=True),
        island_df[island_df["island_id"].isin(used_island_ids)].reset_index(drop=True),
        prefecture_df[prefecture_df["prefecture_id"].isin(used_prefecture_ids)].reset_index(drop=True),
        commune_df[commune_df["commune_id"].isin(used_commune_ids)].reset_index(drop=True),
    )


def validate_master_quality(country_df, island_df, prefecture_df, commune_df, town_master):
    missing_counts = {
        "prefecture_id": int(town_master["prefecture_id"].isna().sum()),
        "commune_id": int(town_master["commune_id"].isna().sum()),
        "town_village_id": int(town_master["town_village_id"].fillna("").eq("").sum()),
    }
    unexpected_missing = {key: value for key, value in missing_counts.items() if value > 0}
    if unexpected_missing:
        raise ValueError(f"Incomplete town master IDs detected: {unexpected_missing}")

    duplicate_count = int(
        town_master.duplicated(
            ["island_id", "prefecture_id", "commune_id", "town_village_name", "latitude", "longitude"]
        ).sum()
    )
    if duplicate_count > 0:
        raise ValueError(f"Duplicate town master rows detected: {duplicate_count}")

    if set(town_master["country_id"].dropna()) - set(country_df["country_id"]):
        raise ValueError("Town master references country IDs missing from master_country.xlsx")
    if set(town_master["island_id"].dropna()) - set(island_df["island_id"]):
        raise ValueError("Town master references island IDs missing from master_island.xlsx")
    if set(town_master["prefecture_id"].dropna()) - set(prefecture_df["prefecture_id"]):
        raise ValueError("Town master references prefecture IDs missing from master_prefecture.xlsx")
    if set(town_master["commune_id"].dropna()) - set(commune_df["commune_id"]):
        raise ValueError("Town master references commune IDs missing from master_commune.xlsx")


def save_master_frames(output_dir, country_df, island_df, prefecture_df, commune_df, town_master=None):
    country_df.to_excel(output_dir / "master_country.xlsx", index=False)
    island_df.to_excel(output_dir / "master_island.xlsx", index=False)
    prefecture_df.to_excel(output_dir / "master_prefecture.xlsx", index=False)
    commune_df.to_excel(output_dir / "master_commune.xlsx", index=False)
    if town_master is not None:
        town_master.to_excel(output_dir / "master_town_village.xlsx", index=False)


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_file = project_root / "raw_data" / "com_admin_boundaries.xlsx"
    clean_input = project_root / "clean_data" / "comoros_administrative_clean.xlsx"
    output_dir = project_root / "masters"
    output_dir.mkdir(parents=True, exist_ok=True)

    country_df, island_df, prefecture_df, commune_df = load_admin_frames(project_root, input_file)
    town_master = None

    local_df = load_clean_localities(clean_input)
    if local_df is not None:
        reconciled_localities = reconcile_admin_ids(local_df, prefecture_df, commune_df)
        town_master = build_town_master(reconciled_localities)
        country_df, island_df, prefecture_df, commune_df = filter_admin_frames_to_used_ids(
            country_df, island_df, prefecture_df, commune_df, town_master
        )
        validate_master_quality(country_df, island_df, prefecture_df, commune_df, town_master)

    save_master_frames(output_dir, country_df, island_df, prefecture_df, commune_df, town_master)
    format_existing_master_workbooks(output_dir)

    print("Official admin masters created successfully in 'masters/' :")
    print("1. master_country.xlsx")
    print("2. master_island.xlsx")
    print("3. master_prefecture.xlsx")
    print("4. master_commune.xlsx")
    print("5. master_town_village.xlsx")


if __name__ == "__main__":
    main()
