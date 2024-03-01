from ec_erp_api.app_config import get_app_config
from ec.bigseller.big_seller_client import BigSellerClient

config = get_app_config()


def main():
    client = BigSellerClient(config["ydm_token"])
    client.login(config["big_seller_mail"], config["big_seller_encoded_passwd"])
    res = client.add_stock_to_erp({
        "detailsAddBoList": [
            {
                "skuId": 28439992,
                "stockPrice": 10.3,
                "shelfList": [
                    {
                        "shelfId": "",
                        "shelfName": "",
                        "stockQty": 1
                    }
                ]
            }
        ],
        "id": "IN-EC-3",
        "inoutTypeId": "1001",
        "isAutoInoutStock": 1,
        "note": "ec-erp 采购单：3入库单： IN-EC-3",
        "warehouseId": 27763,
        "zoneId": None
    })
    print(res)


if __name__ == '__main__':
    main()
