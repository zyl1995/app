from request import Request
from response import Response
from router import DecoratorRouter
from exceptions import NotFound
from template_compilation import Templite

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


@routers(r'/test/$')
def test_view(request, *args):
    template = open('test.html', 'rb')
    text = template.read().decode('utf-8')
    content = Templite(text).render({
        'user_name': 'test',
        'product_lists': [
            {
                'name': 'p1'
            },
            {
                'name': 'p2'
            }
        ]
    })
    return Response(content)
