from collections import deque

from . import google

class MetadataStructure:
    dict_instance = []
    
    def __init__(self, pano_id=None, lat=None, lng=None, date=None, size=None, max_zoom=None, misc={}, timeline={}, linked_panos={}):
        self.pano_id = pano_id
        self.lat = lat
        self.lng = lng
        self.date = date
        self.size = size
        self.max_zoom = max_zoom
        self.timeline = timeline
        self.dict_instance.append(self)
        
    def __repr__(self):
        return (
                f"{self.__class__.__name__}("
                f"pano_id={self.pano_id}, "
                f"lat={self.lat}, "
                f"lng={self.lng}, "
                f"date={self.date}, "
                f"size={self.size}, "
                f"max_zoom={self.max_zoom}, "
                f"timeline={self.timeline}, "
        )
        
    @classmethod
    def dict(cls):
        for instance in cls.dict_instance:
            return instance.__dict__
class PanoQueue:
    def __init__(self, *elements):
        self._elements = deque(elements)

    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        while len(self) > 0:
            yield self.dequeue()

    def enqueue(self, element):
        self._elements.append(element)

    def dequeue(self):
        return self._elements.popleft()
        
class OverpassTooManyRequest(Exception):

    message = "Overpass Too Many Requests"

class OverPassGatewayTimeout(Exception):

    message = "Overpass 504 Gateway Timeout"