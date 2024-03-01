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


__GLOBAL_BACKEND_CACHE__: typing.Dict[str, MysqlBackend] = {}
APP_CONFIG = get_app_config()


def get_backend() -> MysqlBackend:
    project_id = session.get("project_id", "dev")
    if project_id in __GLOBAL_BACKEND_CACHE__:
        return __GLOBAL_BACKEND_CACHE__[project_id]
    db_config = APP_CONFIG["db_config"]
    backend = MysqlBackend(
        project_id, db_config["host"], db_config["port"], db_config["user"], db_config["password"]
    )
    __GLOBAL_BACKEND_CACHE__[project_id] = backend
    return backend


def get_current_user() -> typing.Optional[UserDto]:
    user_name = session.get("user_name")
    if user_name is None:
        return None
    user = get_backend().get_user(user_name)
    return user


def get_current_project_id() -> str:
    return session.get("project_id", "dev")
