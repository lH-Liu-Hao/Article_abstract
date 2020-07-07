import re
from Utility.Baidu_Message.Baidu_article.gne.utils import pre_parse
from lxml.html import HtmlElement
from Utility.Baidu_Message.Baidu_article.gne.defaults import TITLE_HTAG_XPATH, TITLE_SPLIT_CHAR_PATTERN


class TitleExtractor:
    def extract_by_xpath(self, element, title_xpath):
        if title_xpath:
            title_list = element.xpath(title_xpath)
            if title_list:
                return title_list[0]
            else:
                return ''
        return ''

    def extract_by_re(self, html, title_re):
        if title_re:
            title_group = re.search(title_re, html)
            if title_group:
                return title_group.group(1)
            else:
                return ''
        return ''

    def extract_by_title(self, element):
        title_list = element.xpath('//meta[@property="og:title"]/@content')
        if not title_list:
            title_list = element.xpath('//title/text()')
            if not title_list:
                return ''
        title = re.split(TITLE_SPLIT_CHAR_PATTERN, title_list[0])
        if title:
            return title[0]
        else:
            return ''

    def extract_by_htag(self, element):
        title_list = element.xpath(TITLE_HTAG_XPATH)
        if not title_list:
            return ''
        return title_list[0]

    def extract(self, title_xpath, title_re, html):
        element = pre_parse(html)
        title = self.extract_by_xpath(element, title_xpath) or self.extract_by_re(html,
                                                                                  title_re) or self.extract_by_title(
            element) or self.extract_by_htag(element)
        return title
