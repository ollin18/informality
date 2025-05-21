"""
This file estimates the informality rate by
"""
import os

import geopandas as gpd
import hydra
import pandas as pd
from omegaconf import DictConfig


@hydra.main(
    config_path="../../../config/MX/process",
    config_name="homeplace_informality",
    version_base=None,
)
def main(config: DictConfig) -> None:
    dtype_mapping = {
        "str": str,
        "int": "Int64",  # Use Pandas nullable integer type
        "float": float,
    }
    dtype_dict = {
        col: dtype_mapping[dt] for col, dt in config.read_census.dtypes.items()
    }

    ents = ["09", "15"]
    df_list = []
    mzn_list = []
    for ent in ents:
        for types in ["A", "AR"]:
            # Construct the directory paths
            csv_directory = config.data.csv
            shp_directory = config.data.shp

            # Read the CSV file
            csv_file = os.path.join(
                csv_directory, f"conjunto_de_datos_ageb_urbana_{ent}_cpv2020.csv"
            )
            #  df = pd.read_csv(csv_file)
            df = pd.read_csv(
                csv_file,
                usecols=config.read_census.columns,
                dtype=dtype_dict,
                na_values=["*", "N/D"],
                keep_default_na=True,
            )
            df_list.append(df)

            # Read the shapefile
            shp_file = os.path.join(shp_directory, f"2020_1_{ent}_{types}.shp")
            mzn = gpd.read_file(shp_file)
            mzn_list.append(mzn)

    # Concatenate all DataFrames
    dem = pd.concat(df_list, ignore_index=True)
    mzn = gpd.GeoDataFrame(pd.concat(mzn_list, ignore_index=True))
    mzn["CVEGEO"] = mzn["CVE_ENT"] + mzn["CVE_MUN"] + mzn["CVE_LOC"] + mzn["CVE_AGEB"]

    homes = pd.read_csv(
        os.path.join(config.data.mobility, "home_work_locations_by_counts.csv")
    )
    homes = gpd.GeoDataFrame(
        homes,
        geometry=gpd.points_from_xy(homes.cluster_longitude, homes.cluster_latitude),
    )

    homes.set_crs(epsg=4326, inplace=True)
    mzn.to_crs(epsg=4326, inplace=True)

    mzn_filtered_09 = mzn[mzn["CVE_ENT"] == "09"]
    mzn_filtered_15 = mzn[mzn["CVE_ENT"] == "15"]
    points_within_polygons = gpd.sjoin(homes, mzn_filtered_15, predicate="within")
    polygons_with_points = mzn_filtered_15[
        mzn_filtered_15.index.isin(points_within_polygons.index_right.unique())
    ]
    mzn_filtered = pd.concat([mzn_filtered_09, polygons_with_points])

    dem["CVEGEO"] = dem["ENTIDAD"] + dem["MUN"] + dem["LOC"] + dem["AGEB"]
    dem = dem.loc[dem["NOM_LOC"] == "Total AGEB urbana"]
    dem = dem.drop_duplicates(subset=["CVEGEO"], keep="last")
    dem = dem.drop(columns=["NOM_LOC"])
    dem = dem.drop(columns=["ENTIDAD", "MUN", "LOC", "AGEB", "MZA"])
    print(list(dem.columns))
    dem = dem.fillna(0).groupby("CVEGEO").sum().astype(int).reset_index()
    mzn = pd.merge(mzn_filtered, dem, on="CVEGEO", how="left")

    mzn.to_file(
        os.path.join(config.data.staging, "ageb_cdmx_edomex.geojson"), driver="GeoJSON"
    )


if __name__ == "__main__":
    main()
