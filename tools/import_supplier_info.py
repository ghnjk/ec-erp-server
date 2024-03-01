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
from ec_erp_api.models.mysql_backend import MysqlBackend, UserDto, SupplierDto
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common import codec_util


def import_suppliers():
    config = get_app_config()
    db_config = config["db_config"]
    backend = MysqlBackend(
        "philipine", db_config["host"], db_config["port"], db_config["user"], db_config["password"]
    )
    df = pd.read_excel(sys.argv[1], sheet_name="供应商信息")
    _, all_sp = backend.search_suppliers(0, 100)
    for idx, row in df.iterrows():
        supplier_name = row["商家"]
        wxchat = row["商家微信号"]
        notes = row["备注"]
        sp = backend.store_supplier(SupplierDto(
            supplier_id=-1,
            project_id="philipine",
            supplier_name=supplier_name,
            wechat_account=wxchat,
            detail=notes
        ))
        for item in all_sp:
            if item.supplier_name == supplier_name:
                sp.supplier_id = item.supplier_id
        backend.store_supplier(sp)
        

if __name__ == '__main__':
    import_suppliers()
