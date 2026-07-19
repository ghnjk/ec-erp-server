#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: up_seller_sales_manager
@author: jkguo
@create: 2026/07/19
"""
import datetime
import json
import logging
import os
import tempfile
import typing

from ec.bigseller.up_seller_client import UpSellerClient
from ec.upseller_sku_manager import UpSellerSkuManager


class UpSellerSalesManager:
    """按日缓存 UpSeller 变种销量，并聚合为内部单 SKU 日均销量。"""

    CACHE_SCHEMA_VERSION = 1

    def __init__(
            self,
            client: UpSellerClient,
            sku_manager: UpSellerSkuManager,
            cache_dir: str):
        self.client = client
        self.sku_manager = sku_manager
        self.cache_dir = cache_dir
        self.logger = logging.getLogger("INVOKER")

    @staticmethod
    def _to_date(value) -> datetime.date:
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        return datetime.datetime.strptime(str(value), "%Y-%m-%d").date()

    def _cache_path(self, sale_date: datetime.date) -> str:
        return os.path.join(self.cache_dir, sale_date.strftime("%Y-%m-%d") + ".json")

    def _read_cache(self, sale_date: datetime.date) -> typing.List[dict]:
        cache_path = self._cache_path(sale_date)
        with open(cache_path, "r") as fp:
            cache = json.load(fp)
        if cache.get("schemaVersion") != self.CACHE_SCHEMA_VERSION:
            raise ValueError(f"unsupported upseller sales cache schema: {cache_path}")
        if cache.get("date") != sale_date.strftime("%Y-%m-%d"):
            raise ValueError(f"upseller sales cache date mismatch: {cache_path}")
        rows = cache.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"upseller sales cache rows invalid: {cache_path}")
        return rows

    def _write_cache(self, sale_date: datetime.date, rows: typing.List[dict]):
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_path = self._cache_path(sale_date)
        cache = {
            "schemaVersion": self.CACHE_SCHEMA_VERSION,
            "date": sale_date.strftime("%Y-%m-%d"),
            "fetchedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "rows": rows,
        }
        with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.cache_dir,
                delete=False,
                suffix=".tmp",
                prefix=".upseller_sales_") as tmp_file:
            tmp_path = tmp_file.name
            json.dump(cache, tmp_file, indent=2, ensure_ascii=False)
        try:
            os.replace(tmp_path, cache_path)
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def load_daily_rows(self, sale_date) -> typing.List[dict]:
        sale_day = self._to_date(sale_date)
        cache_path = self._cache_path(sale_day)
        if os.path.isfile(cache_path):
            try:
                return self._read_cache(sale_day)
            except Exception as e:
                self.logger.error(f"read upseller sales cache failed, refetch {sale_day}: {e}")
        rows = self.client.load_sku_sales_by_date(sale_day.strftime("%Y-%m-%d"))
        self._write_cache(sale_day, rows)
        return rows

    def aggregate_daily_sales(
            self,
            rows: typing.List[dict]) -> typing.Tuple[typing.Dict[str, int], typing.List[dict]]:
        result: typing.Dict[str, int] = {}
        unmatched = []
        for row in rows:
            quantity = int(row.get("productSales") or 0)
            if quantity <= 0:
                continue
            sku_code = self.sku_manager.resolve_sales_sku(row)
            if not sku_code:
                unmatched.append({
                    "variationSku": row.get("variationSku") or "",
                    "variationId": row.get("variationId"),
                    "shopId": row.get("shopId"),
                    "reason": "sku_mapping_not_found",
                })
                continue
            try:
                single_skus = self.sku_manager.expand_to_single_skus(sku_code)
            except (TypeError, ValueError) as e:
                unmatched.append({
                    "variationSku": row.get("variationSku") or "",
                    "variationId": row.get("variationId"),
                    "shopId": row.get("shopId"),
                    "reason": str(e),
                })
                continue
            for single_sku, unit_count in single_skus.items():
                result[single_sku] = result.get(single_sku, 0) + quantity * unit_count
        return result, unmatched

    def load_avg_daily_sales(self, begin_date, end_date) -> typing.Dict[str, float]:
        """统计 ``[begin_date, end_date)`` 内单 SKU 的日均销量。"""
        if not self.sku_manager.sku_map:
            raise ValueError("upseller sku cache is empty")
        begin_day = self._to_date(begin_date)
        end_day = self._to_date(end_date)
        day_count = (end_day - begin_day).days
        if day_count <= 0:
            raise ValueError("upseller sales date range must not be empty")
        totals: typing.Dict[str, int] = {}
        has_source_sales = False
        current = begin_day
        while current < end_day:
            rows = self.load_daily_rows(current)
            has_source_sales = has_source_sales or any(
                int(row.get("productSales") or 0) > 0 for row in rows)
            daily_sales, unmatched = self.aggregate_daily_sales(rows)
            for sku_code, quantity in daily_sales.items():
                totals[sku_code] = totals.get(sku_code, 0) + quantity
            if unmatched:
                self.logger.error(
                    f"upseller sales has {len(unmatched)} unmatched rows on {current}, "
                    f"samples={json.dumps(unmatched[:5], ensure_ascii=False)}")
            current += datetime.timedelta(days=1)
        if has_source_sales and not totals:
            raise ValueError("all upseller sales rows are unmatched")
        return {
            sku_code: quantity / float(day_count)
            for sku_code, quantity in totals.items()
        }
