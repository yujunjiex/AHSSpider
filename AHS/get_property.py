# coding: UTF-8
"""可以获得爱回收商品种类的关键属性，比如平板电脑/手机等"""
from Tools.tools import *


base_url = "https://www.aihuishou.com"
laptop_url = "https://www.aihuishou.com/laptop"  # 笔记本品牌b52, 页数-p2

tablet_url = "https://www.aihuishou.com/pingban"


property_set = set()  # 平板电脑存在一个使用情况的问题


def put_in_property(base_propertys):
    for _property in base_propertys:  # 添加到set中用作初步判断所需的property
        property_set.add(_property.strip())  # 去除两端的空格


def process(type="laptop"):
    """
    获得各品牌的property结果用于分析可变属性
    :param type:
        laptop: 表示解析笔记本
        tablet: 表示解析平板
    :return:
    """
    if type == "laptop":
        response = get_response(laptop_url)  # 解析笔记本
    else:
        response = get_response(tablet_url)  # 解析平板

    tablet_brand_need = ("小米", "华为")
    laptop_brand_need = ("华为", "小米", "联想", "华硕", "戴尔", "惠普")

    brand_dict = parse_category(response)  # 拿到所有品牌的url
    print(brand_dict)
    print("品牌解析完成！")
    for key, value in brand_dict.items():
        if key not in laptop_brand_need if type == "laptop" else tablet_brand_need:  # 暂时只查看这两个品牌的propertys
            continue
        url = base_url + value
        resp = get_response(url)
        pages = etree.HTML(resp.text).xpath(r"//div[@class='product-list-pager']//a[@class='page'][last()]/text()")[
            0]  # 拿到总页数
        for page in range(1, int(pages) + 1):
            print(f"{key}:正在解析第{page}页")
            if page == 1:
                product_urls = parse_product(resp)
                for _url in product_urls:  # 解析一种商品内的property
                    _resp = get_response(base_url + _url)
                    propertys = parse_property(_resp)
                    print(propertys)
                    put_in_property(propertys)
            else:
                sub_url = url + "-p" + str(page)
                resp = get_response(sub_url)
                product_urls = parse_product(resp)
                for _url in product_urls:  # 解析一种商品内的property
                    _resp = get_response(base_url + _url)
                    propertys = parse_property(_resp)
                    put_in_property(propertys)

    print("结果", property_set)


if __name__ == '__main__':
    process(type="laptop")
# print(get_response("https://www.aihuishou.com/portal-api/product/inquiry-detail-new/17944?quickInquiryValue=0").json())
