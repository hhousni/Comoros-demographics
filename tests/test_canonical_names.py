import pandas as pd


fact = pd.read_csv('datasets/population_fact.csv')

assert 'prefecture_name_local' in fact.columns
assert 'commune_name_local' in fact.columns
assert 'town_village_name_local' in fact.columns
assert 'Fomboni' in set(fact['prefecture_name'].astype(str))
assert 'KM32' in set(fact['prefecture_id'].astype(str))
