import socket
import io
import sys
import os
import signal
from datetime import datetime


class WSGIService:
    # ip协议类型, ipv4
    address_family = socket.AF_INET
    # 套接字类型, tcp
    socket_type = socket.SOCK_STREAM
    # 通用socket类型
    general_socket_type = socket.SOL_SOCKET
    # socket允许重用地址选项
    socket_allow_reuse = socket.SO_REUSEADDR
    # 允许挂起的请求数目
    request_queue_size = 5
    # 一次读socket缓存区的最大值（bit?字节）
    read_limit = 1024
    # 版本号
    server_version = 0.2
    # 日期格式
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT+0800 (CST)'
    # WSGI 环境变量
    WSGI_ENV = dict(
        VERSION='wsgi.version',
        URL_SCHEME='wsgi.url_scheme',
        INPUT='wsgi.input',
        ERROR='wsgi.error',
        MULTITHREAD='wsgi.multiprocess',
        MULTIPROCESS='wsgi.multiprocess',
        RUN_ONCE='wsgi.run_once',
    )
    # CGI 环境变量
    CGI_ENV = dict(
        REQUEST_METHOD='REQUEST_METHOD',
        PATH_INFO='PATH_INFO',
        SERVER_NAME='SERVER_NAME',
        SERVER_PORT='SERVER_PORT'
    )

    def __init__(self, service_address):
        # 创建socket
        self._socket = socket.socket(
            family=self.address_family,
            type=self.socket_type
        )
        # 设置socket的一些选项,这里是将该socket设置为允许重用
        self._socket.setsockopt(
            self.general_socket_type,
            self.socket_allow_reuse,
            1)
        # 绑定socket与地址族（host, port）
        self._socket.bind(service_address)
        # 监听socket, 是否有连接.
        self._socket.listen(self.request_queue_size)
        signal.signal(signal.SIGCHLD, self.handle_pid)
        host, self.server_port = self._socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        # 返回通过框架设置的http报文头部信息
        self.header_set = []
        # cookie
        self.cookies = {}

    def handle_pid(*args, **kwargs):
        while True:
            try:
                pid, status = os.waitpid(
                    -1,
                    os.WNOHANG
                )
            except OSError:
                return
            if pid == 0:
                return

    def set_app(self, application):
        self.application = application

    def start_service(self):
        while True:
            self._connection, address = self._socket.accept()
            pid = os.fork()
            if pid == 0:
                self._socket.close()
                self.handle_one_request()
            else:
                self._connection.close()

    def handle_one_request(self):
        self.request_data = bytes.decode(self._connection.recv(self.read_limit))
        self.request_lines = self.request_data.splitlines()
        print(self.format_like_curl('< {line}\n', self.request_lines))
        self.parse_request()
        self.parse_cookies()
        env = self.get_environ()
        result = self.application(env, self.start_response)
        self.finish_response(result)

    def parse_cookies(self):
        for line in self.request_lines:
            if 'Cookie' not in line:
                continue
            cookies = line.split(':')[1].strip()
            data = cookies.split(';')
            for item in data:
                k, v = item.split('=')
                self.cookies[k] = v

    def finish_response(self, result):
        try:
            status, response_headers = self.header_set
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data
            print(self.format_like_curl('> {line}\n', response.splitlines()))
            self._connection.sendall(str.encode(response))
        finally:
            self._connection.close()
            os._exit(0)

    @staticmethod
    def format_like_curl(template, lines):
        return ''.join(template.format(line=line) for line in lines)

    def get_environ(self):
        env = dict()
        # 所需要的wsgi变量
        env[self.WSGI_ENV['VERSION']] = (1, 0)
        env[self.WSGI_ENV['URL_SCHEME']] = 'http'
        env[self.WSGI_ENV['INPUT']] = io.StringIO(self.request_data)
        env[self.WSGI_ENV['ERROR']] = sys.stderr
        env[self.WSGI_ENV['MULTITHREAD']] = False
        env[self.WSGI_ENV['MULTIPROCESS']] = False
        env[self.WSGI_ENV['RUN_ONCE']] = False
        # 所需要的cgi变量
        env[self.CGI_ENV['REQUEST_METHOD']] = self.request_method
        env[self.CGI_ENV['PATH_INFO']] = self.path
        env[self.CGI_ENV['SERVER_NAME']] = self.server_name
        env[self.CGI_ENV['SERVER_PORT']] = str(self.server_port)
        # 处理cookies
        env['COOKIES'] = self.cookies
        return env

    def start_response(self, status, response_headers, exc_info=False):
        server_headers = [
            ('Data', datetime.utcnow().strftime(self.GMT_FORMAT)),
            ('Server', '{0} {1}'.format(self.__class__.__name__, self.server_version))
        ]
        self.header_set = [status, response_headers + server_headers]

    def parse_request(self):
        first_request_line = self.request_lines[0]
        first_request_line = first_request_line.rstrip('\r\n')
        (
            self.request_method,
            self.path,
            self.request_version
        ) = first_request_line.split()


SERVER_ADDRESS = (HOST, PORT) = '', 8888


def make_server(server_address, application):
    server = WSGIService(server_address)
    server.set_app(application)
    return server


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application as module: callbale')
    app_path = sys.argv[1]
    _module, application = app_path.split(':')
    _module = __import__(_module)
    application = getattr(_module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print('WSGIService: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.start_service()
