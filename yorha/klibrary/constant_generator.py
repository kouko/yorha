def gen_uuid():
    import uuid
    uuid = str(uuid.uuid4())
    return uuid


def gen_nowtime():
    from datetime import datetime
    nowtime = datetime.utcnow().replace(microsecond=0)
    return nowtime


def gen_hash(datetime,uuid:str):
    import hashlib
    hash_value = hashlib.md5(str([str(datetime),uuid]).encode('utf-8')).hexdigest()
    return hash_value