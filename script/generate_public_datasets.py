import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw_data"
REMOTE_MASTER_DIR = ROOT / "external" / "comoros-admin-master" / "masters"
LOCAL_MASTER_DIR = ROOT / "masters"
DATASET_DIR = ROOT / "datasets"

YEARS = list(range(2017, 2043))


def resolve_master_file(directory, stem_name):
    for suffix in [".xlsx", ".csv"]:
        candidate = directory / f"{stem_name}{suffix}"
        if candidate.exists():
            return candidate
    return directory / f"{stem_name}.xlsx"


def resolve_master_dir():
    for candidate in [REMOTE_MASTER_DIR, LOCAL_MASTER_DIR]:
        if candidate.exists() and any(
            resolve_master_file(candidate, name).exists()
            for name in [
                "master_country",
                "master_island",
                "master_prefecture",
                "master_commune",
                "master_town_village",
            ]
        ):
            return candidate
    return LOCAL_MASTER_DIR


MASTER_DIR = resolve_master_dir()


def normalize_name(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    for char in ["-", "/", ".", "'", "(", ")", "_", ",", ";", ":", "’", '"']:
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


def read_population_raw():
    raw_path = RAW_DIR / "Revision_des_Projections_demographiques_hypothese_moyenne_3a125e5b6c.xlsx"
    if not raw_path.exists():
        raise FileNotFoundError(f"Required population file not found: {raw_path}")

    raw_df = pd.read_excel(raw_path, sheet_name="Pop îles ajustée")
    clean_df = raw_df.iloc[67:].copy().reset_index(drop=True)
    clean_df.iloc[0, 0] = "cat"
    clean_df.columns = clean_df.iloc[0]
    clean_df = clean_df.iloc[1:].copy().reset_index(drop=True)
    clean_df = clean_df.dropna(subset=["cat"]).reset_index(drop=True)

    records = []
    current_country = ""
    current_island = ""
    current_prefecture = ""
    current_commune = ""

    for _, row in clean_df.iterrows():
        val = str(row["cat"]).strip() if pd.notna(row["cat"]) else ""
        if not val or val == "cat":
            continue

        if val == "Comores":
            current_country = val
        elif val in {"MWALI", "NDZUWANI", "NGAZIDJA"}:
            current_island = val
        elif val.startswith("Préfecture"):
            current_prefecture = val
        elif val.startswith("Commune"):
            current_commune = val
        else:
            row_data = row.to_dict()
            row_data.update(
                {
                    "country": current_country,
                    "island": current_island,
                    "prefecture": current_prefecture,
                    "commune": current_commune,
                    "town_village": val,
                }
            )
            records.append(row_data)

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError("No demographic rows were extracted from the raw source file.")

    df = df.drop(columns=["cat"], errors="ignore")
    geo_cols = ["country", "island", "prefecture", "commune", "town_village"]
    other_cols = [c for c in df.columns if c not in geo_cols]
    df = df[geo_cols + other_cols].copy()
    return df


def ensure_master_files():
    global MASTER_DIR
    MASTER_DIR = resolve_master_dir()
    required = [
        resolve_master_file(MASTER_DIR, "master_country"),
        resolve_master_file(MASTER_DIR, "master_island"),
        resolve_master_file(MASTER_DIR, "master_prefecture"),
        resolve_master_file(MASTER_DIR, "master_commune"),
        resolve_master_file(MASTER_DIR, "master_town_village"),
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing master files: " + ", ".join(missing) + ". Clone or sync the admin master repo under external/comoros-admin-master or regenerate the local masters."
        )


def read_master_table(stem_name):
    path = resolve_master_file(MASTER_DIR, stem_name)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_excel(path)


def load_master_tables():
    ensure_master_files()
    country = read_master_table("master_country")
    island = read_master_table("master_island")
    prefecture = read_master_table("master_prefecture")
    commune = read_master_table("master_commune")
    town = read_master_table("master_town_village")

    country["country_name_norm"] = country["country_name"].apply(normalize_name)
    island["island_name_norm"] = island["island_name_fr"].apply(normalize_name)
    prefecture["prefecture_name_norm"] = prefecture["prefecture_name"].apply(normalize_name)
    commune["commune_name_norm"] = commune["commune_name"].apply(normalize_name)
    town["town_village_name_norm"] = town["town_village_name"].apply(normalize_name)
    return country, island, prefecture, commune, town


def get_population_fact():
    base = read_population_raw()

    def is_year_column(value):
        if pd.isna(value):
            return False
        try:
            num = float(str(value).strip().replace(",", ""))
        except ValueError:
            return False
        return num.is_integer() and 1900 <= num <= 2100

    value_columns = [col for col in base.columns if col not in {"country", "island", "prefecture", "commune", "town_village"} and is_year_column(col)]
    long = base.melt(
        id_vars=["country", "island", "prefecture", "commune", "town_village"],
        value_vars=value_columns,
        var_name="year",
        value_name="population",
    )
    long["year"] = pd.to_numeric(long["year"], errors="coerce").astype("Int64")
    long = long.dropna(subset=["year", "population"]).copy()
    long["country_name"] = long["country"].str.strip()
    long["island_name"] = long["island"].str.strip()
    long["prefecture_name"] = long["prefecture"].str.replace("^Préfecture de ", "", regex=True).str.strip()
    long["commune_name"] = long["commune"].str.replace("^Commune de ", "", regex=True).str.strip()
    long["town_village_name"] = long["town_village"].str.strip()

    country, island, prefecture, commune, town = load_master_tables()

    country_map = dict(zip(country["country_name_norm"], country["country_id"]))
    island_map = dict(zip(island["island_name_norm"], island["island_id"]))
    prefecture_map = dict(zip(prefecture["prefecture_name_norm"], prefecture["prefecture_id"]))
    commune_map = dict(zip(commune["commune_name_norm"], commune["commune_id"]))
    town_map = dict(zip(town["town_village_name_norm"], town["town_village_id"]))

    island_aliases = {
        "mwali": "KM3",
        "moheli": "KM3",
        "ndzuwani": "KM1",
        "anjouan": "KM1",
        "ngazidja": "KM2",
        "grande comore": "KM2",
        "ngazidja grande comore": "KM2",
    }

    long["country_id"] = long["country_name"].apply(lambda x: country_map.get(normalize_name(x)))
    long["island_id"] = long["island_name"].apply(
        lambda x: island_map.get(normalize_name(x)) or island_aliases.get(normalize_name(x))
    )
    long["prefecture_id"] = long["prefecture_name"].apply(
        lambda x: prefecture_map.get(normalize_name(x)) or find_best_match(x, prefecture_map)
    )

    commune_aliases = {
        "moinbassa": "KM323",
        "bambao mtsanga": "KM111",
        "ngadzale": "KM115",
        "mremani": "KM124",
        "shaweni": "KM122",
        "bandrani ya mitsangani": "KM132",
        "bambao ya djou": "KM273",
        "oichili yaboini": "KM283",
        "ngandzale": "KM115",
    }
    long["commune_id"] = long["commune_name"].apply(
        lambda x: commune_map.get(normalize_name(x)) or find_best_match(x, commune_map) or commune_aliases.get(normalize_name(x))
    )
    long["town_village_id"] = long["town_village_name"].apply(lambda x: town_map.get(normalize_name(x)))

    # Fallback aliases for known official variants not present in the generated masters.
    aliases = {
        "nioumachoua": "KM33",
        "mitsamouli": "KM26",
        "mitsamiouli": "KM26",
        "mboude": "KM26",
        "moya": "KM16",
    }
    long["prefecture_id"] = long["prefecture_name"].apply(
        lambda x: (prefecture_map.get(normalize_name(x)) or find_best_match(x, prefecture_map) or aliases.get(normalize_name(x)))
    )

    long["population"] = pd.to_numeric(long["population"], errors="coerce")
    long["population"] = long["population"].round().astype(int)
    long = long.dropna(subset=["population"]).copy()

    fact = long[
        [
            "country_id",
            "country_name",
            "island_id",
            "island_name",
            "prefecture_id",
            "prefecture_name",
            "commune_id",
            "commune_name",
            "town_village_id",
            "town_village_name",
            "year",
            "population",
        ]
    ].copy()
    fact = fact.sort_values(["year", "island_name", "prefecture_name", "commune_name", "town_village_name"]).reset_index(drop=True)
    fact["year"] = fact["year"].astype(int)

    country, island, prefecture, commune, town = load_master_tables()

    fact["country_name_local"] = fact["country_name"]
    fact["island_name_local"] = fact["island_name"]
    fact["prefecture_name_local"] = fact["prefecture_name"]
    fact["commune_name_local"] = fact["commune_name"]
    fact["town_village_name_local"] = fact["town_village_name"]

    country_lookup = dict(zip(country["country_id"], country["country_name"]))
    island_lookup = dict(zip(island["island_id"], island["island_name_fr"]))
    prefecture_lookup = dict(zip(prefecture["prefecture_id"], prefecture["prefecture_name"]))
    commune_lookup = dict(zip(commune["commune_id"], commune["commune_name"]))
    town_lookup = dict(zip(town["town_village_id"], town["town_village_name"]))

    fact["country_name"] = fact["country_id"].map(country_lookup).fillna(fact["country_name"])
    fact["island_name"] = fact["island_id"].map(island_lookup).fillna(fact["island_name"])
    fact["prefecture_name"] = fact["prefecture_id"].map(prefecture_lookup).fillna(fact["prefecture_name"])
    fact["commune_name"] = fact["commune_id"].map(commune_lookup).fillna(fact["commune_name"])
    fact["town_village_name"] = fact["town_village_id"].map(town_lookup).fillna(fact["town_village_name"])

    return fact


def write_csv(df, filename):
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATASET_DIR / filename
    df.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")


def build_public_datasets():
    fact = get_population_fact()
    fact["population"] = fact["population"].round().astype(int)

    local_fact = fact.copy()
    local_fact = local_fact[
        [
            "country_id",
            "country_name_local",
            "island_id",
            "island_name_local",
            "prefecture_id",
            "prefecture_name_local",
            "commune_id",
            "commune_name_local",
            "town_village_id",
            "town_village_name_local",
            "year",
            "population",
        ]
    ].copy()
    local_fact = local_fact.rename(
        columns={
            "country_name_local": "country_name",
            "island_name_local": "island_name",
            "prefecture_name_local": "prefecture_name",
            "commune_name_local": "commune_name",
            "town_village_name_local": "town_village_name",
        }
    )

    # Main fact table uses canonical names from the master tables.
    write_csv(fact, "population_fact.csv")
    write_csv(local_fact, "population_fact_local.csv")

    island_df = (
        fact.groupby(["country_id", "island_id", "island_name", "year"], as_index=False)["population"].sum()
    )
    island_df["population"] = island_df["population"].round().astype(int)
    write_csv(island_df, "population_by_island.csv")

    prefecture_df = (
        fact.groupby(["country_id", "island_id", "prefecture_id", "prefecture_name", "year"], as_index=False)["population"].sum()
    )
    prefecture_df["population"] = prefecture_df["population"].round().astype(int)
    write_csv(prefecture_df, "population_by_prefecture.csv")

    commune_df = (
        fact.groupby(["country_id", "island_id", "prefecture_id", "prefecture_name", "commune_id", "commune_name", "year"], as_index=False)["population"].sum()
    )
    commune_df["population"] = commune_df["population"].round().astype(int)
    write_csv(commune_df, "population_by_commune.csv")

    town_df = (
        fact.groupby(["country_id", "island_id", "prefecture_id", "prefecture_name", "commune_id", "commune_name", "town_village_id", "town_village_name", "year"], as_index=False)["population"].sum()
    )
    town_df["population"] = town_df["population"].round().astype(int)
    write_csv(town_df, "population_by_town_village.csv")

    # Also export the master reference tables in public CSV form.
    for stem_name in [
        "master_country",
        "master_island",
        "master_prefecture",
        "master_commune",
        "master_town_village",
    ]:
        df = read_master_table(stem_name)
        write_csv(df, f"{stem_name}.csv")


if __name__ == "__main__":
    build_public_datasets()
    print("Public datasets created successfully in datasets/")
