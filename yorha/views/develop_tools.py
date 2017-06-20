# 基本Flask路由需要，只要是View家家戶戶必備
from yorha import app
from flask import render_template, request, session
from yorha.views.auth import login_required

# 資料庫
from yorha import models
from yorha.models import db, Customer, CustomerResponser, CustomerStatus, CustomerName

# 表單
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

#viewmodels
from yorha.viewmodels.customers import customer_filter


@app.route('/dev/gen_fake')
def gen_fack():
    import random
    roop=6666
    mail = ['kouko@ichef.com.tw','kouko2@ichef.com.tw','kouko3@ichef.com.tw','yihan.chang@ichef.com.tw']

    while roop > 0:
        new_customer = Customer()
        new_customer.customer_name.append(CustomerName('kouko' + str(random.randint(1,9999)) ))

        new_customer.customer_responser.append(CustomerResponser( mail[random.randint(0,3)] ))
        new_customer.customer_status.append(CustomerStatus('G' + str(random.randint(1,8)) ))

        new_customer.customer_responser.append(CustomerResponser( mail[random.randint(0,3)] ))
        new_customer.customer_status.append(CustomerStatus('G' + str(random.randint(1,8)) ))

        new_customer.customer_responser.append(CustomerResponser( mail[random.randint(0,3)] ))
        new_customer.customer_status.append(CustomerStatus('G' + str(random.randint(1,8)) ))


        db.session.add(new_customer)
        db.session.commit()
        print(new_customer)
        roop -= 1


    return 'Faked'


@app.route('/dev/q')
def q():

    c_f = customer_filter(CustomerStatus=['G1','G2'], CustomerResponser=['kouko2@ichef.com.tw'])

    for row in c_f:
        print(str(row.name_history[-1]) +'||'+ str(row.responser_history[-1]) +'||'+ str(row.status_history[-1]) )

    return 'OK'


@app.route('/dev/w')
def w():
    write = Customer()
    write.dynamic_model.append(DymModel('TEST'))
    db.session.add(write)
    db.session.commit()
    return 'ok'

@app.route('/dev/s')
def s():
    print(app.config['CUSTOMER_SCHEMA'][0].name)
    return 'ok'


@app.route('/dev/fake_login')
def fake_login():
    session['google_token'] = ('XXXXXXXXXXXXXXXXXXX', '')
    session['user_id'] = '12345678901234567'
    session['user_email'] = 'fakeemail@ichef.com.tw'
    session['user_name'] = 'fakename'
    session['user_domain'] = 'ichef.com.tw'
    return 'Fake_login_ok'


