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

import re, os, json, requests, time, shutil, sys
from datetime import datetime
from random import choice

import overpy

from loguru import logger

import app.settings
import app.models

from . import (
    google,
    base
)

import app.utils

logger.add("logging/streetview.log", backtrace=True, diagnose=True)

overpass_api = overpy.Overpass()

class overpass_route:

    """_summary_
    """

    def __init__(self, lat, lon, radius) -> None:
        self.lat = lat
        self.lon = lon
        self.highway_query = app.settings.config.overpass.query.highway
        self.radius = radius

    def get_coord_around(self) -> set:

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

    _convert_date = lambda raw_date : datetime.strptime(raw_date, "%Y/%m")
    multi_thread = base.MultiThread(max_workers=app.settings.config.worker.max_thread)

    def get_metadata(**kwargs) -> base.MetadataStructure:

        """_summary_

        Returns:
            _type_: _description_
        """

        pano_id = kwargs.get("pano_id")
        lat, lng = kwargs.get("lat"), kwargs.get("lng")
        timeline = kwargs.get("timeline")

        if pano_id == None:
            pano_id = google.metadata._get_panoid_from_coord(lat, lng, 100)
        elif type(pano_id) is list:
            pano_id = pano_id[0]

        raw_md = google.metadata._get_raw_metadata(pano_id)
        logger.debug(f"raw_md {raw_md}")

        pano_timeline = list() # List for store all PanoID and it's historical Iamges

        try:
            street_name = None

            lat, lng = raw_md[1][0][5][0][1][0][2], raw_md[1][0][5][0][1][0][3] 
            image_size = raw_md[1][0][2][2][0] # obtains highest resolution
            image_avail_res = raw_md[1][0][2][3] # obtains all resolutions available
            raw_image_date = raw_md[1][0][6][-1] # [0] for year - [1] for month
            raw_image_date = scraper._convert_date(f"{raw_image_date[0]}/{raw_image_date[1]}")

            for sublist in raw_md[1][0][3]:
                if sublist:
                    street_name = sublist

            if timeline == True and len(raw_md[1][0][5][0][8]) != 0:

                linked_panos = raw_md[1][0][5][0][3][0]

                for pano_info in raw_md[1][0][5][0][8]:
                    raw_pano_info = linked_panos[pano_info[0]]

                    pano_timeline.append({
                        "pano_id": raw_pano_info[0][1],
                        "lat": raw_pano_info[2][0][-2],
                        "lng": raw_pano_info[2][0][-1],
                        "date": scraper._convert_date(f"{pano_info[1][0]}/{pano_info[1][1]}")
                    })
        except IndexError:
            raise base.PanoIDInvalid

        metadata = base.MetadataStructure(
            pano_id=pano_id, 
            lat=lat, 
            lng=lng, 
            street_name = street_name,
            date= raw_image_date,
            size=[image_avail_res[0], image_avail_res[1]],
            max_zoom=len(image_avail_res[0])-1,
            timeline=pano_timeline
        )

        return metadata

    def list_pano_id(lat, lon, radius, timeline=False) -> list:

        """_summary_

        Raises:
            base.PanoIDInvalid: _description_
        """

        op = overpass_route(lat, lon, radius)

        # objects = []

        for lat, lng in op.get_coord_around():

            try:

                md = scraper.get_metadata(
                    pano_id = None,
                    lat = lat,
                    lng= lng,
                    size=None, 
                    max_zoom=None,
                    timeline=timeline
                )
            except Exception:
                logger.exception("What?!")
            else:
                # objects.append(md)

                yield md

            # Uncomment for testing
            # break 

        # return objects

    @app.utils.retry(base.BuildMetadataUrlFail, delay=5, tries=3)
    def save_image(url, filename, local_storage=app.settings.config.images.local_storage, storage_path="images/"):

        try:
            response = requests.get(url)
            img_data = response.content

            if local_storage == True:
                os.makedirs(storage_path, exist_ok=True)
                with open(os.path.join(storage_path, filename), 'wb') as f:
                    f.write(img_data)

            else:
                # function for saving images to another storages will be place here
                # function do_something()

                pass

        except Exception as Error:

            raise base.BuildMetadataUrlFail(Error)

    def img_urls(lat, lng, radius, get_timeline = False):
        
        images_md = scraper.list_pano_id(lat, lng, radius)

        try:
            while True:
                _md = next(images_md)

                pano_id, _date = _md.pano_id, _md.date[0]
                url_lists = google._build_tile_arr(pano_id, _date)

                if get_timeline:
                    for history_pano in md.timeline:
                        for tile in google._build_tile_arr(history_pano["pano_id"], history_pano["date"]):
                            url_lists.append(tile)

                yield url_lists

        except StopIteration:
            logger.warning("No more messages from generator")