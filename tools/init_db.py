#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: init_db
@author: jkguo
@create: 2024/3/1
"""
import os
import re
import sys

sys.path.append("..")
from sqlalchemy.sql import text

from ec_erp_api.models.mysql_backend import MysqlBackend
from ec_erp_api.app_config import get_app_config

_SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ec_erp_db_schema.sql")
_CREATE_TABLE_RE = re.compile(
    r"CREATE TABLE `([^`]+)` \((.*?)\)\s*ENGINE=.*?;",
    re.S | re.I,
)
_COLUMN_RE = re.compile(r"^\s*`([^`]+)`", re.M)
_AUTO_INCREMENT_RE = re.compile(r"\s*AUTO_INCREMENT=\d+", re.I)
_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def _needs_legacy_schema(version):
    """MariaDB 10.2.7 以下、MySQL 5.7 以下没有 JSON 类型，改用原始建表 SQL。"""
    matched = _VERSION_RE.search(version or "")
    if not matched:
        print("无法解析数据库版本: {0}，继续使用模型建表".format(version))
        return False
    version_tuple = (int(matched.group(1)), int(matched.group(2)), int(matched.group(3)))
    if "mariadb" in version.lower():
        return version_tuple < (10, 2, 7)
    return version_tuple < (5, 7, 0)


def _query_version(backend):
    with backend.check_db_engine.connect() as con:
        row = con.execute(text("SELECT VERSION()")).fetchone()
    return row[0]


def _ensure_database(backend):
    with backend.check_db_engine.connect() as con:
        existing_databases = con.execute(text("SHOW DATABASES;"))
        existing_databases = [item[0] for item in existing_databases]
        if backend.db_name not in existing_databases:
            con.execute(text("CREATE DATABASE {0}".format(backend.db_name)))
            print("已创建数据库 {0}".format(backend.db_name))


def _load_schema_tables(schema_path):
    with open(schema_path, "r", encoding="utf-8") as fp:
        content = fp.read()
    tables = []
    for matched in _CREATE_TABLE_RE.finditer(content):
        table_name = matched.group(1)
        columns = _COLUMN_RE.findall(matched.group(2))
        create_sql = _AUTO_INCREMENT_RE.sub("", matched.group(0))
        if not columns:
            raise ValueError("未能解析表 {0} 的字段".format(table_name))
        tables.append((table_name, columns, create_sql))
    if not tables:
        raise ValueError("未能从 {0} 解析出建表语句".format(schema_path))
    return tables


def _apply_legacy_schema(backend):
    tables = _load_schema_tables(_SCHEMA_FILE)
    missing_by_table = {}
    # 建表语句含 00:00:00 这类冒号，不用 SQLAlchemy text()，避免被当成绑定参数。
    raw = backend.db_engine.raw_connection()
    try:
        cursor = raw.cursor()
        for table_name, columns, create_sql in tables:
            cursor.execute(
                "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s",
                (backend.db_name, table_name),
            )
            existing_columns = {row[0] for row in cursor.fetchall()}
            if not existing_columns:
                cursor.execute(create_sql)
                print("已创建表 {0}".format(table_name))
                continue
            missing_columns = [column for column in columns if column not in existing_columns]
            if missing_columns:
                missing_by_table[table_name] = missing_columns
                print("表 {0} 缺少字段: {1}".format(table_name, ", ".join(missing_columns)))
            else:
                print("表 {0} 已存在，字段齐全".format(table_name))
        raw.commit()
    finally:
        raw.close()
    if missing_by_table:
        print("已有表字段不齐全，未继续写入项目。不会删除或修改这些表。")
        sys.exit(1)


def init_db():
    config = get_app_config()
    db_config = config["db_config"]
    project_id = (config.get("sync_tool_project_id") or "").strip()
    if not project_id:
        print("配置文件缺少 sync_tool_project_id，请先在 application.json 中配置")
        sys.exit(1)

    project_name = input("请输入项目名称 project_name: ").strip()
    if not project_name:
        print("项目名称不能为空")
        sys.exit(1)

    print("即将初始化项目: project_id={0}, project_name={1}".format(project_id, project_name))
    backend = MysqlBackend(
        project_id, db_config["host"], db_config["port"], db_config["user"], db_config["password"],
        db_config["db_name"]
    )
    version = _query_version(backend)
    if _needs_legacy_schema(version):
        print("检测到低版本数据库 {0}，使用 ec_erp_db_schema.sql 初始化".format(version))
        _ensure_database(backend)
        _apply_legacy_schema(backend)
    else:
        print("数据库版本 {0}，使用模型建表".format(version))
        backend.init_db()
    backend.store_project(project_id, {
        "project_id": project_id,
        "project_name": project_name,
        "project_config": {}
    })
    print("初始化完成")


if __name__ == '__main__':
    init_db()
