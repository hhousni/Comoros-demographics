"""Published totals (sums of villages) against INSEED's own total rows.

Gaps up to the rounding of the villages are fine. Two inconsistencies of the source are known and
kept on purpose (owner's decision, 2026-10-30): published figures stay the sum of villages.
Any other gap, or a change in these two, fails the test.
"""
import importlib.util
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("generate", ROOT / "script" / "generate_public_datasets.py")
generate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate)

ISLANDS = {"MWALI": "KM3", "NDZUWANI": "KM1", "NGAZIDJA": "KM2"}

# published minus source, in persons, for the commune rows of the INSEED sheet that are not the
# sum of their villages
KNOWN_SOURCE_GAPS = {
    # Commune de SIMA (KM152), 2018-2029: the commune row grows much faster than its villages,
    # then drops back in 2030
    ("KM152", 2018): -186, ("KM152", 2019): -383, ("KM152", 2020): -588, ("KM152", 2021): -802,
    ("KM152", 2022): -1024, ("KM152", 2023): -1250, ("KM152", 2024): -1484, ("KM152", 2025): -1725,
    ("KM152", 2026): -1972, ("KM152", 2027): -2224, ("KM152", 2028): -2481, ("KM152", 2029): -2744,
    # Commune de NGADZALE (KM115), 2040-2042: the commune row is 100 above its villages
    ("KM115", 2040): -100, ("KM115", 2041): -100, ("KM115", 2042): -100,
}


def strip_commune(label):
    return re.sub(r"^Commune( de)? ", "", str(label)).strip()


def comparison():
    fact = pd.read_csv(ROOT / "datasets" / "population_fact.csv", dtype={"year": int})
    commune_ids = {strip_commune(n): i for n, i in zip(fact.commune_name_local, fact.commune_id)}

    source = generate.read_source_totals()
    source["id"] = [
        "KM" if level == "country" else ISLANDS[label] if level == "island" else commune_ids.get(strip_commune(label))
        for level, label in zip(source.level, source.label)
    ]
    assert source.id.notna().all(), source[source.id.isna()].label.unique()

    published, villages = [], {}
    for level, col in [("country", "country_id"), ("island", "island_id"), ("commune", "commune_id")]:
        sums = fact.groupby([col, "year"]).population.sum().rename("published").reset_index()
        published.append(sums.rename(columns={col: "id"}).assign(level=level))
        villages.update(fact.groupby(col).town_village_id.nunique().to_dict())
    merged = source.merge(pd.concat(published), on=["level", "id", "year"], how="outer", validate="1:1")
    assert merged.notna().all().all(), "units or years present on one side only"

    merged["gap"] = merged.published - merged.population
    merged["known"] = [
        sum(g for (c, y), g in KNOWN_SOURCE_GAPS.items() if y == year and c.startswith(unit))
        for unit, year in zip(merged.id, merged.year)
    ]
    # each published village is rounded to the person, so a total can move by half a person per village
    merged["tolerance"] = merged.id.map(villages) * 0.5 + 1
    return merged


def test_published_totals_match_source_except_known_gaps():
    m = comparison()
    off = m[(m.gap - m.known).abs() > m.tolerance]
    assert off.empty, off[["level", "id", "year", "population", "published", "gap", "known"]].to_string()


def test_known_gaps_are_still_there():
    """If INSEED publishes a corrected file, this fails: then remove the gaps from the list and the README."""
    m = comparison().set_index(["id", "year"])
    for key, gap in KNOWN_SOURCE_GAPS.items():
        assert abs(m.loc[key, "gap"] - gap) <= 1, key
