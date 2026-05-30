# Tasks：support-upseller-sku-sync

## 1. SellerClient 抽象层补齐 `refresh_local_sku_cache`

- [x] 1.1 在 `ec/seller_client.py:SellerClient` 协议中新增方法签名 `refresh_local_sku_cache(self) -> None`，并补充 docstring 说明：从上游 ERP 全量拉取 SKU 写入本地缓存（BigSeller → `cookies/all_sku.json`、UpSeller → `cookies/all_up_seller_sku.json`）
- [x] 1.2 在 `ec/big_seller_adapter.py:BigSellerAdapter` 中实现 `refresh_local_sku_cache`：单行调用 `self._sku_manager.load_and_update_all_sku(self._client)`，等价于 `auto_sync_tools/sync_all_sku.py` 旧逻辑
- [x] 1.3 在 `ec/up_seller_adapter.py:UpSellerAdapter` 中实现 `refresh_local_sku_cache`：单行调用 `self._sku_manager.load_and_update_all_sku(self._client)`（`UpSellerSkuManager.load_and_update_all_sku` 已存在，无需新增）
- [x] 1.4 用 `python3 -m py_compile ec/seller_client.py ec/big_seller_adapter.py ec/up_seller_adapter.py` 静态校验三文件语法正确

## 2. 重写 `auto_sync_tools/sync_all_sku.py`

- [x] 2.1 移除 `from ec_erp_api.common.big_seller_util import build_big_seller_client, build_sku_manager` import
- [x] 2.2 改为 `from ec_erp_api.common.seller_util import build_seller_client`
- [x] 2.3 `sync_all_sku()` 函数体改为单行：`build_seller_client().refresh_local_sku_cache()`
- [x] 2.4 保留 `if __name__ == '__main__': sync_all_sku()` 入口与 `sys.path.append("..")` 头部样板
- [x] 2.5 `python3 -m py_compile auto_sync_tools/sync_all_sku.py` 静态校验通过

## 3. 重写 `auto_sync_tools/sync_sku_inventory.py`

- [x] 3.1 import 改造：
  - 移除 `from ec_erp_api.common.big_seller_util import build_big_seller_client, build_backend, MysqlBackend`
  - 改为：
    - `from ec_erp_api.common.big_seller_util import build_backend, MysqlBackend`（仅保留 backend 工厂）
    - `from ec_erp_api.common.seller_util import build_seller_client`
  - 顶部其他 import（time / datetime / sys / typing）保持不变
- [x] 3.2 删除模块级 `get_real_inventory(client, warehouse_id, sku_id)` 函数（其逻辑已被 `BigSellerAdapter.query_sku_detail` 内化为 `inventory_in_warehouse`）
- [x] 3.3 重写 `sync_sku_inventory()`：
  - 删除 `client = build_big_seller_client()`，改为 `seller = build_seller_client()`
  - 删除 `warehouse_id = config["big_seller_warehouse_id"]`（不再使用）
  - 主循环每条 SKU：
    ```
    sku_detail = seller.query_sku_detail(sku_info.sku)
    inv_detail = seller.query_sku_inventory_detail(sku_info.sku)
    sku_info.inventory          = sku_detail.inventory_in_warehouse
    sku_info.erp_sku_id         = sku_detail.erp_sku_id
    sku_info.erp_sku_name       = sku_detail.title or inv_detail.title
    sku_info.erp_sku_image_url  = sku_detail.image_url or inv_detail.image_url
    if inv_detail.avg_daily_sales > 0:
        sku_info.avg_sell_quantity = round(inv_detail.avg_daily_sales * 1.1, 2)
    # else: 不覆盖 sku_info.avg_sell_quantity，保留数据库已有值
    if sku_info.avg_sell_quantity and sku_info.avg_sell_quantity > 0.01:
        sku_info.inventory_support_days = int(sku_info.inventory / sku_info.avg_sell_quantity)
    else:
        sku_info.inventory_support_days = sku_info.inventory / 0.01
    sku_info.shipping_stock_quantity = shipping_sku_map.get(sku_info.sku, 0)
    backend.store_sku(sku_info)
    time.sleep(0.3)
    ```
- [x] 3.4 单条 SKU 异常 SHALL `print` 报错并 `continue`：用 `try / except Exception as e: print(f"sync sku {sku_info.sku} fail: {e}"); continue` 包住单条循环体
- [x] 3.5 在函数顶部注释更新为：
  - "同步策略：仅显式更新 inventory / erp_sku_* / inventory_support_days / shipping_stock_quantity；
     当上游 ERP 提供 avg_daily_sales > 0 时同步 avg_sell_quantity；为 0（典型 UpSeller 路径）则保留数据库历史值。
     sku_pack_length / sku_pack_width / sku_pack_height 等手工维护字段保留旧值"
- [x] 3.6 `python3 -m py_compile auto_sync_tools/sync_sku_inventory.py` 静态校验通过
- [x] 3.7 `grep -nE "big_seller_util|build_big_seller_client|build_sku_manager|big_seller_warehouse_id|warehouseVoList|avgDailySales" auto_sync_tools/sync_all_sku.py auto_sync_tools/sync_sku_inventory.py` 应该只剩下 `from ec_erp_api.common.big_seller_util import build_backend, MysqlBackend` 这一行（来自 sync_sku_inventory.py 的 backend 工厂保留）

## 4. 文档与 spec 同步

- [x] 4.1 更新 `openspec/specs/auto_sync_tools_spec.md`：
  - "脚本清单"表中 `sync_all_sku.py` / `sync_sku_inventory.py` 的"主要用途"列：把 BigSeller 字样改为"通过统一 SellerClient（BigSeller / UpSeller）"
  - 第 3 节 "sync_all_sku.py"：把流程代码块替换为 `build_seller_client().refresh_local_sku_cache()`，新增一行说明"BigSeller 路径写入 `cookies/all_sku.json`，UpSeller 路径写入 `cookies/all_up_seller_sku.json`"
  - 第 6 节 "sync_sku_inventory.py"：流程小节替换 `build_big_seller_client()` 为 `build_seller_client()`，删除 `query_sku_inventory_detail + query_sku_detail` 字段引用，描述按 `SkuDetail` / `InventoryDetail` 抽象表达；新增 "UpSeller 时 `avg_daily_sales=0`，保留 DB 已有 `avg_sell_quantity`" 的兜底说明
  - "常见问题"表新增一行：`UpSeller cookie 失效 → 由 build_seller_client 单例触发 selenium 登录（首次需在测试机预热）`
- [x] 4.2 在 `openspec/specs/bigseller_integration_spec.md` 第 "工厂方法（big_seller_util）" 表后追加一行说明："`build_big_seller_client` / `build_sku_manager` 仍服务于 `sync_order_to_es.py` / `sync_shop_statics_to_es.py` / `auto_preload_order.py` / `auto_return_refund_order_to_warehouse.py`；自动化 SKU/库存同步链路（`sync_all_sku.py` / `sync_sku_inventory.py`）已迁移至 `seller_util.build_seller_client()`，详见 [auto_sync_tools_spec.md](./auto_sync_tools_spec.md)。"
- [x] 4.3 review `openspec/specs/supplier_module_spec.md`：本变更不影响接口；如该文件中 "与 BigSeller 的交互" 小节涉及"自动化任务"描述，仅作 review，不改文字

## 5. 静态校验

- [x] 5.1 `python3 -c "import ast; ast.parse(open('auto_sync_tools/sync_all_sku.py').read()); ast.parse(open('auto_sync_tools/sync_sku_inventory.py').read()); ast.parse(open('ec/seller_client.py').read()); ast.parse(open('ec/big_seller_adapter.py').read()); ast.parse(open('ec/up_seller_adapter.py').read())"` 全部通过
- [x] 5.2 `grep -n "load_and_update_all_sku" ec/big_seller_adapter.py ec/up_seller_adapter.py` 在两个 adapter 的 `refresh_local_sku_cache` 中均能命中
- [x] 5.3 `grep -n "from ec_erp_api.common.seller_util" auto_sync_tools/sync_all_sku.py auto_sync_tools/sync_sku_inventory.py` 两处均命中
- [x] 5.4 `grep -n "from ec_erp_api.common.big_seller_util" auto_sync_tools/sync_all_sku.py` 应为空；`auto_sync_tools/sync_sku_inventory.py` 应仅命中 `import build_backend, MysqlBackend` 一行

## 6. 运行时回归（需运行环境）

- [ ] 6.1 BigSeller 项目国家库（如 philipine）：单跑 `python sync_all_sku.py`，对比改造前后 `cookies/all_sku.json` 行数与文件大小，差异 < 5%
- [ ] 6.2 BigSeller 项目国家库：单跑 `python sync_sku_inventory.py`，抽样 3 个 SKU 在 `t_sku_info` 中 `inventory / erp_sku_name / erp_sku_image_url / avg_sell_quantity / inventory_support_days / shipping_stock_quantity` 与改造前一致
- [ ] 6.3 UpSeller 项目国家库（如 thailand 等）：先在测试机手工执行 `python sync_all_sku.py` 完成 selenium 登录与 cookie 落地，确认 `cookies/all_up_seller_sku.json` 写入
- [ ] 6.4 UpSeller 项目国家库：单跑 `python sync_sku_inventory.py`，抽样 3 个 SKU 验证：
  - `inventory` 与 UpSeller 仓库 `available` 一致
  - `erp_sku_name` / `erp_sku_image_url` 非空
  - `avg_sell_quantity` 与同步前一致（不被覆盖为 0）
  - `inventory_support_days` 已重算
- [ ] 6.5 BigSeller / UpSeller 双侧执行 `SELECT sku, Fsku_pack_length, Fsku_pack_width, Fsku_pack_height FROM t_sku_info LIMIT 5` 抽查，确认 `add-sku-pack-volume` 已有约束未被破坏（体积字段未被清零）

## 7. 上线 / 跟进

- [ ] 7.1 PR review：openspec spec/design/tasks 一致；`grep` 校验项全过；BigSeller 项目灰度抽查无异常
- [ ] 7.2 crontab 不变更（仍是 `python sync_all_sku.py` / `python sync_sku_inventory.py`）；为 UpSeller 项目国家库新增首次 cookie 预热的运维 SOP（写入 `docs/operations/` 或团队 wiki，本变更外）
- [ ] 7.3 创建 follow-up issue：跟进"UpSeller 销量均量接口探测 + 真实 avg 同步"，预计 1 个月内闭环；本提案的 D3 兜底策略仅为过渡
