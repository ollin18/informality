#!/usr/bin/env python
"""
This file removes the empty spaces between geometries via voronoi cells
"""

import multiprocessing as mp
import os

import geopandas as gpd
import hydra
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from omegaconf import DictConfig
from shapely.geometry import (
    MultiPoint,
)
from shapely.ops import voronoi_diagram as svd
from voronoi_aux import close_holes, densify


@hydra.main(
    config_path="../../../config/MX/download", config_name="voronoi", version_base=None
)
#  def main(config: DictConfig) -> None:
#      # Define the list of ent values
#      ents = ["09", "15"]
#
#      # Initialize lists to store DataFrames
#      df_list = []
#      mzn_list = []
#
#      # Base file path
#      #  file_path = os.path.join(os.getcwd(), "..", "..", "data")
#      file_path = os.path.join(config.data.raw)
#
#      for ent in ents:
#          # Construct the directory paths
#          csv_directory = config.data.csv
#          shp_directory = config.data.shp
#
#          # Read the CSV file
#          csv_file = os.path.join(csv_directory, f"conjunto_de_datos_ageb_urbana_{ent}_cpv2020.csv")
#          df = pd.read_csv(csv_file)
#          df_list.append(df)
#
#          # Read the shapefile
#          shp_file = os.path.join(shp_directory, f"{ent}m.shp")
#          mzn = gpd.read_file(shp_file)
#          mzn_list.append(mzn)
#
#      # Concatenate all DataFrames
#      df = pd.concat(df_list, ignore_index=True)
#      mzn = gpd.GeoDataFrame(pd.concat(mzn_list, ignore_index=True))
#      orig_crs = mzn.crs
#
#      homes = pd.read_csv(os.path.join(config.data.mobility, "home_work_locations_by_counts.csv"))
#      homes = gpd.GeoDataFrame(
#          homes,
#          geometry=gpd.points_from_xy(homes.cluster_longitude, homes.cluster_latitude)
#      )
#
#      homes.set_crs(epsg=4326, inplace=True)
#      mzn.to_crs(epsg=4326, inplace=True)
#      mzn_filtered_09 = mzn[mzn["CVE_ENT"] == "09"]
#      mzn_filtered_15 = mzn[mzn["CVE_ENT"] == "15"]
#
#      points_within_polygons = gpd.sjoin(homes, mzn_filtered_15, predicate='within')
#      polygons_with_points = mzn_filtered_15[mzn_filtered_15.index.isin(points_within_polygons.index_right.unique())]
#      mzn_filtered = pd.concat([mzn_filtered_09, polygons_with_points])
#
#      df["CVEGEO"] = (df['ENTIDAD'].apply(lambda x: str(x).zfill(2)) +
#          df['MUN'].apply(lambda x: str(x).zfill(3)) +
#          df['LOC'].apply(lambda x: str(x).zfill(4)) +
#          df['AGEB'].apply(lambda x: str(x).zfill(4)) +
#          df['MZA'].apply(lambda x: str(x).zfill(3)))
#
#      mzn = pd.merge(mzn_filtered, df, on="CVEGEO", how="inner")
#      mzn = mzn.loc[mzn["TIPOMZA"] != "Contenedora"]
#      mzn = mzn.to_crs(orig_crs)
#
#      buffer_distance = 500
#      external_mask = mzn.buffer(buffer_distance)
#      external_mask = external_mask.union_all().buffer(-buffer_distance)
#
#      mzn['geometry'] = mzn.geometry.buffer(0)
#      external_mask = close_holes(external_mask)
#
#      dense_points = Parallel(n_jobs=-1)(
#          delayed(densify)(geometry, 1) for geometry in mzn.geometry
#      )
#
#      # Add the dense points to the GeoDataFrame
#      mzn['dense_points'] = dense_points
#
#      all_points = []
#      for multipoint in mzn.dense_points.explode().to_list():
#          all_points.extend(multipoint.geoms)  # .geoms returns the individual points in the MultiPoint
#
#      as_multipoint = MultiPoint(all_points)
#      all_voronois = svd(as_multipoint, envelope=external_mask)
#      ds_voronoi = gpd.GeoSeries(list(all_voronois.geoms))
#      df_voronoi = gpd.GeoDataFrame(geometry=ds_voronoi)
#
#      df_voronoi.crs = mzn.crs
#
#      cpus = mp.cpu_count()
#      rows = np.arange(df_voronoi.shape[0])
#      pool = mp.Pool(processes = cpus)
#      intersection_chunks = np.array_split(rows, cpus)
#
#      def join_voronoi(subset):
#          df = gpd.sjoin(df_voronoi.iloc[subset], mzn, how="inner", predicate="intersects")
#          return df
#
#      dftojoin = pool.map(join_voronoi, intersection_chunks)
#      pool.close()
#
#      gdf_joined = pd.concat(dftojoin)
#
#      gdf_temp = (gdf_joined.dissolve(by='index_right')
#              .reset_index(drop=False)
#              .rename(columns = {"index_right":"index"})
#              .sort_values("index")
#              .set_index("index"))
#
#      gdf_temp = gdf_temp.drop(columns="dense_points")
#      gdf_temp2 = gdf_temp.simplify(1, True)
#
#      final_dfc = gpd.clip(gdf_temp2, external_mask)
#      gdf_temp["geometry"] = final_dfc
#      gdf_temp = gdf_temp.reset_index(drop=True)
#      gdf_temp.to_crs(epsg=4326, inplace=True)
#
#      gdf_temp.to_file(os.path.join(config.data.maps,"mex_voronoi.geojson"), driver="GeoJSON")
# Move join_voronoi to top-level
def join_voronoi(subset, df_voronoi, mzn):
    """Joins a subset of the voronoi GeoDataFrame with the mzn GeoDataFrame."""
    df = gpd.sjoin(df_voronoi.iloc[subset], mzn, how="inner", predicate="intersects")
    return df


@hydra.main(
    config_path="../../../config/MX/download", config_name="voronoi", version_base=None
)
def main(config: DictConfig) -> None:
    # Define the list of ent values
    ents = ["09", "15"]

    # Initialize lists to store DataFrames
    df_list = []
    mzn_list = []

    # Base file path
    os.path.join(config.data.raw)

    for ent in ents:
        # Construct the directory paths
        csv_directory = config.data.csv
        shp_directory = config.data.shp

        # Read the CSV file
        csv_file = os.path.join(
            csv_directory, f"conjunto_de_datos_ageb_urbana_{ent}_cpv2020.csv"
        )
        df = pd.read_csv(csv_file)
        df_list.append(df)

        # Read the shapefile
        shp_file = os.path.join(shp_directory, f"{ent}m.shp")
        mzn = gpd.read_file(shp_file)
        mzn_list.append(mzn)

    # Concatenate all DataFrames
    df = pd.concat(df_list, ignore_index=True)
    mzn = gpd.GeoDataFrame(pd.concat(mzn_list, ignore_index=True))
    orig_crs = mzn.crs

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

    df["CVEGEO"] = (
        df["ENTIDAD"].apply(lambda x: str(x).zfill(2))
        + df["MUN"].apply(lambda x: str(x).zfill(3))
        + df["LOC"].apply(lambda x: str(x).zfill(4))
        + df["AGEB"].apply(lambda x: str(x).zfill(4))
        + df["MZA"].apply(lambda x: str(x).zfill(3))
    )

    mzn = pd.merge(mzn_filtered, df, on="CVEGEO", how="inner")
    mzn = mzn.loc[mzn["TIPOMZA"] != "Contenedora"]
    mzn = mzn.to_crs(orig_crs)

    buffer_distance = 500
    external_mask = mzn.buffer(buffer_distance)
    external_mask = external_mask.union_all().buffer(-buffer_distance)

    mzn["geometry"] = mzn.geometry.buffer(0)
    external_mask = close_holes(external_mask)

    dense_points = Parallel(n_jobs=-1)(
        delayed(densify)(geometry, 1) for geometry in mzn.geometry
    )

    # Add the dense points to the GeoDataFrame
    mzn["dense_points"] = dense_points

    all_points = []
    for multipoint in mzn.dense_points.explode().to_list():
        all_points.extend(
            multipoint.geoms
        )  # .geoms returns the individual points in the MultiPoint

    as_multipoint = MultiPoint(all_points)
    all_voronois = svd(as_multipoint, envelope=external_mask)
    ds_voronoi = gpd.GeoSeries(list(all_voronois.geoms))
    df_voronoi = gpd.GeoDataFrame(geometry=ds_voronoi)

    df_voronoi.crs = mzn.crs

    # Use multiprocessing
    cpus = mp.cpu_count()
    rows = np.arange(df_voronoi.shape[0])
    intersection_chunks = np.array_split(rows, cpus)

    with mp.Pool(processes=cpus) as pool:
        dftojoin = pool.starmap(
            join_voronoi, [(subset, df_voronoi, mzn) for subset in intersection_chunks]
        )

    gdf_joined = pd.concat(dftojoin)

    gdf_temp = (
        gdf_joined.dissolve(by="index_right")
        .reset_index(drop=False)
        .rename(columns={"index_right": "index"})
        .sort_values("index")
        .set_index("index")
    )

    gdf_temp = gdf_temp.drop(columns="dense_points")
    gdf_temp2 = gdf_temp.simplify(1, True)

    final_dfc = gpd.clip(gdf_temp2, external_mask)
    gdf_temp["geometry"] = final_dfc
    gdf_temp = gdf_temp.reset_index(drop=True)
    gdf_temp.to_crs(epsg=4326, inplace=True)

    gdf_temp.to_file(
        os.path.join(config.data.maps, "mex_voronoi.geojson"), driver="GeoJSON"
    )


if __name__ == "__main__":
    main()
