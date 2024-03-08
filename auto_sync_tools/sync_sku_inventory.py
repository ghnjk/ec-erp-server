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

sys.path.append("..")
from ec_erp_api.common.big_seller_util import build_big_seller_client, build_backend


def load_and_calc_sku_avg_sell_quantity(backend, sku: str) -> float:
    now = time.time()
    day_sec = 24 * 36000
    end_ti = now - 3 * day_sec
    begin_ti = end_ti - 7 * day_sec
    begin_date = datetime.datetime.fromtimestamp(begin_ti)
    end_date = datetime.datetime.fromtimestamp(end_ti)
    all_sale_quantity = 0
    for item in backend.search_sku_sale_estimate(begin_date, end_date, sku):
        all_sale_quantity += item.efficient_quantity
    print(f"load_and_calc_sku_avg_sell_quantity sku {sku} begin_date {begin_date.strftime('%y-%m-%d')} "
          f"end_date {end_date.strftime('%y-%m-%d')} "
          f"avg_sale_quantity: {all_sale_quantity / 7.0}")
    return all_sale_quantity / 7.0


def sync_sku_inventory():
    backend = build_backend("philipine")
    client = build_big_seller_client()
    _, sku_list = backend.search_sku(sku_group=None, sku_name=None, sku=None, offset=0, limit=10000)
    for sku_info in sku_list:
        detail = client.query_sku_detail(int(sku_info.erp_sku_id))
        inventory = 0
        for vo in detail["warehouseVoList"]:
            inventory += vo["available"]
        sku_info.inventory = inventory
        sku_info.erp_sku_name = detail["title"]
        sku_info.erp_sku_image_url = detail["imgUrl"]
        # 计算平均销售sku数量
        sku_info.avg_sell_quantity = load_and_calc_sku_avg_sell_quantity(backend, sku_info.sku)
        # 计算库存支撑天数
        if sku_info.avg_sell_quantity > 0.01:
            sku_info.inventory_support_days = int(sku_info.inventory / sku_info.avg_sell_quantity)
        else:
            sku_info.inventory_support_days = sku_info.inventory / 0.01
        backend.store_sku(sku_info)
        time.sleep(0.1)


if __name__ == '__main__':
    sync_sku_inventory()
