#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: up_seller_adapter
@author: jkguo
@create: 2026/05/02

UpSeller 平台的 SellerClient 适配实现。

字段映射依据：test/up_test/up_seller_response_samples.json 探测样本：
- /api/sku/index-single：SKU 列表行字段 id/idStr/sku/title/imgUrl/isGroup
- /api/sku/detail-single：SKU 详情包含 warehouseVOS（注意大写）每项 warehouseId/available/onhand
- /api/warehouse-sku/list：库存行字段 skuId/sku/skuTitle/imgUrl/onhand/allocated/available
  ⚠ 没有 avgDailySales 字段，UpSeller 当前未在该接口暴露日销均量

入/出库请求体已按前端 getAddData 抓包确认：
- 顶层必填 inoutClass（手动入库默认 other）
- details 数量字段为 qty（不是 BigSeller 的 stockQty）
- details 含 skuId/sku；入库可带 costPrice、shelfNumber、isNewShelfNumber
"""
import logging
import typing
from typing import List, Optional

from ec.bigseller.up_seller_client import UpSellerClient
from ec.seller_client import (
    InventoryDetail,
    SellerClient,
    SkuDetail,
    StockMoveItem,
    StockResult,
)
from ec.up_seller_sales_manager import UpSellerSalesManager
from ec.upseller_sku_manager import UpSellerSkuManager


class UpSellerAdapter(SellerClient):

    def __init__(
            self,
            client: UpSellerClient,
            sku_manager: UpSellerSkuManager,
            email: str,
            password: str,
            warehouse_id: int,
            sales_manager: Optional[UpSellerSalesManager] = None):
        self._client = client
        self._sku_manager = sku_manager
        self._sales_manager = sales_manager
        self._email = email
        self._password = password
        self._warehouse_id = int(warehouse_id)
        self._logger = logging.getLogger("INVOKER")

    def login(self) -> None:
        self._client.login(self._email, self._password)

    def get_warehouse_id(self) -> int:
        return self._warehouse_id

    def _ensure_sku_id(self, sku: str) -> Optional[str]:
        sku_id = self._sku_manager.get_sku_id(sku)
        if sku_id is not None:
            return sku_id
        # 命中失败先用单条搜索接口尝试，避免每次都全量同步
        page = self._client.query_sku_page(
            page_no=1, page_size=5, search_value=sku, search_type="1"
        )
        rows = page.get("rows") or []
        for row in rows:
            if row.get("sku") == sku:
                self._sku_manager.add(row)
                self._sku_manager.dump()
                return self._sku_manager.get_sku_id(sku)
        # 单条搜不到再退回全量同步
        self._sku_manager.load_and_update_all_sku(self._client)
        return self._sku_manager.get_sku_id(sku)

    def get_sku_id(self, sku: str) -> Optional[str]:
        return self._ensure_sku_id(sku)

    @staticmethod
    def _pick_image(*candidates) -> str:
        for v in candidates:
            if v:
                return str(v)
        return ""

    def query_sku_detail(self, sku: str) -> SkuDetail:
        sku_id = self._ensure_sku_id(sku)
        if sku_id is None:
            raise Exception(f"sku {sku} 不存在")
        raw = self._client.query_sku_detail(sku_id, "single")
        inventory = 0
        for vo in raw.get("warehouseVOS") or []:
            if int(vo.get("warehouseId") or 0) != self._warehouse_id:
                continue
            inventory += int(vo.get("available") or 0)
        # 顶层 imgUrl 通常为空，回落到 warehouseVOS / 列表行的 imgUrl
        image_url = self._pick_image(
            raw.get("imgUrl"),
            *(vo.get("imgUrl") for vo in (raw.get("warehouseVOS") or [])),
        )
        return SkuDetail(
            erp_sku_id=str(raw.get("idStr") or raw.get("id") or sku_id),
            title=raw.get("title") or "",
            image_url=image_url,
            inventory_in_warehouse=inventory,
            raw=raw,
        )

    def query_sku_inventory_detail(self, sku: str) -> InventoryDetail:
        raw = self._client.query_sku_inventory_detail(sku, self._warehouse_id)
        if raw is None or (isinstance(raw, dict) and raw.get("error")):
            return InventoryDetail(
                available=0, title="", image_url="", avg_daily_sales=0.0, raw=raw or {}
            )
        # UpSeller `/api/warehouse-sku/list` 不返回 avgDailySales，统一置 0；
        # 业务侧 inventory_support_days 计算会按 0 处理。
        return InventoryDetail(
            available=int(raw.get("available") or 0),
            title=raw.get("skuTitle") or raw.get("title") or "",
            image_url=raw.get("imgUrl") or "",
            avg_daily_sales=0.0,
            raw=raw,
        )

    def _build_inout_details(
            self,
            items: List[StockMoveItem],
            with_cost_price: bool = False) -> typing.List[dict]:
        details = []
        for it in items:
            entry = {
                "skuId": str(it.erp_sku_id),
                "sku": it.sku,
                "qty": int(it.quantity),
                "isNewShelfNumber": 0,
            }
            if with_cost_price and it.unit_price_yuan is not None:
                entry["costPrice"] = float(it.unit_price_yuan)
            details.append(entry)
        return details

    def add_stock_in(self, items: List[StockMoveItem], note: str) -> StockResult:
        # 对齐前端 /zh-CN/inventory/add-inbound-order 的 getAddData 结构
        payload = {
            "warehouseId": str(self._warehouse_id),
            "inoutClass": "other",
            "note": note or "",
            "details": self._build_inout_details(items, with_cost_price=True),
        }
        raw = self._client.add_stock_to_erp(payload)
        return self._extract_stock_result(raw, total=len(items))

    def add_stock_out(self, items: List[StockMoveItem], note: str) -> StockResult:
        payload = {
            "warehouseId": str(self._warehouse_id),
            "inoutClass": "other",
            "note": note or "",
            "details": self._build_inout_details(items, with_cost_price=False),
        }
        raw = self._client.out_stock_from_erp(payload)
        return self._extract_stock_result(raw, total=len(items))

    def refresh_local_sku_cache(self) -> None:
        self._sku_manager.load_and_update_all_sku(self._client)

    def load_sku_avg_daily_sales(self, begin_date, end_date):
        if self._sales_manager is None:
            return None
        return self._sales_manager.load_avg_daily_sales(begin_date, end_date)

    def get_sku_manager(self):
        return self._sku_manager

    def get_wait_print_order_ship_provider_list(self) -> list:
        grouped = {}
        for row in self._iter_wait_print_rows():
            auth_id = str(row.get("authIdStr") or row.get("authId") or "")
            if not auth_id:
                continue
            item = grouped.get(auth_id)
            if item is None:
                item = {
                    "id": auth_id,
                    "name": row.get("providerName") or auth_id,
                    "count": 0,
                    "platform": row.get("platform") or "",
                }
                grouped[auth_id] = item
            item["count"] += 1
        return list(grouped.values())

    def search_wait_print_order(self, shipping_provider_id, current_page, page_size):
        total, rows = self._client.search_wait_print_order_page(
            self._warehouse_id,
            page_num=current_page,
            page_size=page_size,
            auth_id=shipping_provider_id,
        )
        return total, [self._map_wait_print_order(row) for row in rows]

    def get_order_detail(self, order_id) -> dict:
        raw = self._client.get_order_detail_raw(order_id)
        order = raw.get("order") if isinstance(raw.get("order"), dict) else {}
        items = self._collect_order_items(raw, order)
        return {
            "splitOrder": bool(int(order.get("isSplit") or 0)),
            "orderItemVoList": [
                self._map_order_item(item, order) for item in items
            ],
        }

    def download_order_mask_pdf_file(
            self,
            order_id: str,
            mark_id: str,
            platform: str,
            save_pdf_file: str,
            auth_ids: Optional[str] = None) -> None:
        order_ids = [part for part in str(order_id).split(",") if part]
        auth_id_list = [part for part in str(auth_ids or "").split(",") if part]
        self._client.download_order_label_pdf(order_ids, auth_id_list, save_pdf_file)

    def mark_order_printed(self, order_id: str):
        order_ids = [part for part in str(order_id).split(",") if part]
        return self._client.mark_orders_printed(order_ids)

    def _iter_wait_print_rows(self, auth_id=None, page_size: int = 100):
        page_num = 1
        seen = 0
        while page_num <= 200:
            total, rows = self._client.search_wait_print_order_page(
                self._warehouse_id,
                page_num=page_num,
                page_size=page_size,
                auth_id=auth_id,
            )
            if not rows:
                break
            for row in rows:
                yield row
            seen += len(rows)
            if seen >= int(total or 0):
                break
            page_num += 1

    @staticmethod
    def _map_wait_print_order(row: dict) -> dict:
        return {
            "id": str(row.get("idStr") or row.get("id") or ""),
            "shopId": row.get("shopId"),
            "platformOrderId": str(row.get("orderId") or ""),
            "packageNo": row.get("orderNumber") or "",
            "shippingCarrierName": row.get("providerName") or "",
            "trackingNo": row.get("trackingNumber") or "",
            "multilingualViewStatus": "待打单",
            "amount": row.get("orderAmount") or "",
            "platform": row.get("platform") or "",
            "printLabelMark": int(row.get("isPrintLabel") or 0),
            "authId": str(row.get("authIdStr") or row.get("authId") or ""),
        }

    @staticmethod
    def _collect_order_items(raw: dict, order: dict) -> list:
        items = order.get("orderItemList") or []
        if items:
            return items
        collected = []
        for group in raw.get("orderGroupVoList") or []:
            if isinstance(group, dict):
                collected.extend(group.get("orderItemList") or [])
        return collected

    def _map_order_item(self, item: dict, order: dict) -> dict:
        platform_sku = str(item.get("variationSku") or item.get("productSku") or "").strip()
        inventory_sku = self._sku_manager.resolve_sales_sku({
            "shopId": item.get("shopId") or order.get("shopId"),
            "platform": item.get("platform") or order.get("platform"),
            "variationId": item.get("variationId"),
            "variationSku": platform_sku,
        }) or platform_sku
        quantity = int(item.get("productCount") or 0)
        sku_info = self._sku_manager.sku_map.get(inventory_sku) or {}
        group_list = None
        if int(sku_info.get("isGroup") or 0):
            group_list = []
            for child in sku_info.get("groupVOS") or []:
                child_sku = str(child.get("varSku") or "").strip()
                child_num = int(child.get("num") or 0)
                if child_sku and child_num > 0:
                    group_list.append({
                        "varSku": child_sku,
                        "num": child_num,
                    })
            if not group_list:
                group_list = None
        return {
            "id": str(item.get("idStr") or item.get("id") or ""),
            "allocated": quantity,
            "allocating": quantity,
            "varSku": platform_sku,
            "inventorySku": inventory_sku,
            "varSkuGroupVoList": group_list,
        }

    @staticmethod
    def _extract_stock_result(raw, total: int) -> StockResult:
        # UpSeller 接口返回字段尚未在探测中确认，做最大兼容：
        # - 若有 successNum/failNum 直接用
        # - 否则视成功（_check_response 已抛非 0 code），全部计入 success
        if isinstance(raw, dict):
            success = raw.get("successNum")
            fail = raw.get("failNum")
            if success is not None or fail is not None:
                return StockResult(
                    success=int(success or 0),
                    fail=int(fail or 0),
                    raw=raw,
                )
        return StockResult(success=total, fail=0, raw=raw if isinstance(raw, dict) else {"raw": raw})
