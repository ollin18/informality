#!/usr/bin/env python
"""
This file downloads the requiered data from INEGI
"""
import os
import time
from zipfile import ZipFile

import pandas as pd
import requests
from omegaconf import DictConfig
from tqdm import tqdm


def download_file(config: DictConfig, url: str, file_name: str) -> None:
    os.makedirs(os.path.join(config.data.download), exist_ok=True)

    time.sleep(config.runvars.sleep)
    chunk_size = config.runvars.chunk_size

    print(f"Downloading {url}")
    r = requests.get(url, stream=True)
    total_size = int(r.headers["content-length"])

    file_path = os.path.join(config.data.download, file_name)
    print(f"Downloading to {file_path}...")
    with open(file_path, "wb") as f:
        for data in tqdm(
            iterable=r.iter_content(chunk_size=chunk_size),
            total=total_size / chunk_size,
            unit="KB",
        ):
            f.write(data)


def extract_csvfile(
    config: DictConfig, file_key: str, sub_dir: str, file_pattern: str
) -> None:
    csv_dir = os.path.join(config.data.csv)
    os.makedirs(csv_dir, exist_ok=True)

    zip_file = os.path.join(config.data.download, getattr(config.urls, file_key))
    csv_file = os.path.join(
        sub_dir, "conjunto_de_datos", file_pattern.format(config.state)
    )

    try:
        with ZipFile(zip_file, "r") as zip_ref:
            csv_data = zip_ref.read(csv_file)
            # Remove 'conjunto_de_datos' from the file path
            csv_file_name = os.path.basename(csv_file)
            csv_output_path = os.path.join(csv_dir, csv_file_name)
            with open(csv_output_path, "wb") as csv_out_file:
                csv_out_file.write(csv_data)
    except FileNotFoundError:
        print(f"File not found: {zip_file}")
    except KeyError:
        print(f"CSV file {csv_file} not found in the zip archive")
    except Exception as e:
        print(f"An error occurred: {e}")


def combine_csvfile(config: DictConfig, file_key: str, state: str) -> None:
    # Define the directory where the CSV files are located
    csv_dir = os.path.join(config.data.csv)

    # Define the file patterns for the parts
    part1_file = os.path.join(
        csv_dir,
        f"denue_inegi_{state}_1.csv",
    )
    part2_file = os.path.join(
        csv_dir,
        f"denue_inegi_{state}_2.csv",
    )

    # Define the output file path
    combined_file = os.path.join(csv_dir, f"denue_inegi_{state}_.csv")

    try:
        # Read the individual part files
        print(f"Reading part files for state {state}...")
        part1 = pd.read_csv(part1_file, encoding="latin1")
        part2 = pd.read_csv(part2_file, encoding="latin1")

        # Combine the parts
        combined = pd.concat([part1, part2], ignore_index=True)

        # Save the combined file
        combined.to_csv(combined_file, index=False)
        print(f"Combined CSV file saved to: {combined_file}")
        os.remove(part1_file)
        os.remove(part2_file)

    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except pd.errors.EmptyDataError as e:
        print(f"One of the CSV files is empty: {e}")
    except Exception as e:
        print(f"An error occurred while combining the files: {e}")


def extract_shpfile(config: DictConfig) -> None:
    file_path = os.path.join(config.data.download, f"{config.state_name}.zip")
    output_dir = os.path.join(config.data.shp)
    os.makedirs(output_dir, exist_ok=True)

    # Define the shapefile components
    file_prefix = f"conjunto_de_datos/{config.state}{config.shp_type}"
    shp_file = f"{file_prefix}.shp"
    cpg_file = f"{file_prefix}.cpg"
    dbf_file = f"{file_prefix}.dbf"
    prj_file = f"{file_prefix}.prj"
    shx_file = f"{file_prefix}.shx"

    # Extract files from the zip
    with ZipFile(file_path, "r") as zip_ref:
        for file in [shp_file, dbf_file, prj_file, shx_file, cpg_file]:
            if file in zip_ref.namelist():
                file_data = zip_ref.read(file)
                # Remove 'conjunto_de_datos' from the file path
                file_name = os.path.basename(file)
                output_file_path = os.path.join(output_dir, file_name)
                with open(output_file_path, "wb") as output_file:
                    output_file.write(file_data)
            elif file == cpg_file:
                # If the cpg_file does not exist, create it
                cpg_path = os.path.join(output_dir, os.path.basename(cpg_file))
                with open(cpg_path, "w") as out_file:
                    out_file.write(config.runvars.ISO)
