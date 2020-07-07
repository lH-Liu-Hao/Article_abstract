from Utility.Baidu_Message.Baidu_spider.Baidu_base_spider import Baidu_base
from Utility.Baidu_Message.log import log


class Baidu_media_or_hundred(Baidu_base):

    def __init__(self, args, send_type):
        super().__init__(args, send_type)

    async def media_or_hundred_run(self, page):
        '''调用run，生成器形式返回'''
        upload_data = self.run(page)
        async for upload_data_dict in upload_data:
            yield upload_data_dict


if __name__ == "__main__":
    task = {"keyword": "广州", "GroupID": "325645", "TaskID": "256455"}
    baidu_media_hundred = Baidu_media_or_hundred(task)
    aa = baidu_media_hundred.media_or_hundred_run("10", 1)
    print(aa)
