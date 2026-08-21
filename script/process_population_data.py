# This script aims to process the data from the INSEED website
import pandas as pd


# read the data
raw_df = pd.read_excel("raw_data/Revision_des_Projections_demographiques_hypothese_moyenne_3a125e5b6c.xlsx", sheet_name= "Pop îles ajustée")

# clean the data 

# 1. Create a clean, independent copy
clean_df = raw_df.iloc[67:].copy().reset_index(drop=True)

# 2. Now you can assign values freely without warnings
clean_df.iloc[0, 0] = "cat"
clean_df.columns = clean_df.iloc[0]
clean_df = clean_df.iloc[1:].copy().reset_index(drop=True)

clean_df = clean_df.dropna(subset=['cat']).reset_index(drop=True)




# Known island names in Comoros to track island level changes
ISLANDS = {"MWALI", "NDZUWANI", "NGAZIDJA"}

records = []
current_country = ""
current_island = ""
current_prefecture = ""
current_commune = ""

# Loop row by row through your existing DataFrame
for index, row in clean_df.iterrows():
    # Clean the string value in column 'cat'
    val = str(row["cat"]).strip() if pd.notna(row["cat"]) else ""

    # Skip empty lines or header strings
    if not val or val == "cat":
        continue

    # 1. Update Country (and skip adding this aggregate row)
    if val == "Comores":
        current_country = val

    # 2. Update Island (and skip adding this aggregate row)
    elif val in ISLANDS:
        current_island = val

    # 3. Update Prefecture (and skip adding this aggregate row)
    elif val.startswith("Préfecture"):
        current_prefecture = val

    # 4. Update Commune (and skip adding this aggregate row)
    elif val.startswith("Commune"):
        current_commune = val

    # 5. Granular Locality / Town / Village Level
    else:
        # Extract all existing columns from the original row
        row_data = row.to_dict()

        # Append the parsed geographic hierarchy
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

# Create the final DataFrame
final_df = pd.DataFrame(records)

# Reset index to ensure a clean sequential DataFrame
final_df = final_df.reset_index(drop=True)

final_df = final_df.drop(columns=["cat"])

# 1. Define the desired order for the geography columns
geo_cols = ["country", "island", "prefecture", "commune", "town_village"]

# 2. Get all remaining columns (excluding the geo columns)
other_cols = [c for c in final_df.columns if c not in geo_cols]

# 3. Reorder the DataFrame
final_df = final_df[geo_cols + other_cols]



# read the fie withe the coordinates
df = pd.read_excel("raw_data/unique_ville_village_normalized 2.xlsx")


import time
import pandas as pd
import requests

# ---------------------------------------------------------
# 1. Promote first row as column header and drop it
# ---------------------------------------------------------
df.columns = df.iloc[0]
df = df.iloc[1:].copy().reset_index(drop=True)

# ---------------------------------------------------------
# 2. Extract original Latitude and Longitude
#    Format: "-12.159535864520512, 44.41248741807966"
# ---------------------------------------------------------
coords = df["Latitude and longitude"].astype(str).str.split(",", expand=True)
df["lat_orig"] = pd.to_numeric(coords[0].str.strip(), errors="coerce")
df["lon_orig"] = pd.to_numeric(coords[1].str.strip(), errors="coerce")


# ---------------------------------------------------------
# 3. Fetch coordinates from OpenStreetMap using osm_id
# ---------------------------------------------------------
def get_coords_by_osm_id(osm_id):
    if pd.isna(osm_id) or not str(osm_id).strip():
        return None, None

    clean_id = str(osm_id).strip().split(".")[0]  # Remove trailing float decimals if any

    # Query Nominatim API by OSM ID (N = Node)
    url = f"https://nominatim.openstreetmap.org/lookup?osm_ids=N{clean_id}&format=json"
    headers = {"User-Agent": "comoros_osm_lookup"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return float(data["lat"]), float(data["lon"])
    except Exception:
        pass

    return None, None


# Fetch OSM coordinates (with a small delay to respect API limits)
lat_osm_list = []
lon_osm_list = []

for osm_id in df["osm_id"]:
    lat, lon = get_coords_by_osm_id(osm_id)
    lat_osm_list.append(lat)
    lon_osm_list.append(lon)
    time.sleep(1)  # 1-second delay for Nominatim API policy

df["lat_osm"] = lat_osm_list
df["lon_osm"] = lon_osm_list

# ---------------------------------------------------------
# 4. Create final coordinates (OSM priority, fallback to original)
# ---------------------------------------------------------
df["Latitude_final"] = df["lat_osm"].combine_first(df["lat_orig"])
df["Longitude_final"] = df["lon_osm"].combine_first(df["lon_orig"])

# Clean up temporary working columns
df = df.drop(columns=["lat_orig", "lon_orig", "lat_osm", "lon_osm"])
df = df[["ville_village", "Latitude_final", "Longitude_final"]]

final_df = final_df.merge(
    df[["ville_village", "Latitude_final", "Longitude_final"]],
    left_on="town_village",
    right_on="ville_village",
    how="left",
)
final_df.to_excel("clean_data/comoros_administrative_clean.xlsx", index=False)
