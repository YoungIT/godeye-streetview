from typing import List
from pydantic import BaseModel

class create_channel(BaseModel):
    lat: float
    lng: float
    radius: int