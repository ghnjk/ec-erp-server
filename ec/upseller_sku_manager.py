#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: upseller_sku_manager
@author: jkguo
@create: 2026/05/02

UpSeller 平台的 SKU 本地缓存，与 ec/sku_manager.SkuManager 等价但适配 UpSeller 字段：
- BigSeller 走 sku["id"]（int）；UpSeller 走 sku["idStr"]（str），本管理器对外统一用 str。
- BigSeller 通过 skuRelations / shop / platformSku 维护店铺映射；UpSeller 当前业务没有
  类似映射需求，仅保留 sku -> sku_id 的最小集，避免引入未使用字段。
"""
import json
import os
import typing


class UpSellerSkuManager:

    def __init__(self, local_db_path: str = "cookies/all_up_seller_sku.json"):
        self.local_db_path = local_db_path
        self.sku_map: typing.Dict[str, dict] = {}
        self.sku_id_map: typing.Dict[str, str] = {}

    def add(self, sku: dict):
        sku_code = sku.get("sku")
        if not sku_code:
            return
        sku_id = sku.get("idStr") or (str(sku["id"]) if sku.get("id") is not None else None)
        if not sku_id:
            return
        self.sku_map[sku_code] = sku
        self.sku_id_map[sku_id] = sku_code

    def dump(self):
        cache_dir = os.path.dirname(self.local_db_path)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        with open(self.local_db_path, "w") as fp:
            json.dump(self.sku_map, fp, indent=2, ensure_ascii=False)

    def load(self):
        if not os.path.isfile(self.local_db_path):
            return
        with open(self.local_db_path, "r") as fp:
            docs = json.load(fp)
            for sku_code in docs:
                self.add(docs[sku_code])

    def get_sku_id(self, sku_name: str) -> typing.Optional[str]:
        item = self.sku_map.get(sku_name)
        if item is None:
            return None
        return item.get("idStr") or (str(item["id"]) if item.get("id") is not None else None)

    def get_sku_name_by_sku_id(self, sku_id) -> typing.Optional[str]:
        return self.sku_id_map.get(str(sku_id))

    def load_and_update_all_sku(self, client):
        """全量同步 UpSeller 的单 SKU + KIT。

        UpSeller 多变体（variants）SKU 当前业务未使用，故不拉取，避免无谓的 API 流量。
        如未来 ERP 需要识别 variants，再在此扩展 ``include_variants=True`` 即可。
        """
        self.sku_map = {}
        self.sku_id_map = {}
        for r in client.load_all_sku(include_variants=False):
            self.add(r)
        self.dump()
