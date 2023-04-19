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
from random import choice

from loguru import logger

from . import (
    base
)

import app.utils

class urls:
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    def _build_tile_url(pano_id, zoom=3, x=0, y=0):
        """
        Build Google Street View Tile URL
        """
        url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2"
        return url

    def _build_metadata_url(pano_id=None, lat=None, lng=None, mode="GetMetadata", radius=500):
        """
        Build GeoPhotoService call URL from
        Pano ID that contains panorama key data 
        such as image size, location, coordinates,
        date and previous panoramas.
        """
        xdc = "_xdc_._" + "".join([y for x in range(6) if (y := choice(urls.chars)) is not None])

        if mode == "GetMetadata":
            url = f"https://maps.googleapis.com/maps/api/js/GeoPhotoService.GetMetadata?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m2!1sen!2sUS!3m3!1m2!1e2!2s{pano_id}!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback={xdc}"
        elif mode == "SingleImageSearch":
            url = f"https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{lat}!4d{lng}!2d{radius}!3m20!1m1!3b1!2m2!1sen!2sUS!9m1!1e2!11m12!1m3!1e2!2b1!3e2!1m3!1e3!2b1!3e2!1m3!1e10!2b1!3e2!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback={xdc}"
        elif mode == "SatelliteZoom":
            x, y = geo._coordinate_to_tile(lat, lng)
            url = f"https://www.google.com/maps/photometa/ac/v1?pb=!1m1!1smaps_sv.tactile!6m3!1i{x}!2i{y}!3i17!8b1"

        return url

class geo:
    def _project(lat, lng, TILE_SIZE=256):
        siny = math.sin((lat * math.pi) / 180)
        siny = min(max(siny, -0.9999), 0.9999)
        x = TILE_SIZE * (0.5 + lng / 360),
        y = TILE_SIZE * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi)),
        return x[0], y[0]
    def _coordinate_to_tile(lat, lng, tile_size=256, zoom=17):
        x, y = geo._project(lat, lng)
        zoom = 1 << zoom
        tile_x = math.floor((x * zoom) / tile_size)
        tile_y = math.floor((y * zoom) / tile_size)
        return tile_x, tile_y
    
class metadata:

    def _get_panoid_from_coord(lat, lng, radius=500) -> str:

        """
        Returns closest Google panorama ID to given parsed coordinates.
        """
        try:
            url = urls._build_metadata_url(lat=lat, lng=lng, mode="SingleImageSearch", radius=radius)
            r = requests.get(url).text

            if "Search returned no images." in r:
                logger.info("[google]: Finding nearest panorama via satellite zoom...")
                url = urls._build_metadata_url(lat=lat, lng=lng, mode="SatelliteZoom")
                r = requests.get(url).text
                data = json.loads(r[4:])
                pano = data[1][1][0][0][0][1]
            else:
                data = re.findall(r'\[[0-9],"(.+?)"].+?,\[\[null,null,(.+?),(.+?)\]', r)
                pano = data[0][0]

            return pano

        except TypeError as Error:

            logger.error(f"Type Error - {Error}")

    @app.utils.retry(base.BuildMetadataUrlFail, delay=5, tries=3)
    def _get_raw_metadata(pano_id) -> dict:
        """
        Returns panorama ID metadata.
        """
        
        try:
            url = urls._build_metadata_url(pano_id=pano_id, mode="GetMetadata")
            response = str(requests.get(url).content)[38:-3].replace("\\", "\\\\")
            data = json.loads(response)
        
        except Exception as Error:

            raise base.BuildMetadataUrlFail(Error)

        return data

def panoids_from_response(text, closest=False, disp=False, proxies=None):
    """
    Gets panoids from response (gotting asynchronously)
    """

    # Get all the panorama ids and coordinates
    # I think the latest panorama should be the first one. And the previous
    # successive ones ought to be in reverse order from bottom to top. The final
    # images don't seem to correspond to a particular year. So if there is one
    # image per year I expect them to be orded like:
    # 2015
    # XXXX
    # XXXX
    # 2012
    # 2013
    # 2014
    pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', text)
    pans = [{
        "panoid": p[0],
        "lat": float(p[1]),
        "lon": float(p[2])} for p in pans]  # Convert to floats

    # Remove duplicate panoramas
    pans = [p for i, p in enumerate(pans) if p not in pans[:i]]

    if disp:
        for pan in pans:
            print(pan)

    # Get all the dates
    # The dates seem to be at the end of the file. They have a strange format but
    # are in the same order as the panoids except that the latest date is last
    # instead of first.
    dates = re.findall('([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]', text)
    dates = [list(d)[1:] for d in dates]  # Convert to lists and drop the index

    if len(dates) > 0:
        # Convert all values to integers
        dates = [[int(v) for v in d] for d in dates]

        # Make sure the month value is between 1-12
        dates = [d for d in dates if d[1] <= 12 and d[1] >= 1]

        # The last date belongs to the first panorama
        year, month = dates.pop(-1)
        pans[0].update({'year': year, "month": month})

        # The dates then apply in reverse order to the bottom panoramas
        dates.reverse()
        for i, (year, month) in enumerate(dates):
            pans[-1-i].update({'year': year, "month": month})

    # # Make the first value of the dates the index
    # if len(dates) > 0 and dates[-1][0] == '':
    #     dates[-1][0] = '0'
    # dates = [[int(v) for v in d] for d in dates]  # Convert all values to integers
    #
    # # Merge the dates into the panorama dictionaries
    # for i, year, month in dates:
    #     pans[i].update({'year': year, "month": month})

    # Sort the pans array
    def func(x):
        if 'year'in x:
            return datetime(year=x['year'], month=x['month'], day=1)
        else:
            return datetime(year=3000, month=1, day=1)
    pans.sort(key=func)

    if closest:
        return [pans[i] for i in range(len(dates))]
    else:
        return pans
    
def _build_tile_arr(panoid = None, date =None, zoom=4, alternate=False):

    tiles = {}

    coord = list(itertools.product(range(16), range(6)))
    _date = date.strftime("%m_%Y")

    if alternate:
        image_url = 'https://lh3.ggpht.com/p/{}=x{}-y{}-z{}'
        tiles = [("%s_%dx%dy" % (panoid, x, y), image_url.format(panoid, x, y, zoom)) for x, y in coord]
    else:
        image_url = 'https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={}&zoom={}&x={}&y={}'
        tiles = [("%s_%dx%dy" % (panoid, x, y), image_url.format(panoid, zoom, x, y)) for x, y in coord]

    return [{
        "date": _date,
        "tiles": tiles,
    }]

def api_download(panoid, heading, flat_dir, key, width=640, height=640,
                 fov=120, pitch=0, extension='jpg', year=2017, fname=None):
    """
    Download an image using the official API. These are not panoramas.

    Params:
        :panoid: the panorama id
        :heading: the heading of the photo. Each photo is taken with a 360
            camera. You need to specify a direction in degrees as the photo
            will only cover a partial region of the panorama. The recommended
            headings to use are 0, 90, 180, or 270.
        :flat_dir: the direction to save the image to.
        :key: your API key.
        :width: downloaded image width (max 640 for non-premium downloads).
        :height: downloaded image height (max 640 for non-premium downloads).
        :fov: image field-of-view.
        :image_format: desired image format.
        :fname: file name

    You can find instructions to obtain an API key here: https://developers.google.com/maps/documentation/streetview/
    """
    if not fname:
        fname = "%s_%s_%s" % (year, panoid, str(heading))
    image_format = extension if extension != 'jpg' else 'jpeg'

    url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        # maximum permitted size for free calls
        "size": "%dx%d" % (width, height),
        "fov": fov,
        "pitch": pitch,
        "heading": heading,
        "pano": panoid,
        "key": key
    }

    response = requests.get(url, params=params, stream=True)
    try:
        img = Image.open(BytesIO(response.content))
        filename = '%s/%s.%s' % (flat_dir, fname, extension)
        img.save(filename, image_format)
    except:
        print("Image not found")
        filename = None
    del response
    return filename

def download_panorama_v3(panoid, zoom=5, disp=False):
    '''
    v3: save image information in a buffer. (v2: save image to dist then read)
    input:
        panoid: which is an id of image on google maps
        zoom: larger number -> higher resolution, from 1 to 5, better less than 3, some location will fail when zoom larger than 3
        disp: verbose of downloading progress, basically you don't need it
    output:
        panorama image (uncropped)
    '''
    tile_width = 512
    tile_height = 512
    # img_w, img_h = int(np.ceil(416*(2**zoom)/tile_width)*tile_width), int(np.ceil(416*( 2**(zoom-1) )/tile_width)*tile_width)
    img_w, img_h = 416*(2**zoom), 416*( 2**(zoom-1) )
    tiles = tiles_info( panoid, zoom=zoom)
    valid_tiles = []
    # function of download_tiles
    for i, tile in enumerate(tiles):
        x, y, fname, url = tile
        if disp and i % 20 == 0:
            print("Image %d / %d" % (i, len(tiles)))
        if x*tile_width < img_w and y*tile_height < img_h: # tile is valid
            # Try to download the image file
            while True:
                try:
                    response = requests.get(url, stream=True)
                    break
                except requests.ConnectionError:
                    print("Connection error. Trying again in 2 seconds.")
                    time.sleep(2)
            valid_tiles.append( Image.open(BytesIO(response.content)) )
            del response
            
    # function to stich
    panorama = Image.new('RGB', (img_w, img_h))
    i = 0
    for x, y, fname, url in tiles:
        if x*tile_width < img_w and y*tile_height < img_h: # tile is valid
            tile = valid_tiles[i]
            i+=1
            panorama.paste(im=tile, box=(x*tile_width, y*tile_height))
    return np.array(panorama)

def download_flats(panoid, flat_dir, key, width=400, height=300,
                   fov=120, pitch=0, extension='jpg', year=2017):
    for heading in [0, 90, 180, 270]:
        api_download(panoid, heading, flat_dir, key, width, height, fov, pitch, extension, year)
