#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sku_manager
@author: jkguo
@create: 2024/2/7
"""
import json
import typing
from ec.bigseller.big_seller_client import BigSellerClient


class SkuManager(object):

    def __init__(self, local_db_path: str = "cookies/all_sku.json"):
        self.local_db_path = local_db_path
        # sku_map = dict[sku_name, sku_info]
        self.sku_map: dict = {}
        # platform_sku_map = dict[shop_id # platform_sku, sku_name]
        self.platform_sku_map: dict = {}
        # sku_group_attr = dict[sku_name, {
        #   is_group, sku_group_items
        # }]
        self.sku_group_attr: dict = {}

    def add(self, sku: dict):
        key = sku["sku"]
        if key in self.sku_map:
            raise f"conflict sku {key}"
        for item in sku.get("skuRelations", []):
            shop_id = str(item["shop"]["id"]).strip()
            platform_sku = str(item["platformSku"]).strip()
            pk = f"{shop_id}#{platform_sku}"
            self.platform_sku_map[pk] = key
        self.sku_group_attr[sku] = {
            "is_group": sku.get("isGroup", 0),
            "sku_group_items": sku.get("skuGroupVoList", [])
        }
        self.sku_map[key] = sku

    def dump(self):
        with open(self.local_db_path, "w") as fp:
            json.dump(self.sku_map, fp, indent=2, ensure_ascii=False)

    def load(self):
        with open(self.local_db_path, "r") as fp:
            docs = json.load(fp)
            for sku in docs:
                self.add(docs[sku])

    def get_sku_id(self, sku_name: str) -> typing.Optional[int]:
        item = self.sku_map.get(sku_name)
        if item is None:
            return None
        return item["id"]

    def get_sku_name_by_shop_sku(self, shop_id, sku) -> str:
        shop_id = str(shop_id).strip()
        sku = str(sku).strip()
        pk = f"{shop_id}#{sku}"
        return self.platform_sku_map.get(pk, "UNKNOWN")

    def get_sku_group_attr(self, sku_name):
        if sku_name in self.sku_group_attr:
            return self.sku_group_attr[sku_name]
        return {
            "is_group": 0,
            "sku_group_items": []
        }

    def load_and_update_all_sku(self, client: BigSellerClient):
        self.sku_map = {}
        for r in client.load_all_sku():
            self.add(r)
