import streetview
import settings
import models

from utils import(
    _redis_action
)

Message(
    pano_id ="str",
    img_urls = ['123','234'] , 
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

for _message in results:
    redis_manager.push_to_channel(_channel_name, _message)

pulls = redis_manager.pull_from_channel(_channel_name)

for _message in pulls:
    logger.debug(_message)


