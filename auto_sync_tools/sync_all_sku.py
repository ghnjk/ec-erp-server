#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sync_all_sku
@author: jkguo
@create: 2024/10/6
"""
import sys

sys.path.append("..")
from ec_erp_api.common.big_seller_util import build_big_seller_client, build_sku_manager


def sync_all_sku():
    sku_manager = build_sku_manager()
    sku_manager.load_and_update_all_sku(build_big_seller_client())


if __name__ == '__main__':
    sync_all_sku()
