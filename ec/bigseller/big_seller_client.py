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
import logging
import tempfile
import requests
from ec.verifycode.ydm_verify import YdmVerify
from ec_erp_api.common.rate_limiter import RateLimiter


GLOBAL_RATE_LIMITER = RateLimiter(max_count_per_period=1, seconds_per_period=5)


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
        self.logger = logging.getLogger("INVOKER")

    def login(self, email: str, encoded_password: str):
        if self.load_cookies() and self.is_login():
            self.logger.info("use cookie login ok")
            print("use cookie login ok")
            return
        self.__login(email, encoded_password)

    def __login(self, email: str, encoded_password: str):
        # create new session
        self.session = requests.Session()
        # get login web
        self.get(self.login_web_url)
        # get verify code
        access_code, verify_code = self.get_valid_verify_code()
        print(f"access_code {access_code}, verify_code: {verify_code}")
        response = self.post(self.login_url, {
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
            self.logger.info(f"login {email} success save cookies")
            self.save_cookies()
        else:
            raise Exception("login failed")

    def is_login(self):
        response = self.get(self.check_login_url).json()
        return response["data"]

    def get_valid_verify_code(self):
        for i in range(10):
            response = self.get(self.gen_verify_code_url)
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
        """保存cookies到文件，使用临时文件和原子操作"""
        cookies_dir = os.path.dirname(self.cookies_file_path)
        if cookies_dir and not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir, exist_ok=True)
        
        # 使用临时文件，确保原子写入
        with tempfile.NamedTemporaryFile(
            mode='w',
            dir=cookies_dir,
            delete=False,
            suffix='.tmp',
            prefix='.bigseller_cookies'
        ) as tmp_file:
            tmp_file_path = tmp_file.name
            json.dump(self.session.cookies.get_dict(), tmp_file, indent=2)
        
        # 原子操作：移动临时文件到目标位置
        try:
            os.replace(tmp_file_path, self.cookies_file_path)
        except Exception as e:
            # 如果原子操作失败，清理临时文件
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
            raise e

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

            res = self.post(self.query_sku_info_url, req).json()
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
            res = self.post(self.estimate_sku_url, req).json()
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
        res = self.post(self.query_all_sku_class_url, {}).json()
        self.save_cookies()
        return res["data"]

    def query_sku_detail(self, sku_id: int, is_group: int = 0):
        """

        :param sku_id:
        :param is_group:
        :return:
        """
        url = f"{self.query_sku_detail_url}?isGroup={is_group}&skuId={sku_id}"
        res = self.get(url).json()
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
          "inoutTypeId": "1001", // 1001 普通入库 1002 普通出库 1004 退货入库
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
        res = self.post(self.add_stock_url, json=req).json()
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
        res = self.get(self.query_shop_group_url).json()
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
        res = self.get(url).json()
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
        res = self.get(self.query_shop_info_url).json()
        self.save_cookies()
        if res["code"] != 0:
            print(f"query_all_shop_info failed.")
            print(json.dumps(res, indent=2))
            raise Exception(f"query_all_shop_info failed.")
        return res["data"]["allShops"]

    def get_more_sku_mapping(self, sku_id: int):
        """
        deprecated
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
        res = self.get(url).json()
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
            res = self.post("https://www.bigseller.com/api/v1/order/refund/before/pageList.json",
                            json=req).json()
            total_page = res["data"]["page"]["totalPage"]
            total_size = res["data"]["page"]["totalSize"]
            print(f"load page {page_no}/{total_page} data")
            if total_page == 0:
                break
            for r in res["data"]["page"]["rows"]:
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
            "warehouseId": str(warehouse_id),
            "zoneId": ""
        }
        res = self.post(url, req).json()
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
            "orderInfoList": [refund_order]
        }
        res = self.post(url, json=req).json()
        self.save_cookies()
        if res["code"] != 0:
            raise Exception("return_refund_order_to_warehouse failed: http response msg: " + res["msg"])
        return res["data"]

    def download(self, url, file_path):
        self.logger.info(f"DOWNLOAD url {url}...")
        r = self.session.get(url, stream=True)
        chunk_size = 4086
        with open(file_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
        self.logger.info(f"DOWNLOAD url {url} ok.")

    def get_wait_print_order_ship_provider_list(self, ware_house_id: int):
        """
        查询待打印订单按物流方式的统计信息
        :return: [
            {
                "id": 2443914,
                "providerAgentId": 1,
                "authType": null,
                "providerChannelId": 84,
                "trackingNoRequire": null,
                "isAdditional": null,
                "isSenderName": null,
                "name": "Shopee-PH-J&T Express",
                "count": 17,
                "platform": "shopee",
                "site": null,
                "defaultDeliveryType": null,
                "deliveryType": null,
                "callType": null,
                "authId": null,
                "authTimeStr": null,
                "defaultSenderAddress": null,
                "isSupportPickupTime": null,
                "platformProviderName": null,
                "inCount": 17
              }
        ]
        """
        url = "https://www.bigseller.com/api/v1/order/getOrderStatusCount.json"
        req = {
            "scanPictures": None,
            "sampleOrder": None,
            "skuSize": None,
            "skuType": None,
            "shipConfigType": None,
            "invoiceMark": None,
            "dropshipper": None,
            "promotionType": None,
            "platformOrderType": None,
            "priorityProcess": None,
            "shopId": None,
            "platformStatus": None,
            "shipProviderId": None,
            "printStatus": None,
            "paymentMethod": None,
            "hasRemark": None,
            "hasDeducted": None,
            "isWarehouseBack": None,
            "hasLable": "",
            "lableIds": None,
            "timeType": 1,
            "days": "",
            "beginDate": "",
            "endDate": "",
            "searchType": "orderNo",
            "pageWarehouseIds": [str(ware_house_id)],
            "searchContent": None,
            "inquireType": 2,
            "priorityValue": None,
            "failType": None,
            "printLabelMark": None,
            "printPickListMark": None,
            "printCollectMark": None,
            "printSign": None,
            "currentShopPlatform": None,
            "isPreOrder": None,
            "selectedShipList": None,
            "priorityDelivery": None,
            "estimatedProfit": None,
            "showLogisticsArr": 0,
            "showStoreArr": 0,
            "shopGroup": None,
            "blacklist": "",
            "hasBlacklistCloud": "",
            "inCancelBeforeStatus": None,
            "cancelLabelProcess": "",
            "cancelTimeTimeout": "",
            "payType": "",
            "shippedType": "",
            "cancelReasonJson": {},
            "returnType": None,
            "preShip": None,
            "status": "processing",
            "firstShipped": None,
            "allOrder": False,
            "historyOrder": 0,
            "packState": "3",
            "desc": 1,
            "orderBy": "skus",
            "wareType": None,
            "warehouseIdList": [str(ware_house_id)],
            "packageTypes": None,
            "tiktokPackageType": None,
            "waveSearchType": None,
            "orderConditionId": ""
        }
        res = self.post(url, json=req).json()
        if res["code"] != 0:
            print(f"get_order_status_count failed.")
            print(json.dumps(res, indent=2, ensure_ascii=False))
            raise Exception(f"get_order_status_count failed.")
        return res["data"]["shipProviderList"]

    def search_new_order(self, warehouse_id: int, begin_time: str, end_time: str, current_page: int=1, page_size: int=300):
      """
      查询指定仓库的新订单信息
      :param warehouse_id: 仓库id
      :param begin_time: 开始时间 yyyy-mm-dd hh:mm:ss
      :param end_time: 结束时间 yyyy-mm-dd hh:mm:ss
      :param current_page: 当前页码
      :param page_size: 每页大小
      :return: total, order_list(参考search_wait_print_order的返回格式)
      """
      url = "https://www.bigseller.com/api/v1/order/new/pageList.json"
      req = {
        "scanPictures": None,
        "sampleOrder": None,
        "skuSize": None,
        "skuType": None,
        "shipConfigType": None,
        "invoiceMark": None,
        "dropshipper": None,
        "promotionType": None,
        "platformOrderType": None,
        "storePickUp": None,
        "priorityProcess": None,
        "shopId": None,
        "status": "new",
        "platformStatus": None,
        "shipProviderId": None,
        "printStatus": 3,
        "paymentMethod": None,
        "paymentType": None,
        "hasRemark": None,
        "hasDeducted": None,
        "isWarehouseBack": None,
        "hasLable": "",
        "lableIds": None,
        "timeType": 1,
        "days": None,
        "beginDate": begin_time,
        "endDate": end_time,
        "searchType": "orderNo",
        "pageWarehouseIds": None,
        "searchContent": "",
        "inquireType": 2,
        "priorityValue": None,
        "failType": None,
        "printLabelMark": None,
        "printPickListMark": 0,
        "printCollectMark": None,
        "printSign": None,
        "currentShopPlatform": None,
        "isPreOrder": None,
        "selectedShipList": None,
        "priorityDelivery": None,
        "estimatedProfit": None,
        "showLogisticsArr": 0,
        "showStoreArr": 0,
        "shopGroup": None,
        "blacklist": "",
        "hasBlacklistCloud": "",
        "inCancelBeforeStatus": None,
        "cancelLabelProcess": "",
        "cancelTimeTimeout": "",
        "payType": "",
        "shippedType": "",
        "cancelReasonJsonStr": None,
        "returnType": None,
        "preShip": None,
        "printRange": [],
        "crossBorder": "",
        "logisticsServices": None,
        "replaceGoodsFlag": "",
        "quickOrder": None,
        "hasRemarkList": [],
        "printShipLabelMark": None,
        "customerLevelIdList": [],
        "printBillMark": None,
        "packageTypes": None,
        "tiktokPackageType": None,
        "firstShipped": None,
        "allOrder": False,
        "historyOrder": False,
        "packState": "0",
        "desc": 1,
        "orderBy": "printTime",
        "wareType": None,
        "warehouseIdList": [str(warehouse_id)],
        "waveSearchType": None,
        "pageNo": current_page,
        "pageSize": page_size
      }
      res = self.post(url, json=req).json()
      if res["code"] != 0:
          print(f"search_new_order failed.")
          print(json.dumps(res, indent=2))
          raise Exception(f"search_new_order failed.")
      page = res["data"]["page"]
      total = page["totalSize"]
      rows = page["rows"]
      return total, rows

    def set_new_order_to_wait_print(self, order_id: int):
      """
      将新订单标记为待打印
      :param order_id: 订单id
      :return:
      """
      url = "https://www.bigseller.com/api/v1/order/pack.json"
      req = {
          "orderId": str(order_id),
          "flag": 0
      }
      res = self.post(url, data=req).json()
      if res["code"] != 0:
          print(f"set_new_order_to_wait_print failed.")
          print(json.dumps(res, indent=2))
          raise Exception(f"set_new_order_to_wait_print failed.")
      self.save_cookies()
      return res["data"]

    def search_wait_print_order_by_warehouse_id(self, warehouse_id: int, current_page: int=1, page_size: int=300):
        """
        查询指定仓库的待打印订单信息
        :param warehouse_id: 仓库id
        :param current_page: 当前页码
        :param page_size: 每页大小
        :return: total, order_list
        """
        url = "https://www.bigseller.com/api/v1/order/new/pageList.json"
        req = {
            "warehouseIds": [int(warehouse_id)],
            "hasLable": "",
            "timeType": 1,
            "days": "",
            "beginDate": "",
            "endDate": "",
            "searchType": "orderNo",
            "searchContent": "",
            "inquireType": 2,
            "showLogisticsArr": 0,
            "showStoreArr": 0,
            "blacklist": "",
            "hasBlacklistCloud": "",
            "cancelLabelProcess": "",
            "cancelTimeTimeout": "",
            "payType": "",
            "shippedType": "",
            "cancelReasonJson": {},
            "status": "processing",
            "allOrder": False,
            "historyOrder": 0,
            "packState": "3",
            "desc": 1,
            "orderBy": "skus",
            "pageNo": current_page,
            "pageSize": page_size
        }
        res = self.post(url, json=req).json()
        if res["code"] != 0:
            print(f"search_wait_print_order_by_warehouse_id failed for warehouse_id: {warehouse_id}")
            print(json.dumps(res, indent=2))
            raise Exception(f"search_wait_print_order_by_warehouse_id failed for warehouse_id: {warehouse_id}")
        page = res["data"]["page"]
        total = page["totalSize"]
        rows = page["rows"]
        return total, rows

    def search_wait_print_order(self, shipping_provider_id, current_page, page_size):
        """
        查询指定物流方式的待打印订单信息
        :param shipping_provider_id:
        :param current_page:
        :param page_size:
        :return: total, [
            {
              "language": "zh",
              "id": 5133175528,
              "shopId": 2100179,
              "shopName": "Green lawn (09204889221)",
              "platformOrderId": "908069598574548",
              "platformOrderType": 0,
              "platformInvoiceRefNum": null,
              "state": "processing",
              "marketPlaceState": null,
              "lastOrderStatus": "To Ship",
              "viewStatus": "To Ship",
              "multilingualViewStatus": "待打单",
              "thirdWareStatus": "",
              "inCancel": null,
              "inCancelBeforeStatus": null,
              "multilingualCancelBeforeStatus": null,
              "packageNo": "BS8H16335832",
              "packageIndex": "0",
              "amount": "1890.80",
              "amountUnit": "PHP",
              "platform": "lazada",
              "viewPlatfrom": "Lazada",
              "buyerUsername": "Emylene Buco Alfredo",
              "buyerShippingCarrier": "standard - J&T Express PH",
              "rackingNoRequire": null,
              "shipIsAdditional": -1,
              "shipIsSenderName": null,
              "senderName": null,
              "isAdditional": 0,
              "additionalInfo": null,
              "printLabelMark": 0,
              "printBillMark": 0,
              "printBillTime": null,
              "printBillTimeStr": null,
              "printPickListMark": 0,
              "printCollectMark": null,
              "buyerCancelReason": null,
              "shippingCarrierId": 2482504,
              "shippingCarrierName": "Lazada-PH-J&T Express PH",
              "shipmentProvider": "J&T Express PH",
              "shippingConfigOptionId": null,
              "shippingConfigOptionName": null,
              "trackingNo": "820082003415",
              "trackingUrl": null,
              "error": "",
              "errorMsg": "",
              "webErrorLinkKey": null,
              "orderCreateTime": 1727679900000,
              "orderCreateTimeStr": "2024-09-30 07:05",
              "paymentMethod": "Prepaid",
              "payTime": 1727679918000,
              "payTimeStr": "2024-09-30 07:05",
              "cancelTimeStr": null,
              "shippedTime": 1727766318000,
              "shippedTimeStr": "2024-10-01 07:05",
              "finalActionTime": null,
              "finalActionTimeStr": "",
              "deadline": null,
              "deadlineStr": null,
              "strPayTime": null,
              "timeoutSeconds": 1727737518,
              "timoutTips": "23",
              "buyerMessage": null,
              "contactPerson": "Emylene Alfredo",
              "recipient": "Bulacan, Philippines",
              "packState": 3,
              "firstShipped": 0,
              "orderRemarksList": [],
              "remarkTypeIds": "",
              "platformSellerNote": "",
              "isFinalCarrier": null,
              "manualLogistics": null,
              "orderItemList": [
                {
                  "id": 2754347099,
                  "skuId": null,
                  "varSku": "Yellow(CW-7)-2*4m....................",
                  "varAttr": "2M x 4M (H2.5cm) ",
                  "quantity": 1,
                  "image": "https://ph-live.slatic.net/p/aa9fabefae962f67999c794f92f86b10.jpg",
                  "itemPlatformState": "已打包",
                  "varOriginalPrice": "1821.60",
                  "varDiscountedPrice": "1821.60",
                  "amount": "1821.60",
                  "link": "https://www.lazada.com.ph/products/i3629549639-s18909198297.html?urlFlag=true&mp=1",
                  "preOrder": false,
                  "itemFlag": null,
                  "itemSku": "3629549639_PH-18909198297",
                  "itemName": null,
                  "vName": null,
                  "itemNo": null,
                  "isAddition": 0,
                  "inventorySku": null,
                  "inventorySkuImage": null,
                  "available": null,
                  "platformVoucher": 0,
                  "sellerVoucher": 105.8,
                  "promotionQuantity": null,
                  "promotionDiscountPrice": null,
                  "totalPromotion": null,
                  "promotionType": null,
                  "sourcePlatform": null,
                  "sourceUrl": null,
                  "varSkuGroupVoList": null,
                  "allocated": null,
                  "allocating": null,
                  "outCost": null,
                  "weight": null,
                  "size": null,
                  "skuPlatformDiscount": null,
                  "skuSellerDiscount": null,
                  "orderLineId": null,
                  "cost": null,
                  "referencePrice": null,
                  "inventoryShelf": null,
                  "refundQuantity": null,
                  "scItemId": null,
                  "editType": null,
                  "editQuantity": null,
                  "allocatedVos": null,
                  "hidePrice": false
                },
                {
                  "id": 2754347100,
                  "skuId": null,
                  "varSku": "G-2-grape(1PCS)",
                  "varAttr": "grape leaves*1 ",
                  "quantity": 1,
                  "image": "https://ph-live.slatic.net/p/486e761141e2a5469739c24218d29bb8.jpg",
                  "itemPlatformState": "已打包",
                  "varOriginalPrice": "66",
                  "varDiscountedPrice": "66",
                  "amount": "66",
                  "link": "https://www.lazada.com.ph/products/i3630574331-s18915636700.html?urlFlag=true&mp=1",
                  "preOrder": false,
                  "itemFlag": null,
                  "itemSku": "3630574331_PH-18915636700",
                  "itemName": null,
                  "vName": null,
                  "itemNo": null,
                  "isAddition": 0,
                  "inventorySku": null,
                  "inventorySkuImage": null,
                  "available": null,
                  "platformVoucher": 0,
                  "sellerVoucher": 66,
                  "promotionQuantity": null,
                  "promotionDiscountPrice": null,
                  "totalPromotion": null,
                  "promotionType": null,
                  "sourcePlatform": null,
                  "sourceUrl": null,
                  "varSkuGroupVoList": null,
                  "allocated": null,
                  "allocating": null,
                  "outCost": null,
                  "weight": null,
                  "size": null,
                  "skuPlatformDiscount": null,
                  "skuSellerDiscount": null,
                  "orderLineId": null,
                  "cost": null,
                  "referencePrice": null,
                  "inventoryShelf": null,
                  "refundQuantity": null,
                  "scItemId": null,
                  "editType": null,
                  "editQuantity": null,
                  "allocatedVos": null,
                  "hidePrice": false
                }
              ],
              "printLabelTime": null,
              "printLabelTimeStr": null,
              "printPickListTime": null,
              "platformState": "{\n  \"Status\" : [ \"packed\" ]\n}",
              "printPickListTimeStr": null,
              "printCollectTime": null,
              "printCollectTimeStr": null,
              "scanPicturesTime": null,
              "scanPicturesTimeStr": null,
              "scanPicturesMark": null,
              "scanInspectionTime": null,
              "scanInspectionTimeStr": null,
              "autoCancelTimeStr": null,
              "autoCancelCountdownHour": null,
              "hasLabel": 0,
              "shippedOnline": null,
              "labelList": [],
              "invoiceMark": null,
              "expireTimeStr": "2024-10-01 07:05",
              "isPrintInnew": null,
              "itemTotalNum": 2,
              "selfDelivery": null,
              "plus": null,
              "authLogistics": 0,
              "submitTimeStr": null,
              "addressSite": "PH",
              "agentType": "lazada",
              "logisticsStatus": null,
              "thirdPartLogistics": 0,
              "hasBackWarehouse": 0,
              "shipmentWarehouse": "超市仓库",
              "hasDeducted": 0,
              "tiktokSplitOrCombineTag": null,
              "splitOrder": false,
              "bsAction": 0,
              "payStatus": null,
              "preOrder": false,
              "dropShipperLabel": null,
              "markException": 0,
              "printException": 0,
              "showAll": null,
              "canCancel": 1,
              "isAfterSaleOrder": null,
              "riskType": null,
              "editCarrier": 0,
              "paymentVoucher": null,
              "estimatedProfit": 1,
              "feeDetail": {
                "id": 5133175528,
                "totalAmount": "1715.80",
                "discount": "0.00",
                "voucherFrom": "0.00",
                "coins": "0.00",
                "estimatedShippingFee": "0.00",
                "commissionFee": "171.58",
                "serviceFee": "0.00",
                "serviceFeeRate": null,
                "exciseAmount": null,
                "exciseRate": null,
                "shippingFee": null,
                "sellerTransactionFee": "0.00",
                "finalEscrowProductGst": "0.00",
                "finalEscrowShippingGst": "0.00",
                "sellerCoinCashBack": "0.00",
                "productCost": "2639.60",
                "revenueTotal": "1715.80",
                "expenditureTotal": "2811.18",
                "estimatedProfit": "-1095.38",
                "itemMatch": true,
                "shippingRebate": "0.00",
                "settingCommissionRatio": true,
                "sellerShippingDiscounts": "0.00",
                "profitRate": "-63.84%",
                "finalProductProtection": "0.0"
              },
              "priority": false,
              "attachment": null,
              "attachmentName": null,
              "gift": null,
              "hasAddress": 1,
              "canPaid": null,
              "orderLinkKey": null,
              "taxInvoiceRequested": 0,
              "sampleOrder": null,
              "isJit": null,
              "profitRate": "-63.84%",
              "cancelReason": null,
              "userBlackId": 0,
              "userBlackContent": null,
              "trackingType": null,
              "deliveryInfo": null,
              "goodsType": null,
              "cancelLabelProcess": 0,
              "cancelNote": "",
              "applicationCancelTime": null,
              "cancelTimeTimeout": 0,
              "crossBorderOrderFlag": null,
              "changeShipCourier": null,
              "wareType": 0,
              "combinationPackageNo": null,
              "combinationPackageShipMethod": null,
              "isSelfShipOrder": false,
              "storeSite": "PH",
              "defaultProviderId": 3632079,
              "hasBlacklistCloud": false,
              "blacklistCloudDetail": null,
              "platformOtherNo": null,
              "preShip": 0,
              "multipleOrder": false,
              "multipleOrderList": null,
              "isEvalationOrder": 0
            }
        ]
        """
        url = "https://www.bigseller.com/api/v1/order/new/pageList.json"
        req = {
            "shipProviderId": int(shipping_provider_id),
            "hasLable": "",
            "timeType": 1,
            "days": "",
            "beginDate": "",
            "endDate": "",
            "searchType": "orderNo",
            "searchContent": "",
            "inquireType": 2,
            "showLogisticsArr": 0,
            "showStoreArr": 0,
            "blacklist": "",
            "hasBlacklistCloud": "",
            "cancelLabelProcess": "",
            "cancelTimeTimeout": "",
            "payType": "",
            "shippedType": "",
            "cancelReasonJson": {},
            "status": "processing",
            "allOrder": False,
            "historyOrder": 0,
            "packState": "3",
            "desc": 1,
            "orderBy": "skus",
            "pageNo": current_page,
            "pageSize": page_size
        }
        res = self.post(url, json=req).json()
        if res["code"] != 0:
            print(f"search_wait_print_order failed.")
            print(json.dumps(res, indent=2))
            raise Exception(f"search_wait_print_order failed.")
        page = res["data"]["page"]
        total = page["totalSize"]
        rows = page["rows"]
        return total, rows

    def download_order_mask_pdf_file(self, order_id: str, mark_id: str, platform: str, save_pdf_file: str):
        """
        下载需要打印的面单
        :param order_id:
        :param mark_id:
        :param platform:
        :param save_pdf_file:
        :return:
        """
        url = "https://www.bigseller.com/api/v1/print/print/selfLabel/many.json"
        if platform.lower() == "lazada":
            is_lazada = "true"
        else:
            is_lazada = "false"
        req = {
            "orderIds": order_id,
            "mark": mark_id,
            "isLazada": is_lazada
        }
        self.post(url, req)
        file_url = ""
        for i in range(1000):
            try:
                time.sleep(1)
                url = f"https://www.bigseller.com/api/v1/print/print/getOrderPrintProgress.json?mark={mark_id}&type=lable"
                res = self.get(url, timeout=30).json()
                file_url = res.get("data", {}).get("fileUrl")
                if file_url is not None and file_url != "":
                    break
            except Exception as e:
                self.logger.error(e)
        if file_url != "":
            self.download(file_url, save_pdf_file)

    def get_order_detail(self, order_id: int):
        """
        根据订单id查询订单详情
        :param order_id:
        :return: {
              "id": 5186982528,
              "orderStatus": "processing",
              "platform": "tiktok",
              "shopName": "FP Sims (TK:09179989950)",
              "platfromOrderId": "579437861785274382",
              "shopId": 2417193,
              "platformName": "tiktok",
              "viewPlatfrom": "TikTok",
              "buyer": "T***nce G***",
              "buyerId": "7494781700208297998",
              "buyerMessage": null,
              "sellerMessage": "",
              "buyerDesignatedLogistics": "J&T Express",
              "shippingMethod": "TikTok-PH-J&T Express",
              "shippingMethodId": 3632137,
              "shippingConfig": "快递取件",
              "shippingConfigId": 1,
              "rackingNoRequire": 1,
              "trackingNo": "972374486332",
              "trackingUrl": null,
              "senderName": null,
              "isSenderName": null,
              "additionalInfo": {
                "addressId": null,
                "addressInfo": "null<br>null,null<br>null,null",
                "dateId": null,
                "timeId": null,
                "timeSel": ""
              },
              "isAdditional": 1,
              "packageNo": "BS8H16340979",
              "address": {
                "name": "T***nce G***",
                "phone": "(+63)966*****90",
                "country": "Philippines",
                "region": null,
                "province": "Central Luzon",
                "city": "Pampanga",
                "district": null,
                "town": null,
                "zipCode": null,
                "address": "Sa**************************************************************************************************************************************, Pa*****, An**********, Pampanga, Central Luzon,Philippines",
                "addressIds": "2",
                "buyerCountryCode": null,
                "logisticsData": null
              },
              "store": null,
              "ordered": null,
              "orderedTime": 1728233404000,
              "orderedTimeStr": "2024-10-06 16:50",
              "paid": null,
              "payTime": null,
              "payTimeStr": "",
              "amountUnit": "PHP",
              "shippingFee": "0",
              "sellerShippingFee": null,
              "payment": "COD",
              "transferMethod": null,
              "transferAccount": null,
              "orderTotal": "685.40",
              "orderItemVoList": [
                {
                  "id": 1397952660,
                  "skuId": 36101778,
                  "varSku": "(2pack)-G-2-large",
                  "varAttr": "Grape leaf, 12 pcs(get 12 free)",
                  "quantity": 1,
                  "image": "https://p16-oec-va.ibyteimg.com/tos-maliva-i-o3syd03w52-us/ebc9f0b28ca7494783d245d3e5c52787~tplv-o3syd03w52-origin-jpeg.jpeg?from=1413970683",
                  "itemPlatformState": null,
                  "varOriginalPrice": "319.23",
                  "varDiscountedPrice": "319.23",
                  "amount": "319.23",
                  "link": null,
                  "preOrder": false,
                  "itemFlag": "",
                  "itemSku": null,
                  "itemName": "Buy 6 Get 6 Free 2.4Meter Artificial Green Leaf Garland Plants Vine Fake Home Wedding Decoration Colorful Decoration Decorative Fruit Decorative Fruit Ornaments",
                  "vName": "Grape leaf, 12 pcs(get 12 free)",
                  "itemNo": "1729697034552707289",
                  "isAddition": 0,
                  "inventorySku": "G-2-large（2pack） grape leaves",
                  "inventorySkuImage": null,
                  "available": 10,
                  "platformVoucher": null,
                  "sellerVoucher": null,
                  "promotionQuantity": null,
                  "promotionDiscountPrice": null,
                  "totalPromotion": null,
                  "promotionType": null,
                  "sourcePlatform": null,
                  "sourceUrl": null,
                  "varSkuGroupVoList": [
                    {
                      "id": 28042,
                      "skuId": 36101778,
                      "warehouseSkuId": 14530059,
                      "varSkuId": 14556637,
                      "varSku": "G-2-large grape leaves",
                      "varSkuTitle": null,
                      "varSkuImgUrl": null,
                      "num": 24,
                      "costAllocationRatio": 1,
                      "commodityWeight": null,
                      "cost": 7.52,
                      "available": 251,
                      "common": 251,
                      "promotion": 0,
                      "onhand": 13,
                      "isOutOfStock": 0,
                      "skuType": null
                    }
                  ],
                  "allocated": 1,
                  "allocating": 1,
                  "outCost": "0.00",
                  "weight": "0g",
                  "size": "0.00*0.00*0.00",
                  "skuPlatformDiscount": null,
                  "skuSellerDiscount": null,
                  "orderLineId": null,
                  "cost": 0,
                  "referencePrice": 0,
                  "inventoryShelf": null,
                  "refundQuantity": null,
                  "scItemId": null,
                  "editType": null,
                  "editQuantity": null,
                  "allocatedVos": null,
                  "hidePrice": false
                },
                {
                  "id": 1397952663,
                  "skuId": 44373536,
                  "varSku": "(2pack)-G-4-Green",
                  "varAttr": "Green lily leaves, 12 pcs(get 12 free)",
                  "quantity": 1,
                  "image": "https://p16-oec-va.ibyteimg.com/tos-maliva-i-o3syd03w52-us/8c5e8396cef4453ebf1b217aff3218ad~tplv-o3syd03w52-origin-jpeg.jpeg?from=1413970683",
                  "itemPlatformState": null,
                  "varOriginalPrice": "366.17",
                  "varDiscountedPrice": "366.17",
                  "amount": "366.17",
                  "link": null,
                  "preOrder": false,
                  "itemFlag": "",
                  "itemSku": null,
                  "itemName": "Buy 6 Get 6 Free 2.4Meter Artificial Green Leaf Garland Plants Vine Fake Home Wedding Decoration Colorful Decoration Decorative Fruit Decorative Fruit Ornaments",
                  "vName": "Green lily leaves, 12 pcs(get 12 free)",
                  "itemNo": "1729697034552707289",
                  "isAddition": 0,
                  "inventorySku": "(2Pack)G-4-Green dill",
                  "inventorySkuImage": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/20240531060824170c0f12d16f2df85215cd5e54a6bc6a.jpg?imageView2/1/w/300/h/300",
                  "available": 224,
                  "platformVoucher": null,
                  "sellerVoucher": null,
                  "promotionQuantity": null,
                  "promotionDiscountPrice": null,
                  "totalPromotion": null,
                  "promotionType": null,
                  "sourcePlatform": null,
                  "sourceUrl": null,
                  "varSkuGroupVoList": [
                    {
                      "id": 43260,
                      "skuId": 44373536,
                      "warehouseSkuId": 14530357,
                      "varSkuId": 14556933,
                      "varSku": "G-4-green dill leaves",
                      "varSkuTitle": null,
                      "varSkuImgUrl": null,
                      "num": 24,
                      "costAllocationRatio": 1,
                      "commodityWeight": null,
                      "cost": 9.45,
                      "available": 5395,
                      "common": 5395,
                      "promotion": 0,
                      "onhand": 229,
                      "isOutOfStock": 0,
                      "skuType": null
                    }
                  ],
                  "allocated": 1,
                  "allocating": 1,
                  "outCost": "0.00",
                  "weight": "0g",
                  "size": "0.00*0.00*0.00",
                  "skuPlatformDiscount": null,
                  "skuSellerDiscount": null,
                  "orderLineId": null,
                  "cost": 0,
                  "referencePrice": 0,
                  "inventoryShelf": null,
                  "refundQuantity": null,
                  "scItemId": null,
                  "editType": null,
                  "editQuantity": null,
                  "allocatedVos": null,
                  "hidePrice": false
                }
              ],
              "orderRemarksList": [],
              "orderAdditionSkuIds": [],
              "orderLableList": null,
              "currentWarehouseId": 27763,
              "warehouseNameList": [
                {
                  "id": 27763,
                  "name": "超市仓库",
                  "wareType": 0,
                  "thirdAuthId": 0,
                  "authPlatform": null,
                  "isDefault": 1,
                  "defaultReturn": 0,
                  "manager": "",
                  "phone": "",
                  "location": "",
                  "isAreaSeparate": 0,
                  "warehouseZoneList": null
                }
              ],
              "warehouseName": "超市仓库",
              "isFinalCarrier": null,
              "hasLable": 0,
              "splitOrder": false,
              "mainPackageNo": null,
              "cancelSplitOrder": false,
              "weight": 0,
              "packageWeight": 0,
              "invoiceMark": null,
              "invoiceNum": "",
              "orderName": null,
              "multilingualViewStatus": "待打单",
              "discountPrice": null,
              "totalOutCost": "0",
              "packageRemark": null,
              "selfDelivery": null,
              "equipmentDataStr": null,
              "volumeStr": null,
              "isEquipment": 0,
              "shippingAddressId": null,
              "editCarrier": 0,
              "showEditLogisticsBtn": 0,
              "viewStatus": "To Ship",
              "pickupStartTimeStr": null,
              "pickupEndTimeStr": null,
              "thirdPartLogistics": 0,
              "authLogistics": 0,
              "addressSite": "PH",
              "senderAddressVo": null,
              "submitTimeStr": null,
              "markPlaceState": "Awaiting Collection",
              "mp3Order": null,
              "cost": 407.28,
              "length": null,
              "width": null,
              "height": null,
              "sellerName": "",
              "sellerPhone": "",
              "sellerAddress": "",
              "userBlackId": 0,
              "userBlackContent": null,
              "hasBackWarehouse": 0,
              "inWarehouseNote": "",
              "isCanCompare": null,
              "serviceFee": null,
              "serviceFeeRate": null,
              "exciseAmount": null,
              "exciseRate": null,
              "platformStatus": null,
              "isEvalationOrder": 0,
              "isSelfShipOrder": false,
              "isSelfShipOrderAnd3Pl": false,
              "hasBlacklistCloud": false,
              "blacklistCloudDetail": null,
              "depositPrice": null,
              "balancePrice": null,
              "platformOrderType": null,
              "platformOtherNo": null,
              "shippingAddress": null,
              "paymentVoucher": null,
              "orderUpdatedInfo": null,
              "pickupType": null,
              "isJit": null,
              "stringpaymentVoucher": null
            }
        """
        GLOBAL_RATE_LIMITER.acquire(1000)
        url = f"https://www.bigseller.com/api/v1/order/detail.json?id={order_id}&viewBuyerMessage=false"
        res = self.get(url).json()
        if res["code"] != 0:
            print(f"get_order_detail failed.")
            print(json.dumps(res, indent=2, ensure_ascii=False))
            self.logger.error(f"get_order_detail failed. {json.dumps(res, indent=2, ensure_ascii=False)}")
            raise Exception(f"get_order_detail failed.")
        return res["data"]["orderDetail"]

    def mark_order_printed(self, order_id: str):
        """
        将订单标记为已打单
        :param order_id:
        :return:
        """
        url = "https://www.bigseller.com/api/v1/order/confirmLabelPrint.json"
        req = {
            "orderIds": order_id,
            "markType": "auto"
        }
        res = self.post(url, req, timeout=30)
        if res.status_code != 200:
            time.sleep(0.5)
            res = self.post(url, req, timeout=30)
        print(f"mark_order_printed {order_id} result {res.text}")
        return res.json()

    def post(self, url: str, data=None, json=None, timeout=None):
        import json as js
        if data is not None:
            req_text = js.dumps(data, ensure_ascii=False)[: 128]
        else:
            req_text = js.dumps(json, ensure_ascii=False)[: 128]
        self.logger.info(f"POST REQUEST {url} req_text: {req_text}.")
        if timeout is not None:
            res = self.session.post(url, data=data, json=json, timeout=timeout)
        else:
            res = self.session.post(url, data=data, json=json)
        res_code = res.status_code
        res_text = res.text[:1024]
        self.logger.info(f"POST RESPONSE {url} http_code: {res_code} res_text: {res_text}")
        return res

    def get(self, url: str, timeout=None):
        self.logger.info(f"GET REQUEST {url}")
        if timeout is not None:
            res = self.session.get(url, timeout=timeout)
        else:
            res = self.session.get(url)
        res_code = res.status_code
        res_text = res.text[:128]
        self.logger.info(f"GET RESPONSE {url} http_code: {res_code} res_text: {res_text}")
        return res

    def query_sku_inventory_detail(self, sku: str, warehouse_id: int):
        """
        根据sku查询仓库当前sku数和预测sku
        :param sku: sku
        :param warehouse_id: warehouse_id
        :return: {
          "createTime": null,
          "updateTime": null,
          "id": null,
          "warehouseSkuId": 27773442,
          "skuId": 27410427,
          "sku": "A-1-Golden-Maple leaf",
          "warehouseId": 27763,
          "warehouseName": "超市仓库",
          "title": "金色枫叶1pcs",
          "onhand": 12903,
          "allocated": 276,
          "promoReservedStock": 0,
          "available": 12627,
          "common": 12627,
          "onTheWay": 0,
          "transferOnTheWay": 0,
          "purchaseOnTheWay": 0,
          "cost": "8.79",
          "totalCost": "113417.37",
          "threshold": 0,
          "thresholdType": 0,
          "image": "https://res.bigseller.pro/album/279590/20230603074446b4bf29067f2227517d260057c6385011.jpg?imageView2/1/w/300/h/300",
          "isCurrentMapping": null,
          "isGroup": 0,
          "isSelect": null,
          "skuGroupVoList": null,
          "shelves": null,
          "shelfId": null,
          "shelfName": "No Shelf",
          "isStockCount": 0,
          "stockCounting": null,
          "merchantSkuId": "90000642",
          "gtinCode": null,
          "purchaseDays": null,
          "safetyDays": null,
          "commodityLong": 0,
          "commodityWide": 0,
          "commodityHigh": 0,
          "num": 0,
          "commodityWeight": 0,
          "suggestionType": null,
          "putAside": null,
          "avgDailySales": 214.75,
          "purchaseSaleDays": -1,
          "avgJson": null,
          "recommendQuantity": null,
          "isAreaSeparate": 0,
          "shelfVos": null,
          "wareType": 0,
          "skuType": 0,
          "distributionSku": 0,
          "puid": null
        }
        """
        url = "https://www.bigseller.com/api/v1/inventory/pageList.json"
        req = {
            "pageNo": 1,
            "pageSize": 50,
            "searchType": "skuName",
            "searchContent": sku,
            "inquireType": 0,
            "isGroup": 0,
            "queryDistribution": 1,
            "warehouseIds": str(warehouse_id)
        }
        res = self.post(url, data=req, timeout=30)
        if res.status_code != 200:
            time.sleep(0.5)
            res = self.post(url, req, timeout=30)
        print(f"query_sku_inventory_detail {sku} result {res.text}")
        rows = res.json()["data"]["page"]["rows"]
        match_rows = []
        for r in rows:
            if r["sku"] == sku:
                match_rows.append(r)
        if len(match_rows) == 1:
            return match_rows[0]
        return None
