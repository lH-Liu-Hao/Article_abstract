import os
import time
from pathlib import Path
from loguru import logger


def get_log():
    '''
    创建Log文件夹，存储log文件，每个log文件最大存储70MB，超过70MB自动新建一个log文件，命名为当天时间具体到时钟，
    只存储五天内的log文件，超过5天的自动删除
    '''
    log_file_path = Path.cwd()
    str_log_path = os.fspath(log_file_path)
    log_file_path = f'{str_log_path}/Log'
    isexist = os.path.exists(log_file_path)
    if not isexist:
        os.mkdir(log_file_path)
    log_file_name = time.strftime('%Y-%m-%d %H', time.localtime(time.time()))
    log_path = f'{log_file_path}/{log_file_name}.log'
    logger.add(log_path, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                                "<level>{level: <8}</level> | "
                                "<cyan>{file}</cyan>:<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
               rotation="70 MB", retention='5 days', enqueue=True)
    return logger


log = get_log()
