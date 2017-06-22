"""
必須套件除了 Flask-SQLAlchemy之外，
因為Python3的關係，還需要安裝pyMySQL 來取代原本Flask-SQLAlchemy使用的MySQLdb(這傢伙不支援Python3...)，
config內的db連結設定開頭也必須變更為 mysql+pymysql://username:password@server/db

支援Python3就是這麼麻煩 囧

====== 說明一下Column定義的類型
String(長度) 就是一般的字
DateTime  時間，似乎可以直接存Python的datetime物件，佛心來著的（記得要用utc時間歐！）


另外，DB Migration的機制請參考manager.py
"""

from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from yorha import app
from yorha.klibrary.constant_generator import gen_nowtime, gen_uuid

db = SQLAlchemy(app)


def init_customer_schema_collection():
    """
    將Flask config內的DATA_COLUMN設定轉成比教方便運用的collection（Dict in List）形式
    :return: Dict in List
    """
    from yorha.klibrary.camel_snake_converter import camel2snake
    # 從config讀入原始設定
    confing_data_column = app.config.get('CUSTOMER_DATA_COLUMN')
    data_schema_collection = []
    # 產生Class List
    for item in confing_data_column:
        conifing_name = item.get('name')
        conifing_class = item.get('class')
        config_type = item.get('type')
        config_option = item.get('option')
        config_validator = item.get('validator')
        config_search_type = item.get('search_type')

        # 從原始的option產生search時專用的option
        config_search_option = []
        if item.get('option') is not None:
            for index, item in enumerate(config_option):
                if item[0] != '':
                    config_search_option.append(item)
            config_search_option.insert(0, ('' ,'--') )

        # 從原始設定的type產生basic_db_model與field_type，方便DB與Form定義
        if config_type == 'String':
            basic_db_model = 'BasicStringModel'
            field_type = 'StringField'

        elif config_type == 'SelectString':
            basic_db_model = 'BasicStringModel'
            field_type = 'SelectField'

        elif config_type == 'SelectMultipleField':
            basic_db_model = 'BasicStringModel'
            field_type = 'SelectMultipleField'
        else:
            basic_db_model = 'BasicStringModel'
            field_type = 'StringField'

        # 把一個key內的設定值包裝成Class
        class KeyModel():
            def __init__(self):
                self.name = conifing_name
                self.class_name = conifing_class
                self.table_name = camel2snake(conifing_class)
                self.type = config_type
                self.option = config_option
                self.basic_db_model = basic_db_model
                self.field_type = field_type
                self.validator = config_validator
                self.search_type = config_search_type
                self.search_option = config_search_option

        keydata = KeyModel()
        # 將產生的Class放入List
        data_schema_collection.append(keydata)

        # 如果key是選項型態而且還有 others 在最後一個選項的話，就產生一個給others用的文字輸入欄位
        if config_type in ['SelectString','MultiSelectString'] and 'others' in config_option[-1][0]:
            class SubKeyModel():
                def __init__(self):
                    self.name = conifing_name + ' : ' + config_option[-1][1]
                    self.class_name = conifing_class + 'Others'
                    self.parents_class_name = conifing_class
                    self.table_name = camel2snake(conifing_class) + '_others'
                    self.parents_table_name = camel2snake(conifing_class)
                    self.type = 'OthersString'
                    self.option = None
                    self.basic_db_model = 'BasicStringModel'
                    self.field_type = 'StringField'
                    self.validator = None
                    self.search_type = None

            subkeydata = SubKeyModel()
            data_schema_collection.append(subkeydata)


    return data_schema_collection

# 將最後產生好的List放回app.config方便在所有地方取用
app.config['CUSTOMER_SCHEMA'] = init_customer_schema_collection()


"""
建立Customer的基本Class模型
"""
class BasicCustomer():
    """
    建立Customer的基本Class模型
    """
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key= True)
    create_time = db.Column(db.DateTime,index=True)
    create_user = db.Column(db.String(128), index=True)
    customer_uuid = db.Column(db.String(36), index=True)
    def __init__(self):
        # 這些資訊會在資料產生時記錄，方便未來抓戰犯或是分析
        self.create_time = gen_nowtime()
        self.create_user = session['user_email']
        self.customer_uuid = gen_uuid()



"""
建立關聯設定的字典檔(未來應該要用Flask Config產生)
"""
customer_key_relationship = {}
for key in app.config['CUSTOMER_SCHEMA']:
    # 如果設定有search_type的value，就代表此key會在list page上使用，為求效能會把關聯的lazy設定為joined，其他則設為dynamic
    if key.search_type is not None:
        lazy_setting = 'joined'
    else:
        lazy_setting = 'dynamic'
    customer_key_relationship[key.table_name] = db.relationship(key.class_name, backref='customer', order_by= key.class_name + '.id', lazy=lazy_setting )


"""
實際建立名為Customer的class來定義DB
"""
Customer = type('Customer',(BasicCustomer, db.Model),customer_key_relationship)



"""
建立基本的String Class
"""
class BasicStringModel():
    """
    定義最基本的String Data Model，包含新建資料時的LOG資訊與關聯。
    引用時記得要定義__tablename__
    """
    id = db.Column(db.Integer, primary_key=True)
    edit_time = db.Column(db.DateTime, index=True)
    edit_user = db.Column(db.String(128), index=True)
    # 從metaclass定義ForeignKey就是要用@declared_attr來做，SQLAlchemy的ErrorMsg如是說。
    @declared_attr
    def customer_uuid(cls):
        return db.Column(db.String(36), db.ForeignKey('customer.customer_uuid'), index=True)
    # 主要資料
    value = db.Column(db.String(128), index=True)
    # 初始化時自動填入現在時間與session內的user_email作為操作者記錄。
    def __init__(self, value):
        self.value = value
        self.edit_time = gen_nowtime()
        self.edit_user = session['user_email']
    # 定義class本體直接吐出value
    def __repr__(self):
        return self.value

# 用Type魔法動態產生定義DB Table的Class
for key in app.config['CUSTOMER_SCHEMA']:
    globals()[key.class_name] = type(key.class_name, (locals()[key.basic_db_model], db.Model), {'__tablename__': key.table_name })


class SystemUser(db.Model):
    __tablename__ = 'system_user'
    id = db.Column(db.Integer, primary_key=True)
    edit_time = db.Column(db.DateTime, index=True)
    edit_user = db.Column(db.String(128), index=True)
    # 主要資料
    email = db.Column(db.String(128), index=True)
    user_group = db.Column(db.String(128), index=True)
    user_status = db.Column(db.String(128), index=True)

    def __init__(self, email):
        self.edit_time = gen_nowtime()
        self.edit_user = session['user_email']
        self.email = email


