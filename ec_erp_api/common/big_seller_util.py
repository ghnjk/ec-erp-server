#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: big_seller_util
@author: jkguo
@create: 2024/3/4
"""
import os
from ec_erp_api.app_config import get_app_config
from ec.bigseller.big_seller_client import BigSellerClient
from ec.shop_manager import ShopManager

__BIG_SELLER_CLIENT__ = None


def build_big_seller_client() -> BigSellerClient:
    global __BIG_SELLER_CLIENT__
    if __BIG_SELLER_CLIENT__ is None:
        config = get_app_config()
        cookies_dir = config.get("cookies_dir", "../cookies")
        __BIG_SELLER_CLIENT__ = BigSellerClient(config["ydm_token"],
                                                cookies_file_path=os.path.join(cookies_dir, "big_seller.cookies"))
        __BIG_SELLER_CLIENT__.login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
    return __BIG_SELLER_CLIENT__


def build_shop_manager() -> ShopManager:
    config = get_app_config()
    cookies_dir = config.get("cookies_dir", "../cookies")
    sm = ShopManager(shop_info_file=os.path.join(cookies_dir, "shop_group.json"))
    return sm
