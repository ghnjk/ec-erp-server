#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: api_core
@author: jkguo
@create: 2024/4/27
"""
import functools
import time
from flask import request, jsonify
import logging
import json
import traceback


def api_post_request():
    """
    api请求处理器
    用于解析和打包oms请求
    统一发送acc日志
    oms处理函数样例：
    @oms_post_request
    def test_api(oms_body: dict) -> typing.Tuple[int, str, dict]:
        return ret_code, err_msg, res_body
    :return:
    """

    def api_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            start = time.time()
            api_request = request.json
            trace_id = f"TRACE_{time.time()}"
            logging.info(
                f"REQUEST: {trace_id} {request.path} body: {json.dumps(api_request, ensure_ascii=False)}")
            try:
                api_response = func(*args, **kw)
            except Exception as e:
                logging.error(f"EXCEPTION {trace_id} process oms request error: {e}")
                logging.error(traceback.format_exc())
                api_response = jsonify({
                    "result": "1001",
                    "resultMsg": str(e),
                    "traceId": trace_id,
                    "data": None
                })
            end = time.time()
            cost_time_ms = int((end - start) * 1000)
            logging.info(
                f"RESPONSE: {trace_id} {request.path} "
                f"cost {cost_time_ms} ms body: {json.dumps(api_response.get_json(), ensure_ascii=False)}")
            return jsonify(api_response)

        return wrapper

    return api_decorator
