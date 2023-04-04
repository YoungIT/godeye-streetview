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
import overpy

from loguru import logger

import settings

from . import (
    google,
    base
)
from . import google
from . import base

overpass_api = overpy.Overpass()
class overpass_route:

    """_summary_
    """

    def __init__ (self, lat, lon, radius) -> None:
        self.lat = lat
        self.lon = lon
        self.highway_query = settings.config.overpass.query.highway
        self.radius = radius

    def get_coord_around (self) -> set:

        """_summary_
        """

        waypoint = set()

        result = overpass_api.query(  
            self.highway_query.format(radius=self.radius,
                                      latitude=self.lat,
                                      longitude=self.lon)
        )

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

    """_summary_

    Raises:
        base.PanoIDInvalid: _description_

    Returns:
        _type_: _description_
    """

    PanoQueue = base.PanoQueue()
    _convert_date = lambda raw_date : datetime.strptime(raw_date, "%Y/%m")

    def get_metadata(pano_id=None, lat=None, lng=None, date=None, size=None, max_zoom=None,timeline=[]) -> base.MetadataStructure:

        """_summary_

        Returns:
            _type_: _description_
        """

        if pano_id == None:
            pano_id = google.metadata._get_panoid_from_coord(lat, lon)
        elif type(pano_id) is list:
            pano_id = pano_id[0]

        logger.debug("panoid", pano_id) 

        raw_md = google.metadata._get_raw_metadata(pano_id)

        pano_timeline = list() # List for store all PanoID and it's historical Iamges

        logger.debug(raw_md)

        try:
            lat, lng = raw_md[1][0][5][0][1][0][2], raw_md[1][0][5][0][1][0][3] 
            street_name = raw_md[1][0][3][2]
            image_size = raw_md[1][0][2][2][0] # obtains highest resolution
            image_avail_res = raw_md[1][0][2][3] # obtains all resolutions available
            raw_image_date = raw_md[1][0][6][-1] # [0] for year - [1] for month
            raw_image_date = metadata._convert_date(f"{raw_image_date[0]}/{raw_image_date[1]}")

            linked_panos = raw_md[1][0][5][0][3][0]

            for pano_info in raw[1][0][5][0][8]:
                raw_pano_info = linked_panos[pano_info[0]]

                pano_timeline.append({
                    "pano_id": raw_pano_info[0][1],
                    "lat": raw_pano_info[2][0][-2],
                    "lng": raw_pano_info[2][0][-1],
                    "date":metadata._convert_date(f"{pano_info[1][0]}/{pano_info[1][1]}")
                })
        except IndexError:
            raise base.PanoIDInvalid

        metadata = base.MetadataStructure(
            pano_id=pano_id, 
            lat=lat, 
            lng=lng, 
            data=raw_image_date,
            size=size, 
            max_zoom=max_zoom,
            timeline=pano_timeline
        )

        return metadata

    def list_pano_id(lat, lon, radius):

        """_summary_

        Raises:
            base.PanoIDInvalid: _description_
        """

        op = overpass_route(lat, lon, radius)

        for lat, lon in op.get_coord_around():

            md = scraper.get_metadata(lat, lon)

            logger.debug(md)
            break

            # _build_arr = google._build_tile_arr(pano_id)

            # logger.debug(_build_arr)

    def image_downloader(images_year = "last"):

        if images_year == "last":

            pass

scraper.list_pano_id(48.858623, 2.2926242, 100)

# op = overpass_route(48.858623, 2.2926242, 100)
# a = op.query_craft()

# logger.debug(a)



    
    