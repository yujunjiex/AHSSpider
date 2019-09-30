# coding: UTF-8
"""爱回收平台的信息爬取"""
import re
import jsonpath
from collections import defaultdict
from itertools import product
import sys
import threading
import pymongo
from Tools.tools import *
import logging
from AHS.loggers.core_logger import setup_logging

setup_logging('./loggers/config.yaml')
logger = logging.getLogger('core')

client = pymongo.MongoClient(host="127.0.0.1", port=27017)

base_url = "https://www.aihuishou.com"

# 属性api
base_property_api = "https://www.aihuishou.com/portal-api/product/inquiry-detail-new/{}"
quick_query_api = "https://www.aihuishou.com/portal-api/product/quick-inquiry?productId={}"


# 商品的根路径
laptop_url = "https://www.aihuishou.com/laptop"  # 笔记本品牌b52, 页数-p2
tablet_url = "https://www.aihuishou.com/pingban"
goods_url = {
    "tablet": tablet_url,
    "laptop": laptop_url
}

# 商品品牌关键字
tablet_brand_need = ("小米", "华为")  # 平板电脑关键字
# laptop_brand_need = ("戴尔", )  # 笔记本关键字
laptop_brand_need = ("荣耀", "麦本本", "火影", "机械师", "雷神", "炫龙", "雷蛇", "Terrans Force", "msi微星", "三星", "机械革命",
                     "Alienware", "华为", "微软", "小米", "惠普", "神舟", "戴尔", "宏基", "Thinkpad", "联想", "华硕")# , "联想", "华硕")  # 笔记本关键字

brand_need = {"tablet": tablet_brand_need, "laptop": laptop_brand_need}

# 关键属性(通过get_property获得)
tablet_essential_words = ("储存容量", "内存", "网络模式")
laptop_essential_words = ("处理器", "机械硬盘", "固态硬盘", "显卡", "内存", "屏幕类型")
essential_words = {
    "tablet": tablet_essential_words,
    "laptop": laptop_essential_words
}

# 商品-数据库名
AHS_database = {
    "tablet": "AHSTablet",
    "laptop": "AHSLaptop"
}

# 商品类型-商品页url中的参数（比如联想笔记本电脑第10页商品: /product/c5-b105-p10）
flag_dict = {
    "laptop": "c5",
    "tablet": "c6"
}


def parse_ppvid(params, names, ppvids):
    """
    得到ppvid组合对应的name-value(比如处理器-Intel 酷睿 i5 6代)
    :param params: 存放property信息的字典
    :param names: property所有的name(例如处理器，显卡)
    :param ppvids: ppvid组合
    :return: name-value字典
    For Example: {"处理器": "Intel 酷睿 i5 6代", "显卡": "核芯/集成显卡" ...}
    """
    name_to_value = {}
    for index, ppvid in enumerate(ppvids):
        name = names[index]
        for value_item in params[name]:
            if value_item['id'] == ppvid:
                name_to_value[name] = value_item['value']

    return name_to_value


def filter_propertys(info: dict, type="laptop"):
    """
    进行属性信息的筛选
    :param info:
    :param type:
    :return:
    """
    keywords = essential_words[type]
    filter_info = {}
    for name, value in info.items():
        name = name.strip()
        if name in keywords:
            filter_info[name] = value
    return filter_info


def combination_propertys(params, type="laptop"):
    """
    组合property的可能情况
    :param params: 存放property信息的字典
    :return:
    """
    loop_val = []  # 所有property的id集合
    names = []  # 按顺序存放所有的name(例如处理器，显卡)
    for name, value_items in params.items():
        names.append(name)

        if name.strip() in essential_words[type]:
            sub_list = []   # 存放一种property的id集合

            for value_item in value_items:
                sub_list.append(value_item["id"])
            loop_val.append(sub_list)
        else:
            if name.strip() == "边框背板":  # 边框背板选择外壳无划痕
                sub_list = [value_items[1]["id"]]
            else:
                sub_list = [value_items[0]["id"]]  # 其他property默认选第一种情况
            loop_val.append(sub_list)

    all_ppvids = list(product(*loop_val))  # 所有的组合情况
    # for ppvids in all_ppvids:
    total = len(all_ppvids)

    if total > 20:
        for i in range(0, total, total // 10):  # 只取10个间隔数
            ppvids = all_ppvids[i]
            yield ppvids, parse_ppvid(params, names, ppvids)
    else:
        for ppvids in all_ppvids:
            yield ppvids, parse_ppvid(params, names, ppvids)
    # ppvid_test = all_PpvIds[0]
    # print(ppvid_test)
    # name_to_value = parse_ppvid(params, names, ppvid_test)
    # print(name_to_value)


def parse_params(product_id: str, type='laptop'):
    """
    解析查询价格需要的属性参数 PpvIds PhenomenonItemIds(这里默认不填)
    :param product_id:
    :param type: 商品类型
    :return:
    """
    all_params = defaultdict(list)  # 用于组合多种情况
    quick_api_json = get_response(quick_query_api.format(product_id)).json()
    if quick_api_json['code'] == 0:  # 存在quick_api信息
        name = quick_api_json['data']['name']
        value = quick_api_json['data']['items'][0]['name']
        ppvs = quick_api_json['data']['items'][0]['ppvs'][0]
        all_params[name].append({'value': value, 'id': ppvs})

    base_api_json = get_response(base_property_api.format(product_id)).json()
    if base_api_json['code'] == 0:  # 存在base_api信息
        print(base_api_json['data']['product']['name'])  # 产品型号
        property_list = base_api_json['data']['propertyNames']
        for _property in property_list:
            name = _property['name']
            property_value = _property['values']
            for _property_value in property_value:
                value = _property_value["value"]
                ppvs = _property_value['ppvIds'][0]
                all_params[name].append({'id': ppvs, 'value': value})

    yield from combination_propertys(all_params, type)


def get_product_cookie(product_id: str):
    """
    返回某个商品页的cookie
    :param product_id:  产品id即pid
    :return: pid, cookie
    """
    product_url = base_url + "/product/{}.html".format(product_id)
    product_resp = get_response(product_url)
    if product_resp is None:
        return None
    # # 解析pid
    # html = etree.HTML(product_resp.text)
    # pid = html.xpath(r'//div[@class="right"]/div[contains(@class, "footer")]/a/@data-pid')[0]
    cookies = product_resp.cookies.get_dict()

    return cookies


def send_post_request(pid, PpvIds, IsEnvironmentalRecycling="false"):
    """
    模拟发送post请求，响应是重定向的url
    :param pid: 就是product_id
    :param PpvIds: 一个ppvid可能的组合情况, 一个组合对应一个报价
    :param IsEnvironmentalRecycling: 默认"false"即可
    :return:
    """
    # TODO: 不能用一个cookie去访问所有的PpvIds组合 因为一种商品的组合数太多 很有可能会被封掉, 所以这里每post一次都请求一次新的cookie 或者用cookie池
    post_url = "https://www.aihuishou.com/userinquiry/createnew"

    cookies = get_product_cookie(pid)
    # time.sleep(3)  # 拿到cookie后等待两秒发送post请求
    data = {
        'productId': pid,
        'PpvIds': PpvIds,
        'IsEnvironmentalRecycling': IsEnvironmentalRecycling
    }
    # r = requests.post(post_url, data=data, headers=self.headers)
    r = post_request(post_url, data=data, cookies=cookies)
    if r is None:
        return None
    # time.sleep(1)
    try:
        print(r.json())
        if r.json()['code'] != 0:
            return None
    except Exception as e:
        logger.debug(e)
        return None
    # 解析响应中的重定向url
    return parse_price_url(r)


def parse_price_url(r):
    """
    解析重定向url， 构造价格的url
    :param r: post返回的response
    :return:
    """
    jsonobj = r.json()
    price_url = jsonobj['data']['redirectUrl']
    # price_url 的格式是/pc/index.html#/inquiry/6534929115267980857
    # 截取url的inquiry后面的部分6534929115267980857
    # TODO:存在无报价的情况
    if "Noprice" in price_url:
        return None
    key = price_url.split('/')[-1]
    # 构造请求价格json的url'https://www.aihuishou.com/portal-api/inquiry/9138426214174445089'
    price_url = 'https://www.aihuishou.com/portal-api/inquiry/' + key
    # 发送请求
    r = get_response(price_url)
    if r is None:
        return None

    return parse_price(r)


def parse_price(r):
    """解析价格相关的信息"""
    jsonobj = r.json()
    print(jsonobj)
    if jsonobj['code'] != 0:
        return None
    price = jsonpath.jsonpath(jsonobj, r'$.data.amount')[0]
    product_id = jsonpath.jsonpath(jsonobj, r'$.data.product.productId')[0]
    product_name = jsonpath.jsonpath(jsonobj, r'$.data.product.productName')[0]

    return price, product_name, product_id


def insert_to_mongodb(database_name='AHSLaptop', model_name=None, info_dict=None):
    global client
    assert model_name is not None
    assert type(info_dict) is dict
    db = client[database_name]
    db[model_name].insert_one(info_dict)


def process_product_urls(product_urls: list, model_name: str, type="laptop"):
    """处理某一页的商品信息并进行一系列处理后插入数据库中"""
    for product_url in product_urls:
        pid = re.findall(r"\d+", product_url)[0]  # 商品id
        total_item = []
        for ppvids, info in parse_params(pid, type):
            result = send_post_request(pid, ppvids)
            if result is None:
                continue
            price = result[0]
            product_name = result[1]
            product_id = result[2]
            if price == 2:   # 报价两元的多为不合理报价
                continue
            item = {
                "型号": product_name,
                "id": product_id,
                "报价": price
            }
            for k, v in filter_propertys(info, type).items():  # 把筛选过的属性信息也插入进去
                item[k] = v
            print(item)
            total_item.append(item)
            # insert_to_mongodb(database_name=AHS_database[type], model_name=model_name, info_dict=item)
        for item in total_item:
            insert_to_mongodb(database_name=AHS_database[type], model_name=model_name, info_dict=item)


def process_brand_url(brand_name, brand_url, kind, begin_page=None, singer_brand_mode=False):
    """
    处理一种品牌的所有报价信息
    :param brand_name: 品牌名
    :param brand_url: 品牌商品链接
    :param kind: 商品类型(比如laptop)
    :param begin_page: 从第几页开始
    :param singer_brand_mode: 是否开启单个品牌多线程处理任务(每页一个线程)
    :return:
    """

    url = base_url + brand_url
    resp = get_response(url)
    pages = etree.HTML(resp.text).xpath(r"//div[@class='product-list-pager']//a[contains(@class,'page')][last()]/text()")[
        0]  # 拿到总页数
    logger.error(f"{brand_name}的总页数{pages}")
    if begin_page is None:
        begin_page = 1
    # TODO: 对if-else中的逻辑封装成一个函数，并一页开一个子线程来处理
    if singer_brand_mode is True:
        start_singer_brand_mode(url, brand_name, begin_page=begin_page, end_page=int(pages), kind=kind)
    else:
        for page in range(begin_page, int(pages) + 1):
            logger.debug(f"{brand_name}:正在解析第{page}页")
            if page == 1:
                product_urls = parse_product(resp)
                print(product_urls)
                process_product_urls(product_urls, model_name=brand_name, type=kind)  # 把品牌名和处理的品牌类型放入

            else:
                # 拼接从第二页开始的url
                # sub_url = url + "-p" + str(page)  # 如果用这种规则匹配，在第10-19页的url规则不一样。(而平板可以用这种规则适配，因为数量不多)
                sub_url = "https://www.aihuishou.com/product/{}-{}-p{}".format(flag_dict[kind], url.split("/")[-1], str(page))   # 笔记本c5，平板c6
                resp = get_response(sub_url)
                product_urls = parse_product(resp)
                print(product_urls)
                process_product_urls(product_urls, model_name=brand_name, type=kind)


def start_singer_brand_mode(base_url: str, brand_name: str, begin_page: int, end_page: int, kind: str):
    """
    一页开启一个子线程来处理，适合单品牌页数不多的情况
    :param base_url:
    :param brand_name:
    :param begin_page:
    :param end_page:
    :param kind:
    :return:
    """
    flag_dict = {
        "laptop": "c5",
        "tablet": "c6"
    }
    threads = []
    for page in range(begin_page, end_page + 1):
        logger.debug(f"{brand_name}:正在解析第{page}页")
        # 拼接url
        # sub_url = url + "-p" + str(page)  # 如果用这种规则匹配，在第10-19页的url规则不一样且不能用于第一页。(而平板可以用这种规则适配，因为数量不多)
        sub_url = "https://www.aihuishou.com/product/{}-{}-p{}".format(flag_dict[kind], base_url.split("/")[-1], str(page))   # 笔记本c5，平板c6
        resp = get_response(sub_url)
        product_urls = parse_product(resp)
        print(product_urls)
        thread = threading.Thread(target=process_product_urls,
                                  args=(product_urls, brand_name, kind,))
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for t in threads:
        t.join()


def main(kind='laptop', begin_pages=None, singer_brand_mode=False):
    """
    主入口
    :param kind: 要爬取的商品类型
    :param begin_pages: 开始页的字典(比如 {'三星': 9}, 三星就从第9页开始爬取)
    :param singer_brand_mode: 默认为False, 如果为True, 则会对单个品牌分页任务(每页一个线程), 适合对少量品牌页数不多的情况
    :return:
    """
    response = get_response(goods_url[kind])  # 解析笔记本/平板/..
    brand_dict = parse_category(response)  # 拿到所有品牌的url
    print(brand_dict)
    start_multi_thread(brand_dict, kind=kind, begin_pages=begin_pages, singer_brand_mode=singer_brand_mode)


def start_multi_thread(brand_dict: dict, kind: str, begin_pages: dict = None, singer_brand_mode=False):
    """
    多线程来处理任务
    :param begin_pages:
    :param brand_dict: {品牌名: 品牌url}
    :param kind: 品牌类型
    :return:
    """
    threads = []
    logger.error("\n")
    for key, value in brand_dict.items():
        if key not in brand_need[kind]:  # 只获取所需品牌的数据
            continue
        if begin_pages is not None:
            begin_page = begin_pages[key]
        else:
            begin_page = None
        thread = threading.Thread(target=process_brand_url,
                                  args=(key, value, kind, begin_page, singer_brand_mode,), name=key)  # 可以创建一个品牌名-页数的字典，实现程序中断还可以继续运行
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for t in threads:
        t.join()


def install_except_hook():
    """把未捕获的异常输入到logging"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):  # ctrl+c不捕获
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error("{} Uncaught exception".format(threading.current_thread().name),
                     exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


if __name__ == '__main__':
    install_except_hook()
    main('tablet')
    main('laptop')

    # TODO:指定品牌和开始页
    # brand_need["laptop"] = ("戴尔", "联想", "华硕", "惠普")
    # main('laptop', {"华硕": 14, "联想": 14, "戴尔": 16, "惠普": 18})

    # Todo:单品牌模式(可以快速拿到一个品牌的所有商品回收信息)
    # brand_need["laptop"] = ("戴尔",)
    # main('laptop', {"戴尔": 20}, singer_brand_mode=True)
    # brand_need["laptop"] = ("联想",)
    # main('laptop', {"联想": 26}, singer_brand_mode=True)
    # brand_need["laptop"] = ("华硕",)
    # main('laptop', {"华硕": 25}, singer_brand_mode=True)
    # brand_need["laptop"] = ("惠普",)
    # main('laptop', {"惠普": 33}, singer_brand_mode=True)  # 开启线程太多了会造成3001状态码，因为代理短时间内使用次数过多, 开40个线程最后3001:0 = 1:4



