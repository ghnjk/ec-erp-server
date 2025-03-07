#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sync_sku_inventory
@author: jkguo
@create: 2024/3/8
"""
import time
import datetime
import sys
import typing

sys.path.append("..")
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common.big_seller_util import build_big_seller_client, build_backend, MysqlBackend


def load_and_calc_sku_avg_sell_quantity(backend, sku: str) -> float:
    now = time.time()
    day_sec = 24 * 3600
    end_ti = now - 3 * day_sec
    begin_ti = end_ti - 14 * day_sec
    begin_date = datetime.datetime.fromtimestamp(begin_ti)
    end_date = datetime.datetime.fromtimestamp(end_ti)
    all_sale_quantity = 0
    for item in backend.search_sku_sale_estimate(begin_date, end_date, sku):
        all_sale_quantity += item.efficient_quantity
    print(f"load_and_calc_sku_avg_sell_quantity sku {sku} begin_date {begin_date.strftime('%Y-%m-%d')} "
          f"end_date {end_date.strftime('%Y-%m-%d')} "
          f"avg_sale_quantity: {all_sale_quantity / 14.0}")
    return all_sale_quantity / 14.0


def load_all_shipping_sku_info(backend: MysqlBackend):
    """
    加载所有采购中的sku信息,按sku构建map
    :param backend:
    :return:
    """
    shipping_sku_map: typing.Dict[str, int] = {}
    for order in backend.load_shipping_purchase_order():
        for item in order.purchase_skus:
            sku = item["sku"]
            if sku not in shipping_sku_map.keys():
                shipping_sku_map[sku] = 0
            shipping_sku_map[sku] += item.get("quantity", 0) * item.get("sku_unit_quantity", 1)
    return shipping_sku_map


def get_real_inventory(client, warehouse_id, sku_id):
    sku_info = client.query_sku_detail(
        sku_id
    )
    inventory = 0
    for vo in sku_info["warehouseVoList"]:
        if vo["id"] != warehouse_id:
            continue
        inventory += vo["available"]
    return inventory


def sync_sku_inventory():
    config = get_app_config()
    project_id = config.get("sync_tool_project_id", "philipine")
    backend = build_backend(project_id)
    client = build_big_seller_client()
    warehouse_id = config["big_seller_warehouse_id"]
    shipping_sku_map = load_all_shipping_sku_info(backend)
    _, sku_list = backend.search_sku(sku_group=None, sku_name=None, sku=None, offset=0, limit=10000)
    for sku_info in sku_list:
        detail = client.query_sku_inventory_detail(sku_info.sku, warehouse_id)
        if detail is None:
            print(f"{sku_info.sku} query_sku_inventory_detail return None.")
            continue
        inventory = get_real_inventory(client, warehouse_id, sku_info.sku)
        sku_info.inventory = inventory
        sku_info.erp_sku_name = detail["title"]
        sku_info.erp_sku_image_url = detail["image"]
        # 计算平均销售sku数量
        sku_info.avg_sell_quantity = round(detail["avgDailySales"] * 1.1, 2)
        # 计算库存支撑天数
        if sku_info.avg_sell_quantity > 0.01:
            sku_info.inventory_support_days = int(sku_info.inventory / sku_info.avg_sell_quantity)
        else:
            sku_info.inventory_support_days = sku_info.inventory / 0.01
        sku_info.shipping_stock_quantity = shipping_sku_map.get(sku_info.sku, 0)
        backend.store_sku(sku_info)
        time.sleep(0.3)


if __name__ == '__main__':
    sync_sku_inventory()
