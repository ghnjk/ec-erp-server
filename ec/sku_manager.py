#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sku_manager
@author: jkguo
@create: 2024/2/7
"""
import os
import json
import typing
from ec.bigseller.big_seller_client import BigSellerClient


class SkuManager(object):

    def __init__(self, local_db_path: str = "cookies/all_sku.json"):
        self.local_db_path = local_db_path
        self.all_variant_sku_db_path = os.path.join(
            os.path.dirname(self.local_db_path),
            "all_variant_sku_mapping.json"
        )
        # sku_map = dict[sku_name, sku_info]
        self.sku_map: dict = {}
        self.sku_detail_variant = {}
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
        if self.sku_detail_variant[key] is not None:
            for item in self.sku_detail_variant[key]:
                shop_id = str(item["shop"]["id"]).strip()
                platform_sku = str(item["platformSku"]).strip()
                pk = f"{shop_id}#{platform_sku}"
                self.platform_sku_map[pk] = key
        self.sku_group_attr[key] = {
            "is_group": sku.get("isGroup", 0),
            "sku_group_items": sku.get("skuGroupVoList", [])
        }
        self.sku_map[key] = sku

    def dump(self):
        with open(self.local_db_path, "w") as fp:
            json.dump(self.sku_map, fp, indent=2, ensure_ascii=False)
        with open(self.all_variant_sku_db_path, "w") as fp:
            json.dump(self.sku_detail_variant, fp, indent=2, ensure_ascii=False)

    def load(self):
        if os.path.isfile(self.all_variant_sku_db_path) and os.path.isfile(self.all_variant_sku_db_path):
            with open(self.all_variant_sku_db_path, "r") as fp:
                self.sku_detail_variant = json.load(fp)
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
            if r["productCount"] > 0 and r["productCount"] > len(r["skuRelations"]):
                print(f"query more mapping for sku " + r["sku"] + " count " + str(r["productCount"]))
                # 需要从后台拉取详细的sku映射关系
                self.sku_detail_variant[
                    r["sku"]
                ] = r["skuRelations"]
                self.sku_detail_variant[
                    r["sku"]
                ].extends(
                    client.get_more_sku_mapping(r["id"])
                )
            else:
                self.sku_detail_variant[
                    r["sku"]
                ] = r["skuRelations"]
            self.add(r)
        self.dump()
