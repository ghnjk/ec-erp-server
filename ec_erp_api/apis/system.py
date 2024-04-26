#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: system
@author: jkguo
@create: 2024/2/24
"""
from ec_erp_api.common import request_util, response_util, request_context
from flask import (
    Blueprint, session
)
from ec_erp_api.common import codec_util
from ec_erp_api.common.api_core import api_post_request

system_apis = Blueprint('system', __name__)


@system_apis.route('/login_user_with_token', methods=["POST"])
@api_post_request
def login_user_with_token():
    print("login_user_with_token")
    token = request_util.get_str_param("token")
    if token is None or token == "":
        return get_login_user_info()
    else:
        print(f"token: {token}")
        # 将token base64 decode
        token = codec_util.base64_decode(token)
        print(f"token: {token}")
        # 将token字符串按照url query string格式转成dict
        token_dict = request_util.parse_url_query_string(token)
        user_name = token_dict.get("user_name")
        password = token_dict.get("password")
        print(f"user_name: {user_name} password: {password}")
        password = codec_util.calc_sha256(password)
        user = request_context.get_backend().get_user(user_name)
        print(f"user: {user.password}")
        if user is None or user.is_delete or password != user.password:
            return response_util.pack_error_response(1002, "用户不存在或者密码异常")
        session["user_name"] = user.user_name
        session["project_id"] = user.default_project_id
    return get_login_user_info()


@system_apis.route('/login_user', methods=["POST"])
def login_user():
    user_name = request_util.get_str_param("account")
    password = request_util.get_str_param("password")
    password = codec_util.calc_sha256(password)
    user = request_context.get_backend().get_user(user_name)
    if user is None or user.is_delete or password != user.password:
        return response_util.pack_error_response(1002, "用户不存在或者密码异常")
    session["user_name"] = user.user_name
    session["project_id"] = user.default_project_id
    return get_login_user_info()


@system_apis.route("/get_login_user_info", methods=["POST"])
def get_login_user_info():
    user = request_context.get_current_user()
    project_id = request_context.get_current_project_id()
    if user is None:
        return response_util.pack_error_response(1001, "not login.")
    roles = []
    for r in user.roles:
        if r["project_id"] == project_id:
            roles.append(r)
    return response_util.pack_response({
        "userName": user.user_name,
        "groupName": "",
        "roles": roles,
        "admin": user.is_admin
    })
