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
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import overpy

from loguru import logger

import settings

from . import (
    google,
    base
)

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

    _convert_date = lambda raw_date : datetime.strptime(raw_date, "%Y/%m")
    multi_thread = MultiThread(max_workers=settings.config.worker.max_thread)

    def get_metadata(**kwargs) -> base.MetadataStructure:

        """_summary_

        Returns:
            _type_: _description_
        """

        pano_id = kwargs.get(pano_id)
        lat, lng = kwargs.get(lat), kwargs.get(lng)

        if pano_id == None:
            pano_id = google.metadata._get_panoid_from_coord(lat, lng, 100)
        elif type(pano_id) is list:
            pano_id = pano_id[0]

        raw_md = google.metadata._get_raw_metadata(pano_id)

        pano_timeline = list() # List for store all PanoID and it's historical Iamges

        try:
            lat, lng = raw_md[1][0][5][0][1][0][2], raw_md[1][0][5][0][1][0][3] 
            street_name = raw_md[1][0][3][2]
            image_size = raw_md[1][0][2][2][0] # obtains highest resolution
            image_avail_res = raw_md[1][0][2][3] # obtains all resolutions available
            raw_image_date = raw_md[1][0][6][-1] # [0] for year - [1] for month
            raw_image_date = scraper._convert_date(f"{raw_image_date[0]}/{raw_image_date[1]}")

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

        logger.debug(f"datetime {raw_image_date}")

        metadata = base.MetadataStructure(
            pano_id=pano_id, 
            lat=lat, 
            lng=lng, 
            street_name = street_name,
            date=raw_image_date,
            size=[image_avail_res[0], image_avail_res[1]],
            max_zoom=len(image_avail_res[0])-1,
            timeline=pano_timeline
        )

        return metadata

    def list_pano_id(lat, lon, radius):

        """_summary_

        Raises:
            base.PanoIDInvalid: _description_
        """

        op = overpass_route(lat, lon, radius)

        objects = []

        for lat, lng in op.get_coord_around():

            objects.append({
                "pano_id" : None,
                "lat": lat,
                "lng": lng,
                "size":None, 
                "max_zoom":None
            })

            break

        logger.success("Success in process Queue")

        return [scraper.get_metadata(**obj) for obj in objects]

    def save_image(url, local_storage=settings.config.images.local_storage, storage_path="images/"):

        response = requests.get(url)
        img_data = response.content
        img_name = url.split('/')[-1]

        if local_storage:
        os.makedirs(storage_path, exist_ok=True)
            with open(os.path.join(storage_path, img_name), 'wb') as f:
                f.write(img_data)
        else:

            # function for saving images to another storages will be place here
            print(img_data)

    def image_downloader(lat, lon, radius, get_timeline = False):

        for link scraper.list_pano_id(lat, lon, radius)

        with ThreadPoolExecutor(max_workers=settings.config.worker.max_thread) as executor:
            for i, url in enumerate(urls):
                filename = f'image{i}.jpg'
                executor.submit(download_image, url, filename)   
        
        if images_year == "last":

            pass


# a= google.metadata._get_panoid_from_coord(48.858623, 2.2926242, 100)
# logger.debug(a)

scraper.list_pano_id(48.858623, 2.2926242, 100)
# op = overpass_route(48.858623, 2.2926242, 100)

# google.metadata._get_raw_metadata("test")
# logger.debug(a)



    
    