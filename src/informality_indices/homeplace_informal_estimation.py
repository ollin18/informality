#!/usr/bin/env python
"""
This file downloads the requiered data from the Census 2020 including the
geometries
"""

import hydra
import numpy as np
from informality_aux import read_file
from omegaconf import DictConfig


@hydra.main(
    config_path="../../config/process",
    config_name="homeplace_informality",
    version_base=None,
)
def main(config: DictConfig) -> None:
    # Data download
    df = read_file(config)

    # Compute population that are less than 12 yo
    df["P_MEN12"] = df["POBTOT"] - df["P_12YMAS"]

    # Estimate dependants
    df["dependientes"] = df["PDESOCUP"] + df["P_MEN12"]

    # Estimate formal employers by removing younger than 12yo, and the ocupied
    # population
    df["formal"] = df["PDER_SS"] - df["P_MEN12"] - (df["P_12YMAS"] - df["POCUPADA"])
    #
    df["formal"].replace([-np.inf], 0, inplace=True)


if __name__ == "__main__":
    main()
