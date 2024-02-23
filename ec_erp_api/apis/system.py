#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: system
@author: jkguo
@create: 2024/2/24
"""
from ec_erp_api.common import request_util, response_util
from flask import (
    Blueprint, session
)

system_apis = Blueprint('system', __name__)


@system_apis.route('/login_user', methods=["POST"])
def login_user():
    account = request_util.get_str_param("account")
    password = request_util.get_str_param("password")
    session["user_name"] = account
    return response_util.pack_response({
        "userName": account,
        "groupName": "",
        "roles": [
            {
                "id": 9010,
                "systemId": 624,
                "name": "admin",
                "memo": "管理员",
                "level": 1,
                "auditTmplId": 0,
                "tag": "0964a4f9-ada1-4fce-a8d6-c56515c84b1d"
            }
        ],
        "admin": True
    })


@system_apis.route("/get_login_user_info", methods=["POST"])
def get_login_user_info():
    user_name = session.get("user_name")
    if user_name is None:
        return response_util.pack_error_response(1001, "not login.")
    return response_util.pack_response({
        "userName": user_name,
        "groupName": "",
        "roles": [
            {
                "id": 9010,
                "systemId": 624,
                "name": "admin",
                "memo": "管理员",
                "level": 1,
                "auditTmplId": 0,
                "tag": "0964a4f9-ada1-4fce-a8d6-c56515c84b1d"
            }
        ],
        "admin": True
    })
