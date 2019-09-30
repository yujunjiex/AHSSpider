# coding: UTF-8
import pymongo

client = pymongo.MongoClient(host="127.0.0.1", port=27017)

db = client['AHSLaptop']


def get_count():
    """获取数据库下所有表中对应字段的分组数量"""
    count_dict = {}
    for coll_name in db.list_collection_names(session=None):
        table = db[coll_name]
        brand_set = set()
        for i in table.find():
            brand_set.add(i["型号"])
        # print(brand_set)
        count_dict[coll_name] = len(brand_set)
        # break
    return count_dict


def delete_by_id(collection_name, id_list: list):
    coll = db[collection_name]
    print(coll.count())
    for id in id_list:
        query = {'id': id}
        coll.delete_many(query)


if __name__ == '__main__':
    # print(sorted(get_count().items(), key=lambda x: x[1]))
    # delete_by_id("惠普", [27562])
    delete_by_id("华硕", [6384, 25005])
    delete_by_id("联想", [6099, 17143, 19591, 26359, 6121])

