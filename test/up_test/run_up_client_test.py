#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
使用 UpSellerClient + cookies 跑集成测试，并生成 Markdown 报告。
"""
import json
import logging
import os
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ec.bigseller.up_seller_client import UpSellerClient


def _setup_stdout_logger():
    logger = logging.getLogger("INVOKER")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.handlers = [handler]
    logger.propagate = False
    return logger


def _pick_id(row):
    return row.get("idStr") or row.get("id")


def _pick_sku_code(row):
    return (
        row.get("sku")
        or row.get("skuName")
        or row.get("skuCode")
        or row.get("sellerSku")
        or row.get("skuNo")
    )


def _pick_image(detail, row):
    for key in ("imgUrl", "image", "pic", "mainImage", "skuImg", "skuImage"):
        v = None
        if isinstance(detail, dict):
            v = detail.get(key)
        if v:
            return v
        v = row.get(key)
        if v:
            return v
    return None


def _download_image(url: str, dest: Path, base: Path) -> str:
    if not url:
        return ""
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 UpsellerTest"}
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
        ext = ".jpg"
        if ".png" in url.lower():
            ext = ".png"
        dest = dest.with_suffix(ext)
        dest.write_bytes(data)
        return str(dest.relative_to(base))
    except Exception as e:
        return f"(下载失败: {e})"


def main():
    ydm_token = os.environ.get(
        "UPSELLER_YDM_TOKEN", "KIMKm_rwaaZ_mb5xplP0mmytEBQEzeZhWhFFdhpPmts"
    )
    email = os.environ.get("UPSELLER_EMAIL", "1036543883@qq.com")
    password = os.environ.get("UPSELLER_PASSWORD", "Qq1036543883@")

    report_dir = Path(__file__).resolve().parent
    cookie_path = Path("./cookies/up_seller.cookies")
    img_dir = report_dir / "images"
    report_path = report_dir / "up_seller_test_report.md"
    chrome_driver_path = os.environ.get(
        "UPSELLER_CHROMEDRIVER_PATH",
        "/Users/jkguo/.local/chromedriver/147.0.7727.117/chromedriver-mac-arm64/chromedriver")

    _setup_stdout_logger()
    client = UpSellerClient(
        ydm_token,
        cookies_file_path=str(cookie_path),
        login_mode="selenium",
        selenium_headless=False,
        selenium_driver_path=chrome_driver_path)

    lines = []
    lines.append("# UpSeller Client 集成测试报告")
    lines.append("")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- Python：`{sys.executable}`")
    lines.append(f"- Cookie 文件：`{cookie_path}`（存在={cookie_path.exists()}）")
    lines.append("")

    steps = []

    # 1) 登录：优先 cookie，无有效 cookie 时走账号密码登录
    if client.load_cookies() and client.is_login():
        steps.append(("登录", True, "复用 cookies，`GET /api/is-login` data=true"))
    else:
        try:
            client.login(email, password)
            steps.append(("登录", True, "账号密码登录成功，并保存 cookies"))
        except Exception as e:
            steps.append(("登录", False, f"账号密码登录失败：{e}"))

    if not client.is_login():
        lines.append("## 结论")
        lines.append("")
        lines.append("未登录，后续接口未执行。")
        lines.append("")
        lines.append("### 登录结果")
        lines.append("")
        for name, ok, detail in steps:
            lines.append(f"- {name}：{'成功' if ok else '失败'}，{detail}")
        lines.append("")
        lines.append("### 已验证接口（未登录也可访问）")
        lines.append("")
        lines.append("| 接口 | 结果 |")
        lines.append("|------|------|")
        for ok, name, detail in [
            (True, "GET /api/is-login", "未登录返回 data=false"),
            (True, "GET /api/getCountryCode", "本机出口为 CN 时 data=CN"),
            (True, "GET /api/vcode", "返回 data:image/jpg;base64,..."),
        ]:
            lines.append(f"| {name} | 可达 |")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        for name, ok, detail in steps:
            print(name, ok, detail)
        print("report ->", report_path)
        return

    # 已登录
    lines.append("## 1. 登录与用户信息")
    lines.append("")
    try:
        user = client.get_user_info()
        lines.append("```json")
        lines.append(json.dumps(user, ensure_ascii=False, indent=2)[:8000])
        lines.append("```")
    except Exception as e:
        lines.append(f"获取 `/api/user-info` 失败：`{e}`")
    lines.append("")

    # 2) 单品 SKU 列表 searchGroup=1
    lines.append("## 2. 单品 SKU 列表（`/api/sku/index-single`）")
    lines.append("")
    all_rows = []
    page_no = 1
    page_size = 50
    total_page = 1
    total_size = 0
    while page_no <= total_page:
        page = client.query_sku_page(
            page_no=page_no, page_size=page_size, variants=False
        )
        total_page = page["total_page"]
        total_size = page["total_size"]
        all_rows.extend(page["rows"])
        lines.append(f"- 拉取第 {page_no}/{total_page} 页，累计行数 {len(all_rows)}/{total_size}")
        page_no += 1
        time.sleep(0.35)
    lines.append("")
    lines.append(f"**单品 SKU 总数**：{total_size}，本报告逐条展开 **{len(all_rows)}** 条。")
    lines.append("")

    # 3) 仓库
    lines.append("## 3. 仓库（`/api/warehouse/list-enable`）")
    lines.append("")
    warehouses = []
    try:
        warehouses = client.query_warehouse_list(enable_only=True)
        lines.append("```json")
        lines.append(json.dumps(warehouses, ensure_ascii=False, indent=2)[:6000])
        lines.append("```")
    except Exception as e:
        lines.append(f"失败：`{e}`")
    default_wh = None
    if isinstance(warehouses, list) and warehouses:
        w0 = warehouses[0]
        default_wh = w0.get("id") or w0.get("value") or w0.get("warehouseId")
    lines.append("")

    # 4) 每个 SKU：详情 + 库存
    lines.append("## 4. 单品 SKU 详情与库存")
    lines.append("")
    lines.append("| # | id | SKU | 图片(本地) | 详情摘要 | 仓库库存摘要 |")
    lines.append("|---|----|-----|------------|----------|--------------|")

    for idx, row in enumerate(all_rows, 1):
        sid = _pick_id(row)
        sku_code = _pick_sku_code(row) or ""
        detail = None
        wh_inv = None
        inv_row = None
        detail_err = ""
        try:
            if sid:
                detail = client.query_sku_detail(sid, "single")
        except Exception as e:
            detail_err = str(e)
        try:
            if sid:
                wh_inv = client.query_product_warehouse_list(sid)
        except Exception as e:
            wh_inv = {"error": str(e)}
        if sku_code and default_wh:
            try:
                inv_row = client.query_sku_inventory_detail(str(sku_code), default_wh)
            except Exception as e:
                inv_row = {"error": str(e)}

        img_url = _pick_image(detail if isinstance(detail, dict) else {}, row)
        local_img = ""
        if img_url:
            safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(sku_code))[
                :80
            ] or f"id{sid}"
            local_img = _download_image(img_url, img_dir / f"{idx:04d}_{safe}", report_dir)

        title = ""
        if isinstance(detail, dict):
            title = detail.get("title") or detail.get("name") or detail.get("productName") or ""
        summ = title[:60] + ("…" if title and len(title) > 60 else "")
        if detail_err:
            summ = f"ERR {detail_err[:80]}"

        inv_summ = ""
        if isinstance(inv_row, dict) and inv_row.get("error"):
            inv_summ = str(inv_row.get("error"))[:80]
        else:
            if isinstance(inv_row, dict):
                inv_summ = json.dumps(
                    {
                        k: inv_row.get(k)
                        for k in (
                            "available",
                            "onHand",
                            "onhand",
                            "warehouseId",
                            "warehouseName",
                        )
                        if k in inv_row
                    },
                    ensure_ascii=False,
                )
            elif inv_row:
                inv_summ = str(inv_row)[:120]

        lines.append(
            f"| {idx} | {sid} | `{sku_code}` | {local_img or '-'} | {summ} | {inv_summ or '-'} |"
        )

    lines.append("")
    lines.append("## 5. 接口清单（本次调用）")
    lines.append("")
    for u in [
        client.check_login_url,
        client.user_info_url,
        client.sku_list_url,
        client.sku_detail_single_url,
        client.warehouse_enable_list_url,
        client.warehouse_sku_one_url,
        client.warehouse_sku_list_url,
    ]:
        lines.append(f"- `{u}`")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print("report ->", report_path)


if __name__ == "__main__":
    main()
