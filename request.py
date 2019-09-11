import urllib.parse
from webserver import WSGIService


class Request:
    def __init__(self, environ):
        self.environ = environ
        self.COOKIES = self.environ['COOKIES']
        self.request_method = environ[WSGIService.CGI_ENV['REQUEST_METHOD']]
        url_args = urllib.parse.urlparse(environ[WSGIService.CGI_ENV['PATH_INFO']])
        for k, v in zip(url_args._fields, url_args):
            setattr(self, k, v)

    @property
    def get_args(self):
        args = urllib.parse.parse_qs(self.query)
        return {k: v[0] for k, v in args.items()}
