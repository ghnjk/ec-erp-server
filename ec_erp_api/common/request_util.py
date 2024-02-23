#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: request_util
@author: jkguo
@create: 2022/7/10
"""
import typing
from flask import request


def get_trace_id() -> str:
    return request.json["timestamp"]


def get_str_param(key: str, erase_empty_str: bool = False) -> typing.Optional[str]:
    s = request.json.get("body", {}).get(key, None)
    if s == "" and erase_empty_str:
        return None
    return s


def get_bool_param(key: str, default_value: typing.Optional[bool] = None) -> typing.Optional[bool]:
    if key not in request.json.get("body", {}):
        return default_value
    if request.json["body"][key] is None:
        return default_value
    if request.json["body"][key] == "":
        return default_value
    return request.json["body"][key]


def get_int_param(key: str, default_value: typing.Optional[int] = None) -> typing.Optional[int]:
    if key not in request.json.get("body", {}):
        return default_value
    if request.json["body"][key] is None:
        return default_value
    if request.json["body"][key] == "":
        return default_value
    return int(request.json["body"][key])


def get_param(key: str, default_value=None):
    if key not in request.json.get("body", {}):
        return default_value
    if request.json["body"][key] is None:
        return default_value
    if request.json["body"][key] == "":
        return default_value
    return request.json["body"][key]


def check_params(param_name_list: list) -> bool:
    """
    校验flask请求参数
    :param param_name_list:
    :return:
    """
    if not request.json:
        return False
    for p in param_name_list:
        if p not in request.json.get("body", {}):
            return False
    return True
