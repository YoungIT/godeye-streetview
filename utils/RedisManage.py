import redis
import json

class _redis_action:
    def __init__(self, host, port, password=None):
        self.host = host
        self.port = port
        self.password = password
        self.r = redis.Redis(host=host, port=port, password=password)

    def create_channel(self, channel_name):
        self.r.publish(channel_name, '__init__')

    def push_to_channel(self, channel_name, message):
        message = json.dumps(message.dict())
        self.r.publish(channel_name, message)

    def pull_from_channel(self, channel_name):
        pubsub = self.r.pubsub()
        pubsub.subscribe(channel_name)
        for message in pubsub.listen():
            if message['type'] == 'message':
                if message['data'] == b'__init__':
                    continue
                yield message['data']

    def delete_channel(self, channel_name):
        self.r.delete(channel_name)
