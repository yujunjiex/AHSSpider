# coding: UTF-8
"""
工具类
https://github.com/jhao104/proxy_pool
在使用前需配置好上面的代理ip池
并需要购买"高匿代理"以进行不间断爬取
"""
import requests
from lxml import etree
import random
from requests.exceptions import Timeout, RequestException
import time
# import chardet



user_agent_list = [
    'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0)',
    'Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT6.0)',
    'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11',
    'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36'
]


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def get_response(url, retry_count=10, cookies=None):
    ip = get_proxy()    # 获取代理ip
    proxy = {'https': "https://{}".format(str(ip, encoding="utf-8"))}
    while retry_count > 0:
        header = {'User-Agent': random.choice(user_agent_list),
                  'Referer': 'www.aihuishou.com',
                  'Connection': 'keep-alive',
                  'Accept': "*/*",
                  'Origin': 'https://www.aihuishou.com',
              }
        # print("当前代理ip:{}".format(proxy))
        try:
            # 使用代理访问
            resp = requests.get(
                url,
                headers=header,
                proxies=proxy,
                timeout=6,
                cookies=cookies
            )
            if resp.status_code == 502:
                raise RequestException("502 badGateWay")
            return resp

        except (RequestException, Timeout) as e:
            print("{}, 切换到下一个代理ip进行处理".format(e))
            delete_proxy(ip)  # 删除有问题的代理ip
            ip = get_proxy()  # 获取代理ip
            proxy = {'https': "https://{}".format(str(ip, encoding="utf-8"))}
            retry_count -= 1

        except Exception as e:
            print(e)
            retry_count -= 1
    # 出错n次, 删除代理池中代理
    # delete_proxy(proxy)
    return None


def post_request(url, data, retry_count=10, cookies=None):
    ip = get_proxy()    # 获取代理ip
    proxy = {'https': "https://{}".format(str(ip, encoding="utf-8"))}
    # proxy = {'https': "http://180.124.36.47:20968"}
    # proxy = {'https': "http://111.74.220.112:4217"}
    while retry_count > 0:
        header = {'User-Agent': random.choice(user_agent_list),
                  'Referer': 'www.aihuishou.com',
                  'Connection': 'keep-alive',
                  'Accept': "*/*",
                  'Origin': 'https://www.aihuishou.com',
                  # 'Accept-Encoding': 'gzip, deflate, br',
                  # 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                  # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                  # 'Sec-Fetch-Site': 'same-origin',
                  # 'X-Requested-With': 'XMLHttpRequest'
                  }
        # print("当前代理ip:{}".format(proxy))
        try:
            # 使用代理访问
            resp = requests.post(
                url,
                headers=header,
                data=data,
                proxies=proxy,
                timeout=6,
                cookies=cookies
            )
            if resp.status_code == 502:
                raise RequestException("502 badGateWay")
            return resp

        except (RequestException, Timeout) as e:
            print("{}, 切换到下一个代理ip进行处理".format(e))
            delete_proxy(ip)  # 删除有问题的代理ip
            ip = get_proxy()  # 获取代理ip
            proxy = {'https': "http://{}".format(str(ip, encoding="utf-8"))}
            retry_count -= 1

        except Exception as e:
            print(e)
            retry_count -= 1
    # 出错n次, 删除代理池中代理
    # delete_proxy(proxy)
    return None


def parse_category(response):
    html = etree.HTML(response.text)
    # 解析分类的url

    categorys = html.xpath(r"//div[@class='main-right']//ul/li/a")

    category_dict = {}
    for brand in categorys:
        category_dict[brand.xpath("./p/text()")[0].strip()] = brand.xpath("./@href")[0]
    return category_dict


def parse_product(response):
    """解析一页的product_url"""
    html = etree.HTML(response.text)

    product_urls = html.xpath(r'//div[@class="product-list-wrapper"]/ul/li/a/@href')
    return product_urls


def parse_property(response):
    """解析商品的property"""
    html = etree.HTML(response.text)

    base_propertys = html.xpath(r"//div[@id='base-property']/dl/@data-value")
    return base_propertys

