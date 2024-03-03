#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: system
@author: jkguo
@create: 2024/2/24
"""
import copy
import datetime
import os
import time

from ec_erp_api.common import request_util, response_util, request_context
from flask import (
    Blueprint
)
from ec_erp_api.app_config import get_app_config
from ec.bigseller.big_seller_client import BigSellerClient
from ec.sku_manager import SkuManager
from ec_erp_api.models.mysql_backend import PurchaseOrder, SkuDto, SkuPurchasePriceDto, DtoUtil
import json

supplier_apis = Blueprint('supplier', __name__)


@supplier_apis.route('/search_supplier', methods=["POST"])
def search_supplier():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    current_page = request_util.get_int_param("current_page")
    page_size = request_util.get_int_param("page_size")
    offset = (current_page - 1) * page_size
    if offset < 0:
        offset = 0
    total, records = request_context.get_backend().search_suppliers(offset, page_size)
    return response_util.pack_pagination_result(total, records)


@supplier_apis.route('/search_sku', methods=["POST"])
def search_sku():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    sku = request_util.get_str_param("sku")
    if sku is not None:
        sku = sku.strip()
    if sku == "":
        sku = None
    sku_group = request_util.get_str_param("sku_group")
    if sku_group is not None:
        sku_group = sku_group.strip()
    if sku_group == "":
        sku_group = None
    sku_name = request_util.get_str_param("sku_name")
    if sku_name is not None:
        sku_name = sku_name.strip()
    if sku_name == "":
        sku_name = None
    current_page = request_util.get_int_param("current_page")
    page_size = request_util.get_int_param("page_size")
    offset = (current_page - 1) * page_size
    if offset < 0:
        offset = 0
    total, records = request_context.get_backend().search_sku(
        sku_group, sku_name, sku,
        offset, page_size)
    return response_util.pack_pagination_result(total, records)


def load_all_sku(client: BigSellerClient) -> SkuManager:
    config = get_app_config()
    cookies_dir = config.get("cookies_dir", "../cookies")
    sm = SkuManager(local_db_path=os.path.join(cookies_dir, "all_sku.json"))
    for row in client.load_all_sku():
        sm.add(row)
    sm.dump()
    return sm


@supplier_apis.route('/save_sku', methods=["POST"])
def save_sku():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    config = get_app_config()
    cookies_dir = config.get("cookies_dir", "../cookies")
    sm = SkuManager(local_db_path=os.path.join(cookies_dir, "all_sku.json"))
    sm.load()
    client = BigSellerClient(config["ydm_token"], cookies_file_path=os.path.join(cookies_dir, "big_seller.cookies"))
    client.login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
    sku = request_util.get_str_param("sku")
    sku_group = request_util.get_str_param("sku_group")
    sku_name = request_util.get_str_param("sku_name")
    sku_unit_name = request_util.get_str_param("sku_unit_name")
    sku_unit_quantity = request_util.get_int_param("sku_unit_quantity")
    avg_sell_quantity = request_util.get_int_param("avg_sell_quantity")
    shipping_stock_quantity = request_util.get_int_param("shipping_stock_quantity")
    sku_id = sm.get_sku_id(sku)
    if sku_id is None:
        sm = load_all_sku(client)
    sku_id = sm.get_sku_id(sku)
    if sku_id is None:
        return response_util.pack_error_response(1003, f"sku {sku} 不存在")
    sku_info = client.query_sku_detail(
        sku_id
    )
    inventory = 0
    for vo in sku_info["warehouseVoList"]:
        inventory += vo["available"]
    s = SkuDto(
        project_id=request_context.get_current_project_id(),
        sku=sku,
        sku_group=sku_group,
        sku_name=sku_name,
        inventory=inventory,
        erp_sku_name=sku_info["title"],
        erp_sku_image_url=sku_info["imgUrl"],
        erp_sku_id=str(sku_info["id"]),
        erp_sku_info={},
        sku_unit_name=sku_unit_name,
        sku_unit_quantity=sku_unit_quantity,
        avg_sell_quantity=avg_sell_quantity,
        shipping_stock_quantity=shipping_stock_quantity
    )
    request_context.get_backend().store_sku(s)
    return response_util.pack_response(DtoUtil.to_dict(s))


@supplier_apis.route('/sync_all_sku', methods=["POST"])
def sync_all_sku():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    backend = request_context.get_backend()
    _, sku_list = backend.search_sku(sku_group=None, sku_name=None, sku=None, offset=0, limit=10000)
    config = get_app_config()
    cookies_dir = config.get("cookies_dir", "../cookies")
    sm = SkuManager(local_db_path=os.path.join(cookies_dir, "all_sku.json"))
    sm.load()
    client = BigSellerClient(config["ydm_token"], cookies_file_path=os.path.join(cookies_dir, "big_seller.cookies"))
    client.login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
    has_load_all_sku = False
    update_count = 0
    for item in sku_list:
        sku_id = sm.get_sku_id(item.sku)
        if sku_id is None and not has_load_all_sku:
            sm = load_all_sku(client)
            has_load_all_sku = True
        sku_id = sm.get_sku_id(item.sku)
        if sku_id is None:
            continue
        sku_info = client.query_sku_detail(
            sku_id
        )
        inventory = 0
        for vo in sku_info["warehouseVoList"]:
            inventory += vo["available"]
        item.inventory = inventory
        item.erp_sku_name = sku_info["title"]
        item.erp_sku_image_url = sku_info["imgUrl"]
        item.erp_sku_id = str(sku_info["id"])
        backend.store_sku(item)
        update_count += 1
        time.sleep(0.3)
    return response_util.pack_response({
        "update_count": update_count
    })


@supplier_apis.route('/search_sku_purchase_price', methods=["POST"])
def search_sku_purchase_price():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    current_page = request_util.get_int_param("current_page")
    page_size = request_util.get_int_param("page_size")
    offset = (current_page - 1) * page_size
    if offset < 0:
        offset = 0
    total, records = request_context.get_backend().search_sku_purchase_price(offset, page_size)
    return response_util.pack_pagination_result(total, records)


@supplier_apis.route('/search_purchase_order', methods=["POST"])
def search_purchase_order():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    current_page = request_util.get_int_param("current_page")
    page_size = request_util.get_int_param("page_size")
    offset = (current_page - 1) * page_size
    if offset < 0:
        offset = 0
    total, records = request_context.get_backend().search_purchase_order(offset, page_size)
    return response_util.pack_pagination_result(total, records)


@supplier_apis.route('/query_sku_purchase_price', methods=["POST"])
def query_sku_purchase_price():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    supplier_id = request_util.get_int_param("supplier_id")
    sku = request_util.get_str_param("sku")
    price = request_context.get_backend().get_sku_purchase_price(supplier_id, sku)
    if price is None:
        return response_util.pack_response({
            "unit_price": 0
        })
    else:
        return response_util.pack_response({
            "unit_price": price.purchase_price
        })


def build_purchase_order_from_req() -> PurchaseOrder:
    supplier = request_context.get_backend().get_supplier(request_util.get_int_param("supplier_id"))
    if supplier is None:
        raise Exception("供应商不存在")
    purchase_skus = request_util.get_param("purchase_skus", [])
    format_purchase_skus = []
    sku_amount = 0
    for item in purchase_skus:
        sku = item["sku"]
        sku_info = request_context.get_backend().get_sku(sku)
        if sku is None:
            raise Exception(f"商品sku [{sku}] 不存在")
        format_purchase_skus.append({
            "sku": sku,
            "sku_group": sku_info.sku_group,
            "sku_name": sku_info.sku_name,
            "unit_price": int(item["unit_price"]),
            "quantity": int(item["quantity"]),
            "sku_unit_name": sku_info.sku_unit_name,
            "sku_unit_quantity": sku_info.sku_unit_quantity,
            "avg_sell_quantity": sku_info.avg_sell_quantity,
            "shipping_stock_quantity": sku_info.shipping_stock_quantity
        })
        sku_amount += int(item["unit_price"]) * int(item["quantity"])
    store_skus = request_util.get_param("store_skus", [])
    format_store_skus = []
    for item in store_skus:
        sku = item["sku"]
        sku_info = request_context.get_backend().get_sku(sku)
        if sku is None:
            raise Exception(f"商品sku [{sku}] 不存在")
        format_store_skus.append({
            "sku": sku,
            "sku_group": sku_info.sku_group,
            "sku_name": sku_info.sku_name,
            "unit_price": int(item["unit_price"]),
            "quantity": int(item["quantity"]),
            "sku_unit_name": sku_info.sku_unit_name,
            "sku_unit_quantity": sku_info.sku_unit_quantity,
            "avg_sell_quantity": sku_info.avg_sell_quantity,
            "shipping_stock_quantity": sku_info.shipping_stock_quantity,
            "check_in_quantity": int(item["check_in_quantity"])
        })
    order = PurchaseOrder(
        purchase_order_id=request_util.get_int_param("purchase_order_id"),
        project_id=request_context.get_current_project_id(),
        supplier_id=supplier.supplier_id,
        supplier_name=supplier.supplier_name,
        purchase_step=request_util.get_str_param("purchase_step"),
        sku_amount=sku_amount,
        pay_amount=request_util.get_int_param("pay_amount", 0),
        pay_state=request_util.get_int_param("pay_state", 0),
        purchase_date=request_util.get_str_param("purchase_date"),
        expect_arrive_warehouse_date=request_util.get_str_param("expect_arrive_warehouse_date"),
        maritime_port=request_util.get_str_param("maritime_port"),
        shipping_company=request_util.get_str_param("shipping_company"),
        shipping_fee=request_util.get_str_param("shipping_fee"),
        arrive_warehouse_date=request_util.get_str_param("arrive_warehouse_date"),
        remark=request_util.get_str_param("remark"),
        purchase_skus=format_purchase_skus,
        store_skus=format_store_skus
    )
    return order


@supplier_apis.route('/save_purchase_order', methods=["POST"])
def save_purchase_order():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    order = build_purchase_order_from_req()
    request_context.get_backend().store_purchase_order(order)
    return response_util.pack_response({})


def remove_empty_sku(skus: list) -> list:
    res = []
    # 去除数量为0的sku
    for item in skus:
        if item["quantity"] > 0:
            res.append(item)
    return res


def save_purchase_price(order: PurchaseOrder):
    """
    保存供应价格
    :param order:
    :return:
    """
    request_context.validate_user_permission(request_context.PMS_SUPPLIER)
    for item in order.purchase_skus:
        sku = item["sku"]
        sku_info = request_context.get_backend().get_sku(sku)
        price = SkuPurchasePriceDto(
            project_id=request_context.get_current_project_id(),
            sku=item["sku"],
            supplier_id=order.supplier_id,
            supplier_name=order.supplier_name,
            purchase_price=item["unit_price"],
            sku_group=sku_info.sku_group,
            sku_name=sku_info.sku_name,
            erp_sku_image_url=sku_info.erp_sku_image_url
        )
        request_context.get_backend().store_sku_purchase_price(price)


def sync_stock_to_erp(order: PurchaseOrder):
    config = get_app_config()
    cookies_dir = config.get("cookies_dir", "../cookies")
    client = BigSellerClient(config["ydm_token"], cookies_file_path=os.path.join(cookies_dir, "big_seller.cookies"))
    client.login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
    sync_id = f"IN-EC-{order.purchase_order_id}"
    stock_list = []
    for item in order.store_skus:
        sku = item["sku"]
        print(f"sync_stock_to_erp add sku {sku}")
        sku_info = request_context.get_backend().get_sku(sku)
        stock_list.append({
            "skuId": int(sku_info.erp_sku_id),
            "stockPrice": item["unit_price"] / 100.0,
            "shelfList": [
                {
                    "shelfId": "",
                    "shelfName": "",
                    "stockQty": item["check_in_quantity"] * item["sku_unit_quantity"]
                }
            ]
        })
    req = {
        "detailsAddBoList": stock_list,
        "id": "",
        "inoutTypeId": "1001",
        "isAutoInoutStock": 1,
        "note": f"ec-erp 采购单：{order.purchase_order_id} [入库单={sync_id}]",
        "warehouseId": config["big_seller_warehouse_id"],
        "zoneId": None
    }
    print("sync_stock_to_erp req: ", json.dumps(req))
    res = client.add_stock_to_erp(req)
    print("sync_stock_to_erp res: ", json.dumps(res))
    success = res["successNum"]
    fail = res["failNum"]
    print(f"导入erp仓库： 成功： {success} 异常：  {fail}")
    if fail > 0:
        return response_util.pack_error_response(1004, f"导入erp仓库： 成功： {success} 异常：  {fail}")
    else:
        return response_util.pack_response(res)


@supplier_apis.route('/submit_purchase_order_and_next_step', methods=["POST"])
def submit_purchase_order_and_next_step():
    """
    采购流程图：
    草稿 -- 选择采购物品，提交采购单 -->
    供应商捡货中 -- 厂家提供采购清单，采购单确认 -->
    待发货 -- 厂家发货，填写海运公司，填写港口，填写海运费， 预计到达日期 -->
    海运中 -- 抵达海外仓库，点货入库 -->
    已入库 -- 同步erp -->
    完成
    :return:
    """
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    order = build_purchase_order_from_req()
    if order.purchase_step == "草稿":
        order.purchase_skus = remove_empty_sku(order.purchase_skus)
        order.purchase_step = "供应商捡货中"
    elif order.purchase_step == "供应商捡货中":
        order.purchase_skus = remove_empty_sku(order.purchase_skus)
        # 更新供应价到db
        save_purchase_price(order)
        order.purchase_date = datetime.datetime.now().strftime("%Y-%m-%d")
        order.purchase_step = "待发货"
    elif order.purchase_step == "待发货":
        order.store_skus = [
            copy.deepcopy(e) for e in order.purchase_skus
        ]
        for item in order.store_skus:
            item["check_in_quantity"] = item["quantity"]
        order.purchase_step = "海运中"
    elif order.purchase_step == "海运中":
        order.purchase_step = "已入库"
    elif order.purchase_step == "已入库":
        sync_stock_to_erp(order)
        order.purchase_step = "完成"
    else:
        raise Exception("非法状态")
    request_context.get_backend().store_purchase_order(order)
    return response_util.pack_response(DtoUtil.to_dict(order))
