# -*- coding: utf-8 -*-
import time
import requests
from Utility.Baidu_Message.log import log
from Utility.Baidu_Message.config import TOKEN_GET_API, TOKEN_TEST_API, TOKEN_CLIENT_ID, TOKEN_CLIENT_SECRET, \
    ADSL_APIURL, ADSL_USERNAME, ADSL_PASSWORD


class TokenGen:
    def __init__(self, client_id, client_secret, **kwargs):
        """
        :param client_id: 传入的个人 `client_id`
        :param client_secret: 传入的个人 `client_secret`
        :param kwargs:
        """
        self.flag = True
        self.timing = time.time()
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_data = {'client_id': client_id,
                           'client_secret': client_secret,
                           'grant_type': 'client_credentials',
                           'scope': 'getproxyip',
                           }
        # token获取API
        self.token_get_api = TOKEN_GET_API
        # token验证API
        self.token_test_api = TOKEN_TEST_API
        self.token = ''

    def get_token(self):
        """
        当flag为True时获取token
        当flag为False时 - token时效 > 1 hour重新获取新token
                       - token时效 < 1 hour直接返回旧token
        :return:
        """
        if not self.token or self.flag or time.time() - self.timing > 60 * 60:
            self.token = self._request_token()
            # 更新获取到的新token的时间
            self.timing = time.time()
        # 测试token是否可用
        self._test_token(new_token=self.token)
        if self.flag:
            return self.get_token()
        return self.token

    def _request_token(self):
        """
        请求获取token
        :return:
        """
        headers = {'Connection': 'close', }
        try:
            resp = requests.post(url=self.token_get_api, data=self.token_data, headers=headers, timeout=5)
            if resp.status_code == 200:
                resp_json = resp.json()
                return resp_json.get('token_type') + ' ' + resp_json.get('access_token')
        except requests.exceptions.RequestException:
            pass
        return None

    def _test_token(self, new_token):
        """
        测试token
        :param new_token:
        :return:
        """
        headers = {
            'Connection': 'close',
            'Authorization': new_token,
        }
        try:
            resp = requests.get(url=self.token_test_api, headers=headers, timeout=5)
            # 如果状态码401则token失效
            if resp.status_code == 401:
                self.flag = True
            # token可用
            else:
                self.flag = False
        # 验证过程中异常则视为不可用
        except Exception as e:
            log.error('测试token失败...{}'.format(e))
            self.flag = True


def get_ADSL_proxy():
    # 不使用代理 直接放回 {}
    # return {}
    # time.sleep(5)
    token_gen = TokenGen(client_id=TOKEN_CLIENT_ID, client_secret=TOKEN_CLIENT_SECRET)
    proxies = {}
    try:
        headers = {
            'Connection': 'close',
            'Authorization': token_gen.get_token(),
        }
        res = requests.get(url=ADSL_APIURL, headers=headers, timeout=15)
        ip = res.json().get('IP')
        port = res.json().get('Port')
        if ip and port:
            proxy = 'http://{}:{}@{}:{}'.format(ADSL_USERNAME, ADSL_PASSWORD, ip, port)
            proxies = {
                "http": proxy,
                "https": proxy,
            }
            # log.info('获取代理成功...{}'.format(proxies))
    except Exception as e:
        log.error('获取代理失败...{}'.format(e))
    return proxies


if __name__ == '__main__':
    # for i in range(3):
    #     temp_token = token_gen.get_token()
    #     log.info(temp_token)
    #     time.sleep(2)
    info_log.info(get_ADSL_proxy())
    url = 'https://www.toutiao.com/a6639533048863916552'
    # for i in range(100):
    #
    #     r = requests.get(url)
    #     print(r.text)
    get_adsl = get_ADSL_proxy()
    print(get_adsl)
    # r = requests.get(url, proxies=proxies)
    # print(r.text)
