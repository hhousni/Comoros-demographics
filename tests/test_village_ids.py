from pathlib import Path

import pandas as pd

DATASETS = Path(__file__).resolve().parent.parent / "datasets"


def load_fact():
    return pd.read_csv(DATASETS / "population_fact.csv")


def test_each_raw_village_has_its_own_id():
    fact = load_fact()
    per_year = fact.groupby("year")["town_village_id"].nunique()
    rows_per_year = fact.groupby("year").size()
    assert (per_year == rows_per_year).all()


def test_town_village_id_year_is_unique():
    fact = load_fact()
    assert not fact.duplicated(["town_village_id", "year"]).any()


def test_town_village_id_belongs_to_its_commune():
    fact = load_fact()
    ok = [tv.startswith(f"{c}_") for tv, c in zip(fact["town_village_id"], fact["commune_id"])]
    assert all(ok)


def test_town_village_ids_exist_in_master():
    fact = load_fact()
    master = pd.read_csv(DATASETS / "master_town_village.csv")
    assert set(fact["town_village_id"]) <= set(master["town_village_id"])
