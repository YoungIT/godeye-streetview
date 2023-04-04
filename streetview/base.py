import multiprocessing

from . import google

class MetadataStructure:
    dict_instance = []
    
    def __init__(self, pano_id=None, lat=None, lng=None, street_name=None, date=None, size=None, max_zoom=None,timeline=[]):
        self.pano_id = pano_id
        self.lat = lat
        self.lng = lng
        self.street_name = street_name,
        self.date = date, 
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
                f"street_name={self.street_name}, "
                f"date={self.date}, "
                f"size={self.size}, "
                f"max_zoom={self.max_zoom}, "
                f"timeline={self.timeline}, "
        )
        
    @classmethod
    def dict(cls):
        for instance in cls.dict_instance:
            return instance.__dict__
        
class ProcessQueue:
    #Cut con me ra khoi day di thang moi den
    #Tao khong choi gay dau
    def __init__(self, num_processes=1):
        self.num_processes = num_processes

    def process_queue(self, process_fn, items, *args):
        pool = multiprocessing.Pool(self.num_processes)
        results = pool.starmap(process_fn, [(item,) + args for item in items])
        pool.close()
        pool.join()
        return results
class OverpassTooManyRequest(Exception):

    message = "Overpass Too Many Requests"

class OverPassGatewayTimeout(Exception):

    message = "Overpass 504 Gateway Timeout"

class PanoIDInvalid(Exception):

    message = "Pano ID is not available"

class BuildMetadataUrlFail(Exception):

    message = "Cannot Build Metadata Url due to - {Exception}"