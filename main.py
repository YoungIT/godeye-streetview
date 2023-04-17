from fastapi import FastAPI, HTTPException

import settings
import streetview

from models import (
    Message
)
from utils import(
    _redis_action
)
app = FastAPI()
redis_manager = _redis_action(host=settings.redis_config.host, 
                              port=settings.redis_config.port)

@app.post("/redis_action/create_channel")
def initiate_channel(message: Message):

    _message = message.json()
    _channel_name = str(_message["lat"])+"_"+str(_message["lng"])

    results = streetview.scraper.img_urls(
        _message["lat"], _message["lng"], _message["radius"]
    )

    try:
        while True:
            message = next(results)
            redis_manager.push_to_channel(_channel_name, message)
    except StopIteration:

        return {"Success create channel": _channel_name}

@app.post("/redis_action/delete_channel")
def delete_channel():
    
    redis_manager.delete_channel()
