from typing import List
from pydantic import BaseModel

class Message(BaseModel):
    lat: float
    lng: float
    img_urls: List[str]
    pano_id: str