import os

import geopandas as gpd
import numpy as np
from omegaconf import DictConfig
from shapely.geometry import (
    MultiPoint,
    MultiPolygon,
    Polygon,
)
from tqdm import tqdm


def download_file(config: DictConfig, file_name: str) -> None:
    file_path = os.path.join(config.data.download, file_name)
    print(f"Downloading to {file_path}...")
    with open(file_path, "wb") as f:
        for data in tqdm(
            iterable=config.r.iter_content(chunk_size=config.chunk_size),
            total=config.total_size / config.chunk_size,
            unit="KB",
        ):
            f.write(data)


def close_holes(poly: Polygon) -> Polygon:
    coords_list = []
    for pol in poly.geoms:
        # if pol.interiors:
        if len(pol.interiors) > 0:
            coords_list.append(Polygon(list(pol.exterior.coords)))
        else:
            coords_list.append(Polygon(pol.exterior.coords))
    return MultiPolygon(coords_list)


def densify(geometry, distance):
    """
    Densify the boundary of a Polygon geometry by adding points at a specified interval.

    Parameters:
    - geometry: A shapely Polygon or MultiPolygon
    - distance: The distance between interpolated points

    Returns:
    - A MultiPoint object with points along the polygon's boundary
    """

    # Function to densify a LinearRing (used for both exterior and interiors)
    def densify_ring(linear_ring, distance):
        # Interpolate points along the linear ring
        points = [
            linear_ring.interpolate(d)
            for d in np.arange(0, linear_ring.length, distance)
        ]
        return points

    if geometry.is_empty:
        return MultiPoint([])

    # List to collect all points
    all_points = []

    if geometry.geom_type == "Polygon":
        # Densify exterior boundary
        all_points.extend(densify_ring(geometry.exterior, distance))

        # Densify each interior boundary (hole)
        for interior in geometry.interiors:
            all_points.extend(densify_ring(interior, distance))

    elif geometry.geom_type == "MultiPolygon":
        # If geometry is a MultiPolygon, apply densification to each polygon
        for polygon in geometry:
            # Densify exterior boundary
            all_points.extend(densify_ring(polygon.exterior, distance))

            # Densify each interior boundary (hole)
            for interior in polygon.interiors:
                all_points.extend(densify_ring(interior, distance))

    # Convert the list of points to a MultiPoint
    return MultiPoint(all_points)


def join_voronoi(df_voronoi, mzn, subset):
    df = gpd.sjoin(df_voronoi.iloc[subset], mzn, how="inner", predicate="intersects")
    return df
