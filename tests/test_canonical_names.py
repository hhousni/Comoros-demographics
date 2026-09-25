import pandas as pd


def test_population_fact_has_expected_fields():
    fact = pd.read_csv('datasets/population_fact.csv')

    assert 'prefecture_name_local' in fact.columns
    assert 'commune_name_local' in fact.columns
    assert 'town_village_name_local' in fact.columns
    assert 'Fomboni' in set(fact['prefecture_name'].astype(str))
    assert 'KM32' in set(fact['prefecture_id'].astype(str))


def test_population_national_serie_is_country_level():
    country_series = pd.read_csv('datasets/population_serie_longue.csv')

    assert list(country_series.columns) == ['country_id', 'country_name', 'year', 'population']
    assert set(country_series['country_id']) == {'KM'}
    assert country_series['year'].nunique() == 26
    assert len(country_series) == 26
