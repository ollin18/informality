#!/usr/bin/env python
"""
This file downloads the requiered data the ENOE
"""

import hydra
from download_aux import download_file, extract_csvfile
from omegaconf import DictConfig


@hydra.main(
    config_path="../../../config/MX/download", config_name="download", version_base=None
)
def main(config: DictConfig) -> None:
    # Data download
    download_file(config, config.urls.url_enoe, config.urls.file_enoe)
    #  data extraction
    extract_csvfile(
        config,
        "file_enoe",
        f"conjunto_de_datos_sdem_{config.enoe_type}_{config.enoe_year}_{config.enoe_period}t",
        f"conjunto_de_datos_sdem_{config.enoe_type}_{config.enoe_year}_{config.enoe_period}t.csv",
    )


#  conjunto_de_datos_sdem_enoe_2024_1t
#  conjunto_de_datos
#  conjunto_de_datos_sdem_enoe_2024_1t.csv

if __name__ == "__main__":
    main()
