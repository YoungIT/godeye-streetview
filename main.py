from fastapi import FastAPI, BackgroundTasks

import settings
import streetview

from models import (
    create_channel
)
from utils import(
    _redis_action
)

from loguru import logger

app = FastAPI()
redis_manager = _redis_action(host=settings.config.redis_config.host, 
                              port=settings.config.redis_config.port)
_channel_name = settings.config.redis_config.channel_name

def long_task(message: create_channel):
    results = streetview.scraper.img_urls(
        message.lat, message.lng ,message.radius
    )

    try:
        while True:
            url_list = next(results)

            for message in url_list:

                redis_manager.push_to_channel(_channel_name, message)

    except StopIteration:

        logger.success("All messages have been pull out")

@app.post("/redis_action/create_channel")
async def initiate_channel(message: create_channel, background_tasks: BackgroundTasks):

    background_tasks.add_task(long_task, message)

    return {"Success create channel": _channel_name}

@app.post("/redis_action/delete_channel")
def delete_channel():

    """
        Delete Redis Channel by sending a HTTP POST to /redis_action/delete_channel
    """
    
    redis_manager.delete_channel(_channel_name)
