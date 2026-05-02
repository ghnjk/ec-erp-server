#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: big_seller_adapter
@author: jkguo
@create: 2026/05/02

BigSeller 平台的 SellerClient 适配实现。封装 BigSellerClient + SkuManager，
对外暴露 ec.seller_client.SellerClient 抽象接口。

字段映射依据：BigSeller `inventory/merchant/detail` 与 `inventory/merchant/pageList` 历史响应。
"""
from typing import List, Optional

from ec.bigseller.big_seller_client import BigSellerClient
from ec.seller_client import (
    InventoryDetail,
    SellerClient,
    SkuDetail,
    StockMoveItem,
    StockResult,
)
from ec.sku_manager import SkuManager


class BigSellerAdapter(SellerClient):
    """BigSeller 适配器。

    与 ec/sku_manager.py 共生：本地 SKU map 命中失败时回落到 BigSeller 的全量 SKU
    拉取（``load_and_update_all_sku``），与历史 supplier.py 行为保持一致。
    """

    def __init__(
            self,
            client: BigSellerClient,
            sku_manager: SkuManager,
            email: str,
            encoded_password: str,
            warehouse_id: int,
            shelf_id,
            shelf_name: str):
        self._client = client
        self._sku_manager = sku_manager
        self._email = email
        self._encoded_password = encoded_password
        self._warehouse_id = int(warehouse_id)
        self._shelf_id = shelf_id
        self._shelf_name = shelf_name

    def login(self) -> None:
        self._client.login(self._email, self._encoded_password)

    def get_warehouse_id(self) -> int:
        return self._warehouse_id

    def _ensure_sku_id(self, sku: str) -> Optional[int]:
        sku_id = self._sku_manager.get_sku_id(sku)
        if sku_id is not None:
            return sku_id
        self._sku_manager.load_and_update_all_sku(self._client)
        return self._sku_manager.get_sku_id(sku)

    def get_sku_id(self, sku: str) -> Optional[str]:
        sku_id = self._ensure_sku_id(sku)
        return None if sku_id is None else str(sku_id)

    def query_sku_detail(self, sku: str) -> SkuDetail:
        sku_id = self._ensure_sku_id(sku)
        if sku_id is None:
            raise Exception(f"sku {sku} 不存在")
        raw = self._client.query_sku_detail(sku_id)
        inventory = 0
        for vo in raw.get("warehouseVoList") or []:
            if vo.get("id") != self._warehouse_id:
                continue
            inventory += int(vo.get("available") or 0)
        return SkuDetail(
            erp_sku_id=str(raw.get("id")),
            title=raw.get("title") or "",
            image_url=raw.get("imgUrl") or "",
            inventory_in_warehouse=inventory,
            raw=raw,
        )

    def query_sku_inventory_detail(self, sku: str) -> InventoryDetail:
        raw = self._client.query_sku_inventory_detail(sku, self._warehouse_id)
        if raw is None:
            return InventoryDetail(
                available=0, title="", image_url="", avg_daily_sales=0.0, raw={}
            )
        avg = raw.get("avgDailySales")
        if avg is None:
            avg = 0.0
        return InventoryDetail(
            available=int(raw.get("available") or 0),
            title=raw.get("title") or "",
            image_url=raw.get("image") or "",
            avg_daily_sales=float(avg),
            raw=raw,
        )

    def _build_inout_payload(
            self,
            items: List[StockMoveItem],
            note: str,
            inout_type_id: str) -> dict:
        details = []
        for it in items:
            shelf_qty = int(it.quantity)
            details.append({
                "skuId": int(it.erp_sku_id),
                "stockPrice": None if it.unit_price_yuan is None else float(it.unit_price_yuan),
                "shelfList": [
                    {
                        "shelfId": self._shelf_id,
                        "shelfName": self._shelf_name,
                        "stockQty": shelf_qty,
                    }
                ],
            })
        return {
            "detailsAddBoList": details,
            "id": "",
            "inoutTypeId": inout_type_id,
            "isAutoInoutStock": 1,
            "note": note,
            "warehouseId": self._warehouse_id,
            "zoneId": None,
        }

    def _do_inout(self, items, note, inout_type_id) -> StockResult:
        payload = self._build_inout_payload(items, note, inout_type_id)
        raw = self._client.add_stock_to_erp(payload)
        success = int(raw.get("successNum") or 0)
        fail = int(raw.get("failNum") or 0)
        return StockResult(success=success, fail=fail, raw=raw or {})

    def add_stock_in(self, items: List[StockMoveItem], note: str) -> StockResult:
        return self._do_inout(items, note, "1001")

    def add_stock_out(self, items: List[StockMoveItem], note: str) -> StockResult:
        return self._do_inout(items, note, "1002")
