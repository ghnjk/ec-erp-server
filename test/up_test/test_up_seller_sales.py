#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: test_up_seller_sales
@author: jkguo
@create: 2026/07/19
"""
import datetime
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ec.bigseller.up_seller_client import UpSellerClient
from ec.up_seller_sales_manager import UpSellerSalesManager
from ec.upseller_sku_manager import UpSellerSkuManager


def build_page(rows, page_no, total_page):
    return {
        "rows": rows,
        "page_no": page_no,
        "page_size": 1,
        "total_size": total_page,
        "total_page": total_page,
    }


class PagingClient:
    load_sku_sales_by_date = UpSellerClient.load_sku_sales_by_date

    def __init__(self):
        self.product_calls = []
        self.variation_calls = []

    def query_product_sale_page(self, sale_date, page_no, page_size):
        self.product_calls.append(page_no)
        return build_page([{
            "shopId": page_no,
            "platform": "tiktok",
            "productId": "p" + str(page_no),
            "productSku": "",
        }], page_no, 2)

    def query_variation_sale_page(
            self, sale_date, shop_id, product_id, product_sku, page_no, page_size):
        self.variation_calls.append((product_id, page_no))
        total_page = 2 if product_id == "p1" else 1
        return build_page([{
            "shopId": shop_id,
            "platform": "tiktok",
            "productId": product_id,
            "variationId": product_id + "-v" + str(page_no),
            "variationSku": product_id + "-sku" + str(page_no),
            "productSales": page_no,
        }], page_no, total_page)


class DailyClient:

    def __init__(self, rows_by_date):
        self.rows_by_date = rows_by_date
        self.calls = []

    def load_sku_sales_by_date(self, sale_date):
        self.calls.append(sale_date)
        return self.rows_by_date.get(sale_date, [])


class JsonResponse:

    def __init__(self, body):
        self.body = body

    def json(self):
        return self.body


class RelationPagingClient:
    query_sku_relation_detail = UpSellerClient.query_sku_relation_detail
    _check_response = staticmethod(UpSellerClient._check_response)
    _extract_page = staticmethod(UpSellerClient._extract_page)
    sku_relation_detail_url = "https://example.test/api/sku/sku-relation-detail"

    def __init__(self):
        self.calls = []

    def get(self, url, params):
        page_no = params["pageNum"]
        self.calls.append(page_no)
        return JsonResponse({
            "code": 0,
            "data": {
                "list": [{"platformVariantsId": "v" + str(page_no)}],
                "pageNum": page_no,
                "pageSize": 1,
                "total": 2,
                "pages": 2,
            },
        })


class SkuSyncClient:

    def __init__(self, rows, relations):
        self.rows = rows
        self.relations = relations
        self.relation_calls = []

    def load_all_sku(self, include_variants=False):
        return [dict(row) for row in self.rows]

    def query_sku_detail(self, sku_id, sku_type):
        raise AssertionError("unexpected query_sku_detail")

    def query_sku_relation_detail(self, sku_id):
        self.relation_calls.append(str(sku_id))
        return list(self.relations[str(sku_id)])


class UpSellerSalesTest(unittest.TestCase):

    @staticmethod
    def build_sku_manager():
        manager = UpSellerSkuManager()
        manager.add({
            "idStr": "single-1",
            "sku": "SINGLE",
            "isGroup": 0,
            "relationVos": [],
        })
        manager.add({
            "idStr": "group-1",
            "sku": "GROUP",
            "isGroup": 1,
            "relationVos": [{
                "shopId": 953938,
                "platform": "tiktok",
                "platformVariantsId": "variant-group",
                "platformSku": "platform-group",
            }],
            "groupVOS": [{
                "varSku": "SINGLE",
                "num": 6,
            }],
        })
        return manager

    def test_client_loads_product_and_variation_pages(self):
        client = PagingClient()
        rows = client.load_sku_sales_by_date(
            "2026-07-18", page_size=1, request_interval=0)
        self.assertEqual([1, 2], client.product_calls)
        self.assertEqual([("p1", 1), ("p1", 2), ("p2", 1)], client.variation_calls)
        self.assertEqual(3, len(rows))
        self.assertEqual(4, sum(row["productSales"] for row in rows))

    def test_page_helper_pages_field_is_supported(self):
        page = UpSellerClient._extract_page({
            "list": [],
            "pageNum": 1,
            "pageSize": 200,
            "total": 500,
            "pages": 3,
        })
        self.assertEqual(3, page["total_page"])

    def test_client_loads_all_sku_relation_pages(self):
        client = RelationPagingClient()
        rows = client.query_sku_relation_detail("sku-1", page_size=1)
        self.assertEqual([1, 2], client.calls)
        self.assertEqual(["v1", "v2"], [
            row["platformVariantsId"] for row in rows])

    def test_sku_sync_refreshes_incomplete_relation_vos(self):
        row = {
            "idStr": "single-1",
            "sku": "SINGLE",
            "isGroup": 0,
            "mappingStatus": True,
            "relationCount": 2,
            "relationVos": None,
        }
        complete_relations = [{
            "shopId": 953938,
            "platform": "tiktok",
            "platformVariantsId": "variant-1",
            "platformSku": "platform-1",
        }, {
            "shopId": 953938,
            "platform": "tiktok",
            "platformVariantsId": "variant-2",
            "platformSku": "platform-2",
        }]
        client = SkuSyncClient([row], {"single-1": complete_relations})
        with tempfile.TemporaryDirectory() as cache_dir:
            manager = UpSellerSkuManager(
                str(Path(cache_dir) / "all_up_seller_sku.json"))
            manager.add({
                **row,
                "relationVos": complete_relations[:1],
            })
            manager.load_and_update_all_sku(client)

        self.assertEqual(["single-1"], client.relation_calls)
        self.assertEqual(2, len(manager.sku_map["SINGLE"]["relationVos"]))
        self.assertEqual("SINGLE", manager.resolve_sales_sku({
            "shopId": 953938,
            "platform": "tiktok",
            "variationId": "variant-2",
        }))

    def test_sku_sync_skips_relation_query_when_count_matches(self):
        relation = {
            "shopId": 953938,
            "platform": "tiktok",
            "platformVariantsId": "variant-1",
            "platformSku": "platform-1",
        }
        row = {
            "idStr": "single-1",
            "sku": "SINGLE",
            "isGroup": 0,
            "mappingStatus": True,
            "relationCount": 1,
            "relationVos": [relation],
        }
        client = SkuSyncClient([row], {"single-1": [relation]})
        with tempfile.TemporaryDirectory() as cache_dir:
            manager = UpSellerSkuManager(
                str(Path(cache_dir) / "all_up_seller_sku.json"))
            manager.load_and_update_all_sku(client)

        self.assertEqual([], client.relation_calls)
        self.assertEqual([relation], manager.sku_map["SINGLE"]["relationVos"])

    def test_relation_mapping_has_priority_and_group_is_expanded(self):
        sku_manager = self.build_sku_manager()
        sales_manager = UpSellerSalesManager(
            client=DailyClient({}),
            sku_manager=sku_manager,
            cache_dir="unused")
        daily, unmatched = sales_manager.aggregate_daily_sales([{
            "shopId": 953938,
            "platform": "tiktok",
            "variationId": "variant-group",
            "variationSku": "SINGLE",
            "productSales": 2,
        }])
        self.assertEqual({"SINGLE": 12}, daily)
        self.assertEqual([], unmatched)

    def test_unknown_and_incomplete_group_are_reported(self):
        sku_manager = self.build_sku_manager()
        sku_manager.add({
            "idStr": "bad-group",
            "sku": "BAD-GROUP",
            "isGroup": 1,
            "relationVos": [],
            "groupVOS": [],
        })
        sales_manager = UpSellerSalesManager(
            client=DailyClient({}),
            sku_manager=sku_manager,
            cache_dir="unused")
        daily, unmatched = sales_manager.aggregate_daily_sales([
            {"variationSku": "UNKNOWN", "productSales": 1},
            {"variationSku": "BAD-GROUP", "productSales": 1},
        ])
        self.assertEqual({}, daily)
        self.assertEqual(2, len(unmatched))

    def test_cycle_is_rejected(self):
        sku_manager = UpSellerSkuManager()
        sku_manager.add({
            "idStr": "a",
            "sku": "A",
            "isGroup": 1,
            "groupVOS": [{"varSku": "B", "num": 1}],
        })
        sku_manager.add({
            "idStr": "b",
            "sku": "B",
            "isGroup": 1,
            "groupVOS": [{"varSku": "A", "num": 1}],
        })
        with self.assertRaisesRegex(ValueError, "cycle"):
            sku_manager.expand_to_single_skus("A")

    def test_daily_cache_and_average(self):
        sku_manager = self.build_sku_manager()
        rows_by_date = {
            "2026-07-01": [{
                "shopId": 953938,
                "platform": "tiktok",
                "variationId": "variant-group",
                "variationSku": "platform-group",
                "productSales": 1,
            }],
            "2026-07-02": [],
        }
        client = DailyClient(rows_by_date)
        with tempfile.TemporaryDirectory() as cache_dir:
            sales_manager = UpSellerSalesManager(client, sku_manager, cache_dir)
            begin = datetime.date(2026, 7, 1)
            end = datetime.date(2026, 7, 3)
            avg = sales_manager.load_avg_daily_sales(begin, end)
            self.assertEqual(3.0, avg["SINGLE"])
            self.assertEqual(0.0, avg.get("NO-SALE", 0.0))
            self.assertEqual(["2026-07-01", "2026-07-02"], client.calls)

            avg_from_cache = sales_manager.load_avg_daily_sales(begin, end)
            self.assertEqual(avg, avg_from_cache)
            self.assertEqual(["2026-07-01", "2026-07-02"], client.calls)

    def test_all_unmatched_sales_fail_instead_of_zeroing_all_skus(self):
        sku_manager = self.build_sku_manager()
        client = DailyClient({
            "2026-07-01": [{
                "variationSku": "UNKNOWN",
                "productSales": 1,
            }],
        })
        with tempfile.TemporaryDirectory() as cache_dir:
            sales_manager = UpSellerSalesManager(client, sku_manager, cache_dir)
            with self.assertRaisesRegex(ValueError, "all .* unmatched"):
                sales_manager.load_avg_daily_sales("2026-07-01", "2026-07-02")


if __name__ == "__main__":
    unittest.main()
