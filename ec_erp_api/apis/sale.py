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
import logging

sale_apis = Blueprint('sale', __name__)
error_logger = logging.getLogger("ERROR")

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
    
    # 获取当前项目ID
    project_id = request_context.get_current_project_id()
    
    # 创建或更新SKU销售价格
    sku_sale_price = SkuSalePrice(
        project_id=project_id,
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
    
    # 直接返回格式化结果，因为records_dict已经是字典列表了
    return response_util.pack_json_response({
        "total": total,
        "list": records_dict
    })


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
    
    # 获取当前项目ID
    project_id = request_context.get_current_project_id()
    
    # 创建销售订单
    sale_order = SaleOrder(
        project_id=project_id,
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
    
    # 确保project_id一致
    existing_order.project_id = request_context.get_current_project_id()
    
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


def sync_sale_order_to_erp(order: SaleOrder):
    """
    同步销售订单出库到ERP
    参考sync_stock_to_erp的实现，但使用出库类型1002
    """
    config = get_app_config()
    cookies_dir = config.get("cookies_dir", "../cookies")
    client = BigSellerClient(config["ydm_token"], cookies_file_path=os.path.join(cookies_dir, "big_seller.cookies"))
    client.login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
    
    sync_id = f"OUT-EC-{order.order_id}"
    stock_list = []
    
    # 解析sale_sku_list（JSON字符串）
    try:
        sale_sku_list = json.loads(order.sale_sku_list) if isinstance(order.sale_sku_list, str) else order.sale_sku_list
    except Exception as e:
        error_logger.error(f"sync_sale_order_to_erp parse sale_sku_list failed: {e}", exc_info=True)
        print(f"sync_sale_order_to_erp parse sale_sku_list failed: {e}")
        return response_util.pack_error_response(1004, f"解析SKU列表失败: {str(e)}")
    
    # 遍历SKU构建出库列表
    for item in sale_sku_list:
        sku = item.get("sku")
        if not sku:
            continue
        
        print(f"sync_sale_order_to_erp add sku {sku}")
        sku_info = request_context.get_backend().get_sku(sku)
        
        if sku_info is None:
            print(f"sync_sale_order_to_erp sku {sku} not found in database")
            return response_util.pack_error_response(1004, f"SKU {sku} 未找到")
        
        if not sku_info.erp_sku_id:
            print(f"sync_sale_order_to_erp sku {sku} has no erp_sku_id")
            return response_util.pack_error_response(1004, f"SKU {sku} 没有关联的ERP SKU ID")
        
        stock_list.append({
            "skuId": int(sku_info.erp_sku_id),
            "stockPrice": None, 
            "shelfList": [
                {
                    "shelfId": config["big_seller_shelf_id"],
                    "shelfName": config["big_seller_shelf_name"],
                    "stockQty": int(item.get("quantity", 0))  # 销售数量
                }
            ]
        })
    
    if len(stock_list) == 0:
        print("sync_sale_order_to_erp no valid sku to sync")
        return response_util.pack_error_response(1004, "没有有效的SKU需要出库")
    
    # 构建出库请求（inoutTypeId为1002表示普通出库）
    req = {
        "detailsAddBoList": stock_list,
        "id": "",
        "inoutTypeId": "1002",  # 1002 普通出库
        "isAutoInoutStock": 1,
        "note": f"ec-erp 销售订单：{order.order_id} [出库单={sync_id}]",
        "warehouseId": config["big_seller_warehouse_id"],
        "zoneId": None
    }
    
    print("sync_sale_order_to_erp req: ", json.dumps(req))
    res = client.add_stock_to_erp(req)
    print("sync_sale_order_to_erp res: ", json.dumps(res))
    
    success = res["successNum"]
    fail = res["failNum"]
    print(f"同步到ERP仓库出库： 成功： {success} 失败： {fail}")
    
    if fail > 0:
        return response_util.pack_error_response(1004, f"同步到ERP仓库出库： 成功： {success} 失败： {fail}")
    
    # 返回None表示成功
    return None


@sale_apis.route('/submit_sale_order', methods=["POST"])
@api_post_request()
def submit_sale_order():
    """
    确认提交销售订单：
    1：将销售的订单信息，通过add_stock_to_erp接口同步到erp(1002出库)
    2：（将状态从"待同步"改为"已同步"）
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
    
    # 同步出库到ERP
    try:
        sync_result = sync_sale_order_to_erp(existing_order)
        if sync_result is not None:
            # 同步失败，返回错误信息
            return sync_result
    except Exception as e:
        error_logger.error(f"同步到ERP失败: {str(e)}", exc_info=True)
        return response_util.pack_error_response(1006, f"同步到ERP失败: {str(e)}")
    
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
    
    # 直接返回格式化结果，因为records_dict已经是字典列表了
    return response_util.pack_json_response({
        "total": total,
        "list": records_dict
    })

