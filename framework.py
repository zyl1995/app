from request import Request
from response import Response
from views import router
from exceptions import NotFound
from session import RedisSession

_session_id = 'session_id'


def handle_request_response(func):
    def handle(environ, start_response):
        _request = Request(environ)
        _request.session = RedisSession(_request.COOKIES.get(_session_id, None))
        _response = func(_request)
        start_response(_response.status, _response.header)
        print(_response.content)
        return _response.content
    return handle


@handle_request_response
def app(request):
    try:
        _callback, kwargs = router.match(request.path)
    except NotFound as e:
        return Response('Sorry, {}'.format(e.message))
    response = _callback(request, **kwargs)
    session_id = request.COOKIES.pop(_session_id, None)
    if session_id is None:
        response.set_cookie(_session_id, request.session.session_id)
    for k, v in request.COOKIES.items():
        response.set_cookie(k, v)
    return response
