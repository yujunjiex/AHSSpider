# coding: UTF-8
import requests

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

header = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.aihuishou.com/pc/index.html',
            # 'Origin': 'https://www.aihuishou.com',
            # 'Host': 'www.aihuishou.com',
            # 'source': 'pc'
}

# header = {
# 'Host': 'www.aihuishou.com',
# 'Connection': 'keep-alive',
# # 'Content-Length': '490',
# 'Accept': "*/*",
# 'Origin': 'https://www.aihuishou.com',
# 'X-Requested-With': 'XMLHttpRequest',
# 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
# 'Sec-Fetch-Mode': 'cors',
# 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
# 'Sec-Fetch-Site': 'same-origin',
# 'Referer': 'https://www.aihuishou.com/product/17944.html',
# 'Accept-Encoding': 'gzip, deflate, br',
# 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
# }
# from Tools.tools import *
# resp = post_request(post_url, data=data, cookies=cookies)


data = {
    'productId': 25220,
    'PpvIds': [3717, 5019, 6240, 6224, 2046, 3189, 2051, 2056, 6920,
               6922, 2752, 2049, 2039, 2445, 6910],
    # 'PhenomenonItemIds': [9511, 1974, 1976, 2489, 2670, 1992, 1998],
    "IsEnvironmentalRecycling": "false"
}

url = "https://www.aihuishou.com/product/25220.html"
post_url = "https://www.aihuishou.com/userinquiry/createnew"

cookies = requests.get(url, headers=header).cookies.get_dict()

resp = requests.post(post_url, headers=header, data=data, cookies=cookies)
# # print(type(resp))
print(resp.json())


# resp = get_response("http://ip.chinaz.com/")
# print(resp.text)
