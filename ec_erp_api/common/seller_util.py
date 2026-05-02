#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: seller_util
@author: jkguo
@create: 2026/05/02

统一的 SellerClient 工厂：根据 application.json 的 ``use_up_seller`` 自动切换
BigSellerAdapter / UpSellerAdapter。

设计目标：
- 上层 supplier.py 不需要感知 BigSeller 还是 UpSeller，只持有 SellerClient 实例；
- 复用现有的 5 分钟登录态续期策略（与 big_seller_util.build_big_seller_client 等价）；
- 仅替换"构造 + 登录"路径，cookie 持久化仍由各自 client 的 save/load_cookies 负责；
- 不破坏 big_seller_util.build_big_seller_client：warehouse.py / sale.py 等老路径继续可用。
"""
import os
import time

from ec.big_seller_adapter import BigSellerAdapter
from ec.bigseller.big_seller_client import BigSellerClient
from ec.bigseller.up_seller_client import UpSellerClient
from ec.seller_client import SellerClient
from ec.sku_manager import SkuManager
from ec.up_seller_adapter import UpSellerAdapter
from ec.upseller_sku_manager import UpSellerSkuManager
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common.singleton import CachedSingletonInstanceHolder

__SELLER_CLIENT__ = CachedSingletonInstanceHolder(timeout_sec=300)
__SELLER_LOGIN_TIME__ = None
__SELLER_LOGIN_TIMEOUT_SEC__ = 60


def _is_up_seller_enabled() -> bool:
    return bool(get_app_config().get("use_up_seller", False))


def get_seller_warehouse_id() -> int:
    config = get_app_config()
    if _is_up_seller_enabled():
        return int(config["up_seller"]["warehouse_id"])
    return int(config["big_seller_warehouse_id"])


def _build_big_seller_adapter() -> BigSellerAdapter:
    config = get_app_config()
    cookies_dir = config.get("cookies_dir", "../cookies")
    client = BigSellerClient(
        config["ydm_token"],
        cookies_file_path=os.path.join(cookies_dir, "big_seller.cookies"),
    )
    sku_manager = SkuManager(local_db_path=os.path.join(cookies_dir, "all_sku.json"))
    sku_manager.load()
    return BigSellerAdapter(
        client=client,
        sku_manager=sku_manager,
        email=config["big_seller_mail"],
        encoded_password=config["big_seller_encoded_passwd"],
        warehouse_id=int(config["big_seller_warehouse_id"]),
        shelf_id=config.get("big_seller_shelf_id"),
        shelf_name=config.get("big_seller_shelf_name", ""),
    )


def _build_up_seller_adapter() -> UpSellerAdapter:
    config = get_app_config()
    cookies_dir = config.get("cookies_dir", "../cookies")
    up_cfg = config["up_seller"]
    client = UpSellerClient(
        config["ydm_token"],
        cookies_file_path=os.path.join(cookies_dir, "up_seller.cookies"),
        login_mode="selenium",
        selenium_headless=False,
        selenium_driver_path=up_cfg.get("chromedriver_path"),
    )
    sku_manager = UpSellerSkuManager(
        local_db_path=os.path.join(cookies_dir, "all_up_seller_sku.json")
    )
    sku_manager.load()
    return UpSellerAdapter(
        client=client,
        sku_manager=sku_manager,
        email=up_cfg["mail"],
        password=up_cfg["password"],
        warehouse_id=int(up_cfg["warehouse_id"]),
    )


def build_seller_client() -> SellerClient:
    """构造（或复用）当前项目的 SellerClient。

    复用单例缓存，5 分钟内首次/重新登录后保持登录态；超时自动重登。
    """
    global __SELLER_LOGIN_TIME__

    instance = __SELLER_CLIENT__.get()
    if instance is None:
        if _is_up_seller_enabled():
            instance = _build_up_seller_adapter()
        else:
            instance = _build_big_seller_adapter()
        __SELLER_CLIENT__.set(instance)
        instance.login()
        __SELLER_LOGIN_TIME__ = time.time()
        return instance

    current = time.time()
    if (
        __SELLER_LOGIN_TIME__ is not None
        and (current - __SELLER_LOGIN_TIME__) > __SELLER_LOGIN_TIMEOUT_SEC__
    ):
        instance.login()
        __SELLER_LOGIN_TIME__ = current
    return instance
