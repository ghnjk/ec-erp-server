#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sale
@author: jkguo
@create: 2024/2/24
"""
import copy
import datetime
import os
import time
from ec_erp_api.common.api_core import api_post_request
from ec_erp_api.common import request_util, response_util, request_context
from flask import (
    Blueprint
)
from ec_erp_api.app_config import get_app_config
from ec.bigseller.big_seller_client import BigSellerClient
from ec.sku_manager import SkuManager
from ec_erp_api.models.mysql_backend import (
    PurchaseOrder, SkuDto, SkuPurchasePriceDto, DtoUtil, SkuSalePrice, SaleOrder
)
import json

sale_apis = Blueprint('sale', __name__)


@sale_apis.route('/save_sku_sale_price', methods=["POST"])
@api_post_request()
def save_sku_sale_price():
    """
    保存或更新SKU销售价格
    """
    if not request_context.validate_user_permission(request_context.PMS_SALE):
        return response_util.pack_error_response(1008, "权限不足")
    
    sku = request_util.get_str_param("sku")
    if sku is None or sku == "":
        return response_util.pack_error_response(1003, "sku参数不能为空")
    
    unit_price = request_util.get_float_param("unit_price")
    if unit_price is None or unit_price <= 0:
        return response_util.pack_error_response(1003, "unit_price参数必须大于0")
    
    # 创建或更新SKU销售价格
    sku_sale_price = SkuSalePrice(
        sku=sku,
        unit_price=unit_price
    )
    
    backend = request_context.get_backend()
    backend.store_sku_sale_price(sku_sale_price)
    
    return response_util.pack_simple_response()


@sale_apis.route('/search_sku_sale_price', methods=["POST"])
@api_post_request()
def search_sku_sale_price():
    """
    搜索SKU销售价格
    """
    if not request_context.validate_user_permission(request_context.PMS_SALE):
        return response_util.pack_error_response(1008, "权限不足")
    
    sku = request_util.get_str_param("sku")
    if sku is not None:
        sku = sku.strip()
    if sku == "":
        sku = None
    
    current_page = request_util.get_int_param("current_page", default_value=1)
    page_size = request_util.get_int_param("page_size", default_value=20)
    offset = (current_page - 1) * page_size
    if offset < 0:
        offset = 0
    
    backend = request_context.get_backend()
    total, records = backend.search_sku_sale_price(sku, offset, page_size)
    
    # 转换为字典
    records_dict = [DtoUtil.to_dict(record) for record in records]
    
    return response_util.pack_pagination_result(total, records_dict)


@sale_apis.route('/create_sale_order', methods=["POST"])
@api_post_request()
def create_sale_order():
    """
    创建销售订单
    """
    if not request_context.validate_user_permission(request_context.PMS_SALE):
        return response_util.pack_error_response(1008, "权限不足")
    
    # 获取参数
    order_date_str = request_util.get_str_param("order_date")
    if order_date_str is None or order_date_str == "":
        return response_util.pack_error_response(1003, "order_date参数不能为空")
    
    # 获取SKU列表
    sale_sku_list = request_util.get_param("sale_sku_list")
    if sale_sku_list is None or not isinstance(sale_sku_list, list) or len(sale_sku_list) == 0:
        return response_util.pack_error_response(1003, "sale_sku_list参数必须是非空数组")
    
    # 验证并补充SKU列表数据
    backend = request_context.get_backend()
    total_amount = 0.0
    validated_sku_list = []
    
    for idx, sku_item in enumerate(sale_sku_list):
        if not isinstance(sku_item, dict):
            return response_util.pack_error_response(1003, f"sale_sku_list[{idx}]必须是对象")
        
        sku = sku_item.get("sku")
        if not sku or sku == "":
            return response_util.pack_error_response(1003, f"sale_sku_list[{idx}].sku不能为空")
        
        unit_price = sku_item.get("unit_price")
        if unit_price is None or unit_price <= 0:
            return response_util.pack_error_response(1003, f"sale_sku_list[{idx}].unit_price必须大于0")
        
        quantity = sku_item.get("quantity")
        if quantity is None or quantity <= 0:
            return response_util.pack_error_response(1003, f"sale_sku_list[{idx}].quantity必须大于0")
        
        # 从数据库获取SKU信息补充字段
        sku_info = backend.get_sku(sku)
        
        # 计算该SKU的总金额
        sku_total_amount = unit_price * quantity
        total_amount += sku_total_amount
        
        # 构建验证后的SKU项
        validated_sku = {
            "sku": sku,
            "sku_group": sku_item.get("sku_group") or (sku_info.sku_group if sku_info else ""),
            "sku_name": sku_item.get("sku_name") or (sku_info.sku_name if sku_info else ""),
            "erp_sku_image_url": sku_item.get("erp_sku_image_url") or (sku_info.erp_sku_image_url if sku_info else ""),
            "unit_price": unit_price,
            "quantity": quantity,
            "total_amount": sku_total_amount
        }
        validated_sku_list.append(validated_sku)
    
    # 解析订单日期
    try:
        order_date = datetime.datetime.strptime(order_date_str, "%Y-%m-%d %H:%M:%S")
    except:
        try:
            order_date = datetime.datetime.strptime(order_date_str, "%Y-%m-%d")
        except:
            return response_util.pack_error_response(1003, "order_date格式错误，应为 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS")
    
    # 创建销售订单
    sale_order = SaleOrder(
        order_date=order_date,
        sale_sku_list=json.dumps(validated_sku_list, ensure_ascii=False),
        total_amount=total_amount,
        status="待同步",
        is_delete=0
    )
    
    order_id = backend.create_sale_order(sale_order)
    
    return response_util.pack_simple_response({
        "order_id": order_id
    })


@sale_apis.route('/update_sale_order', methods=["POST"])
@api_post_request()
def update_sale_order():
    """
    更新销售订单
    """
    if not request_context.validate_user_permission(request_context.PMS_SALE):
        return response_util.pack_error_response(1008, "权限不足")
    
    # 获取订单ID
    order_id = request_util.get_int_param("order_id")
    if order_id is None or order_id <= 0:
        return response_util.pack_error_response(1003, "order_id参数无效")
    
    backend = request_context.get_backend()
    
    # 查询现有订单
    existing_order = backend.get_sale_order(order_id)
    if existing_order is None:
        return response_util.pack_error_response(1004, f"订单不存在: {order_id}")
    
    # 获取更新参数
    order_date_str = request_util.get_str_param("order_date")
    sale_sku_list = request_util.get_param("sale_sku_list")
    status = request_util.get_str_param("status")
    
    # 更新订单日期
    if order_date_str is not None and order_date_str != "":
        try:
            order_date = datetime.datetime.strptime(order_date_str, "%Y-%m-%d %H:%M:%S")
            existing_order.order_date = order_date
        except:
            try:
                order_date = datetime.datetime.strptime(order_date_str, "%Y-%m-%d")
                existing_order.order_date = order_date
            except:
                return response_util.pack_error_response(1003, "order_date格式错误，应为 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS")
    
    # 更新SKU列表
    if sale_sku_list is not None:
        if not isinstance(sale_sku_list, list) or len(sale_sku_list) == 0:
            return response_util.pack_error_response(1003, "sale_sku_list参数必须是非空数组")
        
        # 验证并补充SKU列表数据
        total_amount = 0.0
        validated_sku_list = []
        
        for idx, sku_item in enumerate(sale_sku_list):
            if not isinstance(sku_item, dict):
                return response_util.pack_error_response(1003, f"sale_sku_list[{idx}]必须是对象")
            
            sku = sku_item.get("sku")
            if not sku or sku == "":
                return response_util.pack_error_response(1003, f"sale_sku_list[{idx}].sku不能为空")
            
            unit_price = sku_item.get("unit_price")
            if unit_price is None or unit_price <= 0:
                return response_util.pack_error_response(1003, f"sale_sku_list[{idx}].unit_price必须大于0")
            
            quantity = sku_item.get("quantity")
            if quantity is None or quantity <= 0:
                return response_util.pack_error_response(1003, f"sale_sku_list[{idx}].quantity必须大于0")
            
            # 从数据库获取SKU信息补充字段
            sku_info = backend.get_sku(sku)
            
            # 计算该SKU的总金额
            sku_total_amount = unit_price * quantity
            total_amount += sku_total_amount
            
            # 构建验证后的SKU项
            validated_sku = {
                "sku": sku,
                "sku_group": sku_item.get("sku_group") or (sku_info.sku_group if sku_info else ""),
                "sku_name": sku_item.get("sku_name") or (sku_info.sku_name if sku_info else ""),
                "erp_sku_image_url": sku_item.get("erp_sku_image_url") or (sku_info.erp_sku_image_url if sku_info else ""),
                "unit_price": unit_price,
                "quantity": quantity,
                "total_amount": sku_total_amount
            }
            validated_sku_list.append(validated_sku)
        
        existing_order.sale_sku_list = json.dumps(validated_sku_list, ensure_ascii=False)
        existing_order.total_amount = total_amount
    
    # 更新状态
    if status is not None and status != "":
        existing_order.status = status
    
    # 更新订单
    backend.update_sale_order(existing_order)
    
    return response_util.pack_simple_response()


@sale_apis.route('/delete_sale_order', methods=["POST"])
@api_post_request()
def delete_sale_order():
    """
    删除销售订单
    """
    if not request_context.validate_user_permission(request_context.PMS_SALE):
        return response_util.pack_error_response(1008, "权限不足")
    
    order_id = request_util.get_int_param("order_id")
    if order_id is None or order_id <= 0:
        return response_util.pack_error_response(1003, "order_id参数无效")
    
    backend = request_context.get_backend()
    
    # 检查订单是否存在
    existing_order = backend.get_sale_order(order_id)
    if existing_order is None:
        return response_util.pack_error_response(1004, f"订单不存在: {order_id}")
    
    # 删除订单
    backend.delete_sale_order(order_id)
    
    return response_util.pack_simple_response()


@sale_apis.route('/submit_sale_order', methods=["POST"])
@api_post_request()
def submit_sale_order():
    """
    确认提交销售订单（将状态从"待同步"改为"已同步"）
    """
    if not request_context.validate_user_permission(request_context.PMS_SALE):
        return response_util.pack_error_response(1008, "权限不足")
    
    order_id = request_util.get_int_param("order_id")
    if order_id is None or order_id <= 0:
        return response_util.pack_error_response(1003, "order_id参数无效")
    
    backend = request_context.get_backend()
    
    # 查询现有订单
    existing_order = backend.get_sale_order(order_id)
    if existing_order is None:
        return response_util.pack_error_response(1004, f"订单不存在: {order_id}")
    
    # 检查订单状态
    if existing_order.status == "已同步":
        return response_util.pack_error_response(1005, "订单已经提交过了")
    
    # 更新状态为已同步
    existing_order.status = "已同步"
    backend.update_sale_order(existing_order)
    
    return response_util.pack_simple_response()


@sale_apis.route('/search_sale_order', methods=["POST"])
@api_post_request()
def search_sale_order():
    """
    搜索销售订单
    """
    if not request_context.validate_user_permission(request_context.PMS_SALE):
        return response_util.pack_error_response(1008, "权限不足")
    
    status = request_util.get_str_param("status")
    if status is not None:
        status = status.strip()
    if status == "":
        status = None
    
    begin_date = request_util.get_str_param("begin_date")
    if begin_date is not None:
        begin_date = begin_date.strip()
    if begin_date == "":
        begin_date = None
    
    end_date = request_util.get_str_param("end_date")
    if end_date is not None:
        end_date = end_date.strip()
    if end_date == "":
        end_date = None
    
    current_page = request_util.get_int_param("current_page", default_value=1)
    page_size = request_util.get_int_param("page_size", default_value=20)
    offset = (current_page - 1) * page_size
    if offset < 0:
        offset = 0
    
    backend = request_context.get_backend()
    total, records = backend.search_sale_order(status, begin_date, end_date, offset, page_size)
    
    # 转换为字典，并解析sale_sku_list
    records_dict = []
    for record in records:
        record_dict = DtoUtil.to_dict(record)
        # 将JSON字符串解析为列表
        if record_dict.get("sale_sku_list"):
            try:
                record_dict["sale_sku_list"] = json.loads(record_dict["sale_sku_list"])
            except:
                record_dict["sale_sku_list"] = []
        else:
            record_dict["sale_sku_list"] = []
        records_dict.append(record_dict)
    
    return response_util.pack_pagination_result(total, records_dict)

