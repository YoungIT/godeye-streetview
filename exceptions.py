class OverpassTooManyRequest(Exception):

    message = "Overpass Too Many Requests"

class OverPassGatewayTimeout(Exception):

    message = "Overpass 504 Gateway Timeout"

class PanoIDInvalid(Exception):

    message = "Pano ID is not available"

class BuildMetadataUrlFail(Exception):

    message = "Cannot Build Metadata Url due to - {Exception}"

class URLNotVaild(Exception):

    message = "The URL is not valid"

class RedisException(Exception):
    pass

class RedisConnectionError(RedisException):
    pass

class RedisTimeoutError(RedisException):
    pass