# 資料庫
from yorha import models
from yorha.models import db, Customer, SystemUser
import importlib

def latest_meta_status(db_class, culumn_value):
    """
    從指定Class中，取得所有Customer最新狀態，且最新狀態符合指定Value的Query指令。
    :return: SQLalchemy的Query指令，可以加上.all()輸出，或是加上.subquery()用在其他Query內。
    """
    # 因為filter會用到in_()，所以要確保用來filter的culumn_value要是個list
    if type(culumn_value) != list:
        culumn_value = [culumn_value]
    # 用customer_uuid GROUP BY後，取最大的id當作該customer最後更新此key的資料
    latest_update_id = db.session\
        .query(db.func.max(db_class.id).label('id'), db_class.customer_uuid)\
        .group_by(db_class.customer_uuid)\
        .subquery()
    # 用上一步拿到的id JOIN自己拿到value（我也知道這很蠢...）
    join_value = db.session\
        .query(db_class.id.label('id'),
               db_class.edit_time.label('time'),
               db_class.customer_uuid.label('uuid'),
               db_class.value.label('value'))\
        .join(latest_update_id, latest_update_id.c.id == db_class.id)\
    # filter出指定value的customer_uuid
    latet_status = join_value\
        .filter(db_class.value.in_(culumn_value))
    return latet_status


def customer_filter(**kwarge):
    """
    用指定條件過濾出符合的顧客，可以用 customer_responser 或 customer_status 這兩個key
    :param kwarge: customer_responser or customer_status
    :return: SQLAlchemy的 Customer object List。
    """
    # 先產生基本的query指令開頭
    result = Customer.query
    # 用loop讓所有User給的key都產生對應的Query指令
    for key,value in kwarge.items():
        if value not in [None, '', [''], []]:
            # 如果valie不是空的話，先用這個神秘的招數把key name當成Class Name叫出該Class來
            target_class = getattr(importlib.import_module('yorha.models'),key)
            # 呼叫latest_meta_status產生filter subquery
            status_filter = latest_meta_status(target_class,value).subquery()
            # 把filter Query加入主要的result Query內
            result = result\
                .join(status_filter, Customer.customer_uuid == status_filter.c.uuid)
    # 加上.all()實際執行query
    result =result.all()
    print(result)
    return result

def list_avantable_user():
    """
    列出目前系統中的使用者（暫時是以曾經登入的人來列表）
    :return: SQLAlchemy的物件List
    """
    avantable_user_list = SystemUser.query.all()
    return avantable_user_list

def avantable_user_for_form():
    """
    將系統內的使用者列表轉成WTForms Selecter可接受的資料格式（值,顯示文字）。
    :return:
    """
    option_list = []
    for user in list_avantable_user():
        option_list.append((user.email,user.email))
    return option_list