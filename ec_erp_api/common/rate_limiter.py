#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @File: rate_limiter.py
# @Author: 
# @Date: 2025/08/15
# @Desc: 

import time
import threading
from typing import List
import logging


app_logger = logging.getLogger("app")


class RateLimiter(object):
    """
    限流器 - 基于滑动时间窗口算法实现
    """

    def __init__(self, max_count_per_period: int, seconds_per_period: int):
        """
        Args:
            max_count_per_period: 每个周期的限流大小
            seconds_per_period: 限流周期时间: 单位秒
        """
        self.max_count_per_period = max_count_per_period
        self.seconds_per_period = seconds_per_period
        self.requests: List[float] = []  # 存储请求时间戳
        self.lock = threading.Lock()  # 线程安全锁

    def _cleanup_old_requests(self) -> None:
        """清理过期的请求记录"""
        current_time = time.time()
        cutoff_time = current_time - self.seconds_per_period
        
        # 移除过期的请求记录
        self.requests = [req_time for req_time in self.requests if req_time > cutoff_time]

    def try_acquire(self) -> bool:
        """
        尝试获取限流器, 如果获取成功则返回True, 否则返回False
        """
        with self.lock:
            self._cleanup_old_requests()
            
            if len(self.requests) < self.max_count_per_period:
                self.requests.append(time.time())
                return True
            else:
                return False
    

    def acquire(self, timeout_sec: int) -> bool:
        """
        获取限流器, 如果获取成功则返回True, 否则返回False
        如果超时, 则返回False

        Args:
            timeout_sec: 超时时间, 单位秒, 超时后自动返回False
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout_sec:
            if self.try_acquire():
                return True
            
            # 稍微等待一下再重试，避免忙等待
            time.sleep(0.01)  # 10ms
        
        # 如果超过100ms, 需要打印等待秒
        elapsed_time = time.time() - start_time
        if elapsed_time > 0.1:  # 超过100ms
            app_logger.info(f"限流器等待超时，等待时间: {elapsed_time:.3f}秒")
        
        return False
    