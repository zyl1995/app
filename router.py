import re
from exceptions import NotFound


class DecoratorRouter:
    def __init__(self):
        self.routing_table = []

    def match(self, path):
        for (pattern, callback) in self.routing_table:
            _match = re.match(pattern, path)
            if _match:
                return (callback, _match.groups())
        raise NotFound()

    def __call__(self, pattern):
        def register_router(func):
            self.routing_table.append((pattern, func))
        return register_router
