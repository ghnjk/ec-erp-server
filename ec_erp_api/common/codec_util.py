#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: codec_util
@author: jkguo
@create: 2024/2/24
"""
import hashlib
import base64


def calc_sha256(s: str, encoding: str = "utf-8") -> str:
    return hashlib.sha256(s.encode(encoding)).hexdigest()


def base64_decode(s: str, encoding: str = "utf-8") -> str:
    """
    将字符串s调用base64进行decode
    :param s:
    :param encoding:
    :return:
    """
    return base64.b64decode(s).decode(encoding)
