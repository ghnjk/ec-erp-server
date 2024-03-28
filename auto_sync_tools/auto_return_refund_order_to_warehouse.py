#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: auto_return_refund_order_to_warehouse
@author: jkguo
@create: 2024/3/11
"""
import time
import sys

sys.path.append("..")
from ec_erp_api import app_config
import datetime
from ec_erp_api.common.big_seller_util import build_big_seller_client


def auto_return_refund_order_to_warehouse():
    config = app_config.get_app_config()
    big_seller_warehouse_id = config["big_seller_warehouse_id"]
    client = build_big_seller_client()
    now = time.time()
    for i in range(5):
        ti = now - (i + 1) * 24 * 3600
        refund_date = datetime.datetime.fromtimestamp(ti).strftime("%Y-%m-%d")
        print(f"auto_return_refund_order_to_warehouse {refund_date} ...")
        for tracking_no in client.query_not_op_refund_order_tracking_no_list(
                refund_date
        ):
            print(f"start auto_return_refund_order_to_warehouse {tracking_no}")
            refund_order = client.query_refund_order_info_by_tracking_no(tracking_no, big_seller_warehouse_id)
            refund_order["historyOrder"] = False
            for item in refund_order["itemList"]:
                item["origin_num"] = item["num"]
            client.return_refund_order_to_warehouse(refund_order, big_seller_warehouse_id)
            time.sleep(0.3)


def disable_urlib_warning():
    import urllib3
    urllib3.disable_warnings()


if __name__ == '__main__':
    disable_urlib_warning()
    auto_return_refund_order_to_warehouse()
