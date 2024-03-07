#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sync_order_to_es.py
@author: jkguo
@create: 2023/8/1
"""
import time
import sys

sys.path.append("..")
from ec_erp_api import app_config
import datetime
from ec.bigseller.big_seller_client import BigSellerClient
from ec.sku_group_matcher import SkuGroupMatcher
from ec.shop_manager import ShopManager
from elasticsearch import Elasticsearch
from ec_erp_api.common.big_seller_util import build_big_seller_client, build_shop_manager, build_sku_manager
from ec_erp_api.common.sku_sale_estimate import SkuSaleEstimate
from ec_erp_api.models.mysql_backend import MysqlBackend
from ec_erp_api.app_config import get_app_config


def build_backend(project_id: str):
    config = get_app_config()
    db_config = config["db_config"]
    backend = MysqlBackend(
        project_id, db_config["host"], db_config["port"], db_config["user"], db_config["password"]
    )
    return backend


def enrich_sku_info(doc: dict, sku_matcher: SkuGroupMatcher, shop_manager: ShopManager):
    # skuGroup
    doc["skuGroup"] = sku_matcher.get_product_label(doc["productName"])
    # shopGroup
    # shopOwner
    doc["shopOwner"] = shop_manager.get_shop_owner(doc["shopId"])
    # saleAmount
    doc["saleAmount"] = int(float(doc["salesStr"]) * 100)
    # refundAmount
    doc["refundAmount"] = int(float(doc["refundsStr"]) * 100)
    # cancelsAmount
    doc["cancelsAmount"] = int(float(doc["cancelsStr"]) * 100)
    # efficientsAmount
    doc["efficientsAmount"] = int(float(doc["efficientsStr"]) * 100)
    # docId
    keys = [
        "time",
        "shopId",
        "skuId"
    ]
    doc_id = ""
    for k in keys:
        if len(doc_id) > 0:
            doc_id += "_"
        doc_id = doc_id + str(doc[k])
    doc["docId"] = doc_id


def sync_sku_orders_to_es(order_date: str):
    conf = app_config.get_app_config()
    client = build_big_seller_client()
    shop_manager = build_shop_manager()
    sku_manager = build_sku_manager()
    backend = build_backend("philipine")
    sku_estimate = SkuSaleEstimate(
        project_id="philipine",
        order_date=order_date,
        backend=backend
    )
    has_reload_sku_manager = False
    sku_matcher = SkuGroupMatcher(app_config.get_config_file("product_label.txt"))
    es = Elasticsearch(conf["es_hosts"], verify_certs=False, http_auth=(conf["es_user"], conf["es_passwd"]))

    # 拉取所有的sku信息
    rows = client.load_sku_estimate_by_date(order_date, order_date)
    for r in rows:
        r["time"] = order_date
        enrich_sku_info(r, sku_matcher, shop_manager)
        es.index(index="ec_analysis_sku", id=r["docId"], body=r)
        sku_name = sku_manager.get_sku_name_by_shop_sku(
            r["shopId"],
            r["sku"]
        )
        if sku_name == "UNKNOWN" and not has_reload_sku_manager:
            has_reload_sku_manager = True
            sku_manager.load_and_update_all_sku(client)
            sku_name = sku_manager.get_sku_name_by_shop_sku(
                r["shopId"],
                r["sku"]
            )
        group_attr = sku_manager.get_sku_group_attr(sku_name)
        if group_attr.get("is_group", 0) == 0 or len(
                group_attr.get("sku_group_items", [])
        ) == 0:
            # 单个sku
            sku_estimate.add_sku_sale(
                sku_name, r["shopId"], r, 1, 1.0, r["productName"]
            )
        else:
            # 复合sku
            for item in group_attr.get("sku_group_items", []):
                var_sku = item["varSku"]
                var_count = int(item["num"])
                var_cost_ratio = float(item["costAllocationRatio"])
                sku_estimate.add_sku_sale(
                    var_sku, r["shopId"], r, var_count, var_cost_ratio, item["varSkuTitle"]
                )
    sku_estimate.store()


def main():
    now = time.time()
    for i in range(1, 2):
        ti = now - (i + 1) * 24 * 3600
        date = datetime.datetime.fromtimestamp(ti).strftime("%Y-%m-%d")
        print(f"sync {date} ...")
        sync_sku_orders_to_es(date)
        time.sleep(0.1)


def disable_urlib_warning():
    import urllib3
    urllib3.disable_warnings()


if __name__ == '__main__':
    disable_urlib_warning()
    main()
