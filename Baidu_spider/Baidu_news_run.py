import datetime
from Utility.Baidu_Message.Baidu_spider.Baidu_media_hundred_spider import Baidu_media_or_hundred


class Baidu_news_upload_data():
    def __init__(self, args, send_type, medium_type):
        self.args = args
        # send_type，1：全局，2：三合一
        self.send_type = send_type
        # 媒体网站 或 百家号
        self.medium_type = medium_type
        # 关键词
        self.keyword = self.args['word']
        # 页码
        # self.page = self.args['page']
        # # 任务id
        # self.task_id = self.task['TaskID']
        self.receive_page = self.args['page']
        self.type = ""
        self.rows = int(self.args['rows'])
        self.page = self.rows // 10
        if self.page == 0:
            self.page = 1

    def upload_data_format(self):
        # 构建最后数据返回的字典格式
        upload_data_dict = {
            "total": 0,
            "QTime": 0,
            "start": 1,
            "HTime": 0,
            "page": 1,
            "results": [],
            "status": 0,
        }
        return upload_data_dict

    async def baidu_run(self):
        '''构建最终上传格式'''
        upload_data_dict = self.upload_data_format()
        start_spider_time = datetime.datetime.now()
        baidu_media = Baidu_media_or_hundred(self.args, self.send_type)
        # 需要上传的数据和当前页数
        upload_data_pagenum = baidu_media.media_or_hundred_run(self.page)
        async for result in upload_data_pagenum:
            data_dict = result[0]
            total_count = result[1]
            upload_data_dict['results'].append(data_dict)
            upload_data_dict['QTime'] = (datetime.datetime.now() - start_spider_time).total_seconds() * 1000 // 1
            upload_data_dict['page'] = self.receive_page
            upload_data_dict['total'] = total_count
        # 返回最终上传的数据 --->返回前page_num页全部采集到的数据
        return upload_data_dict
