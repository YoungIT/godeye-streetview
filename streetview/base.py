from concurrent.futures import ThreadPoolExecutor, as_completed
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

class MultiThread:
    def __init__(self, max_workers=1):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def get_image(self, url, filename):
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)

    def download_images(self, urls):
        futures = []
        for i, url in enumerate(urls):
            filename = f'image{i}.jpg'
            future = self.executor.submit(self.download_image, url, filename)
            futures.append(future)
        return futures

    def execute_task(self, task_fn, *args, **kwargs):
        future = self.executor.submit(task_fn, *args, **kwargs)
        return future
            
class OverpassTooManyRequest(Exception):

    message = "Overpass Too Many Requests"

class OverPassGatewayTimeout(Exception):

    message = "Overpass 504 Gateway Timeout"

class PanoIDInvalid(Exception):

    message = "Pano ID is not available"

class BuildMetadataUrlFail(Exception):

    message = "Cannot Build Metadata Url due to - {Exception}"