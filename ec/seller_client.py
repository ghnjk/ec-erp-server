#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: seller_client
@author: jkguo
@create: 2026/05/02

统一的 Seller 抽象层：屏蔽 BigSeller / UpSeller 在请求体与响应字段上的差异，
让上层 supplier.py 等业务模块按统一接口编程。

字段命名遵循 ERP 内部语义而非任何一家平台原始字段。
"""
from dataclasses import dataclass, field
from typing import List, Optional, Protocol


@dataclass
class SkuDetail:
    """单个 SKU 在 ERP 主仓的详情。"""
    erp_sku_id: str
    title: str
    image_url: str
    inventory_in_warehouse: int
    raw: dict = field(default_factory=dict)


@dataclass
class InventoryDetail:
    """单个 SKU 在指定仓库的库存与销售统计。"""
    available: int
    title: str
    image_url: str
    avg_daily_sales: float
    raw: dict = field(default_factory=dict)


@dataclass
class StockMoveItem:
    """入库/出库的单条 SKU 项，由 supplier.py 统一构造再传入 adapter。"""
    erp_sku_id: str
    sku: str
    quantity: int
    unit_price_yuan: Optional[float] = None


@dataclass
class StockResult:
    """入库/出库结果。"""
    success: int
    fail: int
    raw: dict = field(default_factory=dict)


class SellerClient(Protocol):
    """ERP 与上游 SaaS（BigSeller / UpSeller）交互的统一接口。

    实现类需要保证：
    1. 复用 cookie 维持登录态；超时自动续期由工厂层保证。
    2. 字段映射后返回的 dataclass 字段语义与 BigSeller 历史字段保持一致，
       避免上层 supplier.py 出现差异化分支。
    """

    def login(self) -> None:
        ...

    def get_warehouse_id(self) -> int:
        ...

    def get_sku_id(self, sku: str) -> Optional[str]:
        ...

    def query_sku_detail(self, sku: str) -> SkuDetail:
        ...

    def query_sku_inventory_detail(self, sku: str) -> InventoryDetail:
        ...

    def add_stock_in(self, items: List[StockMoveItem], note: str) -> StockResult:
        ...

    def add_stock_out(self, items: List[StockMoveItem], note: str) -> StockResult:
        ...
