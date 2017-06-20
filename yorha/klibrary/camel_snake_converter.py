"""
變數命名轉換法
駱駝 <==> 蛇 互換
"""
import re

def snake2camel(name):
    return re.sub(r'(?:^|_)([a-z])', lambda x: x.group(1).upper(), name)

def snake2camelback(name):
    return re.sub(r'_([a-z])', lambda x: x.group(1).upper(), name)

def camel2snake(name):
    return name[0].lower() + re.sub(r'(?!^)[A-Z]', lambda x: '_' + x.group(0).lower(), name[1:])

def camelback2snake(name):
    return re.sub(r'[A-Z]', lambda x: '_' + x.group(0).lower(), name)

