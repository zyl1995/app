from response import Response
from router import DecoratorRouter
from utils import render

router = DecoratorRouter()

@router(r'/hello/(?P<name>[\w-]+)/$')
def hello_view(request, name):
    content = 'hello {0} args {1}'.format(name, request.get_args)
    return Response(content)


@router(r'/test/(?P<slug>[\w-]+)/$')
@render('test.html')
def test_view(request, slug, *args, **kwargs):
    context = {
        'user_name': slug,
        'product_lists': [
            {
                'name': 'p1'
            },
            {
                'name': 'p2'
            }
        ]
    }
    return context


@router(r'/login/$')
@render('login.html')
def test_login_view(request, *args, **kwargs):
    if request.request_method == 'GET':
        if request.session['user_id']:
            # 已登录,重定向
            pass
    elif request.request_method == 'POST':
        pass
