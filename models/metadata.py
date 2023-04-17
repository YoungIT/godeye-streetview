from typing import List
from pydantic import BaseModel

class MetadataStructure(BaseModel):
    pano_id: str
    lat: float
    lng: float
    street_name: str
    date: str
    size: int
    max_zoom: int
    timeline: List[str]