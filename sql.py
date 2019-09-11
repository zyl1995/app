import MySQLdb


conn = MySQLdb.connect(
    host='localhost',
    port=3306,
    user='vidsai009',
    passwd='123456',
    db='demo'
)

cur = conn.cursor()


def check_login(username, pwd):
    # 如果登录成功，返回用户数据id
    pass
