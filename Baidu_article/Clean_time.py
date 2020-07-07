import re
import time
import datetime
from Utility.Baidu_Message.Common_code import clean_have_follow_time


class Clean_time():
    def clean_time(self, data_time):
        '''清洗时间，将data_time转变为正确的时间格式和时间戳，最后return'''
        # print(data_time)
        if 'T' in data_time:
            data_time = re.sub('T', ' ', data_time.split('.', 1)[0])
        if '前' in data_time or '昨' in data_time or '内' in data_time \
                or '刚刚' in data_time or '今' in data_time:
            time_date = clean_have_follow_time(data_time)
            tim_st = time.strptime(time_date, "%Y-%m-%d %H:%M:%S")
        else:
            sub_year_month_time = re.sub('年|月|/|\.', '-', data_time)
            sub_second_time = re.sub('秒', '', sub_year_month_time)
            sub_hour_minute_time = re.sub('时|分', ':', sub_second_time)
            len_gang = len(re.findall('-', sub_year_month_time))
            len_colon = len(re.findall(':', sub_hour_minute_time))
            if len_colon == 0:
                sub_day_time = re.sub('日 |日', '', sub_hour_minute_time, 1)
            else:
                sub_day_time = re.sub('日 |日', ' ', sub_hour_minute_time, 1)
            if len_gang == 1:
                # 当前年份 防止最终时间大于当前时间
                currentYear = datetime.datetime.now().year
                add_year_time = f'{currentYear}-{sub_day_time}'
                # 比较转换的时间是否大于当前的时间
                currentTime = int(time.time())
                try:
                    data_sj = time.strptime(add_year_time, "%Y-%m-%d %H:%M:%S")  # 定义格式
                except:
                    try:
                        data_sj = time.strptime(add_year_time, "%Y-%m-%d")  # 定义格式
                    except:
                        data_sj = time.strptime(add_year_time, "%Y-%m-%d %H:%M")  # 定义格式
                time_int = int(time.mktime(data_sj))
                if time_int > currentTime:
                    currentYear -= 1
                    add_year_time = f'{currentYear}-{sub_day_time}'
            else:  # ==2
                len_year = len(sub_day_time.split('-', 1)[0])
                if len_year == 2:
                    add_year_time = f'20{sub_day_time}'
                else:
                    add_year_time = sub_day_time
            if len_colon == 0:
                tim_st = time.strptime(add_year_time, "%Y-%m-%d")
                time_date = f'{add_year_time} 00:00:00'
            elif len_colon == 1:
                try:
                    tim_st = time.strptime(add_year_time, "%Y-%m-%d %H:%M")
                except:
                    tim_st = time.strptime(add_year_time, "%Y-%m-%d%H:%M")
                time_date = f'{add_year_time}:00'
            else:
                if len_gang:
                    time_date = add_year_time
                else:
                    time_date = f'{add_year_time} {sub_day_time}'
                try:
                    tim_st = time.strptime(time_date, "%Y-%m-%d %H:%M:%S")
                except:
                    tim_st = time.strptime(time_date, "%Y-%m-%d%H:%M:%S")
        timestamp = int(time.mktime(tim_st)) * 1000
        return time_date, timestamp
