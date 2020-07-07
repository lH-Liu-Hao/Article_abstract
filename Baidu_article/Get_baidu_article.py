import re
import time
import json
import random
import requests
from Utility.Baidu_Message.Baidu_article.gne import GeneralNewsExtractor
from Utility.Baidu_Message.Baidu_spider.main import get
from Utility.Baidu_Message.log import log
from Utility.Baidu_Message.config import UA_POOL, html_encode_list
from Utility.Baidu_Message.Baidu_spider.Quanju_and_Pro import Quanju_Pro
from Utility.Baidu_Message.Baidu_article.Clean_time import Clean_time
from Utility.Baidu_Message.Common_code import get_md5, clear_source

requests.packages.urllib3.disable_warnings()


class Get_baidu_article():
    def __init__(self, args, send_type, error_count):
        self.args = args
        self.send_type = send_type
        self.UA = random.choice(UA_POOL)
        self.error_count = error_count
        self.quanju_pro = Quanju_Pro()

    def post_data_dict_format(self, page_data_dict):
        post_data_format = {
            "total": 1,
            "QTime": 0,
            "start": 1,
            "HTime": 0,
            "page": 1,
            "results": [
                {
                    # ID
                    'ID': page_data_dict['ID'],
                    # 任务ID
                    'TaskID': 0,
                    # 'TaskName': page_data_dict.get('TaskName', ''),
                    # 分组ID
                    'GroupID': 0,
                    # 博主名/公众号名  Author
                    'Name': '',
                    # 站点类型  1：百度，7：微博，14：微信
                    'SiteType': 1,
                    # 是否首页  1.网站首页 2.子版块首页
                    'Headline': 0,
                    # 是否境外
                    "Overseas": 0,
                    # 链接
                    'Url': page_data_dict['Url'],
                    # 标题
                    'Title': page_data_dict['Title'],
                    # 内容
                    'Content': page_data_dict['Content'],
                    # 来源    多个用竖线隔开（每个本身不分词）
                    # 'From': page_data_dict.get('From', ''),
                    # 发布时间
                    'Time': page_data_dict['Time'],
                    # 信源标签
                    'Tags': 0,
                    # 内容中的地域ID  DAreaWords  内容中出现的地点词
                    'Places': '',
                    # 话题ID
                    'TopicID': 0,
                    # 是否话题封面
                    'Cover': 0,
                    # 话题数量
                    'TopicCount': 0,
                    # 是否已存在相同文章 IsSame  0为没有相同文章  1为有相同文章。
                    'Reduplicate': 0,
                    # 博文ID
                    'BlogID': '',
                    # 内容提及的博主名  多个用竖线隔开
                    'At': '',
                    # 博主ID
                    'UID': '',
                    # 博主名
                    # 'Author': '',
                    # 性别
                    'Sex': 0,
                    # 省份
                    'Province': '',
                    # 城市
                    'City': '',
                    # 博主影响力级别
                    'Level': 0,
                    # 微博类型(验证类型)
                    'VerifiedType': 0,
                    # 是否原创  1.原创 0.转发 2.评论
                    'Original': 1,
                    # []ID
                    'QuoteUrl': '',
                    # []博文ID
                    'QuoteBlogID': '',
                    # []微博内容
                    'QuoteContent': '',
                    # []内容提及的博主名
                    'QuoteAt': '',
                    # []博主ID
                    'QuoteUID': '',
                    # []博主名
                    'QuoteAuthor': '',
                    # 新加
                    # 微博图片地址
                    'QuoteImageUrl': '',
                    # 微博发文时间
                    'QuoteTime': 0,
                    # 微博头像地址
                    'PortraitUrl': '',
                    # 带HTML标签的内容
                    'ContentSource': page_data_dict.get('ContentSource', ''),
                    # 公众号ID
                    'AccountID': '',
                    # 公众号名称
                    # 'Account': '',
                    # 公众号本身的标签
                    # 'Tag': '',
                    # 新版舆情分类
                    'DNSenWords': '',
                    # 添加时间
                    'AddOn': page_data_dict['AddOn'],
                    # 微博类型（有图无图之类的）
                    'WeiboType': '',
                    # 采集groupname
                    # 'GroupName': page_data_dict.get('GroupName', ''),
                    # 图片url
                    'ImageUrl': '',
                    # domain
                    'Domain': '',
                    # 公众号
                    'Account': '',
                    # 采集类型  微信 1：信源，2：元搜索  文章 0 信源 1 元搜索
                    'CrawlerType': 0,
                    'Keyword': page_data_dict.get('Keyword', ''),
                    # 粉丝
                    'Fans': 0,
                }
            ],
            "status": 0,
        }
        return post_data_format

    def get_article_html(self, url):
        '''获得编码格式正确后的源码'''
        headers = {
            "User-Agent": self.UA
        }
        try:
            res = requests.get(url=url, headers=headers, verify=False, timeout=60)
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            if res.status_code == 200:
                try:
                    result = res.json()
                    log.info(f"该url-{url}源码为json格式")
                    return
                except:
                    charset = re.search('<meta.*?charset(.*?)>', res.text)
                    if charset:
                        charset = re.sub('"|=|/', '', charset.group(1)).lower()
                        for html_encode in html_encode_list:
                            if html_encode in charset:
                                charset = html_encode
                        if charset == 'unicode':
                            charset = 'unicode_escape'
                        if 'huaxia' in url:
                            charset = 'gb2312'
                        result = res.content.decode(charset, 'ignore')
                    else:
                        try:
                            result = res.content.decode()
                        except:
                            result = res.text
            else:
                self.error_count += 1
                result = ""
                log.error(f"请求该url-{url}的详情页出错，状态码-{res.status_code}")
        except Exception as e:
            self.error_count += 1
            result = ""
            log.error(f'访问该url-{url}失败-原因-{str(e)}')
        return result

    def get_articel_detail(self, url):
        # print(url)
        '''对个别网站添加筛选条件，以正确获得所需数据，返回的data为字典'''
        extractor = GeneralNewsExtractor()
        result = self.get_article_html(url)
        if result:
            if 'sohu' in url:
                time_xpath = "//meta[@itemprop='datePublished']/@content"
                data = extractor.extract(result, time_xpath=time_xpath)
            elif 'www.cqn.com.cn' in url:
                noise_node_list = ['//div[@class="Detail_Statement"]']
                data = extractor.extract(result, noise_node_list=noise_node_list)
            elif '//auto.sina.com.cn' in url:
                noise_node_list = ['//div[@id="div2"]']
                content_rule = '//div[@id="artibody"]'
                data = extractor.extract(result, noise_node_list=noise_node_list, content_rule=content_rule)
            elif 'auto.sina.com' in url:
                noise_node_list = ['//div[@class="fm1000 foot"]', '//div[@class="artInfo"]', '//div[@class="tool"]']
                data = extractor.extract(result, noise_node_list=noise_node_list)
            elif 'tech.sina.com' in url:
                noise_node_list = ['//div[@class="tech-con"]']
                data = extractor.extract(result, noise_node_list=noise_node_list)
            elif 'news.iresearch.cn' in url:
                noise_node_list = ['//div[@class="g-box2"]']
                data = extractor.extract(result, noise_node_list=noise_node_list)
            elif 'sports.online.sh.cn' in url:
                time_re = '<date>(.*?)\.0</date>'
                data = extractor.extract(result, time_re=time_re)
            elif '36kr.com' in url:
                time_re = '"published_at":"(.*?)"'
                data = extractor.extract(result, time_re=time_re)
            elif 'auto.ifeng.com' in url:
                time_xpath = '//span[@id="pubtime_baidu"]/text()'
                data = extractor.extract(result, time_xpath=time_xpath)
            elif 'news.ifeng.com' in url:
                time_xpath = '//meta[@itemprop="uploadDate"]/@content'
                data = extractor.extract(result, time_xpath=time_xpath)
            elif 'tech.ifeng.com' in url or 'finance.ifeng.com' in url or 'fashion.ifeng.com' in url:
                time_xpath = '//meta[@name="og:time "]/@content'
                content_rule = '//div[@class="main_content-LcrEruCc"]'
                data = extractor.extract(result, time_xpath=time_xpath, content_rule=content_rule)
            elif 'ifeng.com' in url:
                time_xpath = '//meta[@name="og:time "]/@content | //span[@id="pubtime_baidu"]/text() | //meta[@itemprop="uploadDate"]/@content'
                data = extractor.extract(result, time_xpath=time_xpath)
            elif 'www.cqcb.com' in url:
                time_re = '<div class="post">(.*?)　来源'
                data = extractor.extract(result, time_re=time_re)
            elif 'cq.cbg.cn' in url:
                noise_node_list = ['//div[@class="zheren"]']
                data = extractor.extract(result, noise_node_list=noise_node_list)
            elif 'weather.com.cn' in url:
                noise_node_list = ['//div[@class="bottomFooter"]']
                data = extractor.extract(result, noise_node_list=noise_node_list)
            elif 'chinanews.com' in url:
                noise_node_list = ['//div[@id="top"]']
                data = extractor.extract(result, noise_node_list=noise_node_list)
            elif 'cq.cqnews.net' in url:
                content_rule = '//div[@class="left_news"]'
                data = extractor.extract(result, content_rule=content_rule)
            elif 'www.xy178.com' in url:
                time_re = '<div.*?padding-b10.*?</span>(\d+-\d+-\d+ \d+:\d+:\d+).*?<'
                data = extractor.extract(result, time_re=time_re)
            elif 'news.bitauto.com' in url:
                content_rule = '//div[@id="content_bit"]'
                data = extractor.extract(result, content_rule=content_rule)
            elif 'www.csdn.net' in url:
                time_xpath = '//div[@class="tit_bar"]/span[@class="ago"][1]/text()'
                content_rule = '//div[contains(@class,"news_content")]'
                data = extractor.extract(result, time_xpath=time_xpath, content_rule=content_rule)
            elif 'new.qq.com' in url:
                time_re = '"pubtime": "(.*?)"'
                data = extractor.extract(result, time_re=time_re)
            elif 'bio1000.com' in url:
                content_rule = '//article[@class="article-content"]'
                time_xpath = '//div[@class="article-meta"]/span[@class="item"][1]/text()'
                data = extractor.extract(result, content_rule=content_rule, time_xpath=time_xpath)
            elif 'baijiahao.baidu.com' in url:  # 百家号
                time_xpath = '//meta[@itemprop="dateUpdate"]/@content'
                noise_node_list = ['//div[@id="header_wrap"]', '//div[@id="right-container"]']
                data = extractor.extract(result, noise_node_list=noise_node_list, time_xpath=time_xpath)
            elif 'www.takefoto.cn' in url:
                title_xpath = '//h1[contains(@class,"arc_title")]/text()'
                content_rule = '//div[@id="post"]'
                data = extractor.extract(result, title_xpath=title_xpath, content_rule=content_rule)
            else:
                data = extractor.extract(result)
        else:
            data = ""
        return data

    def clean_title(self, data, url):
        '''清洗标题，清除多余符号'''
        data_title = data['title']
        if data_title:
            real_title = re.sub('\\r|\\n|\\t', '', data_title).strip()
        else:
            real_title = ''
            log.error(f"获取该-{url}的详情页的标题为空")
        return real_title

    def clean_time(self, data, url):
        '''清洗时间，获得正确格式的日期和时间戳'''
        data_time = data['publish_time']
        if data_time:
            time_date, timestamp = Clean_time().clean_time(data_time)
        else:
            time_date = ''
            timestamp = ''
            log.error(f"获取该-{url}的详情页的时间为空")
        return time_date, timestamp

    def clean_content(self, data, url, conthtml):
        '''清洗正文内容'''
        data_content = data['content']
        if data_content:
            real_content = re.sub('\\n', '', data_content)
        else:
            real_content = ''
            log.error(f"获取该-{url}的详情页的内容为空")
        last_real_content = clear_source(conthtml, url, real_content)
        return last_real_content

    def get_conthtml(self, data, url):
        '''拿取详情源码'''
        conthtml = data['conthtml']
        if conthtml:
            conthtml = re.sub(r'\\', '', conthtml)
        else:
            conthtml = ''
            log.error(f"获取该-{url}的详情源码为空")
        return conthtml

    def new_data(self, data, url):
        '''重新拼凑清洗后的数据'''
        real_title = self.clean_title(data, url)
        time_date, timestamp = self.clean_time(data, url)
        conthtml = self.get_conthtml(data, url)
        real_content = self.clean_content(data, url, conthtml)
        add_timestamp = int(time.time()) * 1000
        if real_title and time_date and real_content:
            new_data = {
                "ID": get_md5(url),
                'Title': real_title,
                'Content': real_content,
                'AddOn': add_timestamp,
                'Time': timestamp,
                "Url": url,
                'Language': 2052,
                'ContentSource': conthtml,
            }
            send_data_dict = self.post_data_dict_format(page_data_dict=new_data)
        else:
            send_data_dict = {
                "errors": {
                    'title': real_title or f'没有获得文章-{url}-标题，为空',
                    'time': time_date or f'没有获得文章-{url}-时间，为空',
                    'content': real_content.encode("gbk", "ignore").decode("gbk", "ignore") or f'没有获得文章-{url}-内容，为空'
                }
            }
            self.error_count += 1
            log.error(f"拼接新的data错误为空")

        # log.info(f'链接--{url}--拼接后的内容--{send_data_dict}')
        return send_data_dict

    def run(self):
        '''运行'''
        url = self.args['url']
        data = self.get_articel_detail(url)
        if data:
            new_data = self.new_data(data, url)
            return new_data, self.error_count
        else:
            log.error('没有正确获得data')
            return data, self.error_count


def baidu_article_main(args, send_type):
    get_baidu_article = Get_baidu_article(args, send_type, 0)
    new_data, error_count = get_baidu_article.run()
    return new_data


def test(args, send_type, words):
    # 测试
    error_counts = 0
    for word in words:
        args['word'] = word
        upload_data_dict = get(args, send_type)
        results = upload_data_dict['results']
        for result in results:
            url = result['Url']
            srgs = {
                'url': url
            }
            get_baidu_article = Get_baidu_article(srgs, send_type, 0)
            new_data, error_count = get_baidu_article.run()
            error_counts += error_count
            print(new_data)
    log.info(f'错误数量-{error_counts}')


if __name__ == '__main__':
    # words = ['广州', '皮肤', '伙伴', '冒险', '合作', '手游', '杭州', '豪车', '造型', '国内']
    # args = {
    #     'word': '',
    #     'rows': 30,
    #     'page': 1,
    #
    # }
    # send_type = 1
    # baidu_article_main(args,send_type)
    error_count = 0
    args = {
        'url': 'http://news.changsha.cn/xctt/html/110187/20200114/65709.shtml',
    }
    send_type = 1
    get_baidu_article = Get_baidu_article(args, send_type, error_count)
    new_data, error_count = get_baidu_article.run()
    log.info(f'数据--{json.dumps(new_data, ensure_ascii=False, indent=4)}')
    # print('错误数量',error_count)
