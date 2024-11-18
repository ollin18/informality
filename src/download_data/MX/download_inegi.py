#!/usr/bin/env python
"""
This file downloads the requiered data from the Census 2020 including the
geometries
"""

import hydra
from download_aux import download_file, extract_csvfile, extract_shpfile
from omegaconf import DictConfig


@hydra.main(
    config_path="../../../config/MX/download", config_name="download", version_base=None
)
def main(config: DictConfig) -> None:
    # Data download
    download_file(config, config.urls.url_request, config.urls.file_state)
    # shapefile download
    download_file(config, config.urls.url_shp_request, f"{config.state_name}.zip")
    #  shp extraction
    extract_shpfile(config)
    #  data extraction
    extract_csvfile(
        config,
        "file_state",
        f"ageb_mza_urbana_{config.state}_cpv2020",
        f"conjunto_de_datos_ageb_urbana_{config.state}_cpv2020.csv",
    )


if __name__ == "__main__":
    main()
