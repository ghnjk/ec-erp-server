#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: add_user
@author: jkguo
@create: 2024/3/1
"""
import getpass
import sys

sys.path.append("..")
from ec_erp_api.models.mysql_backend import MysqlBackend, UserDto
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common import codec_util


ROLE_OPTIONS = [
    {
        "name": "supply",
        "memo": "供应链管理",
    },
    {
        "name": "warehouse",
        "memo": "仓库管理",
    },
]


def _read_text(prompt: str, argv_index: int, secret: bool = False) -> str:
    if len(sys.argv) > argv_index and sys.argv[argv_index].strip():
        return sys.argv[argv_index].strip()
    while True:
        if secret:
            value = getpass.getpass(prompt).strip()
        else:
            value = input(prompt).strip()
        if value:
            return value
        print("输入不能为空，请重新输入。")


def _confirm(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} [y/N]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no", ""):
            return False
        print("请输入 y 或 n。")


def _collect_roles(project_id: str):
    roles = []
    for role in ROLE_OPTIONS:
        if _confirm(f"是否加入「{role['memo']}」权限"):
            roles.append({
                "project_id": project_id,
                "name": role["name"],
                "memo": role["memo"],
                "level": 1,
            })
    return roles


def add_user():
    project_id = _read_text("请输入项目ID: ", 1)
    user_name = _read_text("请输入用户名: ", 2)
    password = _read_text("请输入密码: ", 3, secret=True)
    roles = _collect_roles(project_id)
    is_admin = 1 if _confirm("是否加入「管理员」权限") else 0

    config = get_app_config()
    db_config = config["db_config"]
    backend = MysqlBackend(
        project_id, db_config["host"], db_config["port"], db_config["user"], db_config["password"],
        db_name=db_config["db_name"]
    )
    backend.store_user(UserDto(
        user_name=user_name,
        default_project_id=project_id,
        password=codec_util.calc_sha256(password),
        roles=roles,
        is_admin=is_admin
    ))
    print(f"add user {user_name} success.")


if __name__ == '__main__':
    add_user()
