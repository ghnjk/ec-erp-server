#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: codec_util
@author: jkguo
@create: 2024/2/24
"""
import hashlib


def calc_sha256(s: str, encoding: str = "utf-8") -> str:
    return hashlib.sha256(s.encode(encoding)).hexdigest()
