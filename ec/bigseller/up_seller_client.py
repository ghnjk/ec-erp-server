#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: up_seller_client
@author: jkguo
@create: 2026/05/01
"""
import base64
import json
import logging
import os
import tempfile
import time
import typing
import uuid

import requests

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from ec.verifycode.ydm_verify import YdmVerify


# UpSeller 前端 (`bundle.index.*.js` 模块 89907) 用 AES-256-ECB/PKCS7 + Base64
# 加密登录表单。密钥由前端常量经一次 AES 解密"洗白"得到，等价于 32 字节 UTF-8 串。
# 当前 `app.upseller.com` / `app.upseller.cn` 的 `c.S` 登录加密不按 `getCountryCode`
# 切换 key；国家只决定走 TencentCaptcha 还是 Cloudflare token。
_UP_SELLER_LOGIN_KEY_INTL = b"Y6MxcOCNj5Pjx$@rwMW6VNVa8fYVOTR&"
_UP_SELLER_LOGIN_KEY_CN = b"2Y4Mgj$hwJV6qa62z64#b2!HkLz2pP5g"
_UP_SELLER_LOGIN_KEY_APP = _UP_SELLER_LOGIN_KEY_CN
# 前端 `c.S(t, e)` 在拼接 `t` 与 `e` 时使用的字面分隔符，对应 UTF-8 字节 0xC2 0xB1 0xC2 0xB1
_UP_SELLER_JOIN_SEP = "\u00b1\u00b1"


def _up_seller_aes_encrypt(plaintext: str, key: bytes) -> str:
    """对应前端 CryptoJS.AES.encrypt(plain, keyWordArray, {ECB, Pkcs7}).toString()。"""
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))
    return base64.b64encode(encrypted).decode("ascii")


def _up_seller_cs_encode(*parts, key: bytes = _UP_SELLER_LOGIN_KEY_INTL) -> str:
    """对应前端 module 89907 导出的 `S` 函数: `[t,e].filter(Boolean).join("±±")`
    后再做 AES-256-ECB/PKCS7 + Base64。"""
    truthy = [str(p) for p in parts if p]
    plain = _UP_SELLER_JOIN_SEP.join(truthy)
    return _up_seller_aes_encrypt(plain, key)


def build_default_login_body_encoder(
        country_code: typing.Optional[str] = None
) -> typing.Callable[[dict], str]:
    """构造默认的 UpSeller 登录 `body` 字段编码器。

    与前端 `bundle.login.*.js` 中 `doLogin` 的处理一致:

    1. password 字段先做 `AES(password ±± timeStamper)`；
    2. 按前端 `Object.assign({}, formData, {}, overrides)` 的插入顺序构造 payload；
    3. 用 `AES(JSON.stringify(payload))` 得到最终 body。

    `country_code` 只保留作兼容参数。当前前端在 `app.upseller.com` 上无论国家返回
    CN 还是非 CN，`c.S` 都使用同一套 app key；CN 场景仍需要补齐 TencentCaptcha 的
    token/randStr 字段，非 CN 场景需要 Cloudflare token。"""
    _ = country_code
    key = _UP_SELLER_LOGIN_KEY_APP

    def encoder(payload: dict) -> str:
        plain_password = payload.get("password", "")
        password_time_stamper = payload.get("timeStamper") or int(time.time() * 1000)
        encrypted_password = _up_seller_cs_encode(
            plain_password, password_time_stamper, key=key)

        # JS `Object.assign` 保留已有 key 的插入位置；这里显式复刻前端 formData 顺序。
        merged = {}
        for field in ("email", "password", "vcode", "remember"):
            if field in payload:
                merged[field] = payload[field]
        merged["password"] = encrypted_password

        for field, value in payload.items():
            if field not in merged and field not in ("token", "randStr", "timeStamper", "deviceId"):
                merged[field] = value

        for field in ("token", "randStr", "timeStamper", "deviceId"):
            value = payload.get(field)
            if value is not None:
                merged[field] = value

        body_json = json.dumps(merged, separators=(",", ":"), ensure_ascii=False)
        return _up_seller_cs_encode(body_json, key=key)

    return encoder


class UpSellerClient:
    """
    UpSeller Web client.

    UpSeller 登录接口会把登录表单整体加密后以 form 字段 body 提交；默认
    `login_body_encoder` 已基于前端 `bundle.index.*.js` 模块 89907 还原
    AES-256-ECB/PKCS7 + Base64 算法，并按当前登录页的字段顺序生成 body。当
    `getCountryCode` 返回 CN 时仍需要 TencentCaptcha token/randStr；如有特殊场景
    可通过构造参数注入自定义编码器。
    已登录 cookie 可直接复用登录态调用 SKU 和库存接口。
    """

    def __init__(
            self,
            ydm_token: str,
            cookies_file_path: str = "cookies/up_seller.cookies",
            login_body_encoder: typing.Optional[typing.Callable[[dict], str]] = None,
            login_mode: str = "api",
            selenium_timeout: int = 120,
            selenium_headless: bool = True,
            selenium_driver_path: typing.Optional[str] = None):
        self.base_url = "https://app.upseller.com"
        self.home_web_url = f"{self.base_url}/zh-CN/home"
        self.login_web_url = f"{self.base_url}/zh-CN/login"
        self.check_login_url = f"{self.base_url}/api/is-login"
        self.user_info_url = f"{self.base_url}/api/user-info"
        self.login_url = f"{self.base_url}/api/login"
        self.country_code_url = f"{self.base_url}/api/getCountryCode"
        self.verify_code_url = f"{self.base_url}/api/vcode"
        self.sku_list_url = f"{self.base_url}/api/sku/index-single"
        self.sku_variant_list_url = f"{self.base_url}/api/sku/index-variants"
        self.sku_detail_single_url = f"{self.base_url}/api/sku/detail-single"
        self.sku_detail_spu_url = f"{self.base_url}/api/sku/detail-spu"
        self.sku_detail_group_url = f"{self.base_url}/api/sku/detail-group"
        self.warehouse_list_url = f"{self.base_url}/api/warehouse/index"
        self.warehouse_enable_list_url = f"{self.base_url}/api/warehouse/list-enable"
        self.warehouse_sku_list_url = f"{self.base_url}/api/warehouse-sku/list"
        self.warehouse_sku_one_url = f"{self.base_url}/api/warehouse-sku/one-sku"
        self.add_stock_url = f"{self.base_url}/api/warehouse-inout-list/add-in"
        self.add_stock_examine_url = f"{self.base_url}/api/warehouse-inout-list/add-in-to-examine"
        self.out_stock_url = f"{self.base_url}/api/warehouse-inout-list/add-out"

        self.session = requests.Session()
        self.auto_verify_coder = YdmVerify(ydm_token)
        self.cookies_file_path = cookies_file_path
        self.login_body_encoder = login_body_encoder
        self.login_mode = login_mode
        self.selenium_timeout = selenium_timeout
        self.selenium_headless = selenium_headless
        self.selenium_driver_path = selenium_driver_path
        self.default_timeout = 30
        self.logger = logging.getLogger("INVOKER")
        self.device_id = str(uuid.uuid4())
        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Origin": self.base_url,
            "Referer": self.login_web_url,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "DeviceId": self.device_id,
        })

    def login(self, email: str, password: str, remember: bool = True):
        if self.load_cookies() and self.is_login():
            self.logger.info("use upseller cookie login ok")
            print("use upseller cookie login ok")
            return
        if self.login_mode == "selenium":
            self.__login_by_selenium(email, password, remember)
            return
        if self.login_mode != "api":
            raise ValueError(f"unsupported upseller login_mode: {self.login_mode}")
        self.__login(email, password, remember)

    def __login(self, email: str, password: str, remember: bool = True):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Origin": self.base_url,
            "Referer": self.login_web_url,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "DeviceId": self.device_id,
        })
        self.get(self.login_web_url)
        verify_code = self.get_valid_verify_code(email)
        country_code = self.get_country_code()
        login_payload = {
            "email": email.strip(),
            "password": password,
            "vcode": str(verify_code),
            "remember": 1 if remember else 0,
            "timeStamper": int(time.time() * 1000),
            "deviceId": self.device_id,
            "token": None,
            "randStr": None,
        }
        if country_code == "CN":
            self.logger.info("upseller login in CN may require TencentCaptcha token")
        self.logger.debug(f"upseller login_payload: {json.dumps(login_payload, ensure_ascii=False)}")

        encoder = self.login_body_encoder or build_default_login_body_encoder(country_code)
        encrypted_body = encoder(login_payload)
        res = self.post_form(self.login_url, {"body": encrypted_body}).json()
        if res.get("code") != 0:
            raise Exception(f"upseller login failed: {json.dumps(res, ensure_ascii=False)}")
        if not self.is_login():
            raise Exception("upseller login failed: is_login=false")
        self.save_cookies()

    def __login_by_selenium(self, email: str, password: str, remember: bool = True):
        try:
            from selenium import webdriver
            from selenium.common.exceptions import TimeoutException
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait
        except ImportError as e:
            raise ImportError(
                "selenium login_mode requires selenium. "
                "Install it with: python -m pip install selenium"
            ) from e

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Origin": self.base_url,
            "Referer": self.login_web_url,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "DeviceId": self.device_id,
        })
        options = Options()
        if self.selenium_headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        if self.selenium_driver_path:
            service = Service(executable_path=self.selenium_driver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, self.selenium_timeout)
        try:
            driver.get(self.login_web_url)
            self._load_session_cookies_to_driver(driver)
            driver.get(self.login_web_url)

            inputs = wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "input"))
            if len(inputs) < 3:
                raise Exception("upseller selenium login failed: login inputs not found")

            self._clear_and_send_keys(inputs[0], email)
            driver.execute_script("arguments[0].blur();", inputs[0])
            verify_code = self._get_selenium_verify_code(driver, wait)
            self._clear_and_send_keys(inputs[1], password)
            self._clear_and_send_keys(inputs[2], verify_code)

            if remember:
                self._click_remember_checkbox_if_needed(driver)

            submit_button = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "button.ant-btn-primary, button[type='submit'], .main_btn"
            )))
            submit_button.click()

            try:
                wait.until(lambda d: self._driver_is_login_success(d))
            except TimeoutException as e:
                raise Exception(
                    "upseller selenium login timeout. "
                    "If TencentCaptcha or Cloudflare challenge appears, solve it in Chrome and rerun."
                ) from e

            self._load_driver_cookies_to_session(driver)
            if not self.is_login():
                raise Exception("upseller selenium login failed: is_login=false")
            self.save_cookies()
        finally:
            driver.quit()

    def _load_session_cookies_to_driver(self, driver):
        for cookie in self.session.cookies:
            cookie_dict = {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain if cookie.domain else "app.upseller.com",
                "path": cookie.path or "/",
            }
            if cookie.expires:
                cookie_dict["expiry"] = int(cookie.expires)
            try:
                driver.add_cookie(cookie_dict)
            except Exception as e:
                self.logger.info(f"skip selenium add cookie {cookie.name}: {e}")

    def _load_driver_cookies_to_session(self, driver):
        self.session.cookies.clear()
        for cookie in driver.get_cookies():
            self.session.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain") or "app.upseller.com",
                path=cookie.get("path") or "/")

    def _get_selenium_verify_code(self, driver, wait):
        from selenium.webdriver.common.by import By

        image_base64 = wait.until(lambda d: self._find_selenium_verify_image_base64(d, By))
        for _ in range(10):
            verify_res = self.auto_verify_coder.common_verify(image_base64, "10110")
            if verify_res["code"] == 10000:
                return verify_res["data"]["data"]
            time.sleep(3)
            image_base64 = self._find_selenium_verify_image_base64(driver, By)
        raise Exception("get selenium verify code failed.")

    def _find_selenium_verify_image_base64(self, driver, by):
        candidates = []
        candidates.extend(driver.find_elements(by.CSS_SELECTOR, "img"))
        candidates.extend(driver.find_elements(
            by.CSS_SELECTOR,
            ".send_code_btn, [class*='captcha'], [class*='Captcha'], [class*='vcode']"))

        for element in candidates:
            try:
                if not element.is_displayed():
                    continue
                src = element.get_attribute("src") or ""
                if src.startswith("data:image/") and "base64," in src:
                    return src.split("base64,", 1)[1]
                if "/api/vcode" in src or src.startswith("blob:"):
                    return base64.b64encode(element.screenshot_as_png).decode("ascii")
                width = element.size.get("width", 0)
                height = element.size.get("height", 0)
                if width >= 50 and height >= 20:
                    image_base64 = base64.b64encode(element.screenshot_as_png).decode("ascii")
                    if image_base64:
                        return image_base64
            except Exception as e:
                self.logger.info(f"skip selenium captcha candidate: {e}")
        return None

    @staticmethod
    def _clear_and_send_keys(element, value):
        element.click()
        element.clear()
        element.send_keys(value)

    def _click_remember_checkbox_if_needed(self, driver):
        from selenium.webdriver.common.by import By

        try:
            checkbox = driver.find_element(By.CSS_SELECTOR, ".ant-checkbox-input")
            if not checkbox.is_selected():
                driver.find_element(By.CSS_SELECTOR, ".ant-checkbox-wrapper").click()
        except Exception as e:
            self.logger.info(f"skip remember checkbox: {e}")

    def _driver_is_login_success(self, driver):
        if "/login" not in driver.current_url:
            return True
        try:
            return bool(driver.execute_async_script(
                "const done = arguments[0];"
                "fetch('/api/is-login', {credentials: 'include'})"
                ".then(r => r.json()).then(j => done(!!j.data)).catch(() => done(false));"
            ))
        except Exception:
            return False

    def is_login(self):
        response = self.get(self.check_login_url).json()
        return response.get("code") == 0 and bool(response.get("data"))

    def get_country_code(self):
        res = self.get(self.country_code_url).json()
        self._check_response(res, "get_country_code")
        return res.get("data")

    def get_user_info(self):
        res = self.get(self.user_info_url).json()
        self._check_response(res, "get_user_info")
        return res.get("data")

    def get_valid_verify_code(self, email: str):
        for _ in range(10):
            response = self.get(self.verify_code_url, params={
                "email": email,
                "t": int(time.time() * 1000)
            })
            res_json = response.json()
            self._check_response(res_json, "get_valid_verify_code")
            image_base64 = res_json["data"]
            if image_base64.startswith("data:image/jpg;base64,"):
                image_base64 = image_base64[len("data:image/jpg;base64,"):]
            elif image_base64.startswith("data:image/png;base64,"):
                image_base64 = image_base64[len("data:image/png;base64,"):]
            verify_res = self.auto_verify_coder.common_verify(image_base64, "10110")
            if verify_res["code"] == 10000:
                return verify_res["data"]["data"]
            time.sleep(3)
        raise Exception("get_valid_verify_code failed.")

    def save_cookies(self):
        cookies_dir = os.path.dirname(self.cookies_file_path)
        if cookies_dir and not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(
                mode="w",
                dir=cookies_dir or None,
                delete=False,
                suffix=".tmp",
                prefix=".upseller_cookies") as tmp_file:
            tmp_file_path = tmp_file.name
            json.dump(self.session.cookies.get_dict(), tmp_file, indent=2)
        try:
            os.replace(tmp_file_path, self.cookies_file_path)
        except Exception as e:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
            raise e

    def load_cookies(self):
        if not os.path.isfile(self.cookies_file_path):
            return False
        with open(self.cookies_file_path, "r") as fp:
            self.session.cookies.update(json.load(fp))
            return True

    def load_all_sku(self, page_size: int = 50, include_variants: bool = False):
        rows = []
        page_no = 1
        while True:
            page = self.query_sku_page(page_no=page_no, page_size=page_size)
            rows.extend(page["rows"])
            print(f"load upseller sku page {page_no}/{page['total_page']}")
            if page_no >= page["total_page"]:
                print(f"load all {page['total_size']} upseller sku")
                break
            page_no += 1
            time.sleep(0.5)
        if include_variants:
            rows.extend(self.load_all_sku_variants(page_size=page_size))
        self.save_cookies()
        return rows

    def load_all_sku_variants(self, page_size: int = 50):
        rows = []
        page_no = 1
        while True:
            page = self.query_sku_page(
                page_no=page_no,
                page_size=page_size,
                variants=True)
            rows.extend(page["rows"])
            if page_no >= page["total_page"]:
                break
            page_no += 1
            time.sleep(0.5)
        return rows

    def query_sku_page(
            self,
            page_no: int = 1,
            page_size: int = 50,
            search_value: str = "",
            search_type: str = "1",
            variants: bool = False,
            extra_filter: typing.Optional[dict] = None):
        req = {
            "pageNum": page_no,
            "pageSize": page_size,
            "searchGroup": 0 if variants else 1,
            "searchType": search_type if search_value else None,
            "searchValue": search_value or None,
        }
        if extra_filter:
            req.update(extra_filter)
        url = self.sku_variant_list_url if variants else self.sku_list_url
        res = self.post(url, json=req).json()
        self._check_response(res, "query_sku_page")
        return self._extract_page(res.get("data"))

    def query_sku_detail(self, sku_id: typing.Union[int, str], sku_type: str = "single"):
        url_map = {
            "single": self.sku_detail_single_url,
            "spu": self.sku_detail_spu_url,
            "group": self.sku_detail_group_url,
        }
        url = url_map.get(sku_type)
        if not url:
            raise ValueError(f"unsupported sku_type: {sku_type}")
        res = self.post(url, json={"id": str(sku_id)}).json()
        self._check_response(res, "query_sku_detail")
        self.save_cookies()
        return res.get("data")

    def query_warehouse_list(self, enable_only: bool = False):
        url = self.warehouse_enable_list_url if enable_only else self.warehouse_list_url
        res = self.post(url, json={}).json()
        self._check_response(res, "query_warehouse_list")
        return res.get("data")

    def query_sku_inventory_page(
            self,
            page_no: int = 1,
            page_size: int = 50,
            sku: str = "",
            warehouse_id: typing.Optional[typing.Union[int, str]] = None,
            extra_filter: typing.Optional[dict] = None):
        req = {
            "pageNum": page_no,
            "pageSize": page_size,
            "searchType": "1" if sku else None,
            "searchValue": sku or None,
            "warehouseId": str(warehouse_id) if warehouse_id else None,
        }
        if extra_filter:
            req.update(extra_filter)
        res = self.post(self.warehouse_sku_list_url, json=req).json()
        self._check_response(res, "query_sku_inventory_page")
        return self._extract_page(res.get("data"))

    def query_sku_inventory_detail(self, sku: str, warehouse_id: typing.Union[int, str]):
        page = self.query_sku_inventory_page(
            page_no=1,
            page_size=50,
            sku=sku,
            warehouse_id=warehouse_id)
        match_rows = []
        for row in page["rows"]:
            row_sku = row.get("sku") or row.get("skuName") or row.get("skuCode")
            if row_sku == sku:
                match_rows.append(row)
        if len(match_rows) == 1:
            return match_rows[0]
        if page["rows"]:
            return page["rows"][0]
        return None

    def query_product_warehouse_list(self, sku_id: typing.Union[int, str]):
        res = self.post(self.warehouse_sku_one_url, json={"id": str(sku_id)}).json()
        self._check_response(res, "query_product_warehouse_list")
        return res.get("data")

    def add_stock_to_erp(self, req: dict, submit_to_examine: bool = False):
        url = self.add_stock_examine_url if submit_to_examine else self.add_stock_url
        res = self.post(url, json=req).json()
        self.save_cookies()
        self._check_response(res, "add_stock_to_erp")
        return res.get("data")

    def out_stock_from_erp(self, req: dict):
        res = self.post(self.out_stock_url, json=req).json()
        self.save_cookies()
        self._check_response(res, "out_stock_from_erp")
        return res.get("data")

    def post(self, url: str, data=None, json=None, timeout=None):
        import json as js
        req_text = js.dumps(data if data is not None else json, ensure_ascii=False)[:128]
        self.logger.info(f"UPSELLER POST REQUEST {url} req_text: {req_text}.")
        res = self.session.post(
            url,
            data=data,
            json=json,
            timeout=timeout or self.default_timeout)
        self.logger.info(
            f"UPSELLER POST RESPONSE {url} http_code: {res.status_code} "
            f"res_text: {res.text[:1024]}")
        return res

    def post_form(self, url: str, data=None, timeout=None):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.logger.info(f"UPSELLER POST FORM REQUEST {url}.")
        res = self.session.post(
            url,
            data=data,
            headers=headers,
            timeout=timeout or self.default_timeout)
        self.logger.info(
            f"UPSELLER POST FORM RESPONSE {url} http_code: {res.status_code} "
            f"res_text: {res.text[:1024]}")
        return res

    def get(self, url: str, params=None, timeout=None):
        self.logger.info(f"UPSELLER GET REQUEST {url}")
        res = self.session.get(
            url,
            params=params,
            timeout=timeout or self.default_timeout)
        self.logger.info(
            f"UPSELLER GET RESPONSE {url} http_code: {res.status_code} "
            f"res_text: {res.text[:256]}")
        return res

    @staticmethod
    def _check_response(res: dict, action: str):
        if res.get("code") != 0:
            raise Exception(f"{action} failed: {json.dumps(res, ensure_ascii=False)}")

    @staticmethod
    def _extract_page(data):
        if data is None:
            return {
                "rows": [],
                "total_size": 0,
                "total_page": 1,
                "page_no": 1,
                "page_size": 0,
            }
        if isinstance(data, list):
            return {
                "rows": data,
                "total_size": len(data),
                "total_page": 1,
                "page_no": 1,
                "page_size": len(data),
            }
        rows = data.get("list") or data.get("rows") or data.get("records") or []
        page_no = data.get("pageNum") or data.get("pageNo") or data.get("current") or 1
        page_size = data.get("pageSize") or data.get("size") or len(rows)
        total_size = data.get("total") or data.get("totalSize") or len(rows)
        total_page = data.get("totalPage")
        if not total_page:
            total_page = max((total_size + page_size - 1) // page_size, 1) if page_size else 1
        return {
            "rows": rows,
            "total_size": total_size,
            "total_page": total_page,
            "page_no": page_no,
            "page_size": page_size,
        }
