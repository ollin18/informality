"""
This file estimates the informality rate by
"""

import os

import geopandas as gpd
import hydra
import numpy as np
import pandas as pd
from omegaconf import DictConfig


@hydra.main(
    config_path="../../../config/MX/process",
    config_name="homeplace_informality",
    version_base=None,
)
def main(config: DictConfig) -> None:
    mzn = gpd.read_file(os.path.join(config.data.staging, "ageb_cdmx_edomex.geojson"))
    print(mzn["POBTOT"].sum())
    dem = mzn.copy()
    #  dem = dem.dropna(subset="PEA")
    dem["P_MEN12"] = dem["POBTOT"] - dem["P_12YMAS"]

    all_insured = dem.loc[(dem["PDER_SS"] == dem["POBTOT"])].copy()
    all_insured["formal"] = all_insured["POCUPADA"]

    no_inhab = dem.loc[dem.PROM_OCUP.isna()].copy()
    no_inhab["formal"] = no_inhab[["POCUPADA", "PDER_SS"]].min(axis=1)

    all_insured = pd.concat([all_insured, no_inhab])
    to_find = dem.iloc[~(dem.index.isin(all_insured.index))].copy()

    more_child = to_find.loc[to_find["P_MEN12"] >= to_find["PDER_SS"]]
    more_child["formal"] = more_child["POCUPADA"] * (
        (more_child["PDER_SS"]) / (to_find["POBTOT"])
    )

    less_child = to_find.loc[to_find["P_MEN12"] < to_find["PDER_SS"]]
    less_child["formal"] = less_child["POCUPADA"] * (
        (less_child["PDER_SS"] - less_child["P_MEN12"]) / (less_child["POBTOT"])
    )

    #  to_find = pd.concat([more_child,less_child])
    #  dem = pd.concat([all_insured, to_find])

    # Reset indices before concatenation to ensure no duplicates
    all_insured = all_insured.reset_index(drop=True)
    more_child = more_child.reset_index(drop=True)
    less_child = less_child.reset_index(drop=True)
    dem = pd.concat([all_insured, more_child, less_child], ignore_index=True)

    dem["formal_rate"] = dem["formal"] / dem["POCUPADA"]

    dem["formal_rate"].replace([-np.inf], 0, inplace=True)
    dem["formal_rate"].replace([np.inf], 0, inplace=True)

    dem["informalidad"] = dem["formal_rate"]
    dem.loc[dem["formal_rate"] > 0, "informalidad"] = 1 - dem["formal_rate"]

    dem["informality_level"] = pd.qcut(
        dem["informalidad"], [0, 0.3, 0.7, 1], labels=["Low", "Medium", "High"]
    )
    print(dem["POBTOT"].sum())
    dem.to_file(
        os.path.join(config.data.staging, "ageb_cdmx_edomex_informality.geojson"),
        driver="GeoJSON",
    )


if __name__ == "__main__":
    main()
