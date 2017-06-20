from flask import Flask , url_for, render_template

app = Flask(__name__)
app.config.from_object('config') # 將設定檔指定為 config.py

from yorha.views.auth import login_required

from yorha.views import auth
from yorha.views import db_writetest
from yorha.views import customers
from yorha.views import develop_tools #dev用的功能

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/test')
@login_required
def test():
    return 'test'

