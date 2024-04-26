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
from logging.handlers import RotatingFileHandler


def clear_logger_handlers(logger):
    if logger is not None:
        for handler in logger.handlers:
            logger.removeHandler(handler)


def set_file_logger(
        log_file_path,
        log_level=logging.DEBUG,
        max_file_size_mb=500,
        max_file_count=20,
        encoding="UTF-8",
        logger=None,
):
    """
    (重新)设定设定日志文件
    """
    if logger is None:
        logger = logging.getLogger()
    logger.setLevel(log_level)
    clear_logger_handlers(logger)
    formatter = logging.Formatter(
        "[%(asctime)s %(msecs)03d][%(process)d][tid=%(thread)d][%(name)s][%(levelname)s] %(message)s [%(filename)s"
        " %(funcName)s %(lineno)s] ",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = RotatingFileHandler(
        log_file_path,
        maxBytes=max_file_size_mb * 1024 * 1024,
        backupCount=max_file_count,
        encoding=encoding,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


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
            logger = logging.getLogger("ACC")
            start = time.time()
            api_request = request.json
            trace_id = f"TRACE_{time.time()}"
            logger.info(
                f"REQUEST: {trace_id} {request.path} body: {json.dumps(api_request, ensure_ascii=False)}")
            try:
                api_response = func(*args, **kw)
            except Exception as e:
                logger.error(f"EXCEPTION {trace_id} process oms request error: {e}")
                logger.error(traceback.format_exc())
                api_response = {
                    "result": "1001",
                    "resultMsg": str(e),
                    "traceId": trace_id,
                    "data": None
                }
            end = time.time()
            cost_time_ms = int((end - start) * 1000)
            logger.info(
                f"RESPONSE: {trace_id} {request.path} "
                f"cost {cost_time_ms} ms body: {json.dumps(api_response, ensure_ascii=False)}")
            return jsonify(api_response)

        return wrapper

    return api_decorator
