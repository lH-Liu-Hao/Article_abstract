import html as _html
from lxml import etree
from Utility.Baidu_Message.Baidu_article.gne.utils import pre_parse, remove_noise_node
from Utility.Baidu_Message.Baidu_article.gne.extractor import ContentExtractor, TitleExtractor, TimeExtractor, \
    AuthorExtractor


class GeneralNewsExtractor:
    def __init__(self):
        self.content_extractor = ContentExtractor()
        self.title_extractor = TitleExtractor()
        self.author_extractor = AuthorExtractor()
        self.time_extractor = TimeExtractor()

    def extract(self, html, title_xpath=None, title_re=None, time_xpath=None, time_re=None, noise_node_list=None,
                content_rule=None):
        element = pre_parse(html)
        cont_element = remove_noise_node(element, noise_node_list)
        content = self.content_extractor.extract(cont_element, content_rule, html)
        title = self.title_extractor.extract(title_xpath=title_xpath, title_re=title_re, html=html)
        publish_time = self.time_extractor.extractor(time_xpath=time_xpath, time_re=time_re, html=html)
        author = self.author_extractor.extractor(html=html)
        if content:
            content_zero = content[0]
            if content_zero:
                content_one = content_zero[1]
                if content_one:
                    content = content_one['text']
                    node = content_one['node']
                    conthtml = _html.unescape(etree.tostring(node, method='html').decode())
                else:
                    content = ''
                    conthtml = ''
            else:
                content = ''
                conthtml = ''
        else:
            content = ''
            conthtml = ''
        return {'title': title,
                'author': author,
                'publish_time': publish_time,
                'content': content,
                'conthtml': conthtml
                }
