import streetview
import settings
import models

from utils import(
    _redis_action
)

from loguru import logger

redis_manager = _redis_action(host=settings.config.redis_config.host, 
                              port=settings.config.redis_config.port)

_message = {
    "lat":48.858623,
    "lng":2.2926242,
    "radius":100
}
_channel_name = str(_message["lat"])+"_"+str(_message["lng"])

results = streetview.scraper.img_urls(
    _message["lat"], _message["lng"], _message["radius"]
)

try:
    while True:
        message = next(results)
        redis_manager.push_to_channel(_channel_name, message)
except StopIteration:
    logger.warning("No more messages from generator")


# pulls = redis_manager.pull_from_channel(_channel_name)

# for _message in pulls:
#     logger.debug(f"pull message {_message}")


