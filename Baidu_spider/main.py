import time
import asyncio
from Utility.Baidu_Message.Baidu_spider.Baidu_news_run import Baidu_news_upload_data
from Utility.Baidu_Message.log import log as logger


# 协程
def async_run(args, send_type, medium_type):
    '''运行'''
    logger.info("调用协程开始")
    baidu_news_upload_data = Baidu_news_upload_data(args, send_type, medium_type)
    baidu_run = baidu_news_upload_data.baidu_run()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        upload_data_dict = loop.run_until_complete(baidu_run)
        return upload_data_dict
    finally:
        loop.close()


def get(args, send_type):
    # print(args)
    medium_type = 1
    startime = time.time()
    upload_data_dict = async_run(args, send_type, medium_type)
    endtime = time.time()
    need_time = endtime - startime
    logger.info(f"调用协程完成---所用时间{need_time}")
    return upload_data_dict
