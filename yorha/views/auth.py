from flask import redirect, url_for, session, request, jsonify, json
from flask_oauthlib.client import OAuth
from functools import wraps
from yorha import app
from yorha.models import SystemUser,db

oauth = OAuth(app)
domain_limit = app.config.get('GOOGLE_CLIENT_LOGIN_DOMAIN_LIMIT')

google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_CLIENT_ID'),
    consumer_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': ('profile','email'),
        # 指定Domain的Google帳號，但是只有Google那邊的介面會顯示，實際上沒有強制力囧囧
        'hd': app.config.get('GOOGLE_CLIENT_LOGIN_DOMAIN_LIMIT')
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# 判斷是否有Google Token，以及在有domain限制設定時User的Google Account Domain是否符合設定
def check_login_legally():
    rule = [session.get('google_token'), app.config.get('GOOGLE_CLIENT_LOGIN_DOMAIN_LIMIT'), session.get('user_domain')]
    if rule[0] != None and rule[1] == None:
        return True
    elif rule[0] != None and rule[1] != None and rule[2] == rule[1]:
        return True
    else:
        return False

"""
這是歡樂判斷是否已登入，如果沒登入就跳轉login的裝飾器，放在@route後面 >>「@login_required」
"""
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session['prelogin_path'] = request.path # 取得本次request的path，記在session裡等Login成功的時候用。
        if check_login_legally() is False and app.config.get('GOOGLE_AUTH') == True:
            return redirect(url_for('login'))
        else:
            return f(*args, **kwargs)
    return decorated_function


# 將User轉去Google拿Token，然後回到authorized頁面
@app.route('/auth/login')
def login():
    return google.authorize(callback=url_for('authorized',_external=True))


# Logout, 從Auth裡把google_token抹掉～
@app.route('/auth/logout')
def logout():
    session.pop('google_token', None)
    session.clear()
    print(session)
    return 'logout'


# 從Google回來之後檢查有沒有要到token，有的話跟google要hd參數檢查Domain是否符合設定
# ＯＫ後導去User原本想去的頁面，沒有的話就比中指
@app.route('/auth/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    else:
        # 先把驗證的Token存到Session
        session['google_token'] = (resp['access_token'], '')
        # 用Token去Google那邊拿User資訊後存到Session，用來辨識誰是誰～
        session['user_id'] = google.get('userinfo').data.get('id')
        session['user_email'] = google.get('userinfo').data.get('email')
        session['user_name'] = google.get('userinfo').data.get('name')
        session['user_domain'] = google.get('userinfo').data.get('hd')
        # 驗證該User是否符合設定的登入條件（Domain符合）
        if not check_login_legally():
            return 'Not Auth Domain'
        else:
            # 檢查是否曾經登入過，如果沒有就在DB的花名冊上記下一筆
            find_exist_user = SystemUser.query.filter(SystemUser.email == session['user_email']).first()
            if not find_exist_user:
                new_user = SystemUser(session['user_email'])
                db.session.add(new_user)
                db.session.commit()

        if 'prelogin_path' in session:
            redir_path = session['prelogin_path']
            session.pop('prelogin_path',None)
        else:
            redir_path = url_for('index')
        return redirect(redir_path)

# flask_oauthlib 需要這一段來定義跟Google發request時要去哪邊找token～
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


