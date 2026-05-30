#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sync_sku_inventory
@author: jkguo
@create: 2024/3/8

同步策略：仅显式更新 inventory / erp_sku_* / inventory_support_days / shipping_stock_quantity；
当上游 ERP 提供 avg_daily_sales > 0 时同步 avg_sell_quantity；为 0（典型 UpSeller 路径，
或 BigSeller 真无销量）则保留数据库已有值，不破坏运营人工维护的均量。
sku_pack_length / sku_pack_width / sku_pack_height 等手工维护字段保留旧值
（依赖复用既有 ORM 实例，未显式覆盖的字段不会变化）。
ERP 类型由 application.json:use_up_seller 决定，由 seller_util.build_seller_client() 统一路由。
"""
import time
import datetime
import sys
import typing

sys.path.append("..")
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common.big_seller_util import build_backend, MysqlBackend
from ec_erp_api.common.seller_util import build_seller_client


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


def sync_sku_inventory():
    config = get_app_config()
    project_id = config.get("sync_tool_project_id", "philipine")
    backend = build_backend(project_id)
    seller = build_seller_client()
    shipping_sku_map = load_all_shipping_sku_info(backend)
    _, sku_list = backend.search_sku(sku_group=None, sku_name=None, sku=None, offset=0, limit=10000)
    for sku_info in sku_list:
        try:
            sku_detail = seller.query_sku_detail(sku_info.sku)
            inv_detail = seller.query_sku_inventory_detail(sku_info.sku)
            sku_info.inventory = sku_detail.inventory_in_warehouse
            sku_info.erp_sku_id = sku_detail.erp_sku_id
            sku_info.erp_sku_name = sku_detail.title or inv_detail.title
            sku_info.erp_sku_image_url = sku_detail.image_url or inv_detail.image_url
            # avg_daily_sales > 0 时按上游均量刷新；为 0 则保留 DB 历史值（UpSeller 当前不暴露该字段）
            if inv_detail.avg_daily_sales > 0:
                sku_info.avg_sell_quantity = round(inv_detail.avg_daily_sales * 1.1, 2)
            if sku_info.avg_sell_quantity and sku_info.avg_sell_quantity > 0.01:
                sku_info.inventory_support_days = int(sku_info.inventory / sku_info.avg_sell_quantity)
            else:
                sku_info.inventory_support_days = sku_info.inventory / 0.01
            sku_info.shipping_stock_quantity = shipping_sku_map.get(sku_info.sku, 0)
            backend.store_sku(sku_info)
        except Exception as e:
            print(f"sync sku {sku_info.sku} fail: {e}")
            continue
        time.sleep(0.3)


if __name__ == '__main__':
    sync_sku_inventory()
