#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: big_seller_util
@author: jkguo
@create: 2024/3/4
"""
import os
import time
from ec_erp_api.app_config import get_app_config
from ec.bigseller.big_seller_client import BigSellerClient
from ec.shop_manager import ShopManager
from ec.sku_manager import SkuManager
from ec_erp_api.models.mysql_backend import MysqlBackend
from ec_erp_api.common.singleton import CachedSingletonInstanceHolder

__BIG_SELLER_CLIENT__ = CachedSingletonInstanceHolder(timeout_sec=300)
__SKU_MANAGER__ = CachedSingletonInstanceHolder(timeout_sec=60)
__BIG_SELLER_LOGIN_TIME__ = None
__BIG_SELLER_LOGIN_TIMEOUT_SEC__ = 300  # 5分钟


def build_big_seller_client() -> BigSellerClient:
    global __BIG_SELLER_LOGIN_TIME__
    
    # 检查客户端是否存在
    if __BIG_SELLER_CLIENT__.get() is None:
        config = get_app_config()
        cookies_dir = config.get("cookies_dir", "../cookies")
        __BIG_SELLER_CLIENT__.set(BigSellerClient(config["ydm_token"],
                                                  cookies_file_path=os.path.join(cookies_dir, "big_seller.cookies")))
        __BIG_SELLER_CLIENT__.get().login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
        __BIG_SELLER_LOGIN_TIME__ = time.time()
    else:
        # 检查登录态是否过期（超过5分钟）
        current_time = time.time()
        if __BIG_SELLER_LOGIN_TIME__ is not None and (current_time - __BIG_SELLER_LOGIN_TIME__) > __BIG_SELLER_LOGIN_TIMEOUT_SEC__:
            config = get_app_config()
            __BIG_SELLER_CLIENT__.get().login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
            __BIG_SELLER_LOGIN_TIME__ = current_time

    return __BIG_SELLER_CLIENT__.get()


def build_shop_manager() -> ShopManager:
    config = get_app_config()
    cookies_dir = config.get("cookies_dir", "../cookies")
    sm = ShopManager(shop_info_file=os.path.join(cookies_dir, "shop_group.json"))
    return sm


def build_sku_manager() -> SkuManager:
    if __SKU_MANAGER__.get() is None:
        config = get_app_config()
        cookies_dir = config.get("cookies_dir", "../cookies")
        sku_manager = SkuManager(
            os.path.join(cookies_dir, "all_sku.json")
        )
        sku_manager.load()
        __SKU_MANAGER__.set(sku_manager)
    return __SKU_MANAGER__.get()


def build_backend(project_id: str) -> MysqlBackend:
    config = get_app_config()
    db_config = config["db_config"]
    db_name = db_config.get("db_name", "ec_erp_db")
    backend = MysqlBackend(
        project_id, db_config["host"], db_config["port"], db_config["user"], db_config["password"],
        db_name=db_name
    )
    return backend
