import errno
from response import Response
from exceptions import NotFound, TempliteSyntaxError
from template_compilation import Templite


def render(context, template):
    try:
        with open(template, encoding='utf-8') as fp:
            text = fp.read()
    except IOError as e:
        # if e.errno == errno.ENOENT:
        #     raise TemplateDoesNotExist(origin)
        raise
    return Response(Templite(text).render(context))
