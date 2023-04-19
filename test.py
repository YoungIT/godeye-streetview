import app.streetview
import app.settings
import app.models
import redis
import json

from app.utils import(
    _redis_action
)

from loguru import logger

redis_manager = _redis_action(host="127.0.0.1", 
                              port=app.settings.config.redis_config.port)

_message = {
    "lat":48.858623,
    "lng":2.2926242,
    "radius":100
}
_channel_name = app.settings.config.redis_config.channel_name

results = app.streetview.scraper.img_urls(
    _message["lat"], _message["lng"], _message["radius"]
)

import time

t1 = time.time()
try:
    while True:
        url_list = next(results)

        for message in url_list:

            logger.debug(message)
            redis_manager.push_to_channel(_channel_name, message)

except StopIteration:
    logger.warning("No more messages from generator")

end = time.time() - t1

logger.success(f"Took {end} to finish")

