from flask_sqlalchemy import SQLAlchemy
from yorha.models import db, Customer, CustomerResponser
from yorha import app


@app.route('/write')
def write():
    # TC1 = Customers()
    # TC1.responser_history.append(Responser('kouko.d@ichef.com.tw'))
    # db.session.add(TC1)
    # db.session.commit()

    # target = Customer.query.filter(Customer.responser_history.any(responser ='kouko.d2@ichef.com.tw')).first()
    # # target.responser_history.append(Responser('kouko.d2@ichef.com.tw'))
    # db.session.add(target)
    # db.session.commit()

    print('==================')
    print(target.create_user)
    print(target.responser_history[-1].id)
    print('==================')
    return 'ok'