import socket
import select

HOST, PORT = '', 9999

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(5)
# socket设置为非阻塞
listen_socket.setblocking(0)
# 创建一个epoll对象
epoll = select.epoll()
# 将（socket文件描述符,socket读事件）注册到epoll对象中（红黑二叉树）
# 通过中断通知把epoll对象的对应节点放入队列
epoll.register(listen_socket.fileno(), select.EPOLLIN)

try:
    connections = {}
    requests = {}
    responses = {}
    while True:
        # 1秒时间内epoll的是否有事件发生（队列返回）
        events = epoll.poll(1)
        if not events:
            print('not event, continue')
            continue
        for fd, event in events:
            # 说明有新连接到来
            if fd == listen_socket.fileno():
                connection, addr = listen_socket.accept()
                # 将该连接socket设为非阻塞
                connection.setblocking(0)
                # 对该连接socket读事件进行监听
                epoll.register(connection.fileno(), select.EPOLLIN)
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
            # 触发读事件
            elif event & select.EPOLLIN:
                requests[fd] += connections[fd].recv(1024)
                # 无数据，可能是客户端已关闭
                if not requests[fd]:
                    connections[fd].close()
                    del requests[fd]
                    del connections[fd]
                    # 不再监听该文件描述符
                    epoll.modify(fd, 0)
                else:
                    epoll.modify(fd, select.EPOLLOUT)
            # 触发写事件
            elif event & select.EPOLLOUT:
                byteswritten = connections[fd].send(responses[fd])
                responses[fd] = responses[byteswritten:]
                if len(responses[fd]) == 0:
                    epoll.modify(fd, 0)
                    epoll.modify(fd, select.EPOLLIN)
            elif event & select.EPOLLHUP:
                connections[fd].close()
                del connections[fd]
                del requests[fd]
                del responses[fd]



finally:
    pass