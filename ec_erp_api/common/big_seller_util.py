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
from ec.sku_manager import SkuManager
from ec_erp_api.models.mysql_backend import MysqlBackend
from ec_erp_api.common.singleton import CachedSingletonInstanceHolder

__BIG_SELLER_CLIENT__ = CachedSingletonInstanceHolder(timeout_sec=300)
__SKU_MANAGER__ = CachedSingletonInstanceHolder(timeout_sec=60)


def build_big_seller_client() -> BigSellerClient:
    if __BIG_SELLER_CLIENT__.get() is None:
        config = get_app_config()
        cookies_dir = config.get("cookies_dir", "../cookies")
        __BIG_SELLER_CLIENT__.set(BigSellerClient(config["ydm_token"],
                                                  cookies_file_path=os.path.join(cookies_dir, "big_seller.cookies")))
        __BIG_SELLER_CLIENT__.get().login(config["big_seller_mail"], config["big_seller_encoded_passwd"])

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
    db_name = config.get("db_name", "ec_erp_db")
    backend = MysqlBackend(
        project_id, db_config["host"], db_config["port"], db_config["user"], db_config["password"],
        db_name=db_name
    )
    return backend
