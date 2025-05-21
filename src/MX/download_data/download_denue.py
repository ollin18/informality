#!/usr/bin/env python
"""
This file downloads the requiered data from INEGI
"""

import hydra
from download_aux import combine_csvfile, download_file, extract_csvfile
from omegaconf import DictConfig


@hydra.main(
    config_path="../../../config/MX/download", config_name="download", version_base=None
)
def main(config: DictConfig) -> None:
    config.state = str(config.state)
    # Data download
    if config.state == "15":  # Special case for Estado de México with two parts
        download_file(config, config.urls.url_denue_part1, config.urls.file_denue_part1)
        download_file(config, config.urls.url_denue_part2, config.urls.file_denue_part2)

        extract_csvfile(
            config,
            "file_denue_part1",
            "",
            "denue_inegi_{}_1.csv",
        )
        extract_csvfile(
            config,
            "file_denue_part2",
            "",
            "denue_inegi_{}_2.csv",
        )
        combine_csvfile(config, "file_denue", config.state)
    else:
        download_file(config, config.urls.url_denue, config.urls.file_denue)

        extract_csvfile(
            config,
            "file_denue",
            "",
            "denue_inegi_{}_.csv",
        )


if __name__ == "__main__":
    main()
