#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: system
@author: jkguo
@create: 2024/2/24
"""
import copy
import datetime
import time
from ec_erp_api.common.api_core import api_post_request
from ec_erp_api.common import request_util, response_util, request_context
from flask import (
    Blueprint
)
from ec_erp_api.common.seller_util import build_seller_client
from ec.seller_client import StockMoveItem
from ec_erp_api.models.mysql_backend import PurchaseOrder, SkuDto, SkuPurchasePriceDto, DtoUtil

supplier_apis = Blueprint('supplier', __name__)


@supplier_apis.route('/search_supplier', methods=["POST"])
@api_post_request()
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
@api_post_request()
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
    inventory_support_days = request_util.get_int_param("inventory_support_days", 0)
    sort_types = request_util.get_param("sort")

    current_page = request_util.get_int_param("current_page")
    page_size = request_util.get_int_param("page_size")
    offset = (current_page - 1) * page_size
    if offset < 0:
        offset = 0
    total, records = request_context.get_backend().search_sku(
        sku_group, sku_name, sku,
        offset, page_size, inventory_support_days, sort_types)
    return response_util.pack_pagination_result(total, records)


@supplier_apis.route('/save_sku', methods=["POST"])
@api_post_request()
def save_sku():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    seller = build_seller_client()
    sku = request_util.get_str_param("sku")
    sku_group = request_util.get_str_param("sku_group")
    sku_name = request_util.get_str_param("sku_name")
    sku_unit_name = request_util.get_str_param("sku_unit_name")
    sku_unit_quantity = request_util.get_int_param("sku_unit_quantity")
    # 打包体积字段（cm，可选，默认 0；老客户端不传时不会破坏行为）
    sku_pack_length = request_util.get_int_param("sku_pack_length", 0)
    sku_pack_width = request_util.get_int_param("sku_pack_width", 0)
    sku_pack_height = request_util.get_int_param("sku_pack_height", 0)
    avg_sell_quantity = request_util.get_int_param("avg_sell_quantity")
    shipping_stock_quantity = request_util.get_int_param("shipping_stock_quantity")
    inventory_support_days = request_util.get_int_param("inventory_support_days")
    if seller.get_sku_id(sku) is None:
        return response_util.pack_error_response(1003, f"sku {sku} 不存在")
    sku_detail = seller.query_sku_detail(sku)
    s = SkuDto(
        project_id=request_context.get_current_project_id(),
        sku=sku,
        sku_group=sku_group,
        sku_name=sku_name,
        inventory=sku_detail.inventory_in_warehouse,
        erp_sku_name=sku_detail.title,
        erp_sku_image_url=sku_detail.image_url,
        erp_sku_id=sku_detail.erp_sku_id,
        erp_sku_info={},
        sku_unit_name=sku_unit_name,
        sku_unit_quantity=sku_unit_quantity,
        sku_pack_length=sku_pack_length,
        sku_pack_width=sku_pack_width,
        sku_pack_height=sku_pack_height,
        avg_sell_quantity=avg_sell_quantity,
        inventory_support_days=inventory_support_days,
        shipping_stock_quantity=shipping_stock_quantity
    )
    request_context.get_backend().store_sku(s)
    return response_util.pack_response(DtoUtil.to_dict(s))


@supplier_apis.route('/add_sku', methods=["POST"])
@api_post_request()
def add_sku():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    seller = build_seller_client()
    skus = request_util.get_str_param("skus").strip()
    backend = request_context.get_backend()
    op_detail = {}
    success_count = 0
    ignore_count = 0
    fail_count = 0
    for line in skus.split("\n"):
        line = line.strip()
        if len(line) <= 0:
            continue
        sku = line
        # 检测数据库中是否有该sku
        if backend.get_sku(sku) is not None:
            op_detail[sku] = "ignored"
            ignore_count += 1
            continue
        sku_group = "待定"
        sku_name = ""
        sku_unit_name = ""
        sku_unit_quantity = 1
        shipping_stock_quantity = 0
        if seller.get_sku_id(sku) is None:
            op_detail[sku] = f"sku {sku} 不存在"
            fail_count += 1
            continue
        sku_detail = seller.query_sku_detail(sku)
        inv_detail = seller.query_sku_inventory_detail(sku)
        # 计算平均销售sku数量
        if inv_detail.avg_daily_sales <= 0:
            avg_sell_quantity = 0
        else:
            avg_sell_quantity = round(inv_detail.avg_daily_sales * 1.1, 2)
        # 计算库存支撑天数
        inventory = sku_detail.inventory_in_warehouse
        if avg_sell_quantity > 0.01:
            inventory_support_days = int(inventory / avg_sell_quantity)
        else:
            inventory_support_days = inventory / 0.01
        s = SkuDto(
            project_id=request_context.get_current_project_id(),
            sku=sku,
            sku_group=sku_group,
            sku_name=sku_name,
            inventory=inventory,
            erp_sku_name=sku_detail.title,
            erp_sku_image_url=sku_detail.image_url,
            erp_sku_id=sku_detail.erp_sku_id,
            erp_sku_info={},
            sku_unit_name=sku_unit_name,
            sku_unit_quantity=sku_unit_quantity,
            sku_pack_length=0,
            sku_pack_width=0,
            sku_pack_height=0,
            avg_sell_quantity=avg_sell_quantity,
            inventory_support_days=inventory_support_days,
            shipping_stock_quantity=shipping_stock_quantity
        )
        request_context.get_backend().store_sku(s)
        success_count += 1
        op_detail[sku] = f"success"
    return response_util.pack_response({
        "success_count": success_count,
        "ignore_count": ignore_count,
        "fail_count": fail_count,
        "detail": op_detail
    })


@supplier_apis.route('/sync_all_sku', methods=["POST"])
@api_post_request()
def sync_all_sku():
    # 同步策略：仅显式更新 inventory / erp_sku_* / avg_sell_quantity /
    # inventory_support_days / shipping_stock_quantity；
    # sku_pack_length / sku_pack_width / sku_pack_height 等手工维护字段保留旧值。
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    backend = request_context.get_backend()
    _, sku_list = backend.search_sku(sku_group=None, sku_name=None, sku=None, offset=0, limit=10000)
    seller = build_seller_client()
    update_count = 0
    fail_count = 0
    for item in sku_list:
        if seller.get_sku_id(item.sku) is None:
            print(f"cannot found sku {item.sku} in sku manager.")
            fail_count += 1
            continue
        sku_detail = seller.query_sku_detail(item.sku)
        inv_detail = seller.query_sku_inventory_detail(item.sku)
        item.inventory = sku_detail.inventory_in_warehouse
        item.erp_sku_name = sku_detail.title
        item.erp_sku_image_url = sku_detail.image_url
        item.erp_sku_id = sku_detail.erp_sku_id
        # 计算平均销售sku数量
        item.avg_sell_quantity = round(inv_detail.avg_daily_sales * 1.1, 2)
        # 计算库存支撑天数
        if item.avg_sell_quantity > 0.01:
            item.inventory_support_days = int(item.inventory / item.avg_sell_quantity)
        else:
            item.inventory_support_days = item.inventory / 0.01
        backend.store_sku(item)
        update_count += 1
        time.sleep(0.3)
    return response_util.pack_response({
        "update_count": update_count,
        "fail_count": fail_count
    })


@supplier_apis.route('/search_sku_purchase_price', methods=["POST"])
@api_post_request()
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
@api_post_request()
def search_purchase_order():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    order_type = request_util.get_int_param("order_type")
    if order_type is None or order_type not in (1, 2):
        return response_util.pack_error_response(1003, "order_type参数无效，必须为1(境内进货)或2(境外线下)")
    current_page = request_util.get_int_param("current_page")
    page_size = request_util.get_int_param("page_size")
    offset = (current_page - 1) * page_size
    if offset < 0:
        offset = 0
    total, records = request_context.get_backend().search_purchase_order(offset, page_size, order_type)
    return response_util.pack_pagination_result(total, records)


@supplier_apis.route('/query_sku_purchase_price', methods=["POST"])
@api_post_request()
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
    # 注：采购单 SKU 快照仅冗余销售/采购相关字段（unit_price / sku_unit_quantity 等），
    # 不冗余打包体积字段（sku_pack_*），按 OpenSpec change add-sku-pack-volume 设计：
    # 体积属于 t_sku_info 主数据，使用方按需读取，避免历史快照过早绑定可变属性。
    order_type = request_util.get_int_param("order_type")
    if order_type is None or order_type not in (1, 2):
        raise Exception("order_type参数无效，必须为1(境内进货)或2(境外线下)")

    if order_type == 2:
        supplier_id = 10000000
        supplier_name = "线下销售"
    else:
        supplier = request_context.get_backend().get_supplier(request_util.get_int_param("supplier_id"))
        if supplier is None:
            raise Exception("供应商不存在")
        supplier_id = supplier.supplier_id
        supplier_name = supplier.supplier_name
    purchase_skus = request_util.get_param("purchase_skus", [])
    format_purchase_skus = []
    sku_amount = 0
    for item in purchase_skus:
        sku = item["sku"]
        sku_info = request_context.get_backend().get_sku(sku)
        if sku is None:
            raise Exception(f"商品sku [{sku}] 不存在")
        if item["quantity"] is None:
            quantity = None
        else:
            quantity = int(item["quantity"])
        format_purchase_skus.append({
            "sku": sku,
            "sku_group": sku_info.sku_group,
            "sku_name": sku_info.sku_name,
            "unit_price": int(item["unit_price"]),
            "quantity": quantity,
            "sku_unit_name": sku_info.sku_unit_name,
            "sku_unit_quantity": sku_info.sku_unit_quantity,
            "avg_sell_quantity": sku_info.avg_sell_quantity,
            "shipping_stock_quantity": sku_info.shipping_stock_quantity
        })
        if quantity is not None:
            sku_amount += int(item["unit_price"]) * quantity
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
        order_type=order_type,
        supplier_id=supplier_id,
        supplier_name=supplier_name,
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
@api_post_request()
def save_purchase_order():
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    order = build_purchase_order_from_req()
    if order.order_type is None or order.order_type not in (1, 2):
        return response_util.pack_error_response(1003, "order_type参数无效，必须为1(境内进货)或2(境外线下)")
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


def _build_stock_move_items(order: PurchaseOrder, with_price: bool):
    items = []
    for entry in order.store_skus:
        sku = entry["sku"]
        sku_info = request_context.get_backend().get_sku(sku)
        if sku_info is None:
            raise Exception(f"SKU {sku} 未找到")
        if not sku_info.erp_sku_id:
            raise Exception(f"SKU {sku} 没有关联的ERP SKU ID")
        items.append(StockMoveItem(
            erp_sku_id=str(sku_info.erp_sku_id),
            sku=sku,
            quantity=int(entry["check_in_quantity"]) * int(entry["sku_unit_quantity"]),
            unit_price_yuan=(entry["unit_price"] / 100.0) if with_price else None,
        ))
    return items


def sync_stock_to_erp(order: PurchaseOrder):
    seller = build_seller_client()
    sync_id = f"IN-EC-{order.purchase_order_id}"
    items = _build_stock_move_items(order, with_price=True)
    note = f"ec-erp 采购单：{order.purchase_order_id} [入库单={sync_id}]"
    for it in items:
        print(f"sync_stock_to_erp add sku {it.sku}")
    res = seller.add_stock_in(items, note)
    print(f"导入erp仓库： 成功： {res.success} 异常：  {res.fail}")
    if res.fail > 0:
        return response_util.pack_error_response(
            1004, f"导入erp仓库： 成功： {res.success} 异常：  {res.fail}")
    return response_util.pack_response(res.raw)


def sync_stock_out_to_erp(order: PurchaseOrder):
    """
    境外线下采购单同步ERP出库（BigSeller inoutTypeId=1002 / UpSeller add-out 接口）
    """
    seller = build_seller_client()
    sync_id = f"OUT-EC-PO-{order.purchase_order_id}"
    try:
        items = _build_stock_move_items(order, with_price=False)
    except Exception as e:
        return response_util.pack_error_response(1004, str(e))
    if len(items) == 0:
        return response_util.pack_error_response(1004, "没有有效的SKU需要出库")
    note = f"ec-erp 境外线下销售单：{order.purchase_order_id} [出库单={sync_id}]"
    for it in items:
        print(f"sync_stock_out_to_erp add sku {it.sku}")
    res = seller.add_stock_out(items, note)
    print(f"境外采购出库ERP： 成功： {res.success} 失败： {res.fail}")
    if res.fail > 0:
        return response_util.pack_error_response(
            1004, f"境外采购出库ERP： 成功： {res.success} 失败： {res.fail}")
    return response_util.pack_response(res.raw)


@supplier_apis.route('/submit_purchase_order_and_next_step', methods=["POST"])
@api_post_request()
def submit_purchase_order_and_next_step():
    """
    类型1(境内进货)采购流程图：
    草稿 -- 选择采购物品，提交采购单 -->
    供应商捡货中 -- 厂家提供采购清单，采购单确认 -->
    待发货 -- 厂家发货，填写海运公司，填写港口，填写海运费， 预计到达日期 -->
    海运中 -- 抵达海外仓库，点货入库 -->
    已入库 -- 同步erp -->
    完成

    类型2(境外线下)采购流程图：
    草稿 -- 选择采购物品，提交采购单 -->
    境外拣货 -- 确认出货 -->
    已出库 -- 同步ERP出库 -->
    完成
    :return:
    """
    if not request_context.validate_user_permission(request_context.PMS_SUPPLIER):
        return response_util.pack_error_response(1008, "权限不足")
    order = build_purchase_order_from_req()
    if order.order_type is None or order.order_type not in (1, 2):
        return response_util.pack_error_response(1003, "order_type参数无效，必须为1(境内进货)或2(境外线下)")
    if order.order_type == 1:
        return _submit_purchase_order_type1(order)
    else:
        return _submit_purchase_order_type2(order)


def _submit_purchase_order_type1(order: PurchaseOrder):
    """境内进货采购单流程扭转"""
    if order.purchase_step == "草稿":
        order.purchase_skus = remove_empty_sku(order.purchase_skus)
        order.purchase_step = "供应商捡货中"
    elif order.purchase_step == "供应商捡货中":
        order.purchase_skus = remove_empty_sku(order.purchase_skus)
        for item in order.purchase_skus:
            if item["quantity"] is None:
                return response_util.pack_error_response(1004, "存在未确定数量的sku")
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


def _submit_purchase_order_type2(order: PurchaseOrder):
    """境外线下采购单流程扭转"""
    if order.purchase_step == "草稿":
        order.purchase_skus = remove_empty_sku(order.purchase_skus)
        for item in order.purchase_skus:
            if item["quantity"] is None:
                return response_util.pack_error_response(1004, "存在未确定数量的sku")
        order.purchase_date = datetime.datetime.now().strftime("%Y-%m-%d")
        order.store_skus = [
            copy.deepcopy(e) for e in order.purchase_skus
        ]
        for item in order.store_skus:
            item["check_in_quantity"] = item["quantity"]
        order.purchase_step = "境外拣货"
    elif order.purchase_step == "境外拣货":
        # 保存价格
        save_purchase_price(order)
        order.purchase_step = "已出库"
    elif order.purchase_step == "已出库":
        sync_stock_out_to_erp(order)
        order.purchase_step = "完成"
    else:
        raise Exception("非法状态")
    request_context.get_backend().store_purchase_order(order)
    return response_util.pack_response(DtoUtil.to_dict(order))
