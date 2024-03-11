#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: big_seller_client
@author: jkguo
@create: 2023/8/1
"""
import json
import os
import time
import typing

import requests
from ec.verifycode.ydm_verify import YdmVerify


class BigSellerClient:

    def __init__(self, ydm_token: str, cookies_file_path="cookies/big_seller.cookies"):
        self.check_login_url = "https://www.bigseller.com/api/v1/isLogin.json"
        self.login_web_url = "https://www.bigseller.com/zh_CN/login.htm"
        self.login_url = "https://www.bigseller.com/api/v2/user/login.json"
        self.gen_verify_code_url = "https://www.bigseller.com/api/v2/genVerifyCode.json"
        self.estimate_sku_url = "https://www.bigseller.com/api/v1/items/pageList.json"
        self.query_sku_info_url = "https://www.bigseller.com/api/v1/inventory/merchant/pageList.json"
        self.query_all_sku_class_url = "https://www.bigseller.com/api/v1/inventory/merchant/classifyList.json"
        self.query_sku_detail_url = "https://www.bigseller.com/api/v1/inventory/merchant/detail.json"
        self.add_stock_url = "https://www.bigseller.com/api/v1/inventory/inout/list/add.json"
        self.query_shop_group_url = "https://www.bigseller.com/api/v1/shop/group/page.json"
        self.query_shop_sell_static_url = "https://www.bigseller.com/api/v1/getStoreAnalysisDetail.json"
        self.query_shop_info_url = "https://www.bigseller.com/api/v1/shopsAndPlatforms.json"
        self.session = requests.Session()
        self.auto_verify_coder = YdmVerify(ydm_token)
        self.cookies_file_path = cookies_file_path

    def login(self, email: str, encoded_password: str):
        if self.load_cookies() and self.is_login():
            print("use cookie login ok")
            return
        self.__login(email, encoded_password)

    def __login(self, email: str, encoded_password: str):
        # create new session
        self.session = requests.Session()
        # get login web
        self.session.get(self.login_web_url)
        # get verify code
        access_code, verify_code = self.get_valid_verify_code()
        print(f"access_code {access_code}, verify_code: {verify_code}")
        response = self.session.post(self.login_url, {
            "email": email,
            "password": encoded_password,
            "verifyCode": str(verify_code),
            "accessCode": access_code
        })
        print("login response header:")
        print(response.headers)
        print("login response json:")
        print(response.json())
        if self.is_login():
            print(f"login {email} success save cookies")
            self.save_cookies()
        else:
            raise Exception("login failed")

    def is_login(self):
        response = self.session.get(self.check_login_url).json()
        return response["data"]

    def get_valid_verify_code(self):
        for i in range(10):
            response = self.session.get(self.gen_verify_code_url)
            image_base64: str = response.json()["data"]["base64Image"]
            if image_base64.startswith("data:image/png;base64,"):
                image_base64 = image_base64[len("data:image/png;base64,"):]
            # verify code
            verify_res = self.auto_verify_coder.common_verify(image_base64, "10110")
            if verify_res["code"] == 10000:
                verify_code = verify_res["data"]["data"]
                return response.json()["data"]["accessCode"], verify_code
            time.sleep(3)
        raise Exception("get_valid_verify_code failed.")

    def save_cookies(self):
        with open(self.cookies_file_path, "w") as f:
            f.write(json.dumps(self.session.cookies.get_dict(), indent=2))

    def load_cookies(self):
        if not os.path.isfile(self.cookies_file_path):
            return False
        with open(self.cookies_file_path, "r") as fp:
            self.session.cookies.update(json.load(fp))
            return True

    def load_all_sku(self):
        """
        查询所有的sku和匹配关系
        :return:[
            {
                "id": 38793152,
                "imgUrl": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/2024020609544240b650d0ca6e68ab265f7a5e01222b55.png?imageView2/1/w/300/h/300",
                "sku": "SC-17-2m*1m",
                "title": "2平米的防晒网",
                "productCount": 1,
                "mappingStatus": 1,
                "skuRelations": [
                  {
                    "id": 115531298,
                    "puid": 279590,
                    "skuId": 38793152,
                    "platform": "lazada",
                    "shop": {
                      "createTime": 1678092565000,
                      "updateTime": 1705567752000,
                      "id": 2100179,
                      "puid": 279590,
                      "name": "Green lawn (09204889221)",
                      "status": 1,
                      "authTime": 1705567752000,
                      "platform": "lazada",
                      "areaType": 1,
                      "salesMarket": "PH",
                      "vipShopNumType": 0,
                      "socialMedia": 0,
                      "isRun": 0,
                      "commissionRatio": 10.0,
                      "isCustom": 0,
                      "site": null,
                      "is3pf": null,
                      "shopType": null,
                      "cnsc": null
                    },
                    "platformSku": "SC-17-2m*1m."
                  }
                ],
                "isGroup": 1,
                "skuGroupVoList": [
                  {
                    "id": 32840,
                    "skuId": 38793152,
                    "varSkuId": 38793139,
                    "varSku": "SC-17-2m*0.5m",
                    "varSkuTitle": "17mm的最低尺寸",
                    "varSkuImgUrl": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/202402060957272ed23312886b5c7d136f326e961efef8.jpg",
                    "num": 2,
                    "costAllocationRatio": 1.0,
                    "commodityWeight": 0,
                    "cost": null,
                    "available": 0,
                    "common": 0,
                    "promotion": 0,
                    "onhand": 0,
                    "isOutOfStock": null
                  }
                ],
                "commodityWeight": "0.00",
                "commodityVolume": "0*0*0",
                "merchantSkuId": "90001684",
                "gtinCode": null,
                "classifyName": "未分类",
                "referencePrice": "0.0000",
                "createTimeStr": "2024-02-06 17:59",
                "updateTimeStr": "2024-02-06 17:59",
                "saleStatus": 1,
                "retailList": null,
                "remark": null,
                "remarkTimeStr": null
              }
        ]
        """
        rows = []
        page_size = 300
        page_no = 1
        while True:
            req = {
                "pageSize": page_size,
                "pageNo": page_no,
                "searchType": "skuName",
                "searchContent": "",
                "inquireType": 0,
                "saleStatus": 1
            }
            res = self.session.post(self.query_sku_info_url, req).json()
            total_page = res["data"]["totalPage"]
            total_size = res["data"]["totalSize"]
            print(f"load page {page_no}/{total_page} data")
            rows.extend(res["data"]["rows"])
            if total_page <= page_no:
                print(f"load all {total_size} sku")
                break
            page_no += 1
            time.sleep(0.5)
        self.save_cookies()
        return rows

    def load_sku_estimate_by_date(self, begin_date: str, end_date: str):
        """
        拉取所有的sku统计信息
        :param begin_date:
        :param end_date:
        :return:
        [
            {
            "shopId": 1011019,
            "skuId": "2564380115_PH-13043455155",
            "shopName": "CL party needs (09771708907)",
            "productName": "sophia balloon set/birthday balloon decorations",
            "image": "https://sg-live-01.slatic.net/p/5fd515afaf806ff15bb9e12d7ac9616c.jpg",
            "platform": "lazada",
            "sku": "QQ-2...",
            "varAttr": [
              "Theme:Princess Elsa(52pcs)"
            ],
            "salesStr": "167.13",
            "salesAverageStr": "167.13",
            "salesVolume": 1,
            "ordersNum": 1,
            "packageNum": 1,
            "refundsStr": "0.00",
            "refundsVolume": 0,
            "refundsOrders": 0,
            "cancelsStr": "0.00",
            "cancelsVolume": 0,
            "cancelsOrders": 0,
            "efficientsStr": "167.13",
            "efficientsVolume": 1,
            "efficientsOrders": 1
          }
        ]
        """
        rows = []
        page_size = 200
        page_no = 1
        while True:
            req = {
                "pageSize": page_size,
                "pageNo": page_no,
                "platform": "",
                "shopId": "",
                "searchType": "sku",
                "searchContent": "",
                "inquireType": 0,
                "beginDate": begin_date,
                "endDate": end_date,
                "orderBy": "",
                "desc": 0,
                "categoryList": ""
            }
            res = self.session.post(self.estimate_sku_url, req).json()
            total_page = res["data"]["totalPage"]
            total_size = res["data"]["totalSize"]
            print(f"load page {page_no}/{total_page} data")
            rows.extend(res["data"]["rows"])
            if total_page <= page_no:
                print(f"load all {total_size} sku")
                break
            page_no += 1
        self.save_cookies()
        return rows

    def load_all_sku_classes(self):
        res = self.session.post(self.query_all_sku_class_url, {}).json()
        self.save_cookies()
        return res["data"]

    def query_sku_detail(self, sku_id: int, is_group: int = 0):
        """

        :param sku_id:
        :param is_group:
        :return:
        """
        url = f"{self.query_sku_detail_url}?isGroup={is_group}&skuId={sku_id}"
        res = self.session.get(url).json()
        self.save_cookies()
        if res["code"] != 0:
            print(f"query_sku_detail sku id {sku_id} failed.")
            print(json.dumps(res, indent=2))
            raise Exception(f"query_sku_detail sku id {sku_id} failed.")
        return res["data"]["detail"]

    def add_stock_to_erp(self, req):
        """
        入库
        req:
        {
          "detailsAddBoList": [
            {
              "skuId": 21575327,
              "stockPrice": 861.86,
              "shelfList": [
                {
                  "shelfId": "",
                  "shelfName": "",
                  "stockQty": 1
                }
              ]
            }
          ],
          "id": "",
          "inoutTypeId": "1001", // 1001 普通入库 1004 退货入库
          "isAutoInoutStock": 1,
          "note": "test",
          "warehouseId": 27763,
          "zoneId": null
        }
        :param req:
        :return:
        {
          "successNum": 1,
          "failNum": 0,
          "skipNum": 0,
          "errorsMap": [],
          "errors": [],
          "failMap": {},
          "error": ""
        }
        """
        res = self.session.post(self.add_stock_url, json=req).json()
        self.save_cookies()
        if res["code"] != 0:
            raise Exception("add_stock_to_erp failed: http response msg: " + res["msg"])
        return res["data"]["data"]

    def query_shop_group(self):
        """
        查询店铺分组信息
        :return:
            [
                {
                  "id": 15006,
                  "groupName": "斌超",
                  "shopCount": 10,
                  "shopName": "CL Car Home (09776706660),CL car needs (09179989950),Decoration shop (09459947468),DIMI (09298645333),FP Sims (TK:09179989950),Green lawn (09204889221),JOYMOE SPORT (09303000100),Lawn Shop (09622104056),Party Store (09451737990）,XLX TURF Mall (09204905623)",
                  "shopIds": [
                    1039274,
                    1039281,
                    1236901,
                    1039262,
                    2417193,
                    2100179,
                    1241575,
                    2033152,
                    1233867,
                    2100070
                  ]
                }
            ]
        """
        res = self.session.get(self.query_shop_group_url).json()
        self.save_cookies()
        if res["code"] != 0:
            print(f"query_shop_group sku failed.")
            print(json.dumps(res, indent=2))
            raise Exception(f"query_shop_group failed.")
        return res["data"]

    def query_shop_sell_static(self, begin_date: str, end_date: str):
        """
        按天查询[begin_date, end_date]店铺销售数据
        :param begin_date: yyyy-mm-dd
        :param end_date: yyyy-mm-dd
        :return:
            [
                {
                  "shopId": "1011019",
                  "shopName": "CL party needs (09771708907)",
                  "validSellAmount": 492449.49,
                  "validOrderCount": 511,
                  "sellAmountSum": 545240.9,
                  "productAmountSum": 477607.42,
                  "orderCountSum": 564,
                  "packageCountSum": 571,
                  "customerCount": 535,
                  "refundAmount": 0,
                  "refundOrderCount": 0,
                  "refundCustomerCount": 0,
                  "cancelOrderCount": 53,
                  "cancelOrderAmount": 52791.41,
                  "perCustomerPrice": 1019.14,
                  "cancelOrderAmountStr": "52791.41",
                  "sellAmountSumStr": "545240.90",
                  "productAmountSumStr": "477607.42",
                  "validSellAmountStr": "492449.49",
                  "perCustomerPriceStr": "1019.14",
                  "refundAmountStr": "0.00"
                }
            ]
        """
        url = f"{self.query_shop_sell_static_url}?platform=&queryType=day" \
              f"&beginDate={begin_date}&endDate={end_date}&type=store&shopIds="
        res = self.session.get(url).json()
        self.save_cookies()
        if res["code"] != 0:
            print(f"query_shop_sell_static sku failed.")
            print(json.dumps(res, indent=2))
            raise Exception(f"query_shop_sell_static failed.")
        return res["data"]

    def query_all_shop_info(self):
        """
        查询所有店铺信息
        :return:
            [
              {
                "id": 2546523,
                "name": "Artificial decor (TK:09298645333)",
                "platform": "tiktok",
                "site": "PH",
                "status": null,
                "is3pf": null,
                "shopType": null,
                "marketPlaceEaseMode": null,
                "cnsc": null
              }
            ]
        """
        res = self.session.get(self.query_shop_info_url).json()
        self.save_cookies()
        if res["code"] != 0:
            print(f"query_all_shop_info failed.")
            print(json.dumps(res, indent=2))
            raise Exception(f"query_all_shop_info failed.")
        return res["data"]["allShops"]

    def get_more_sku_mapping(self, sku_id: int):
        """
        返回额外的sku映射关系
        :param sku_id:
        :return: [
            {
                "id": 20064789,
                "puid": 279590,
                "skuId": 9300380,
                "platform": "lazada",
                "shop": {
                    "createTime": 1648112054000,
                    "updateTime": 1705567593000,
                    "id": 1039262,
                    "puid": 279590,
                    "name": "DIMI (09298645333)",
                    "status": 1,
                    "authTime": 1705567593000,
                    "platform": "lazada",
                    "areaType": 1,
                    "salesMarket": "PH",
                    "vipShopNumType": 0,
                    "socialMedia": 0,
                    "isRun": 0,
                    "commissionRatio": 10.0,
                    "isCustom": 0,
                    "site": null,
                    "is3pf": null,
                    "shopType": null,
                    "marketPlaceEaseMode": null,
                    "cnsc": null
                },
                "platformSku": "QQ-1...."
            }]
        """
        url = f"https://www.bigseller.com/api/v1/inventory/merchant/getMoreSkuMapping.json?skuId={sku_id}"
        res = self.session.get(url).json()
        if res["code"] != 0:
            print(f"query_all_shop_info failed.")
            print(json.dumps(res, indent=2))
            raise Exception(f"query_all_shop_info failed.")
        return res["data"][str(sku_id)]

    def query_not_op_refund_order_tracking_no_list(self, refund_date: str) -> typing.List[str]:
        """
        查询所有已退回待处理订单的运单号列表
        :param refund_date:
        :return:
        """
        tracking_no_list = []
        page_size = 50
        page_no = 1
        while True:
            req = {
                "pageSize": page_size,
                "pageNo": page_no,
                "beginDate": None,
                "endDate": None,
                "isProcessed": None,
                "returnStatus": 1,
                "processingStatus": "",
                "marketplaceStatus": None,
                "expireDays": None,
                "searchType": "orderNo",
                "searchContent": "",
                "shopId": "",
                "shopGroup": "",
                "showShopArr": False,
                "shippingCarrier": None,
                "paymentMethod": None,
                "orderBy": "OrderedTime",
                "historyOrder": False,
                "desc": False,
                "platform": "",
                "days": None,
                "daysType": None,
                "orderDays": None,
                "beginOrderDate": None,
                "endOrderDate": None,
                "warehouseId": None,
                "type": None,
                "returnDays": None,
                "requestType": None,
                "beginReturnDate": refund_date,
                "endReturnDate": refund_date
            }
            res = self.session.post("https://www.bigseller.com/api/v1/order/refund/before/pageList.json",
                                    json=req).json()
            total_page = res["data"]["totalPage"]
            total_size = res["data"]["totalSize"]
            print(f"load page {page_no}/{total_page} data")
            for r in res["data"]["rows"]:
                tracking_no_list.append(
                    r["trackingNo"]
                )
            if total_page <= page_no:
                print(f"load all {total_size} refund orders")
                break
            page_no += 1
        self.save_cookies()
        return tracking_no_list

    def query_refund_order_info_by_tracking_no(self, tracking_no: str, warehouse_id: int):
        """
        根据运单号查询退单详细信息
        :param tracking_no:
        :param warehouse_id:
        :return: {
            "orderId": 3660987642,
            "reverseId": null,
            "packageNo": "BS8H16200105",
            "platformOrderId": "805023393560144",
            "platformReverseId": null,
            "trackingNo": "MP0779253015",
            "warehouseId": 27763,
            "processingStatus": null,
            "platform": "lazada",
            "showSelected": false,
            "error": null,
            "simpleOrderList": null,
            "itemList": [
              {
                "itemId": 2310783692,
                "itemName": "12pcs 56cm Artificial Pampas Grass Bouquet Simulation Dried Flower Reed Holiday Wedding Party Home",
                "sku": "A-11-Beige Reed leaf(Pack of 12)",
                "num": 1,
                "image": "https://ph-live.slatic.net/p/7d923aa7013ecbcae0d8d54d04fe1a83.jpg",
                "isAddition": 0,
                "skuList": [
                  {
                    "skuId": 28614458,
                    "itemName": "米色芦苇叶",
                    "sku": "A-11-Beige Reed leaf",
                    "image": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/20230706074750640dc2ad09607578d8b1546866c91cf7.jpg?imageView2/1/w/300/h/300",
                    "num": 12,
                    "shelfId": null,
                    "shelfName": null,
                    "canModify": 0,
                    "isAddition": null,
                    "rate": 12,
                    "skuGroupId": 20874
                  }
                ]
              },
              {
                "itemId": 2310783693,
                "itemName": "12pcs 56cm Artificial Pampas Grass Bouquet Simulation Dried Flower Reed Holiday Wedding Party Home",
                "sku": "A-11-Brown Reed leaf(Pack of 12)",
                "num": 1,
                "image": "https://ph-live.slatic.net/p/df9f2698fd6e99aabed846629904cc6f.jpg",
                "isAddition": 0,
                "skuList": [
                  {
                    "skuId": 32855167,
                    "itemName": "褐色芦苇叶-1pcs",
                    "sku": "A-11-Brown Reed leaf",
                    "image": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/20230921032407789265c025e8d2aadb754cf2c48f9366.jpg?imageView2/1/w/300/h/300",
                    "num": 12,
                    "shelfId": null,
                    "shelfName": null,
                    "canModify": 0,
                    "isAddition": null,
                    "rate": 12,
                    "skuGroupId": 23131
                  }
                ]
              },
              {
                "itemId": 2310783694,
                "itemName": "12pcs 56cm Artificial Pampas Grass Bouquet Simulation Dried Flower Reed Holiday Wedding Party Home",
                "sku": "A-11-Grey Reed leaf(Pack of 12).",
                "num": 1,
                "image": "https://ph-live.slatic.net/p/ee0650ffc0b4c5e5a27cbc304e416a80.jpg",
                "isAddition": 0,
                "skuList": [
                  {
                    "skuId": 36800655,
                    "itemName": "灰色芦苇叶一条",
                    "sku": "A-11-Grey Reed leaf",
                    "image": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/20240103064922aa407aed7142bd60f8a3ef881ce5317b.jpg?imageView2/1/w/300/h/300",
                    "num": 12,
                    "shelfId": null,
                    "shelfName": null,
                    "canModify": 0,
                    "isAddition": null,
                    "rate": 12,
                    "skuGroupId": 28959
                  }
                ]
              }
            ],
            "split": false
          }
        """
        url = f"https://www.bigseller.com/api/v1/order/refund/before/getReturnInfo.json"
        req = {
            "searchContent": tracking_no,
            "historyOrder": False,
            "warehouseId": str(warehouse_id)
            "zoneId": ""
        }
        res = self.session.get(url, req).json()
        if res["code"] != 0:
            print(f"query_refund_order_info_by_tracking_no failed.")
            print(json.dumps(res, indent=2))
            raise Exception(f"query_refund_order_info_by_tracking_no failed.")
        return res["data"]

    def return_refund_order_to_warehouse(self, refund_order: dict, warehouse_id: int):
        """
        自动退单
        :param refund_order: 由query_refund_order_info_by_tracking_no查询的信息
        :param warehouse_id: 仓库id
        :return:
        """
        url = "https://www.bigseller.com/api/v1/order/refund/before/returnWarehousing.json"
        req = {
          "warehouseId": warehouse_id,
          "opType": 1,
          "isScan": 1,
          "orderInfoList": refund_order
        }
        res = self.session.post(url, json=req).json()
        self.save_cookies()
        if res["code"] != 0:
            raise Exception("return_refund_order_to_warehouse failed: http response msg: " + res["msg"])
        return res["data"]["data"]