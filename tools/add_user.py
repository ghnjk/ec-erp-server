#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: init_db
@author: jkguo
@create: 2024/3/1
"""
import sys
from ec_erp_api.models.mysql_backend import MysqlBackend, UserDto
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common import codec_util


def init_db():
    config = get_app_config()
    db_config = config["db_config"]
    backend = MysqlBackend(
        "philipine", db_config["host"], db_config["port"], db_config["user"], db_config["password"]
    )
    backend.store_user(UserDto(
        user_name=sys.argv[1],
        default_project_id="philipine",
        password=codec_util.calc_sha256(sys.argv[2]),
        roles=[
            {
                "project_id": "philipine",
                "name": "supply",
                "memo": "供应链管理",
                "level": 1
            },
            {
                "project_id": "philipine",
                "name": "storehouse",
                "memo": "仓库管理",
                "level": 1
            }
        ],
        is_admin=1
    ))
    print(f"add user {sys.argv[1]} success.")


if __name__ == '__main__':
    init_db()
