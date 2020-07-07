import re
import time
import json
import requests
import random
import aiohttp
import html as _html
from lxml import etree
from Utility.Baidu_Message.log import log
from Utility.Baidu_Message.Get_time import get_real_time
from Utility.Baidu_Message.Get_ADSL_Proxy import get_ADSL_proxy
from Utility.Baidu_Message.config import UA_POOL
from Utility.Baidu_Message.Common_code import get_md5
from Utility.Baidu_Message.Baidu_spider.Quanju_and_Pro import Quanju_Pro

requests.packages.urllib3.disable_warnings()


class Baidu_base():
    def __init__(self, args, send_type):
        self.args = args
        self.keyword = self.args['word']
        self.sum_content_count = 0
        self.sum_error_content_count = 0
        self.real_page = 1
        self.proxy = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            "Host": "www.baidu.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
        }
        self.headers['User-Agent'] = random.choice(UA_POOL)
        self.medium = 1
        self.url = f"http://www.baidu.com/s?ie=utf-8&cl=2&rtt=1&bsst=1&rsv_dl=news_b_pn&tn=news&wd={self.keyword}&medium={self.medium}&pn="
        # 上传数据的类型--全局或三合一
        self.send_type = send_type
        self.max_page = 0
        self.logger = log

    def send_type_dict(self, page_data_dict):
        Quanju_and_Pro = Quanju_Pro()

        # #上传数据全局格式
        # if self.send_type == 1:
        #     send_type_dict = Quanju_and_Pro.common_dict
        # #上传数据其中三合一格式
        # else:
        #     commit_dict = Quanju_and_Pro.common_dict
        #     commit_dict['headers']['topic'] = "probaidu"
        #     send_type_dict = commit_dict
        send_type_dict = Quanju_and_Pro.create_baidu_solr_dict(page_data_dict)
        return send_type_dict

    async def get_cont(self, con_html, xpath_rule):
        '''
        xpath规则获取多个标签下的文本，再组合在一起
        :param con_html:
        :param xpath_rule:
        :return:
        '''
        doc = etree.HTML(con_html)
        con = doc.xpath(xpath_rule)
        content = "".join(x.strip() for x in con)
        return content

    async def exp_code(self, field, url, e, error_count, count):  # 抽取出错后的通用代码
        self.logger.exception(f'获取{field}字段出现错误--当前页面url-->{url}-->错误原因-->{e}')
        error_count += 1
        count += 1

    async def get_res(self, url, page_num=0, page_datas=None):
        '''获得element对象和源码'''
        # 抽取请求的通用代码
        real_page = page_num + 1
        if self.proxy:
            proxy = get_ADSL_proxy()['http']
        else:
            proxy = ""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, verify_ssl=False, proxy=proxy) as res:
                    if res.status != 200:
                        self.logger.info(f"请求第{real_page}页失败--url-->{url}--状态码-->{res.status}")
                        return page_datas
                    real_result = await res.text()
                    doc = etree.HTML(real_result)
            return doc, real_result
        except Exception as e:
            self.logger.exception(f"在{self.medium_type}请求第{real_page}页获得response失败--url-->{url}--原因-->{str(e)}")

    async def comback(self, page_num, num):
        # 回调函数
        real_page_datas = []
        real_page = page_num - num
        for page in range(real_page):
            pn = page * 10
            sub_url = re.sub('medium=(.*?)&', f'medium={self.medium}&', self.url)
            real_url = sub_url + str(pn)
            page_datas = await self.parse_page(real_url, real_page)
            real_page_datas.append(page_datas)
        return real_page_datas

    async def the_page_exist(self, url, page_num, page_datas):
        '''对该关键词进项判断是否有相关资讯，得出最大页码'''
        doc_result = await self.get_res(url, page_num, page_datas)
        doc = doc_result[0]
        real_result = doc_result[1]
        news_total_num = re.search('找到相关资讯约(.*?)篇', real_result)
        if news_total_num == 0:
            self.logger.info(f"该关键词{self.keyword}没有找到相关资讯")
            return page_datas, 0
        the_page_exist = doc.xpath('//p[@id="page"]//span[@class="pc"]/text()')
        if the_page_exist:
            self.max_page = int(the_page_exist[-1].strip())
        else:
            self.max_page = 1

    async def get_last_page_count(self, url):
        '''
        获得数据的总数目，最多100条，请求最后一页统计最后一页的数目，加上前面数量即总数目
        :param url:
        :return:
        '''
        doc_result = await self.get_res(url)
        doc = doc_result[0]
        the_page_exist = doc.xpath('//p[@id="page"]//span[@class="pc"]/text()')
        if the_page_exist:
            max_page = int(the_page_exist[-1].strip())
        else:
            max_page = 1
        pn = (max_page - 1) * 10
        url = self.url + str(pn)
        doc_result = await self.get_res(url)
        doc = doc_result[0]
        count = len(doc.xpath('//div[@class="result"]'))
        total_count = (max_page - 1) * 10 + count
        return total_count

    async def parse_page(self, url, page_num):
        '''
        获取每一页的数据
        :param url:
        :return:
        '''
        if self.medium == 1:
            self.medium_type = "媒体网站"
        else:
            self.medium_type = "百家号"
        self.real_page = page_num + 1
        # 详情数量
        content_count = 0
        # 失败详情数量
        error_content_count = 0
        # 该页的全部数据
        page_datas = []
        doc_result = await self.get_res(url, page_num, page_datas)
        doc = doc_result[0]
        await self.the_page_exist(url, page_num, page_datas)
        # 判断页数是否大于最大请求页10,当page_num=9,实际页数第10页
        if page_num > 9:
            self.logger.info(f'请求的页数已经大于10页--在{self.medium_type}')
            if self.medium == 1:
                self.medium = 2
            else:
                return page_datas
            num = 9
            page_datas = await self.comback(page_num, num)
            return page_datas
        # 判断请求的页数是否大于搜索到的关键词的实际页数
        real_page_num = page_num + 1
        if real_page_num > self.max_page:
            self.real_page = 1
            if self.medium == 2:
                self.logger.info(f'已经请求完该关键词{self.keyword}的全部页码，无更多数据')
            self.logger.info(f"请求的页数大于在--{self.medium_type}--{self.keyword}--的实际页数---实际页数{self.max_page}")
            # 当能在媒体网站拿到任意数据都不再去请求百家号
            if self.sum_content_count % 10 == 0:
                self.medium = 2
                self.medium_type = "百家号"
                num = self.max_page
                page_datas = await self.comback(page_num, num)
            else:
                self.logger.info(f"暂不提供百家号数据--{self.keyword}")
            return page_datas
        try:
            every = doc.xpath('//div[@class="result"]')
            for every_one in every:
                one_html = _html.unescape(etree.tostring(every_one, method="html").decode())
                one_doc = etree.HTML(one_html)
                try:
                    title = await self.get_cont(one_html, '//h3[@class="c-title"]/a//text()')
                except Exception as e:
                    await self.exp_code("标题", url, e, self.sum_error_content_count, error_content_count)
                    continue
                try:
                    url = one_doc.xpath('//h3[@class="c-title"]/a/@href')[0].strip()
                except Exception as e:
                    await self.exp_code("文章详情url", url, e, self.sum_error_content_count, error_content_count)
                    continue
                try:
                    source_and_time = one_doc.xpath('//p[@class="c-author"]//text()')
                    source_and_time_con = ''.join(x.strip() for x in source_and_time)
                    source, false_time = source_and_time_con.split(" ", 1)
                    From = source.strip()
                    time_date, timestamp = get_real_time(false_time.strip())
                except Exception as e:
                    await self.exp_code("来源和时间", url, e, self.sum_error_content_count, error_content_count)
                    continue
                try:
                    content = await self.get_cont(one_html,
                                                  '//div[contains(@class,"c-summary")]/text() | //div[contains(@class,"c-summary")]/em/text()')
                except Exception as e:
                    await self.exp_code("内容", url, e, self.sum_error_content_count, error_content_count)
                    continue
                add_timestamp = int(time.time()) * 1000
                content_html = re.sub('[\n\r\t]', '', one_html)
                page_data_dict = {
                    "ID": get_md5(url),
                    'TaskName': From,
                    'GroupName': From,
                    'AddOn': add_timestamp,
                    "Title": title,
                    "Url": url,
                    "Time": timestamp,
                    "Content": content,
                    "From": From,
                    # 站点语言(1.简体中文 2.繁体中文 3.英文 4.日文 5.韩文 6.藏语 7.蒙古语)
                    'Language': 2052,
                    'Keyword': self.keyword,
                    'ContentSource': content_html,
                }
                send_type_dict = self.send_type_dict(page_data_dict)
                page_datas.append(send_type_dict)
                self.sum_content_count += 1
                content_count += 1
        except Exception as e:
            self.logger.exception(f'获取所需字段出现未匹配成功或其他错误--当前页面url-->{url}-->错误原因-->{e}')
        # print('数据****',page_datas)
        return page_datas

    async def parse_turn_page(self, page):
        '''翻页'''
        url = self.url + '0'
        total_count = await self.get_last_page_count(url)
        try:
            for page_num in range(page):  # 循环获取全部页数的数据
                pn = page_num * 10  # 单获取当前页数的数据
                url = self.url + str(pn)
                page_datas = await self.parse_page(url, page_num)
                yield page_datas, total_count
        except Exception as e:
            self.logger.exception(f'循环请求失败--错误原因--{e}')
        self.logger.info(f'实际请求第{page}页完成')

    async def run(self, page):
        '''
        将每一页的数据返回
        '''
        page_datas_count = self.parse_turn_page(page)
        async for i in page_datas_count:
            page_datas = i[0]
            total_count = i[1]
            if page_datas:
                for data_dict in page_datas:
                    yield data_dict, total_count
        self.logger.info(f"{page}页最终成功获取到的详情数量--{self.sum_content_count}条")


if __name__ == "__main__":
    task = {"keyword": "广州", "GroupID": "325645", "TaskID": "256455"}
    keyword = task['keyword']
    medium = 1
    baidu_base = Baidu_base(task)
    page = '10'
    collect_type = "百度_媒体网站"
