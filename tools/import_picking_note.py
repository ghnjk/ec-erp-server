#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: import_picking_note
@author: jkguo
@create: 2024/5/23
"""
import sys

import pandas as pd

sys.path.append("..")
from ec_erp_api.models.mysql_backend import MysqlBackend, SkuPickingNote
from ec_erp_api.app_config import get_app_config


def import_picking_notes():
    """从Excel导入SKU拣货备注数据"""
    config = get_app_config()
    db_config = config["db_config"]
    project_id = config["sync_tool_project_id"]
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python import_picking_note.py <excel文件路径>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    backend = MysqlBackend(
        project_id, db_config["host"], db_config["port"], db_config["user"], db_config["password"],
        db_config.get("db_name", "ec_erp_db")
    )
    
    # 读取Excel文件
    df = pd.read_excel(excel_path, sheet_name="pick_note")
    
    # 获取现有的拣货备注记录
    _, existing_notes = backend.search_sku_picking_note(0, 1000)
    existing_skus = {note.sku: note for note in existing_notes}
    
    # 导入数据
    imported_count = 0
    updated_count = 0
    
    for idx, row in df.iterrows():
        sku = row["sku"]
        picking_unit = float(row["1拣货单位=多少sku?"])
        picking_unit_name = row["拣货单位名"]
        picking_sku_name = row["拣货SKU名"]
        
        # 处理包装模式相关字段
        support_pkg_picking = bool(row.get("是否支持PKG打包") == "是")
        pkg_picking_unit = float(row.get("1 PKG=多少SKU", 0.0))
        pkg_picking_unit_name = row.get("PKG打包单位名", "")
        
        # 创建或更新记录
        note = SkuPickingNote(
            project_id=project_id,
            sku=sku,
            picking_unit=picking_unit,
            picking_unit_name=picking_unit_name,
            support_pkg_picking=support_pkg_picking,
            pkg_picking_unit=pkg_picking_unit,
            pkg_picking_unit_name=pkg_picking_unit_name,
            picking_sku_name=picking_sku_name
        )
        
        if sku in existing_skus:
            updated_count += 1
        else:
            imported_count += 1
            
        backend.store_sku_picking_note(note)
    
    print(f"导入完成！新增记录：{imported_count}，更新记录：{updated_count}")


if __name__ == '__main__':
    import_picking_notes()
