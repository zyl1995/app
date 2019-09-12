import MySQLdb
from random import Random
from hashlib import md5

conn = MySQLdb.connect(
    host='localhost',
    port=3306,
    user='vidsai009',
    passwd='123456',
    db='demo'
)

cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)


def _create_user(**kwargs):
    cur.execute(
        """INSERT INTO auth_user
         (user_name, pwd, salt)
         VALUES ('{user_name}', '{pwd}', '{salt}')""".format(**kwargs)
    )
    conn.commit()


def _get_user(user_name):
    cur.execute(
        """select * from auth_user where user_name = '{}'""".format(user_name)
    )
    values = cur.fetchall()
    return values[0]


def create_salt(length=5):
    salt = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    len_chars = len(chars) - 1
    random = Random()
    for _ in range(length):
        # 每次从chars中随机取一位
        salt += chars[random.randint(0, len_chars)]
    return salt

def create_user(user_name, pwd):
    salt = create_salt()
    md5_obj = md5()
    md5_obj.update(bytes(pwd + salt , encoding='utf-8'))
    _create_user(user_name=user_name, salt=salt, pwd=md5_obj.hexdigest())


def check_pwd(pwd, user_pwd, user_salt):
    md5_obj = md5()
    md5_obj.update(bytes(pwd + user_salt , encoding='utf-8'))
    return user_pwd == md5_obj.hexdigest()


def check_login(request, user_name, pwd):
    result = _get_user(user_name=user_name)
    id, user_pwd, user_salt = result['id'], result['pwd'], result['salt']
    verified = check_pwd(pwd, user_pwd, user_salt)
    if verified:
        request.session['user_id'] = id
    return verified
