"""
轉換值型的工具，用來把Python物件轉
目前有List <=> Str
"""
def str_list_converter(input_value):
    if type(input_value) == str and ',' in input_value:
        converted = input_value.split(',')
    elif type(input_value) == str:
        converted = [input_value]
    elif type(input_value) == list:
        converted = ','.join(input_value)
    else:
        converted = input_value
    return converted

def str2list(input_value):
    if input_value != None:
        converted = str(input_value).split(',')
        return converted
    else:
        return None

def list2str(input_value):
    if input_value != None:
        converted = ','.join(input_value)
        return converted
    else:
        return None