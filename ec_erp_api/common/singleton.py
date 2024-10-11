#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: singleton
@author: jkguo
@create: 2024/10/11
"""
import time


class CachedSingletonInstanceHolder(object):

    def __init__(self, instance=None, timeout_sec: float = 1800):
        self.instance = instance
        self.last_access_time = time.time()
        self.timeout_sec = timeout_sec

    def get(self):
        if time.time() - self.last_access_time > self.timeout_sec:
            self.instance = None
        else:
            self.last_access_time = time.time()
        return self.instance

    def set(self, instance):
        self.instance = instance
        self.last_access_time = time.time()
