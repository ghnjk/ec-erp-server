#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sync_shop_statics_to_es
@author: jkguo
@create: 2024/3/4
"""
import time
import datetime
import sys

sys.path.append("..")
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common.big_seller_util import build_big_seller_client, build_shop_manager
from ec.shop_manager import ShopManager
from elasticsearch import Elasticsearch


def enrich_shop_static_info(doc: dict, shop_manager: ShopManager) -> dict:
    shop_id = str(doc["shopId"])
    # shopOwner
    doc["shopOwner"] = shop_manager.get_shop_owner(shop_id)
    # platform
    doc["platform"] = shop_manager.get_shop_platform(shop_id)
    # docId
    keys = [
        "time",
        "shopId"
    ]
    doc_id = ""
    for k in keys:
        if len(doc_id) > 0:
            doc_id += "_"
        doc_id = doc_id + str(doc[k])
    doc["docId"] = doc_id
    return doc


def sync_shop_statics_to_es():
    config = get_app_config()
    client = build_big_seller_client()
    shop_manager = build_shop_manager()
    shop_manager.load_an_update_sm(client)
    es = Elasticsearch(config["es_hosts"], verify_certs=False, http_auth=(config["es_user"], config["es_passwd"]))

    now = time.time()
    for i in range(3):
        ti = now - (i + 1) * 24 * 3600
        order_date = datetime.datetime.fromtimestamp(ti).strftime("%Y-%m-%d")
        print(f"sync_shop_statics_to_es {order_date} ...")
        rows = client.query_shop_sell_static(order_date, order_date)
        for r in rows:
            r["time"] = order_date
            enrich_shop_static_info(r, shop_manager)
            es.index(index="ec_shop_sell_static", id=r["docId"], body=r)
        time.sleep(0.1)


def disable_urlib_warning():
    import urllib3
    urllib3.disable_warnings()


if __name__ == '__main__':
    disable_urlib_warning()
    sync_shop_statics_to_es()
