
設定
============

# 基本設定
# Flask的設定key name一定要全大寫
import datetime

DEBUG = True

# For Google Login
GOOGLE_AUTH = True
GOOGLE_CLIENT_ID =
GOOGLE_CLIENT_SECRET =
GOOGLE_CLIENT_LOGIN_DOMAIN_LIMIT =

# For Session 安全性
SECRET_KEY =
PERMANENT_SESSION_LIFETIME = 43200  # Session過期時間，單位應該是秒

# For SQLALchemy 資料庫設定
SQLALCHEMY_DATABASE_URI =
SQLALCHEMY_TRACK_MODIFICATIONS = True  # 要開才有辦法自動Migrade~

# 資料欄位設定
"""

- 欄位順序：如果最後定義用的是Dict的話，好像需要？ 囧
-
- name:顯示給使用者用的名稱：介面上會顯示的名稱
- class：標準大駝峰寫法的名稱，當成Class名。系統會自動轉換成snake樣式當成DB table名。
- type：資料格式與輸入樣式
    String：文字輸入筐
    SelectString：文字選項
    MultiSelectString：多選文字選項（未實裝對應的搜尋功能）

    Interger：整數（未實裝）
    SelectInterger：數字選項（未實裝）


- option：如果輸入樣式是有限選項形式的話，那就會有選項的設定。
    如果選項有「其他」，value必須要是「others」而且放在最後一項
    這樣才會自動產生Others的文字輸入欄位

- validator:
    'required':True 必填
    'email':True 信箱格式（實裝未確認）

"""
CUSTOMER_DATA_COLUMN = [
    {'name': '顧客名稱',
     'class': 'CustomerName',
     'type': 'String',
     'validator': {'required': True}
    },
    {'name': '負責人',
     'class': 'CustomerResponser',
     'type': 'SelectString',
     'option': [('yihan.chang@ichef.com.tw','kouko1'),
                ('yihan.chang2@ichef.com.tw','kouko2'),
                ('yihan.chang3@ichef.com.tw','kouko3')],
     'validator': {'required': True},
     'search_type':'SelectString'
    },
    {'name': '顧客狀態',
     'class': 'CustomerStatus',
     'type': 'SelectString',
     'option': [('',''),
                ('G1','狀態G1'),
                ('G2','狀態G2'),
                ('G3','狀態G3'),
                ('G4','狀態G4'),
                ('G5','狀態G5')],
     'validator': {'required': True},
     'search_type':'MultiSelectString'
    },
    {'name': '進線方式',
     'class': 'LeadsType',
     'type': 'SelectString',
     'option': [('', ''),
                ('phone', '電話'),
                ('website', '官網留言'),
                ('facebook', '臉書'),
                ('email', 'email'),
                ('stranger', '陌開'),
                ('line', 'Line'),
                ('others', '其他')],
     'validator': {'required': True}
     },
    {'name': 'GG原因',
     'class': 'CustomerDropReasons',
     'type': 'MultiSelectString',
     'option': [('G1', '狀態G1'),
                ('G2', '狀態G2'),
                ('G3', '狀態G3'),
                ('G4', '狀態G4'),
                ('G5', '狀態G5')]
     }
]

CUSOMER_STATUS_OPTION = [('',''),
                          ('G1','狀態G1'),
                          ('G2','狀態G2'),
                          ('G3','狀態G3'),
                          ('G4','狀態G4'),
                          ('G5','狀態G5')]