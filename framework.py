from request import Request
from response import Response
from router import DecoratorRouter
from exceptions import NotFound

routers = DecoratorRouter()


def handle_request_response(func):
    def handle(environ, start_response):
        _request = Request(environ)
        _response = func(_request)
        start_response(_response.status, _response.header)
        print(_response.content)
        return _response.content
    return handle


@handle_request_response
def app(request):
    try:
        _callback, args = routers.match(request.path)
    except NotFound as e:
        return Response('Sorry, {}'.format(e.message))
    return _callback(request, *args)


@routers(r'/hello/(.*)/$')
def hello_view(request, name):
    content = 'hello {0} args{1}'.format(name, request.get_args)
    return Response(content)
