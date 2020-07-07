import re
from Utility.Baidu_Message.Baidu_article.gne.utils import pre_parse
from lxml.html import HtmlElement
from Utility.Baidu_Message.Baidu_article.gne.defaults import AUTHOR_PATTERN


class AuthorExtractor:
    def __init__(self):
        self.author_pattern = AUTHOR_PATTERN

    def extractor(self, html):
        element = pre_parse(html)
        text = ''.join(element.xpath('.//text()'))
        for pattern in self.author_pattern:
            author_obj = re.search(pattern, text)
            if author_obj:
                return author_obj.group(1)
        return ''
