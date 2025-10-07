#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: response_util
@author: jkguo
@create: 2024/2/24
"""
from ec_erp_api.common.request_util import get_trace_id
from ec_erp_api.models.mysql_backend import DtoUtil


def pack_error_response(result: int = -1, result_msg: str = "fail"):
    return {
        "result": result,
        "resultMsg": result_msg,
        "traceId": get_trace_id(),
    }


def pack_error_json_response(result: int = -1, result_msg: str = "fail"):
    return {
        "result": result,
        "resultMsg": result_msg,
        "traceId": get_trace_id(),
    }


def pack_response(data: dict, result: int = 0, result_msg: str = "success"):
    return {
        "result": result,
        "resultMsg": result_msg,
        "traceId": get_trace_id(),
        "data": data
    }


def pack_json_response(data: dict, result: int = 0, result_msg: str = "success"):
    return {
        "result": result,
        "resultMsg": result_msg,
        "traceId": get_trace_id(),
        "data": data
    }


def pack_simple_response(data: dict = None):
    """
    返回简单的成功响应
    :param data: 响应数据，如果为None则返回空字典
    :return: 响应字典
    """
    if data is None:
        data = {}
    return pack_response(data)


def pack_pagination_result(total: int, records):
    return {
        "result": 0,
        "resultMsg": "success",
        "traceId": get_trace_id(),
        "data": {
            "total": total,
            "list": [DtoUtil.to_dict(r) for r in records]
        }
    }
