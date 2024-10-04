#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: warehouse
@author: jkguo
@create: 2024/10/3
"""
import copy
import datetime
import os
import time
from ec_erp_api.common.api_core import api_post_request
from ec_erp_api.common import request_util, response_util, request_context, big_seller_util
from flask import (
    Blueprint
)
from ec_erp_api.models.mysql_backend import MysqlBackend, DtoUtil
from ec_erp_api.app_config import get_app_config
from ec.bigseller.big_seller_client import BigSellerClient
from ec.sku_manager import SkuManager
from ec_erp_api.models.mysql_backend import OrderPrintTask, SkuPickingNote
import json

warehouse_apis = Blueprint('warehouse', __name__)


@warehouse_apis.route('/get_wait_print_order_ship_provider_list', methods=["POST"])
@api_post_request()
def get_order_statics():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    config = get_app_config()
    client = BigSellerClient(config["ydm_token"], cookies_file_path=os.path.join(cookies_dir, "big_seller.cookies"))
    client.login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
    res = client.get_wait_print_order_ship_provider_list()
    return response_util.pack_json_response({
        "ship_provider_list": res
    })


@warehouse_apis.route('/search_wait_print_order', methods=["POST"])
@api_post_request()
def search_wait_print_order():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    shipping_provider_id = request_util.get_str_param("shipping_provider_id")
    current_page = request_util.get_int_param("current_page")
    page_size = request_util.get_int_param("page_size")
    client = big_seller_util.build_big_seller_client()
    total, rows = client.search_wait_print_order(shipping_provider_id, current_page, page_size)
    return response_util.pack_pagination_result(total, rows)


class OrderSkuCounter(object):

    def __init__(self):
        self.all_unit_skus = {}

    def add(self, sku, quantity, sku_info):
        if sku not in self.all_unit_skus.keys():
            self.all_unit_skus[sku] = {
                "sku": "sku",
                "quantity": "quantity",
                "sku_info": sku_info
            }
        else:
            self.all_unit_skus[sku]["quantity"] = self.all_unit_skus[sku]["quantity"] + quantity


class OrderAnalysis(object):

    def __init__(self, sku_manager: SkuManager, backend: MysqlBackend):
        self.sku_manager = sku_manager
        self.backend = backend
        self.need_manual_mark_sku_list = []
        self.need_manual_mark_sku_keys = set()

    def parse_all_orders(self, order_list):
        for order in order_list:
            shop_id = order["shopId"]
            platform = order["platform"]
            counter = OrderSkuCounter()
            picking_notes = []
            # 匹配所有sku，转成单一的sku并合并
            for item in order["orderItemList"]:
                var_sku = item["varSku"]
                quantity = item["quantity"]
                sku_name = self.sku_manager.get_sku_name_by_shop_sku(shop_id, var_sku)
                if sku_name == "UNKNOWN":
                    print(f"商品信息匹配失败. shop id {shop_id} var_sku {var_sku}")
                    raise Exception(f"商品信息匹配失败. shop id {shop_id} var_sku {var_sku}")
                sku_group_attr = self.sku_manager.get_sku_group_attr(sku_name)
                if sku_group_attr["is_group"] == 0:
                    sku_info = self.sku_manager.sku_map[sku_name]
                    counter.add(sku_name, quantity, sku_info)
                else:
                    for var_item in sku_group_attr["sku_group_items"]:
                        item_sku = var_item["varSku"]
                        item_num = var_item["num"]
                        sku_info = self.sku_manager.sku_map[item_sku]
                        counter.add(sku_name, quantity * item_num, sku_info)
            # 添加拣货备注
            for key in counter.all_unit_skus.keys():
                unit_sku = counter.all_unit_skus[key]
                quantity = unit_sku["quantity"]
                note = self.backend.get_sku_picking_note(unit_sku["sku"])
                if note is None:
                    self._add_need_note_sku(unit_sku)
                else:
                    picking_notes.append({
                        "picking_unit": "{:.1f}".format(quantity / note.picking_unit),
                        "picking_unit_name": note.picking_unit_name,
                        "picking_sku_name": note.picking_sku_name
                    })
            order["pickingNotes"] = picking_notes

    def _add_need_note_sku(self, unit_sku):
        sku = unit_sku["sku"]
        sku_info = unit_sku["sku_info"]
        image_url = sku_info["imgUrl"]
        if sku not in self.need_manual_mark_sku_keys:
            self.need_manual_mark_sku_keys.add(sku)
            self.need_manual_mark_sku_list.append({
                "sku": sku,
                "image_url": image_url
            })


def append_log_to_task(task: OrderPrintTask, log: str):
    from datetime import datetime
    # 获取当前日期和时间
    now = datetime.now()
    # 格式化日期和时间
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
    if task.logs is None:
        task.logs = []
    task.logs.append(f"{formatted_now} - {log}")


@warehouse_apis.route('/pre_submit_print_order', methods=["POST"])
@api_post_request()
def pre_submit_print_order():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    order_list = request_util.get_param("order_list")
    sku_manager = big_seller_util.build_sku_manager()
    backend = request_context.get_backend()
    order_analysis = OrderAnalysis(sku_manager, backend)
    order_analysis.parse_all_orders(order_list)
    if len(order_analysis.need_manual_mark_sku_list) == 0:
        # 所有货品都有拣货备注
        task_id = str(int(time.time() * 100))
        task = OrderPrintTask()
        task.project_id = request_context.get_current_project_id()
        task.task_id = task_id
        task.current_step = "初始化..."
        task.progress = 0
        task.order_list = order_list
        append_log_to_task(task, "初始化打印任务.")
        backend.store_order_print_task(task)
    else:
        task_id = None
    return response_util.pack_json_response({
        "task_id": task_id,
        "need_manual_mark_sku_list": order_analysis.need_manual_mark_sku_list
    })


@warehouse_apis.route('/submit_manual_mark_sku_picking_note', methods=["POST"])
@api_post_request()
def submit_manual_mark_sku_picking_note():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    manual_mark_sku_list = request_util.get_param("manual_mark_sku_list")
    backend = request_context.get_backend()
    for item in manual_mark_sku_list:
        note = SkuPickingNote()
        note.project_id = request_context.get_current_project_id()
        note.sku = item["sku"]
        note.picking_unit = float(item["picking_unit"])
        note.picking_unit_name = item["picking_unit_name"]
        note.picking_sku_name = item["picking_sku_name"]
        backend.store_sku_picking_note(note)
    return response_util.pack_json_response({
        "manual_mark_sku_list": manual_mark_sku_list
    })


@warehouse_apis.route('/start_run_print_order_task', methods=["POST"])
@api_post_request()
def submit_print_order():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    task_id = request_util.get_str_param("task_id")
    backend = request_context.get_backend()
    task = backend.get_order_print_task(task_id)
    if task is None:
        return response_util.pack_error_response(result_msg=f"打印任务{task_id}不存在")
    append_log_to_task(task, "启动打印任务")
    # todo start a thread and run the task
    return response_util.pack_json_response({
        "task": DtoUtil.to_dict(task)
    })


@warehouse_apis.route('/query_print_order_task', methods=["POST"])
@api_post_request()
def query_print_order_task():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    task_id = request_util.get_str_param("task_id")
    backend = request_context.get_backend()
    task = backend.get_order_print_task(task_id)
    if task is None:
        return response_util.pack_error_response(result_msg=f"打印任务{task_id}不存在")
    return response_util.pack_json_response({
        "task": DtoUtil.to_dict(task)
    })
