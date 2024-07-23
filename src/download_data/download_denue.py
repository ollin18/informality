#!/usr/bin/env python
"""
This file downloads the requiered data from INEGI
"""

import hydra
from download_aux import download_file, extract_csvfile
from omegaconf import DictConfig


@hydra.main(
    config_path="../../config/download", config_name="download", version_base=None
)
def main(config: DictConfig) -> None:
    # Data download
    download_file(
        config, config.urls.url_denue, config.urls.file_denue
    )  # f"denue_{config.state}_{config.denue_month}_{config.denue_year}.zip")
    #  data extraction
    extract_csvfile(config, "file_denue", "", "denue_inegi_{}_.csv")


if __name__ == "__main__":
    main()
