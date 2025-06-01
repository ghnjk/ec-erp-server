#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: warehouse
@author: jkguo
@create: 2024/10/3
"""
import time
from ec_erp_api.common.api_core import api_post_request
from ec_erp_api.common import request_util, response_util, request_context, big_seller_util
from flask import (
    Blueprint
)
from ec_erp_api.models.mysql_backend import MysqlBackend, DtoUtil
from ec_erp_api.business.order_printing import PrintOrderThread, append_log_to_task
from ec.sku_manager import SkuManager
from ec.bigseller.big_seller_client import BigSellerClient
from ec_erp_api.models.mysql_backend import OrderPrintTask, SkuPickingNote

warehouse_apis = Blueprint('warehouse', __name__)


@warehouse_apis.route('/get_wait_print_order_ship_provider_list', methods=["POST"])
@api_post_request()
def get_order_statics():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    from ec_erp_api.app_config import get_app_config
    config = get_app_config()
    client = big_seller_util.build_big_seller_client()
    res = client.get_wait_print_order_ship_provider_list(
        config.get("big_seller_warehouse_id")
    )
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
    return response_util.pack_json_response(
        {
            "total": total,
            "list": rows
        }
    )


class OrderSkuCounter(object):

    def __init__(self):
        self.all_unit_skus = {}

    def add(self, sku, quantity, sku_info):
        if sku not in self.all_unit_skus.keys():
            self.all_unit_skus[sku] = {
                "sku": sku,
                "quantity": quantity,
                "sku_info": sku_info
            }
        else:
            self.all_unit_skus[sku]["quantity"] = self.all_unit_skus[sku]["quantity"] + quantity


class OrderAnalysis(object):

    def __init__(self, sku_manager: SkuManager, backend: MysqlBackend, client: BigSellerClient):
        self.sku_manager = sku_manager
        self.backend = backend
        self.client = client
        self.need_manual_mark_sku_list = []
        self.need_manual_mark_sku_keys = set()
        self.sku_sample_desc = {}

    def parse_all_orders(self, order_list):
        for order in order_list:
            shop_id = order["shopId"]
            counter = OrderSkuCounter()
            picking_notes = []
            order_id = order["id"]
            platform_order_no = order["platformOrderId"]
            # 直接查询erp的订单详情的sku匹配结果
            detail = self._get_order_detail(order_id)
            sku_match_detail = []
            for item in detail["orderItemVoList"]:
                allocated = item["allocated"]
                allocating = item["allocating"]
                if allocated != allocating:
                    raise Exception(f"order {platform_order_no} sku 匹配信息异常")
                # 店铺上的sku
                var_sku = item["varSku"]
                # 平台匹配的sku
                inventory_sku = item["inventorySku"]
                # 平台匹配组合sku信息 单一sku时，为null
                var_sku_group_list = item.get("varSkuGroupVoList", None)
                sku_match_detail.append({
                    "var_sku": var_sku,
                    "inventory_sku": inventory_sku,
                    "var_sku_group_list": var_sku_group_list,
                    "allocated": allocated
                })
                if var_sku_group_list is None or len(var_sku_group_list) == 0:
                    # 单1sku
                    sku_info = self.sku_manager.sku_map.get(inventory_sku, {})
                    self.sku_sample_desc[inventory_sku] = self._build_sample_desc(
                        inventory_sku, allocated, inventory_sku, allocated
                    )
                    counter.add(inventory_sku, allocated, sku_info)
                else:
                    # 组合sku
                    note = self.backend.get_sku_picking_note(inventory_sku)
                    if note is not None:
                        # 不能拆分的组合sku
                        if "not_split_var_skus" not in order:
                            order["not_split_var_skus"] = []
                        order["not_split_var_skus"].append({
                            "inventory_sku": inventory_sku,
                            "allocated": allocated,
                            "sku_info": sku_info,
                            "note": DtoUtil.to_dict(note)
                        })
                        sku_info = self.sku_manager.sku_map.get(inventory_sku, {})
                        counter.add(inventory_sku, allocated, sku_info)
                    else:
                        for var_item in var_sku_group_list:
                            item_sku = var_item["varSku"]
                            item_num = var_item["num"]
                            sku_info = self.sku_manager.sku_map.get(item_sku, {})
                            self.sku_sample_desc[item_sku] = self._build_sample_desc(
                                inventory_sku, allocated, item_sku, allocated * item_num
                            )
                            counter.add(item_sku, allocated * item_num, sku_info)
            order["sku_match_detail"] = sku_match_detail
            # # 匹配所有sku，转成单一的sku并合并
            # for item in order["orderItemList"]:
            #     var_sku = item["varSku"]
            #     quantity = item["quantity"]
            #     sku_name = self.sku_manager.get_sku_name_by_shop_sku(shop_id, var_sku)
            #     if sku_name == "UNKNOWN":
            #         sku_name = self._try_find_sku_name_by_order_id(order_id, var_sku)
            #     if sku_name == "UNKNOWN":
            #         print(f"商品信息匹配失败. shop id {shop_id} var_sku {var_sku}")
            #         raise Exception(f"商品信息匹配失败. shop id {shop_id} var_sku {var_sku}")
            #     sku_group_attr = self.sku_manager.get_sku_group_attr(sku_name)
            #     if sku_group_attr["is_group"] == 0:
            #         sku_info = self.sku_manager.sku_map[sku_name]
            #         self.sku_sample_desc[sku_name] = self._build_sample_desc(
            #             sku_name, quantity, sku_name, quantity
            #         )
            #         counter.add(sku_name, quantity, sku_info)
            #     else:
            #         for var_item in sku_group_attr["sku_group_items"]:
            #             item_sku = var_item["varSku"]
            #             item_num = var_item["num"]
            #             sku_info = self.sku_manager.sku_map[item_sku]
            #             self.sku_sample_desc[item_sku] = self._build_sample_desc(
            #                 sku_name, quantity, item_sku, quantity * item_num
            #             )
            #             counter.add(item_sku, quantity * item_num, sku_info)
            # 添加拣货备注
            for key in counter.all_unit_skus.keys():
                unit_sku = counter.all_unit_skus[key]
                quantity = unit_sku["quantity"]
                note = self.backend.get_sku_picking_note(unit_sku["sku"])
                if note is None:
                    self._add_need_note_sku(unit_sku)
                else:
                    if note.support_pkg_picking and 1 <= note.pkg_picking_unit <= quantity:
                        pkg_count = int(quantity) // int(note.pkg_picking_unit)
                        quantity -= pkg_count * int(note.pkg_picking_unit)
                        picking_notes.append({
                            "picking_quantity": f"{pkg_count}",
                            "picking_unit_name": note.pkg_picking_unit_name,
                            "picking_sku_name": note.picking_sku_name
                        })
                    if quantity > 0:
                        picking_quantity = quantity / note.picking_unit
                        if abs(picking_quantity - round(picking_quantity)) < 0.0001:
                            picking_quantity = str(int(picking_quantity))
                        else:
                            picking_quantity = str(round(picking_quantity, 1))
                        picking_notes.append({
                            "picking_quantity": picking_quantity,
                            "picking_unit_name": note.picking_unit_name,
                            "picking_sku_name": note.picking_sku_name
                        })
            order["pickingNotes"] = picking_notes

    def _add_need_note_sku(self, unit_sku):
        sku = unit_sku["sku"]
        image_url = unit_sku["sku_info"].get("imgUrl")
        if sku not in self.need_manual_mark_sku_keys:
            self.need_manual_mark_sku_keys.add(sku)
            self.need_manual_mark_sku_list.append({
                "sku": sku,
                "image_url": image_url,
                "desc": self.sku_sample_desc[sku]
            })

    def _build_sample_desc(self, sku_name, quantity, item_sku, item_quantity):
        """
        生成前端辅助用户备注信息的案例
        :param sku_name:
        :param quantity:
        :param item_sku:
        :param item_quantity:
        :return:
        """
        return f"案例：买家购买{quantity}个[{sku_name}] => 实际扣除sku: {item_quantity}个[{item_sku}]"

    def _try_find_sku_name_by_order_id(self, order_id, var_sku):
        """
        尝试从叮当详情中找到sku
        :param order_id:
        :param var_sku:
        :return:
        """
        detail = self.client.get_order_detail(order_id)
        for item in detail["orderItemVoList"]:
            if item["varSku"] == var_sku:
                sku_id = item["skuId"]
                sku_name = self.sku_manager.get_sku_name_by_sku_id(sku_id)
                if sku_name is not None:
                    return sku_name
        return "UNKNOWN"

    def _get_order_detail(self, order_id):
        """
        获取订单详情，需要优先从本地缓存文件获取
        :param order_id:
        :return:
        """
        import os
        import json
        from ec_erp_api.app_config import get_app_config
        config = get_app_config()
        cookies_dir = config.get("cookies_dir", "../cookies")
        cache_dir = os.path.join(cookies_dir, "order_cache")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        cache_file = os.path.join(cache_dir, f"{order_id}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                detail = json.load(f)
        else:
            detail = self.client.get_order_detail(order_id)
            with open(cache_file, "w") as f:
                json.dump(detail, f)
        return detail


@warehouse_apis.route('/pre_submit_print_order', methods=["POST"])
@api_post_request()
def pre_submit_print_order():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    order_list = request_util.get_param("order_list")
    sku_manager = big_seller_util.build_sku_manager()
    backend = request_context.get_backend()
    client = big_seller_util.build_big_seller_client()
    order_analysis = OrderAnalysis(sku_manager, backend, client)
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


@warehouse_apis.route('/search_manual_mark_sku_picking_note', methods=["POST"])
@api_post_request()
def search_manual_mark_sku_picking_note():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    current_page = request_util.get_int_param("current_page")
    sku_manager = big_seller_util.build_sku_manager()
    page_size = request_util.get_int_param("page_size")
    search_sku = request_util.get_str_param("search_sku")
    offset = (current_page - 1) * page_size
    total, records = request_context.get_backend().search_sku_picking_note(search_sku, offset, page_size)
    res_list = []
    for r in records:
        item = DtoUtil.to_dict(r)
        sku_info = sku_manager.sku_map.get(r.sku)
        if sku_info is not None:
            item["erp_sku_image_url"] = sku_info["imgUrl"]
            item["erp_sku_name"] = sku_info["title"]
        else:
            item["erp_sku_image_url"] = ""
            item["erp_sku_name"] = ""
        res_list.append(item)
    return response_util.pack_json_response({
        "total": total,
        "list": res_list
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
        note.support_pkg_picking = item.get("support_pkg_picking", False)
        note.pkg_picking_unit = float(item["pkg_picking_unit"])
        note.pkg_picking_unit_name = item["pkg_picking_unit_name"]
        if note.support_pkg_picking and note.picking_unit > note.pkg_picking_unit:
            temp_unit = note.pkg_picking_unit
            temp_unit_name = note.pkg_picking_unit_name
            note.pkg_picking_unit = note.picking_unit
            note.pkg_picking_unit_name = note.picking_unit_name
            note.picking_unit = temp_unit
            note.picking_unit_name = temp_unit_name
        note.picking_sku_name = item["picking_sku_name"]
        backend.store_sku_picking_note(note)
    return response_util.pack_json_response({
        "manual_mark_sku_list": manual_mark_sku_list
    })


@warehouse_apis.route('/start_run_print_order_task', methods=["POST"])
@api_post_request()
def start_run_print_order_task():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    task_id = request_util.get_str_param("task_id")
    backend = request_context.get_backend()
    task = backend.get_order_print_task(task_id)
    if task is None:
        return response_util.pack_error_response(result_msg=f"打印任务{task_id}不存在")
    append_log_to_task(task, "启动打印任务")
    backend.update_order_print_task_without_order_list(task)
    t = PrintOrderThread(
        task, request_context.get_backend(), big_seller_util.build_big_seller_client()
    )
    t.start()
    task_dict = DtoUtil.to_dict(task)
    del task_dict["order_list"]
    return response_util.pack_json_response({
        "task": task_dict
    })


@warehouse_apis.route('/query_print_order_task', methods=["POST"])
@api_post_request()
def query_print_order_task():
    if not request_context.validate_user_permission(request_context.PMS_WAREHOUSE):
        return response_util.pack_error_response(1008, "权限不足")
    task_id = request_util.get_str_param("task_id")
    backend = request_context.get_backend()
    task = backend.get_order_print_task_summary(task_id)
    if task is None:
        return response_util.pack_error_response(result_msg=f"打印任务{task_id}不存在")
    return response_util.pack_json_response({
        "task": DtoUtil.to_dict(task, OrderPrintTask.columns)
    })
