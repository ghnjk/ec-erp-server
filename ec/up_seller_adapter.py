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

注意：UpSeller 的入库 (/api/warehouse-inout-list/add-in) 和出库 (/api/warehouse-inout-list/add-out)
请求体字段在探测阶段未做真实写入测试，本适配器按文档字段名 + BigSeller 对应字段语义构造
请求体；首次实战入库时若 UpSeller 返回字段错误需要根据真实响应再调整。
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
from ec.upseller_sku_manager import UpSellerSkuManager


class UpSellerAdapter(SellerClient):

    def __init__(
            self,
            client: UpSellerClient,
            sku_manager: UpSellerSkuManager,
            email: str,
            password: str,
            warehouse_id: int):
        self._client = client
        self._sku_manager = sku_manager
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

    def _build_inout_details(self, items: List[StockMoveItem]) -> typing.List[dict]:
        details = []
        for it in items:
            entry = {
                "skuId": str(it.erp_sku_id),
                "sku": it.sku,
                "warehouseId": str(self._warehouse_id),
                "stockQty": int(it.quantity),
            }
            if it.unit_price_yuan is not None:
                entry["costPrice"] = float(it.unit_price_yuan)
            details.append(entry)
        return details

    def add_stock_in(self, items: List[StockMoveItem], note: str) -> StockResult:
        payload = {
            "warehouseId": str(self._warehouse_id),
            "note": note,
            "details": self._build_inout_details(items),
        }
        raw = self._client.add_stock_to_erp(payload)
        return self._extract_stock_result(raw, total=len(items))

    def add_stock_out(self, items: List[StockMoveItem], note: str) -> StockResult:
        payload = {
            "warehouseId": str(self._warehouse_id),
            "note": note,
            "details": self._build_inout_details(items),
        }
        raw = self._client.out_stock_from_erp(payload)
        return self._extract_stock_result(raw, total=len(items))

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
