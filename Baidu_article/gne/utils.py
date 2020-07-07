import re
from lxml.html import etree
from urllib.parse import urlparse, urljoin
from Utility.Baidu_Message.Baidu_article.gne.defaults import USELESS_TAG, TAGS_CAN_BE_REMOVE_IF_EMPTY, USELESS_ATTR, \
    HIGH_WEIGHT_ARRT_KEYWORD
from lxml.html import fromstring, HtmlElement


def normalize_node(element: HtmlElement):
    etree.strip_elements(element, *USELESS_TAG)
    for node in iter_node(element):
        # if node.tag.lower() in USELESS_TAG:
        #     remove_node(node)

        # inspired by readability.
        if node.tag.lower() in TAGS_CAN_BE_REMOVE_IF_EMPTY and is_empty_element(node):
            remove_node(node)

        # p 标签下面的 span 标签中的文字，可以合并到 p 标签中
        if node.tag.lower() == 'p':
            etree.strip_tags(node, 'span')
            etree.strip_tags(node, 'strong')

        # if a div tag does not contain any sub node, it could be converted to p node.
        if node.tag.lower() == 'div' and not node.getchildren():
            node.tag = 'p'

        if node.tag.lower() == 'span' and not node.getchildren():
            node.tag = 'p'

        # remove empty p tag
        if node.tag.lower() == 'p' and not node.xpath('.//img'):
            if not (node.text and node.text.strip()):
                drop_tag(node)

        class_name = node.get('class')
        if class_name:
            for attribute in USELESS_ATTR:
                if ' ' in class_name:  # 判断类名是否有多个以空格相隔，先切割，#构建列表
                    classnames = class_name.split(' ')
                else:
                    classnames = [class_name]  # 只有一个
                for name in classnames:  # 遍历列表中的类名，判断是否存在需删除的类名
                    if attribute == name:
                        remove_node(node)
                        break


def pre_parse(html):
    html = re.sub('</?br.*?>', '', html)
    element = fromstring(html)
    normalize_node(element)
    return element


def remove_noise_node(element, noise_xpath_list):
    if not noise_xpath_list:
        return element
    for noise_xpath in noise_xpath_list:
        nodes = element.xpath(noise_xpath)
        for node in nodes:
            remove_node(node)
    return element


def iter_node(element: HtmlElement):
    yield element
    for sub_element in element:
        if isinstance(sub_element, HtmlElement):
            yield from iter_node(sub_element)


def remove_node(node: HtmlElement):
    """
    this is a in-place operation, not necessary to return
    :param node:
    :return:
    """
    parent = node.getparent()
    if parent is not None:
        parent.remove(node)


def drop_tag(node: HtmlElement):
    """
    only delete the tag, but merge its text to parent.
    :param node:
    :return:
    """
    parent = node.getparent()
    if parent is not None:
        node.drop_tag()


def is_empty_element(node: HtmlElement):
    return not node.getchildren() and not node.text


def pad_host_for_images(host, url):
    """
    网站上的图片可能有如下几种格式：
    完整的绝对路径：https://xxx.com/1.jpg
    完全不含 host 的相对路径： /1.jpg
    含 host 但是不含 scheme:  xxx.com/1.jpg 或者  ://xxx.com/1.jpg
    :param host:
    :param url:
    :return:
    """
    if url.startswith('http'):
        return url
    parsed_uri = urlparse(host)
    scheme = parsed_uri.scheme
    if url.startswith(':'):
        return f'{scheme}{url}'
    if url.startswith('//'):
        return f'{scheme}:{url}'
    return urljoin(host, url)


def get_high_weight_keyword_pattern():
    return re.compile('|'.join(HIGH_WEIGHT_ARRT_KEYWORD), flags=re.I)
