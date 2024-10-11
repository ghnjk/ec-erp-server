#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: request_context
@author: jkguo
@create: 2024/2/24
"""
import typing

from ec_erp_api.models.mysql_backend import MysqlBackend, UserDto
from flask import session
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common.singleton import CachedSingletonInstanceHolder

__GLOBAL_BACKEND_CACHE__: typing.Dict[str, CachedSingletonInstanceHolder] = {}
APP_CONFIG = get_app_config()


def get_backend() -> MysqlBackend:
    project_id = session.get("project_id", "dev")
    if project_id in __GLOBAL_BACKEND_CACHE__ and __GLOBAL_BACKEND_CACHE__[project_id].get() is not None:
        return __GLOBAL_BACKEND_CACHE__[project_id].get()
    db_config = APP_CONFIG["db_config"]
    backend = MysqlBackend(
        project_id, db_config["host"], db_config["port"], db_config["user"], db_config["password"]
    )
    __GLOBAL_BACKEND_CACHE__[project_id] = CachedSingletonInstanceHolder(backend, timeout_sec=1800)
    return backend


def get_current_user() -> typing.Optional[UserDto]:
    user_name = session.get("user_name")
    if user_name is None:
        return None
    user = get_backend().get_user(user_name)
    return user


def get_current_project_id() -> str:
    return session.get("project_id", "dev")


PMS_SUPPLIER = "supply"
PMS_WAREHOUSE = "warehouse"


def validate_user_permission(permission_name: str) -> bool:
    """
    校验用户指定permission_name的权限
    :param permission_name:
    :return:
    """
    user_name = session.get("user_name")
    if user_name is None:
        return False
    user = get_backend().get_user(user_name)
    if user.is_admin:
        # 管理员有所有的权限
        return True
    project_id = session.get("project_id", "dev")
    for r in user.roles:
        if r["project_id"] != project_id:
            continue
        if r["name"] == permission_name:
            # 找到对应权限
            return True
    return False
