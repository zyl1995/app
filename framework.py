from request import Request
from response import Response

def app(environ, start_response):
    _request = Request(environ)
    _content = '{}'.format(_request.get_args)
    _response = Response(_content)
    start_response(_response.status, _response.header)
    print(_response.content)
    return _response.content
