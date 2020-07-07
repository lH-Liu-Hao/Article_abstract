import re
import time
import hashlib
import datetime
from urllib.parse import urljoin


def get_md5(text):
    if isinstance(text, bytes):
        text = text
    else:
        text = text.encode()
    md5 = hashlib.md5()
    md5.update(text)
    return md5.hexdigest()


def clean_have_follow_time(data_time):
    '''
    根据传进来的时间进行判断，超过24小时前的就会是年月日格式，24小时内的就是多少小时前格式
    获取几秒钟前、几分钟前、几小时前、几天前，几个月前、及几年前的具体时间
    :param delta_time 格式如：50秒前，10小时前，31天前，5个月前，8年前
    :return: 具体时间 %Y-%m-%d %H:%M:%S
    :param data_time:
    :return:
    '''
    # 获取表达式中的数字
    # 获取表达式中的文字
    delta_word = re.findall("\D+", data_time)[0]
    if '时' in data_time and '分' in data_time:  # 判断时和分是否同时存在，存在则表示是今天 20时30分这种格式，将时和分替换为:，否则则是3分钟前这种格式,保持原样
        sub_second_time = re.sub('秒', '', data_time)
        last_time_text = re.sub('时|分', ':', sub_second_time)
    else:
        last_time_text = data_time
    if delta_word and ':' in last_time_text:  # 处理今天 02:21,今天02：21：23，昨天02：21类似这种日期格式
        len_colon = len(re.findall(':', last_time_text))
        if len_colon == 1:  # 判断：的数量，如果为1则拼接
            time_hour = f'{last_time_text.split(delta_word, 1)[1]}:00'
        else:
            time_hour = last_time_text.split(delta_word, 1)[1]
        if '今天' in delta_word:
            timestamp = time.time()
        elif '昨天' in delta_word:
            timestamp = time.time() - 60 * 60 * 24
        elif '前天' in delta_word:
            timestamp = time.time() - 60 * 60 * 24 * 2
        else:
            return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timearray = time.localtime(timestamp)
        time_date = f"{time.strftime('%Y-%m-%d', timearray)} {time_hour}"
    else:
        delta_num = int(re.findall("\d+", data_time)[0])
        units = {
            "刚刚": 60,
            "天内": delta_num * 24 * 60 * 60,
            "秒前": delta_num,
            "秒钟前": delta_num,
            "分钟前": delta_num * 60,
            "小时前": delta_num * 60 * 60,
            "天前": delta_num * 24 * 60 * 60,
            '前天': 2 * 24 * 60 * 60,
            '昨天': 24 * 60 * 60,
            '今天': 60,
            '周前': delta_num * 24 * 7 * 60 * 60,
            "个月前": int(delta_num * 365.0 / 12) * 24 * 60 * 60,
            "月前": int(delta_num * 365.0 / 12) * 24 * 60 * 60,
            "年前": delta_num * 365 * 24 * 60 * 60,
        }
        delta_time = datetime.timedelta(seconds=units[delta_word])
        time_date = (datetime.datetime.now() - delta_time).strftime('%Y-%m-%d %H:%M:%S')
    return time_date


def clear_source(content_source, url, old_content):
    # 对content进行格式化，方便阅读
    try:
        if content_source:
            content_source = re.sub('[{}\[\]]', '', content_source)  # 清除{}[]符号
            content_source = re.sub('[.]', '#1', content_source)
            content_source = re.sub('[*]', '#2', content_source)
            content_source = re.sub('[?]', '#3', content_source)
            content_source = re.sub('[(]', '#4', content_source)
            content_source = re.sub('[)]', '#5', content_source)  # 替换有转义意义的字符，分别用不同值代替
            # 清楚script和style标签及里面的内容，前提需要将原文的换行符替换为空，并且将转义字符替换，才不会在替换过程报错
            clear_script = re.sub('<script.*?>.*?</script>|<style>.*?</style>', '', content_source.replace('\n', ''))
            P_contents = re.findall('<[pP].*?>.*?</[pP]>', clear_script)  # 寻找全部p标签
            texts = []
            for p in P_contents:  # 循环遍历，
                p_text = re.search('<[pP].*?>(.*?)</[pP]>', p).group(1).strip()  # 找到每个p标签里的内容，在前面添加四个空格作为新p，跟旧p替换
                new_P = re.sub(p_text, f'    {p_text}', p)
                texts.append([new_P, p])
            for new_p, old_p in texts:
                clear_script = re.sub(old_p, new_p, clear_script)  # 将旧p全部替换为新p
            sub_n = re.sub('<[pP].*?>|<br>', '\\n', clear_script)  # p标签和br标签替换为换行符
            sub_img = re.sub('<img', '%img', sub_n)  # 替换为%是为了防止下面的将全部<.*?>替换为空
            clear_tag = re.sub('<.*?>|&nbsp;', '', sub_img)
            content = re.sub('%img', '<img', clear_tag)  # 换回去
            content = re.sub('#1', '.', content)
            content = re.sub('#2', '*', content)
            content = re.sub('#3', '?', content)
            content = re.sub('#4', '(', content)
            content = re.sub('#5', ')', content)  # 换回原意
            src_list = re.findall('src="(.*?)"', content)
            mylist = [i for i in src_list if i != '']  # 清除列表有空字符串，防止下面替换过程中出现替换太多次的结果
            add_hrefs = []
            # 将相对路径替换为绝对路径
            for old_href in mylist:
                if not old_href.startswith('http'):
                    new_href = urljoin(url, old_href)
                    add_hrefs.append([new_href, old_href])
            for new_href, old_href in add_hrefs:
                content = re.sub(old_href, new_href, content)
            if content == '':  # 如果为空，则用原content
                content = old_content
        else:
            content = old_content
    except Exception as e:
        content = old_content
    return content
