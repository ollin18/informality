#!/usr/bin/env python
"""
This file downloads the requiered data from INEGI
"""

import os

import pandas as pd
from omegaconf import DictConfig


def read_file(config: DictConfig) -> pd.DataFrame:
    columns = config.read_census.columns
    dtypes = dict(config.read_census.dtypes)

    # Function to coerce non-numeric values
    def coerce_numeric(x):
        return pd.to_numeric(x, errors="coerce")

    # Create a dictionary for converters
    converters = {col: coerce_numeric for col in columns if col not in dtypes}

    df = pd.read_csv(
        os.path.join(config.data.csv, config.country, config.urls.file_state),
        usecols=columns,
        dtype=dtypes,
        converters=converters,
    )

    df = df.assign(
        CVEGEO=df["ENTIDAD"] + df["MUN"] + df["LOC"] + df["AGEB"] + df["MZA"]
    )

    return df
