class Quanju_Pro():
    def __init__(self):
        '''全局和多合一的格式'''
        self.upload_data = {
            # 检索总数
            "total": 0,
            # 全局
            "quanju": [],
            # 三合一
            "pro": [],
        }
        self.common_dict = {
            "headers": {
                "topic": "baidu",
                "keyword": "",
                "timestamp": 0,
            },
            "body": {
                # 任务名
                'TaskName': '',
                # 链接
                'Url': '',
                # 标题
                'Title': '',
                # 内容
                'Content': '',
                # 时间
                'Time': 0,
                # 添加时间
                'AddOn': 0,
                # 站点语言(1.简体中文 2.繁体中文 3.英文 4.日文 5.韩文 6.藏语 7.蒙古语)
                'Language': 1,
                # 来源
                'From': '',
            }

        }

    def create_baidu_solr_dict(self, page_data_dict):
        # 百度多合一包字段
        baidu_solr_data = {
            # ID
            'ID': page_data_dict['ID'],
            # 任务ID
            'TaskID': 0,
            'TaskName': page_data_dict.get('TaskName', ''),
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
            'From': page_data_dict.get('From', ''),
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
            # 公众号本身的标签
            # 'Tag': '',
            # 新版舆情分类
            'DNSenWords': '',
            # 添加时间
            'AddOn': page_data_dict['AddOn'],
            # 微博类型（有图无图之类的）
            'WeiboType': '',
            # 采集groupname
            'GroupName': page_data_dict.get('GroupName', ''),
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
        return baidu_solr_data
