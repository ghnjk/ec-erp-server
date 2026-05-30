#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: up_seller_selenium_cookie
@author: jkguo
@create: 2026/05/02

启动 Chrome 供人工登录 UpSeller，检测登录成功后保存 cookies。
"""
import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHROME_DRIVER_PATH = (
    "/Users/jkguo/.local/chromedriver/147.0.7727.117/"
    "chromedriver-mac-arm64/chromedriver"
)
DEFAULT_COOKIE_FILE = ROOT / "cookies" / "up_seller.cookies"
BASE_URL = "https://app.upseller.com"
LOGIN_URL = f"{BASE_URL}/zh-CN/login"
HOME_URL = f"{BASE_URL}/zh-CN/home"
CHECK_LOGIN_URL = f"{BASE_URL}/api/is-login"


def parse_args():
    parser = argparse.ArgumentParser(
        description="人工登录 UpSeller 并保存 cookies，供 UpSellerClient 后续复用。")
    parser.add_argument(
        "--driver-path",
        default=os.environ.get("UPSELLER_CHROMEDRIVER_PATH", DEFAULT_CHROME_DRIVER_PATH),
        help="ChromeDriver 可执行文件路径。")
    parser.add_argument(
        "--cookie-file",
        default=os.environ.get("UPSELLER_COOKIE_FILE", str(DEFAULT_COOKIE_FILE)),
        help="保存 cookies 的 JSON 文件路径。")
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("UPSELLER_LOGIN_TIMEOUT", "300")),
        help="等待人工登录成功的最长秒数。")
    parser.add_argument(
        "--chrome-binary",
        default=os.environ.get("UPSELLER_CHROME_BINARY"),
        help="Chrome 可执行文件路径，默认使用系统 Chrome。")
    return parser.parse_args()


def build_driver(driver_path: str, chrome_binary: str = None):
    options = Options()
    if chrome_binary:
        options.binary_location = chrome_binary
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    service = Service(executable_path=driver_path)
    return webdriver.Chrome(service=service, options=options)


def browser_is_login_success(driver) -> bool:
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


def driver_cookies_to_dict(driver) -> dict:
    return {
        cookie["name"]: cookie["value"]
        for cookie in driver.get_cookies()
        if cookie.get("name") and cookie.get("value") is not None
    }


def check_login_by_requests(cookies: dict) -> bool:
    session = requests.Session()
    session.cookies.update(cookies)
    response = session.get(CHECK_LOGIN_URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("code") == 0 and bool(data.get("data"))


def save_cookies(cookie_file: Path, cookies: dict):
    cookie_file.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
            mode="w",
            dir=str(cookie_file.parent),
            delete=False,
            suffix=".tmp",
            prefix=".upseller_cookies") as tmp_file:
        tmp_file_path = tmp_file.name
        json.dump(cookies, tmp_file, indent=2)
    try:
        os.replace(tmp_file_path, cookie_file)
    except Exception:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        raise


def main():
    args = parse_args()
    cookie_file = Path(args.cookie_file).expanduser().resolve()

    if not os.path.isfile(args.driver_path):
        raise FileNotFoundError(f"ChromeDriver 不存在: {args.driver_path}")

    print(f"ChromeDriver: {args.driver_path}")
    print(f"Cookie 文件: {cookie_file}")
    print(f"请在打开的 Chrome 中人工登录 UpSeller，脚本会在 {args.timeout} 秒内自动检测登录状态。")

    driver = build_driver(args.driver_path, args.chrome_binary)
    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, args.timeout)
        try:
            wait.until(browser_is_login_success)
        except TimeoutException as e:
            raise TimeoutException(
                f"等待 UpSeller 登录超时，请确认是否已在 {args.timeout} 秒内完成登录。"
            ) from e

        time.sleep(1)
        driver.get(HOME_URL)
        cookies = driver_cookies_to_dict(driver)
        if not cookies:
            raise Exception("浏览器中未获取到 UpSeller cookies。")
        if not check_login_by_requests(cookies):
            raise Exception("已获取 cookies，但 requests 校验 /api/is-login 未通过。")

        save_cookies(cookie_file, cookies)
        print(f"登录成功，已保存 {len(cookies)} 个 cookies 到: {cookie_file}")
    finally:
        driver.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"保存 UpSeller cookies 失败: {e}", file=sys.stderr)
        sys.exit(1)
