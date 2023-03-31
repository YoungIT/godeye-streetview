# -*- coding: utf-8 -*-
"""
:Module: ``streetview``
:Author: `Adrian Letchford <http://www.dradrian.com>`_
:Organisation: `Warwick Business School <http://www.wbs.ac.uk/>`_, `University of Warwick <http://www.warwick.ac.uk/>`_.


This is a light module for downloading photos from Google street view. The
functions allow you to retrieve current and **old** photos.

The photos on Google street view are panoramas and are refered to as such.
However, you have the option of downloading flat photos, or panoramas.

Retrieving photos is a two step process. First, you must translate GPS
coordinates into panorama ids. The following code retrieves a list of
the closest panoramas giving you their id and date:
"""

import re, math, os, json, requests, itertools, time, shutil
from datetime import datetime
from PIL import Image
from io import BytesIO
from random import choice

import numpy as np
import hydra
from omegaconf import DictConfig, OmegaConf

from loguru import logger

from . import google
from . import base

overpass_api = overpy.Overpass()
class overpass_route:

    """_summary_
    """

    @hydra.main(config_path="..settings/", config_name="config")
    def __init__ (self, lat, lon, radius, cfg: DictConfig) -> None:

        logger.debug(OmegaConf.to_yaml(cfg.overpass.highway))

        self.lat = lat
        self.lon = lon
        self.highway_filter = cfg.overpass.highway
        self.radius = radius

    def query_craft (self):

        return f"""
            way(around:{self.radius},{self.lat},{self.lon})[highway~"^({self.highway_filter})$"];
            out;
        """
    
    def get_coord_around (self) -> set:

        """_summary_
        """

        waypoint = set()

        result = overpass_api.query(self.query_craft)

        for way in result.get_ways():
            while True:
                try:
                    nodes = way.get_nodes(resolve_missing=True)
                    for node in way.nodes:
                        waypoint.add( (node.lat, node.lon) )
                    
                except base.OverpassTooManyRequest:
                    time.sleep(1)
                    continue
                except base.OverPassGatewayTimeout:
                    time.sleep(10)
                    continue
                break
                
        return waypoint
class scraper:

    PanoQueue = base.PanoQueue()

    def get_metadata() -> base.MetadataStructure:

        return metadata

    def list_pano_id(lat, lon, radius):

        op = overpass_route(lat, lon, radius)

        for lat, lon in op.get_coord_around():

            pano_id = google.metadata._get_panoid_from_coord(lat, lon)

            md = google._build_tile_arr()

            md = scraper.get_metadata()

    
    