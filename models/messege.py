from typing import List
from pydantic import BaseModel

class Message(BaseModel):
    img_urls: List
    pano_id: str