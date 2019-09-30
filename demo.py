import tornado.ioloop
import tornado.web


class MainHandle(tornado.web.RedirectHandler):

    def get(self):
        self.write("hhh")


def make_app():
    return tornado.web.Application([
        (r"/test/", MainHandle)
    ])

if __name__ == '__main__':
    app = make_app()
    app.listen(8999)
    tornado.ioloop.IOLoop.current().start()
