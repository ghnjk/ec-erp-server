#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: response_util
@author: jkguo
@create: 2024/2/24
"""
from flask import jsonify
from ec_erp_api.common.request_util import get_trace_id


def pack_error_response(result: int = -1, result_msg: str = "fail"):
    return jsonify({
        "result": result,
        "resultMsg": result_msg,
        "traceId": get_trace_id(),
    })


def pack_response(data: dict, result: int = 0, result_msg: str = "success"):
    return jsonify({
        "result": result,
        "resultMsg": result_msg,
        "traceId": get_trace_id(),
        "data": data
    })
