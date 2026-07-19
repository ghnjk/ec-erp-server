#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: upseller_sku_manager
@author: jkguo
@create: 2026/05/02

UpSeller 平台的 SKU 本地缓存，与 ec/sku_manager.SkuManager 等价但适配 UpSeller 字段：
- BigSeller 走 sku["id"]（int）；UpSeller 走 sku["idStr"]（str），本管理器对外统一用 str。
- 通过 relationVos 维护平台变种到内部 SKU 的精确映射。
- 通过 isGroup / groupVOS 递归拆分组合 SKU。
"""
import json
import os
import typing


class UpSellerSkuManager:

    def __init__(self, local_db_path: str = "cookies/all_up_seller_sku.json"):
        self.local_db_path = local_db_path
        self.sku_map: typing.Dict[str, dict] = {}
        self.sku_id_map: typing.Dict[str, str] = {}
        self.relation_variant_id_map: typing.Dict[str, str] = {}
        self.relation_sku_map: typing.Dict[str, str] = {}

    @staticmethod
    def _relation_key(shop_id, platform, value) -> str:
        return "#".join([
            str(shop_id or "").strip(),
            str(platform or "").strip().lower(),
            str(value or "").strip(),
        ])

    def add(self, sku: dict):
        sku_code = sku.get("sku")
        if not sku_code:
            return
        sku_id = sku.get("idStr") or (str(sku["id"]) if sku.get("id") is not None else None)
        if not sku_id:
            return
        self.sku_map[sku_code] = sku
        self.sku_id_map[sku_id] = sku_code
        for relation in sku.get("relationVos") or []:
            shop_id = relation.get("shopId")
            platform = relation.get("platform")
            variation_id = relation.get("platformVariantsId")
            platform_sku = relation.get("platformSku")
            if shop_id and variation_id:
                self.relation_variant_id_map[
                    self._relation_key(shop_id, platform, variation_id)
                ] = sku_code
            if shop_id and platform_sku:
                self.relation_sku_map[
                    self._relation_key(shop_id, platform, platform_sku)
                ] = sku_code

    def dump(self):
        cache_dir = os.path.dirname(self.local_db_path)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        with open(self.local_db_path, "w") as fp:
            json.dump(self.sku_map, fp, indent=2, ensure_ascii=False)

    def load(self):
        if not os.path.isfile(self.local_db_path):
            return
        with open(self.local_db_path, "r") as fp:
            docs = json.load(fp)
            for sku_code in docs:
                self.add(docs[sku_code])

    def get_sku_id(self, sku_name: str) -> typing.Optional[str]:
        item = self.sku_map.get(sku_name)
        if item is None:
            return None
        return item.get("idStr") or (str(item["id"]) if item.get("id") is not None else None)

    def get_sku_name_by_sku_id(self, sku_id) -> typing.Optional[str]:
        return self.sku_id_map.get(str(sku_id))

    def resolve_sales_sku(self, sale_row: dict) -> typing.Optional[str]:
        """把平台销售变种映射为 UpSeller 内部 SKU，禁止模糊匹配。"""
        shop_id = sale_row.get("shopId")
        platform = sale_row.get("platform")
        variation_id = sale_row.get("variationId")
        variation_sku = str(sale_row.get("variationSku") or "").strip()
        if shop_id and variation_id:
            sku_code = self.relation_variant_id_map.get(
                self._relation_key(shop_id, platform, variation_id))
            if sku_code:
                return sku_code
        if shop_id and variation_sku:
            sku_code = self.relation_sku_map.get(
                self._relation_key(shop_id, platform, variation_sku))
            if sku_code:
                return sku_code
        if variation_sku in self.sku_map:
            return variation_sku
        return None

    def expand_to_single_skus(self, sku_code: str) -> typing.Dict[str, int]:
        """递归拆分组合 SKU，返回 ``单 SKU -> 每组数量``。"""
        result: typing.Dict[str, int] = {}

        def expand(current_sku: str, multiplier: int, path: typing.Set[str]):
            if current_sku in path:
                raise ValueError(f"upseller sku group cycle: {current_sku}")
            sku = self.sku_map.get(current_sku)
            if sku is None:
                raise ValueError(f"upseller sku not found: {current_sku}")
            if not int(sku.get("isGroup") or 0):
                result[current_sku] = result.get(current_sku, 0) + multiplier
                return
            group_items = sku.get("groupVOS") or []
            if not group_items:
                raise ValueError(f"upseller sku group detail missing: {current_sku}")
            next_path = set(path)
            next_path.add(current_sku)
            for item in group_items:
                child_sku = str(item.get("varSku") or "").strip()
                child_count = int(item.get("num") or 0)
                if not child_sku or child_count <= 0:
                    raise ValueError(f"upseller sku group item invalid: {current_sku}")
                expand(child_sku, multiplier * child_count, next_path)

        expand(str(sku_code).strip(), 1, set())
        return result

    def load_and_update_all_sku(self, client):
        """全量同步 UpSeller 的单 SKU + KIT。

        UpSeller 多变体（variants）SKU 当前业务未使用，故不拉取，避免无谓的 API 流量。
        如未来 ERP 需要识别 variants，再在此扩展 ``include_variants=True`` 即可。
        """
        old_sku_map = self.sku_map
        self.sku_map = {}
        self.sku_id_map = {}
        self.relation_variant_id_map = {}
        self.relation_sku_map = {}
        for r in client.load_all_sku(include_variants=False):
            old_row = old_sku_map.get(r.get("sku")) or {}
            current_id = str(r.get("idStr") or r.get("id") or "")
            old_id = str(old_row.get("idStr") or old_row.get("id") or "")
            can_reuse_old_detail = bool(current_id and current_id == old_id)
            if can_reuse_old_detail and not r.get("relationVos") and old_row.get("relationVos"):
                r["relationVos"] = old_row["relationVos"]
            if can_reuse_old_detail and not r.get("groupVOS") and old_row.get("groupVOS"):
                r["groupVOS"] = old_row["groupVOS"]
            needs_group = int(r.get("isGroup") or 0) and not r.get("groupVOS")
            needs_relation = bool(r.get("mappingStatus")) and not r.get("relationVos")
            if needs_group or needs_relation:
                sku_type = "group" if int(r.get("isGroup") or 0) else "single"
                detail = client.query_sku_detail(
                    r.get("idStr") or r.get("id"), sku_type=sku_type)
                if isinstance(detail, dict):
                    r.update(detail)
            self.add(r)
        self.dump()
