#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: up_seller_cookie
@author: jkguo
@create: 2026/07/12

Linux 可用的 UpSeller 自动登录脚本：不依赖 Chrome / Selenium。
流程：
1. 优先复用已有 cookies；
2. 图片验证码走云码 YdmVerify；
3. CN 出口：Node.js + jsdom 获取腾讯云 TencentCaptcha ticket；
4. 非 CN：云码 funnel type=40012 获取 Cloudflare Turnstile token；
5. 若风控 score<0.7，自动发送邮箱验证码，再走 /api/login-recaptcha。
"""
import argparse
import logging
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ec.bigseller.up_seller_client import UpSellerClient


DEFAULT_COOKIE_FILE = ROOT / "cookies" / "up_seller.cookies"
DEFAULT_TENCENT_SCRIPT = ROOT / "tools" / "upseller_tencent_captcha.js"


def parse_args():
    parser = argparse.ArgumentParser(
        description="自动登录 UpSeller 并保存 cookies（纯 HTTP，不依赖 Chrome/Selenium）。")
    parser.add_argument(
        "--email",
        default=os.environ.get("UPSELLER_EMAIL"),
        help="UpSeller 登录邮箱。")
    parser.add_argument(
        "--password",
        default=os.environ.get("UPSELLER_PASSWORD"),
        help="UpSeller 登录密码。")
    parser.add_argument(
        "--ydm-token",
        default=os.environ.get("UPSELLER_YDM_TOKEN") or os.environ.get("YDM_TOKEN"),
        help="云码 ydm_token。")
    parser.add_argument(
        "--cookie-file",
        default=os.environ.get("UPSELLER_COOKIE_FILE", str(DEFAULT_COOKIE_FILE)),
        help="保存 cookies 的 JSON 文件路径。")
    parser.add_argument(
        "--email-code",
        default=os.environ.get("UPSELLER_EMAIL_CODE"),
        help="风控二次校验邮箱验证码；首次触发时可不传，脚本会先发码。")
    parser.add_argument(
        "--node-bin",
        default=os.environ.get("UPSELLER_NODE_BIN", "node"),
        help="Node.js 可执行文件，用于腾讯验证码 jsdom 脚本。")
    parser.add_argument(
        "--tencent-script",
        default=os.environ.get(
            "UPSELLER_TENCENT_SCRIPT", str(DEFAULT_TENCENT_SCRIPT)),
        help="腾讯验证码 Node 脚本路径。")
    parser.add_argument(
        "--force",
        action="store_true",
        help="忽略已有有效 cookies，强制重新登录。")
    parser.add_argument(
        "--prompt-email-code",
        action="store_true",
        help="需要邮箱验证码时从终端交互输入。")
    return parser.parse_args()


def _setup_logger():
    logger = logging.getLogger("INVOKER")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.handlers = [handler]
    logger.propagate = False
    return logger


def main():
    args = parse_args()
    if not args.email or not args.password:
        raise SystemExit("缺少 --email / --password（或环境变量 UPSELLER_EMAIL / UPSELLER_PASSWORD）")
    if not args.ydm_token:
        raise SystemExit("缺少 --ydm-token（或环境变量 UPSELLER_YDM_TOKEN / YDM_TOKEN）")

    cookie_file = Path(args.cookie_file).expanduser().resolve()
    _setup_logger()
    client = UpSellerClient(
        args.ydm_token,
        cookies_file_path=str(cookie_file),
        login_mode="api",
        email_verify_code=args.email_code,
        tencent_captcha_script=args.tencent_script,
        node_bin=args.node_bin)

    print(f"Cookie 文件: {cookie_file}")
    print(f"登录账号: {args.email}")
    print(f"Tencent 脚本: {args.tencent_script}")

    if not args.force and client.load_cookies() and client.is_login():
        print("已有有效 cookies，无需重新登录。")
        return

    try:
        client.login(args.email, args.password, remember=True, force=args.force)
    except Exception as e:
        msg = str(e)
        if "email verification code" not in msg:
            raise
        if not args.prompt_email_code and not args.email_code:
            print(msg)
            print("请查收邮箱验证码后执行：")
            print(
                f"  {sys.executable} {Path(__file__).name} "
                f"--email '{args.email}' --password '***' "
                f"--ydm-token '***' --email-code <CODE>")
            raise SystemExit(2)
        code = args.email_code
        if not code and args.prompt_email_code:
            code = input("请输入邮箱验证码: ").strip()
        if not code:
            raise SystemExit("未提供邮箱验证码")
        # 发码已在异常路径中完成；这里只提交 login-recaptcha。
        client.login_with_email_code(
            email=args.email,
            password=args.password,
            verify_code=code,
            remember=True,
            auth_type=1)

    if not client.is_login():
        raise SystemExit("登录后 is_login=false")
    print(f"登录成功，cookies 已保存到: {cookie_file}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"保存 UpSeller cookies 失败: {e}", file=sys.stderr)
        sys.exit(1)
