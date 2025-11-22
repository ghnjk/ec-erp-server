#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: auto_preload_order
@author: jkguo
@create: 2025/11/22
"""
import time
import sys
import logging
import os
import json
from datetime import datetime, timedelta

sys.path.append("..")
from ec_erp_api.app_config import get_app_config
from ec_erp_api.common.api_core import set_file_logger
from ec_erp_api.common.big_seller_util import build_big_seller_client
from ec.bigseller.big_seller_client import BigSellerClient


set_file_logger("../logs/preload_order.log", logger=logging.getLogger("preload_order"))
logger = logging.getLogger("preload_order")


def _query_all_new_orders(client, warehouse_id: int, begin_time_str: str, end_time_str: str):
    """
    查询所有新订单
    :param client: BigSeller 客户端
    :param warehouse_id: 仓库ID
    :param begin_time_str: 开始时间
    :param end_time_str: 结束时间
    :return: 订单列表
    """
    logger.info("[_query_all_new_orders] 开始分页查询所有新订单")

    all_orders = []
    current_page = 1
    page_size = 300
    has_more = True
    total_orders = 0

    while has_more:
        try:
            logger.info(f"[_query_all_new_orders] 查询第 {current_page} 页订单")
            total_orders, orders = client.search_new_order(
                warehouse_id, begin_time_str, end_time_str, current_page, page_size
            )

            logger.info(
                f"[_query_all_new_orders] 第 {current_page} 页查询成功，获得 {len(orders)} 个订单，"
                f"总计 {total_orders} 个"
            )

            all_orders.extend(orders)

            # 检查是否有下一页
            if len(orders) < page_size or len(all_orders) >= total_orders:
                has_more = False
            else:
                current_page += 1

        except Exception as e:
            logger.error(f"[_query_all_new_orders] 查询第 {current_page} 页失败: {str(e)}")
            has_more = False

    logger.info(f"[_query_all_new_orders] 查询完成，共获得 {len(all_orders)} 个订单")
    return all_orders


def _mark_orders_to_wait_print(client: BigSellerClient, orders: list):
    """
    标记订单为待打印
    :param client: BigSeller 客户端
    :param orders: 订单列表
    :return: (标记成功数, 成功的订单ID列表, 标记失败的订单ID列表)
    """
    logger.info(f"[_mark_orders_to_wait_print] 开始标记 {len(orders)} 个订单为待打印")

    marked_success = 0
    successful_order_ids = []
    failed_order_ids = []

    for idx, order in enumerate(orders, 1):
        order_id = order.get("id")
        if not order_id:
            logger.warning("[_mark_orders_to_wait_print] 订单没有ID，跳过")
            continue

        # 标记为待打印（支持重试1次）
        success = False
        for attempt in range(2):  # 最多尝试2次（初次 + 1次重试）
            try:
                if attempt > 0:
                    logger.info(
                        f"[_mark_orders_to_wait_print] 订单 {order_id} 重试标记为待打印 "
                        f"(第 {attempt} 次重试) [{idx}/{len(orders)}]"
                    )
                client.set_new_order_to_wait_print(order_id)
                marked_success += 1
                successful_order_ids.append(order_id)
                logger.info(f"[_mark_orders_to_wait_print] 订单 {order_id} 已标记为待打印 [{idx}/{len(orders)}]")
                success = True
                break
            except Exception as e:
                if attempt == 0:
                    logger.warning(
                        f"[_mark_orders_to_wait_print] 订单 {order_id} 首次标记失败: {str(e)}"
                    )
                else:
                    logger.error(
                        f"[_mark_orders_to_wait_print] 订单 {order_id} 重试标记仍然失败: {str(e)}"
                    )
                time.sleep(1)

        if not success:
            failed_order_ids.append(order_id)
            logger.error(f"[_mark_orders_to_wait_print] 订单 {order_id} 标记为待打印最终失败")

        # 等待1秒
        time.sleep(1)

    logger.info(
        f"[_mark_orders_to_wait_print] 标记完成，成功: {marked_success}, 失败: {len(failed_order_ids)}"
    )
    return marked_success, successful_order_ids, failed_order_ids


def _validate_order_items(order_detail: dict) -> bool:
    """
    验证订单中所有orderItemVoList的allocated是否等于allocating
    :param order_detail: 订单详情
    :return: 验证是否通过
    """
    order_item_list = order_detail.get("orderItemVoList", [])
    
    if not order_item_list:
        logger.warning("[_validate_order_items] 订单没有orderItemVoList")
        return False
    
    for idx, item in enumerate(order_item_list):
        allocated = item.get("allocated")
        allocating = item.get("allocating")
        
        if allocated != allocating:
            logger.warning(
                f"[_validate_order_items] 订单项验证失败: 项索引={idx}, allocated={allocated}, allocating={allocating}"
            )
            return False
    
    logger.info(f"[_validate_order_items] 订单项验证通过，共 {len(order_item_list)} 项")
    return True


def _write_order_to_cache(order_id: int, order_detail: dict) -> bool:
    """
    将订单详情写入缓存文件
    :param order_id: 订单ID
    :param order_detail: 订单详情
    :return: 是否写入成功
    """
    config = get_app_config()
    cookies_dir = config.get("cookies_dir", "../cookies")
    cache_dir = os.path.join(cookies_dir, "order_cache")
    
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    cache_file = os.path.join(cache_dir, f"{order_id}.json")
    
    try:
        with open(cache_file, "w") as f:
            json.dump(order_detail, f, indent=2)
        logger.info(f"[_write_order_to_cache] 订单 {order_id} 已写入缓存文件: {cache_file}")
        return True
    except Exception as e:
        logger.error(f"[_write_order_to_cache] 订单 {order_id} 写入缓存文件失败: {str(e)}")
        return False


def _cache_order_details(client: BigSellerClient, order_ids: list):
    """
    缓存订单详情
    执行逻辑：
    1、获取订单详情
    2、验证订单中所有orderItemVoList的allocated是否等于allocating
    3、验证通过则写入缓存文件
    :param client: BigSeller 客户端
    :param order_ids: 订单ID列表
    :return: 缓存成功数
    """
    logger.info(f"[_cache_order_details] 开始缓存 {len(order_ids)} 个订单的详情")

    cached_success = 0

    for idx, order_id in enumerate(order_ids, 1):
        try:
            # 获取订单详情
            detail = client.get_order_detail(order_id)
            logger.info(f"[_cache_order_details] 订单 {order_id} 详情已获取 [{idx}/{len(order_ids)}]")
            
            # 验证订单项
            if not _validate_order_items(detail):
                logger.warning(
                    f"[_cache_order_details] 订单 {order_id} 项验证不通过，不缓存 [{idx}/{len(order_ids)}]"
                )
                continue
            
            # 写入缓存文件
            if _write_order_to_cache(order_id, detail):
                cached_success += 1
                logger.info(f"[_cache_order_details] 订单 {order_id} 详情已缓存 [{idx}/{len(order_ids)}]")
            else:
                logger.error(f"[_cache_order_details] 订单 {order_id} 缓存写入失败 [{idx}/{len(order_ids)}]")

        except Exception as e:
            logger.error(
                f"[_cache_order_details] 获取订单 {order_id} 详情失败: {str(e)} [{idx}/{len(order_ids)}]"
            )

    logger.info(f"[_cache_order_details] 缓存完成，成功: {cached_success}, 失败: {len(order_ids) - cached_success}")
    return cached_success


def _generate_report(begin_time_str: str, end_time_str: str, warehouse_id: int, 
                     total_queried: int, total_marked: int, total_cached: int, total_failed: int):
    """
    生成预加载报告
    :param begin_time_str: 开始时间
    :param end_time_str: 结束时间
    :param warehouse_id: 仓库ID
    :param total_queried: 查询订单总数
    :param total_marked: 标记成功数
    :param total_cached: 缓存成功数
    :param total_failed: 处理失败数
    :return: 报告字符串
    """
    report = (
        f"\n"
        f"========== auto_preload_order 预加载报告 ==========\n"
        f"开始时间: {begin_time_str}\n"
        f"结束时间: {end_time_str}\n"
        f"仓库ID: {warehouse_id}\n"
        f"\n"
        f"查询结果统计:\n"
        f"- 查询订单总数: {total_queried}\n"
        f"- 标记成功: {total_marked}\n"
        f"- 缓存成功: {total_cached}\n"
        f"- 处理失败: {total_failed}\n"
        f"====================================================\n"
    )
    return report


def auto_preload_order():
    """
    自动预加载订单
    执行逻辑：
    1、分页调用search_new_order查询最近24小时的订单，每页大小300
    2、逐个订单调用set_new_order_to_wait_print标记为待打印，每个单执行一次后等待1秒。需要兼容标记失败的情况，并重试1次。
    3、对标记成功的订单，调用get_order_detail获取订单详情，并缓存到本地文件。
    4、输出预加载概要信息报告
    """

    try:
        logger.info("[auto_preload_order] ========== 开始自动预加载订单任务 ==========")

        # 获取配置
        config = get_app_config()
        warehouse_id = config.get("big_seller_warehouse_id")

        # 计算时间范围（最近24小时）
        end_time = datetime.now()
        begin_time = end_time - timedelta(hours=24)
        begin_time_str = begin_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"[auto_preload_order] 查询时间范围: {begin_time_str} ~ {end_time_str}")
        logger.info(f"[auto_preload_order] 仓库ID: {warehouse_id}")

        # 获取 BigSeller 客户端
        client = build_big_seller_client()
        client.login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
        logger.info("[auto_preload_order] BigSeller 客户端初始化成功")

        # 步骤1：查询所有新订单
        all_orders = _query_all_new_orders(client, warehouse_id, begin_time_str, end_time_str)
        total_queried = len(all_orders)
        logger.info(f"[auto_preload_order] 步骤1完成：查询到 {total_queried} 个订单")

        if total_queried == 0:
            logger.info("[auto_preload_order] 没有查询到订单，任务完成")
            report = _generate_report(begin_time_str, end_time_str, warehouse_id, 0, 0, 0, 0)
            logger.info(report)
            print(report)
            return

        # 步骤2：标记订单为待打印
        total_marked, successful_order_ids, failed_order_ids = _mark_orders_to_wait_print(client, all_orders)
        logger.info(f"[auto_preload_order] 步骤2完成：标记成功 {total_marked} 个订单")

        # 步骤3：缓存标记成功的订单详情
        total_cached = _cache_order_details(client, successful_order_ids)
        logger.info(f"[auto_preload_order] 步骤3完成：缓存成功 {total_cached} 个订单详情")

        # 步骤4：生成报告
        total_failed = len(failed_order_ids)
        report = _generate_report(begin_time_str, end_time_str, warehouse_id, 
                                 total_queried, total_marked, total_cached, total_failed)
        logger.info(report)
        print(report)

        logger.info("[auto_preload_order] ========== 自动预加载订单任务完成 ==========\n")

    except Exception as e:
        logger.error(f"[auto_preload_order] 自动预加载订单失败: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    auto_preload_order()
