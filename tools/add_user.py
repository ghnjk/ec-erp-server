#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: init_db
@author: jkguo
@create: 2024/3/1
"""
import sys
import pandas as pd

sys.path.append("..")
from ec_erp_api.models.mysql_backend import MysqlBackend, UserDto, SupplierDto
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common import codec_util


def add_user():
    if len(sys.argv) != 4:
        print(f"invalid arguments. {sys.argv[0]} project_id user password")
        exit(-1)
    project_id = sys.argv[1]
    config = get_app_config()
    db_config = config["db_config"]
    backend = MysqlBackend(
        project_id, db_config["host"], db_config["port"], db_config["user"], db_config["password"],
        db_name=db_config["db_name"]
    )
    backend.store_user(UserDto(
        user_name=sys.argv[2],
        default_project_id=project_id,
        password=codec_util.calc_sha256(sys.argv[3]),
        roles=[
            {
                "project_id": project_id,
                "name": "supply",
                "memo": "供应链管理",
                "level": 1
            },
            {
                "project_id": project_id,
                "name": "storehouse",
                "memo": "仓库管理",
                "level": 1
            }
        ],
        is_admin=1
    ))
    print(f"add user {sys.argv[1]} success.")


if __name__ == '__main__':
    add_user()
