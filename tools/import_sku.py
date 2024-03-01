#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: import_supplier_info
@author: jkguo
@create: 2024/3/1
"""
import sys

import pandas as pd

sys.path.append("..")
from ec_erp_api.models.mysql_backend import MysqlBackend, UserDto, SkuDto
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common import codec_util
from ec.bigseller.big_seller_client import BigSellerClient
from ec.sku_manager import SkuManager


def import_sku():
    config = get_app_config()
    db_config = config["db_config"]
    backend = MysqlBackend(
        "philipine", db_config["host"], db_config["port"], db_config["user"], db_config["password"]
    )
    client = BigSellerClient(config["ydm_token"], cookies_file_path="../cookies/big_seller.cookies")
    client.login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
    sm = SkuManager(local_db_path="../cookies/all_sku.json")
    for row in client.load_all_sku():
        sm.add(row)
    sm.dump()
    df = pd.read_excel(sys.argv[1], sheet_name="SKU信息")
    for idx, row in df.iterrows():
        sku_group = row["SKU分组"]
        sku_name = row["产品名称"]
        sku = row["SKU"]
        sku_info = client.query_sku_detail(
            sm.get_sku_id_by_sku_name(sku)
        )
        inventory = 0
        for vo in sku_info["warehouseVoList"]:
            inventory += vo["available"]
        s = SkuDto(
            project_id="philipine",
            sku=sku,
            sku_group=sku_group,
            sku_name=sku_name,
            inventory=inventory,
            erp_sku_name=sku_info["title"],
            erp_sku_image_url=sku_info["imgUrl"],
            erp_sku_id=str(sku_info["id"]),
            erp_sku_info=sku_info
        )
        backend.store_sku(s)


if __name__ == '__main__':
    import_sku()
