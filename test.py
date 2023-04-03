import streetview

# from loguru import logger

# latitude, longitude = 48.858136, 2.292267

# panoid = streetview.metadata._get_panoid_from_coord(latitude, longitude)

# raw_md = streetview.metadata._get_raw_metadata(panoid)
# logger.debug(raw_md)

# try:
#     lat, lng = raw_md[1][0][5][0][1][0][2], raw_md[1][0][5][0][1][0][3] 
#     image_size = raw_md[1][0][2][2][0] # obtains highest resolution
#     image_avail_res = raw_md[1][0][2][3] # obtains all resolutions available
#     raw_image_date = raw_md[1][0][6][-1] # [0] for year - [1] for month
#     raw_image_date = f"{raw_image_date[0]}/{raw_image_date[1]}"

# except IndexError:
#     logger.waring("ERROR")

# logger.debug(raw_md[0])
# logger.debug(raw_image_date)
