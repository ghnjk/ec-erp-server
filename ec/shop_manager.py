#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: shop_manager
@author: jkguo
@create: 2023/8/1
"""
import json
import os.path
from ec.bigseller.big_seller_client import BigSellerClient


class ShopManager(object):

    def __init__(self, shop_info_file: str = "cookies/shop_group.json"):
        """
        map[shopId, shop_info]
        shop info {
            "id": 2546523,
            "name": "Artificial decor (TK:09298645333)",
            "platform": "tiktok",
            "site": "PH",
            "status": null,
            "is3pf": null,
            "shopType": null,
            "marketPlaceEaseMode": null,
            "cnsc": null,
            "shopOwner": "xxx"
        }
        :param shop_info_file:
        """
        self.shop_info = {}
        self.shop_info_file = shop_info_file
        self.__load_shop_info()

    def get_shop_platform(self, shop_id: str):
        shop_id = str(shop_id)
        if shop_id not in self.shop_info.keys():
            print(f"UNKNOWN SHOP {shop_id}")
        return self.shop_info.get(shop_id, {}).get("platform", "UNKNOWN")

    def get_shop_owner(self, shop_id: str):
        shop_id = str(shop_id)
        if shop_id not in self.shop_info.keys():
            print(f"UNKNOWN SHOP {shop_id}")
        return self.shop_info.get(shop_id, {}).get("shopOwner", "UNKNOWN")

    def __load_shop_info(self):
        if os.path.isfile(self.shop_info_file):
            with open(self.shop_info_file, "r") as fp:
                self.shop_info = json.load(fp)

    def load_an_update_sm(self, client: BigSellerClient):
        shop_owner_map = {}
        for item in client.query_shop_group():
            group_name = item["groupName"]
            for shop_id in item["shopIds"]:
                shop_owner_map[str(shop_id)] = group_name
        for shop in client.query_all_shop_info():
            shop_id = str(shop["id"])
            shop["shopOwner"] = shop_owner_map.get(shop_id, "UNKNOWN")
            self.shop_info[shop_id] = shop

    def dump(self):
        with open(self.shop_info_file, "w") as fp:
            json.dump(self.shop_info, fp, indent=2, ensure_ascii=False)
