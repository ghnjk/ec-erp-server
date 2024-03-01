#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: init_db
@author: jkguo
@create: 2024/3/1
"""
import sys

sys.path.append("..")
from ec_erp_api.models.mysql_backend import MysqlBackend
from ec_erp_api.app_config import get_app_config


def init_db():
    config = get_app_config()
    db_config = config["db_config"]
    backend = MysqlBackend(
        "philipine", db_config["host"], db_config["port"], db_config["user"], db_config["password"]
    )
    # 创建库表
    backend.init_db()
    # 创建项目
    backend.store_project("philipine", {
        "project_id": "philipine",
        "project_name": "菲律宾电商",
        "project_config": {}
    })


if __name__ == '__main__':
    init_db()
