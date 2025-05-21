import os

import geopandas as gpd
import hydra
import numpy as np
import pandas as pd
from ecomplexity import ecomplexity
from omegaconf import DictConfig


@hydra.main(
    config_path="../../../config/MX/process",
    config_name="homeplace_informality",
    version_base=None,
)
def main(config: DictConfig) -> None:
    mzn = gpd.read_file(
        os.path.join(config.data.staging, "ageb_cdmx_edomex_informality.geojson")
    )
    denue_list = []
    for ent in ["09", "15"]:
        df = pd.read_csv(
            os.path.join(config.data.csv, f"denue_inegi_{ent}_.csv"), encoding="latin-1"
        )
        denue_list.append(df)

    denue = pd.concat(denue_list, ignore_index=True)
    denue = denue.rename(
        columns={
            "cve_mun": "mun",
            "cve_ent": "ent",
            "cve_loc": "loc",
            "Manzana": "manzana",
            "Ageb": "ageb",
            "per_ocu": "emple7c",
            "scian_label": "scian",
        }
    )

    denue_gdf = gpd.GeoDataFrame(
        denue,
        geometry=gpd.points_from_xy(denue["longitud"], denue["latitud"]),
        crs=mzn.crs,  # Ensure the coordinate reference system matches `mzn`
    )

    result = gpd.sjoin(
        denue_gdf, mzn[["CVEGEO", "geometry"]], how="left", predicate="within"
    )

    denue["CVEGEO"] = result["CVEGEO"]
    denue["naics"] = (
        denue["codigo_act"]
        .astype(str)
        .apply(lambda x: x[:4] if x.startswith("5417") else x[:2])
        .replace(config.naics_to_desc)
    )
    denue = denue.loc[denue["CVEGEO"].isin(mzn["CVEGEO"])]

    # Function to generate a random number based on the 'emple7c' column
    def generate_random_personas(row):
        if " a " in row:
            # Extract the range and generate random number within the range
            lower, upper = map(int, row.replace(" personas", "").split(" a "))
            if lower == 0:
                lower = 1
            return np.random.randint(lower, upper)
        elif "251" in row:
            # For 'y más' case, generate random number between 251 and 500
            return np.random.randint(251, 500)

    # Apply the function to create a new column
    denue["workers"] = denue["emple7c"].apply(generate_random_personas)
    denue = denue.loc[denue["naics"] != "Agriculture"]

    location_sector_matrix = pd.pivot_table(
        denue,
        values="workers",
        index="CVEGEO",
        columns="naics",
        aggfunc="sum",
        fill_value=0,
    )
    workers_df = location_sector_matrix.reset_index().melt(
        id_vars=["CVEGEO"], var_name="naics", value_name="workers"
    )
    workers_df["year"] = 2024
    trade_cols = {"time": "year", "loc": "CVEGEO", "prod": "naics", "val": "workers"}
    cdata = ecomplexity(workers_df, trade_cols)
    eci = cdata[["CVEGEO", "eci"]].drop_duplicates().reset_index(drop=True)
    mzn = pd.merge(mzn, eci, on="CVEGEO", how="left")
    bins = [-float("inf"), 0, np.median(mzn.loc[mzn["eci"] > 0]["eci"]), float("inf")]
    labels = ["Low", "Medium", "High"]

    # Segment using pd.cut
    mzn["eci_level"] = pd.cut(mzn["eci"], bins=bins, labels=labels)
    mzn = mzn[
        [
            "CVEGEO",
            "POBTOT",
            "PEA",
            "informalidad",
            "informality_level",
            "eci",
            "eci_level",
            "geometry",
        ]
    ].rename(
        columns={
            "CVEGEO": "geomid",
            "POBTOT": "population",
            "PEA": "workers",
            "informalidad": "informality_rate",
        }
    )

    mzn.to_file(
        os.path.join(config.data.clean, "map_informality_eci.geojson"), driver="GeoJSON"
    )


if __name__ == "__main__":
    main()
