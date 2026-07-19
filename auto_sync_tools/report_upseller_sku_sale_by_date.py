#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: report_upseller_sku_sale_by_date
@author: jkguo
@create: 2026/07/19

按指定自然日生成 UpSeller 单一 SKU 销售数量 CSV 报告。
"""
import argparse
import csv
import datetime
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ec.bigseller.up_seller_client import UpSellerClient
from ec.up_seller_sales_manager import UpSellerSalesManager
from ec.upseller_sku_manager import UpSellerSkuManager
from ec_erp_api.app_config import get_app_config


def parse_sale_date(value: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as e:
        raise argparse.ArgumentTypeError("日期格式必须为 YYYY-MM-DD") from e


def build_report_rows(
        sale_date: datetime.date,
        daily_sales: dict,
        sku_manager: UpSellerSkuManager):
    rows = []
    for sku_code, quantity in daily_sales.items():
        sku_info = sku_manager.sku_map.get(sku_code) or {}
        rows.append({
            "date": sale_date.strftime("%Y-%m-%d"),
            "sku": sku_code,
            "sku_name": sku_info.get("title") or "",
            "sale_quantity": int(quantity),
        })
    rows.sort(key=lambda row: (-row["sale_quantity"], row["sku"]))
    return rows


def write_csv_atomic(output_path: str, fieldnames, rows):
    output_path = os.path.abspath(output_path)
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            newline="",
            dir=output_dir,
            delete=False,
            suffix=".tmp",
            prefix=".upseller_sale_report_") as tmp_file:
        tmp_path = tmp_file.name
        writer = csv.DictWriter(tmp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    try:
        os.replace(tmp_path, output_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
    return output_path


def build_sales_manager(cookies_dir: str):
    config = get_app_config()
    cookie_file = os.path.join(cookies_dir, "up_seller.cookies")
    sku_file = os.path.join(cookies_dir, "all_up_seller_sku.json")
    client = UpSellerClient(
        config.get("ydm_token", ""),
        cookies_file_path=cookie_file,
        login_mode="api",
    )
    if not client.load_cookies() or not client.is_login():
        raise RuntimeError(
            f"UpSeller Cookie 无效，请先更新登录态: {cookie_file}")
    sku_manager = UpSellerSkuManager(local_db_path=sku_file)
    sku_manager.load()
    if not sku_manager.sku_map:
        raise RuntimeError(
            f"UpSeller SKU 缓存为空，请先执行 sync_all_sku.py: {sku_file}")
    sales_manager = UpSellerSalesManager(
        client=client,
        sku_manager=sku_manager,
        cache_dir=os.path.join(cookies_dir, "up_seller_sales"),
    )
    return sales_manager, sku_manager


def generate_report(
        sale_date: datetime.date,
        cookies_dir: str,
        output_path: str):
    sales_manager, sku_manager = build_sales_manager(cookies_dir)
    raw_rows = sales_manager.load_daily_rows(sale_date)
    daily_sales, unmatched = sales_manager.aggregate_daily_sales(raw_rows)
    report_rows = build_report_rows(sale_date, daily_sales, sku_manager)
    report_path = write_csv_atomic(
        output_path,
        ["date", "sku", "sku_name", "sale_quantity"],
        report_rows)

    unmatched_path = None
    if unmatched:
        stem, ext = os.path.splitext(report_path)
        unmatched_path = write_csv_atomic(
            stem + "_unmatched" + (ext or ".csv"),
            ["variationSku", "variationId", "shopId", "reason"],
            unmatched)
    return {
        "report_path": report_path,
        "unmatched_path": unmatched_path,
        "variation_count": len(raw_rows),
        "platform_sale_quantity": sum(
            int(row.get("productSales") or 0) for row in raw_rows),
        "single_sku_count": len(report_rows),
        "single_sku_sale_quantity": sum(
            row["sale_quantity"] for row in report_rows),
        "unmatched_count": len(unmatched),
    }


def parse_args():
    config = get_app_config()
    default_cookies_dir = config.get("cookies_dir", str(ROOT / "cookies"))
    parser = argparse.ArgumentParser(
        description="生成指定日期的 UpSeller 单一 SKU 销售数量报告")
    parser.add_argument(
        "date",
        type=parse_sale_date,
        help="销售日期，格式 YYYY-MM-DD")
    parser.add_argument(
        "--cookies-dir",
        default=default_cookies_dir,
        help="Cookie 与 SKU 缓存目录")
    parser.add_argument(
        "--output",
        help="报告 CSV 路径；默认写入 data/report/")
    return parser.parse_args()


def main():
    args = parse_args()
    output_path = args.output or str(
        ROOT / "data" / "report" /
        f"upseller_sku_sale_{args.date.strftime('%Y-%m-%d')}.csv")
    result = generate_report(
        sale_date=args.date,
        cookies_dir=os.path.abspath(args.cookies_dir),
        output_path=output_path)
    print(f"report: {result['report_path']}")
    print(
        f"variation_count: {result['variation_count']}, "
        f"platform_sale_quantity: {result['platform_sale_quantity']}")
    print(
        f"single_sku_count: {result['single_sku_count']}, "
        f"single_sku_sale_quantity: {result['single_sku_sale_quantity']}")
    print(f"unmatched_count: {result['unmatched_count']}")
    if result["unmatched_path"]:
        print(f"unmatched_report: {result['unmatched_path']}")


if __name__ == "__main__":
    main()
