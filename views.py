from response import Response, RedirectResponse
from router import DecoratorRouter
from utils import render
from sql import check_login

router = DecoratorRouter()

@router(r'/hello/(?P<name>[\w-]+)/$')
def hello_view(request, name):
    content = 'hello {0} args {1}'.format(name, request.get_args)
    return Response(content)


@router(r'/test/(?P<slug>[\w-]+)/$')
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
    return render(context, 'test.html')


@router(r'/login/$')
def test_login_view(request, *args, **kwargs):
    if request.request_method == 'GET':
        if request.session['user_id']:
            # 已登录,重定向
            return RedirectResponse('/book/')
        return render(None, 'login.html')
    elif request.request_method == 'POST':
        verified = check_login(request, **request.post_args)
        if verified:
            # 登录成功,重定向
            return RedirectResponse('/book/')
        return render({'msg': '登录失败'}, 'login.html')


@router(r'/book/$')
def test_book_view(request, *args, **kwargs):
    if request.request_method == 'GET':
        if request.session['user_id']:
            # 已登录,重定向
            return render(None, 'book.html')
        return RedirectResponse('/login/')

