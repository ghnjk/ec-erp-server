#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: sku_sale_estimate
@author: jkguo
@create: 2024/3/6
"""
import typing
from datetime import datetime

from ec_erp_api.models.mysql_backend import SkuSaleEstimateDto, MysqlBackend, SkuDto


class SkuSaleEstimate(object):

    def __init__(self, project_id: str, order_date: str, backend: MysqlBackend):
        self.project_id = project_id
        self.order_date = datetime.strptime(order_date, "%Y-%m-%d")
        # sku_est_data = map<sku, map<shop_id, SkuSaleEstimate> >
        self.sku_est_data: typing.Dict[str, typing.Dict[str, SkuSaleEstimateDto]] = {}
        self.backend = backend
        self.sku_dto_map = {}

    def add_sku_sale(self, sku: str, shop_id: str, sale_doc: dict,
                     var_count: int, var_cost_ratio: float, var_sku_name: str):
        """
        添加sku销售记录
        :param sku:  sku
        :param shop_id: 商铺id
        :param sale_doc: 销售记录
        :param var_count: 复合sku的数
        :param var_cost_ratio: 符合sku时，改子sku的成本比例
        :param var_sku_name: 符合sku时，子sku的sku名
        :return:
        """
        est = self._get_shop_est_dict(sku, shop_id, sale_doc, var_sku_name)
        est.sale_quantity += int(sale_doc["salesVolume"]) * var_count
        est.sale_amount += int(sale_doc["saleAmount"] * var_cost_ratio)
        est.cancel_quantity += int(sale_doc["cancelsVolume"]) * var_count
        est.cancel_amount += int(sale_doc["cancelsAmount"] * var_cost_ratio)
        est.cancel_orders += sale_doc["cancelsOrders"]
        est.refund_quantity += int(sale_doc["refundsVolume"]) * var_count
        est.refund_amount += int(sale_doc["refundAmount"] * var_cost_ratio)
        est.refund_orders += sale_doc["refundsOrders"]
        est.efficient_quantity += int(sale_doc["efficientsVolume"]) * var_count
        est.efficient_amount += int(sale_doc["efficientsAmount"] * var_cost_ratio)
        est.efficient_orders += sale_doc["efficientsOrders"]

    def store(self):
        for sku in self.sku_est_data.keys():
            for shop_id in self.sku_est_data[sku].keys():
                est = self.sku_est_data[sku][shop_id]
                self.backend.store_sku_sale_estimate(est)

    def _get_shop_est_dict(self, sku: str, shop_id: str, sale_doc: dict, var_sku_name: str) -> SkuSaleEstimateDto:
        sku = str(sku).strip()
        shop_id = str(shop_id).strip()

        # sku 信息
        sku_dto = self._get_sku_from_db(sku)
        if sku_dto is None:
            sku_group = "UNKNOWN"
            sku_name = var_sku_name
        else:
            sku_group = sku_dto.sku_group
            sku_name = sku_dto.sku_name
        if sku not in self.sku_est_data:
            self.sku_est_data[sku] = {}
        sku_dict = self.sku_est_data[sku]
        if shop_id not in sku_dict:
            sku_dict[shop_id] = SkuSaleEstimateDto(
                project_id=self.project_id,
                order_date=self.order_date,
                sku=sku,
                shop_id=shop_id,
                sku_class=sale_doc["skuGroup"],
                sku_group=sku_group,
                sku_name=sku_name,
                shop_name=sale_doc["shopOwner"],
                shop_owner=sale_doc["shopOwner"],
                sale_amount=0,
                sale_quantity=0,
                cancel_amount=0,
                cancel_quantity=0,
                cancel_orders=0,
                refund_amount=0,
                refund_quantity=0,
                refund_orders=0,
                efficient_amount=0,
                efficient_quantity=0,
                efficient_orders=0
            )
        return sku_dict[shop_id]

    def _get_sku_from_db(self, sku: str) -> typing.Optional[SkuDto]:
        if sku not in self.sku_dto_map:
            self.sku_dto_map[sku] = self.backend.get_sku(sku)
        return self.sku_dto_map[sku]
