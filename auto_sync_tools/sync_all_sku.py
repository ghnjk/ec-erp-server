#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sync_all_sku
@author: jkguo
@create: 2024/10/6

通过统一 SellerClient（BigSeller / UpSeller）刷新本地 SKU 缓存。
- BigSeller 路径 → cookies/all_sku.json + cookies/all_variant_sku_mapping.json
- UpSeller 路径 → cookies/all_up_seller_sku.json
ERP 类型由 application.json:use_up_seller 决定，由 seller_util 统一路由。
"""
import sys

sys.path.append("..")
from ec_erp_api.common.seller_util import build_seller_client


def sync_all_sku():
    build_seller_client().refresh_local_sku_cache()


if __name__ == '__main__':
    sync_all_sku()
