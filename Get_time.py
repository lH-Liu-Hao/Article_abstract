import re
import time
import datetime
from .Common_code import clean_have_follow_time


def get_real_time(delta_time):
    """
    """
    if '年' in delta_time:
        tim = f'{delta_time}:00'
        timeArray = time.strptime(tim, "%Y年%m月%d日 %H:%M:%S")
        time_date = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    else:
        time_date = clean_have_follow_time(delta_time)
    tim_st = time.strptime(time_date, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(tim_st)) * 1000
    return time_date, timestamp


# 格式化时间
def get_time(time_str):
    if len(time_str) >= 8 and re.search('^\d{8}', time_str):
        return '{}-{}-{}'.format(time_str[:4], time_str[4:6], time_str[6:8])
    else:
        return time_str
