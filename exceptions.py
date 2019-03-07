class NotFound(Exception):
    STATUS = 404
    DEFAULT_MESSAGE = 'This Page Not Found'

    def __init__(self, message=None):
        self.status = self.STATUS
        self.message = message or self.DEFAULT_MESSAGE
