import http.client


class Response:
    def __init__(self, content=[], status=200, charset='utf-8', content_type='text/html'):
        self.content = content
        content_type = '{content_type}; charset={charset}'.format(content_type=content_type, charset=charset)
        self.header = [('content_type', content_type)]
        self._status = status

    @property
    def status(self):
        status_string = http.client.responses.get(self._status, 'UNKNOWN')
        return '{status} {status_string}'.format(status=self._status, status_string=status_string)
