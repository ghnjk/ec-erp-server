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
from typing import Dict, List, Optional, Protocol


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

    def refresh_local_sku_cache(self) -> None:
        """从上游 ERP 全量拉取 SKU 列表并写入本地缓存。

        - BigSeller 实现 → ``cookies/all_sku.json`` + ``cookies/all_variant_sku_mapping.json``
        - UpSeller 实现 → ``cookies/all_up_seller_sku.json``

        与 ``auto_sync_tools/sync_all_sku.py`` 配合使用：定时任务通过本方法
        刷新本地 SKU 缓存，无需在脚本中区分上游平台。如果上游接口失败，
        实现应抛异常而不是静默忽略。
        """
        ...

    def load_sku_avg_daily_sales(
            self,
            begin_date,
            end_date) -> Optional[Dict[str, float]]:
        """加载指定自然日区间的本地 SKU 日均销量。

        返回 ``None`` 表示当前 ERP 继续使用 ``InventoryDetail.avg_daily_sales``；
        返回字典（允许为空）表示区间统计完整，未出现的 SKU 视为真实零销量。
        """
        ...

    def get_sku_manager(self):
        """返回当前平台的本地 SKU 缓存，供拣货备注匹配图片和名称。"""
        ...

    def get_wait_print_order_ship_provider_list(self) -> list:
        """待打单按物流方式汇总。元素至少包含 id、name、count。"""
        ...

    def search_wait_print_order(self, shipping_provider_id, current_page, page_size):
        """按物流方式分页查询待打单。返回 (total, rows)，行字段与仓库列表接口一致。"""
        ...

    def get_order_detail(self, order_id) -> dict:
        """订单详情，字段对齐仓库拣货分析使用的 BigSeller orderDetail。"""
        ...

    def download_order_mask_pdf_file(
            self,
            order_id: str,
            mark_id: str,
            platform: str,
            save_pdf_file: str,
            auth_ids: Optional[str] = None) -> None:
        """下载这一批订单的面单 PDF。auth_ids 仅 UpSeller 需要。"""
        ...

    def mark_order_printed(self, order_id: str):
        """把逗号分隔的订单标记为面单已打印。"""
        ...
