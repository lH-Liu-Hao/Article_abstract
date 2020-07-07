import re
import html as _html
from lxml import etree
from lxml.html import HtmlElement
from Utility.Baidu_Message.Baidu_article.gne.utils import pre_parse
from Utility.Baidu_Message.Baidu_article.gne.defaults import DATETIME_PATTERN


class TimeExtractor:
    def __init__(self):
        self.time_pattern = DATETIME_PATTERN

    def extract_by_xpath(self, element, time_xpath, html):
        if time_xpath:
            time_list = element.xpath(time_xpath)
            if time_list:
                return time_list[0]
            else:
                doc = etree.HTML(html)
                time_list = doc.xpath(time_xpath)
                if time_list:
                    return time_list[0]
                else:
                    return ''
        return ''

    def extract_by_re(self, html, time_re):
        if time_re:
            time_group = re.search(time_re, html)
            if time_group:
                return time_group.group(1)
            else:
                time_group = re.search(time_re, html, re.S)
                if time_group:
                    return time_group.group(1)
                else:
                    return ''
        else:
            return ''

    def extract_by_time(self, element: HtmlElement):
        text = ''.join(element.xpath('//text()'))
        try:
            for dt in self.time_pattern:
                dt_obj = re.search(dt, text)
                if dt_obj:
                    return dt_obj.group(1).strip()
            else:
                return ''
        except Exception as e:
            print(f'时间默认取规则出错{e}')
            return ''

    def extractor(self, time_xpath, time_re, html):
        element = pre_parse(html)
        # conthtml = _html.unescape(etree.tostring(element,method='html').decode())
        time_date = self.extract_by_xpath(element, time_xpath, html) or self.extract_by_re(html,
                                                                                           time_re) or self.extract_by_time(
            element)
        return time_date
