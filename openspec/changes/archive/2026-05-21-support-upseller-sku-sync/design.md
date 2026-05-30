# 设计：自动同步任务接入统一 SellerClient

## Context

`apis/supplier.py` 已通过 `ec_erp_api/common/seller_util.py:build_seller_client()` 接入 `ec/seller_client.py:SellerClient` 抽象（`BigSellerAdapter` / `UpSellerAdapter`），按 `application.json` 的 `use_up_seller` 自动路由 ERP，且：

- 单例缓存 + 5 分钟登录续期；
- 字段映射统一为 ERP 内部语义（`SkuDetail` / `InventoryDetail` / `StockMoveItem` / `StockResult`）；
- 仓库 ID 统一通过 `get_seller_warehouse_id()` 获取。

而 `auto_sync_tools/` 下的两个脚本仍走老路径：

```python
# auto_sync_tools/sync_all_sku.py（现状）
from ec_erp_api.common.big_seller_util import build_big_seller_client, build_sku_manager
sku_manager = build_sku_manager()
sku_manager.load_and_update_all_sku(build_big_seller_client())

# auto_sync_tools/sync_sku_inventory.py（现状）
from ec_erp_api.common.big_seller_util import build_big_seller_client, build_backend, MysqlBackend
client = build_big_seller_client()
warehouse_id = config["big_seller_warehouse_id"]
detail = client.query_sku_inventory_detail(sku_info.sku, warehouse_id)
inventory = get_real_inventory(client, warehouse_id, sku_info.erp_sku_id)  # 自己访问 warehouseVoList
sku_info.avg_sell_quantity = round(detail["avgDailySales"] * 1.1, 2)
```

约束：

- 与 `apis/supplier.py` 保持同源；不允许在脚本里再写一份"判断 use_up_seller"分支；
- 不破坏 BigSeller 项目的现网行为（同步结果与字段值在等价口径上一致）；
- UpSeller 项目首跑不能因字段缺失（`avgDailySales` 没有等）而抛异常；
- 脚本仍使用 `print` 日志（与 `auto_sync_tools_spec.md` 第 6 节"日志规范（建议）"保持兼容，本次不改造日志体系）。

参考：

- `ec_erp_api/common/seller_util.py`
- `ec_erp_api/common/big_seller_util.py`（继续保留以服务 sync_order_to_es / sync_shop_statics_to_es / auto_preload_order / auto_return_refund_order_to_warehouse 等还未 UpSeller 化的脚本）
- `ec/seller_client.py`、`ec/big_seller_adapter.py`、`ec/up_seller_adapter.py`
- `ec/sku_manager.py`、`ec/upseller_sku_manager.py`

## Goals / Non-Goals

**Goals**

- `sync_all_sku.py` / `sync_sku_inventory.py` 在 BigSeller / UpSeller 两类 project 下使用同一份代码、同一条 crontab 都能正确执行；
- 与 `apis/supplier.py` 共享 `build_seller_client()` 单例（同进程）/ 同样的字段映射与登录续期策略；
- 同步结果在 BigSeller 项目上与改造前等价（inventory / erp_sku_name / erp_sku_image_url / avg_sell_quantity / inventory_support_days / shipping_stock_quantity）；
- UpSeller 项目首跑：可成功完成 SKU 主数据与库存同步，且不破坏数据库已有人工维护字段（如 sku_pack_*、avg_sell_quantity 历史值见 D3）。

**Non-Goals**

- 不重构定时任务的日志/调度框架（仍 print + crontab）；
- 不为 UpSeller 补充 `avgDailySales` 接口探测（UpSeller 当前未暴露该字段，本设计按 0 处理）；
- 不改造 `sync_order_to_es.py` / `sync_shop_statics_to_es.py` / `auto_preload_order.py` / `auto_return_refund_order_to_warehouse.py`，它们的 UpSeller 化属于后续提案；
- 不修改 BigSeller 单例缓存逻辑、Cookie 路径策略；
- 不调整 `t_sku_info` schema 与 ORM。

## Decisions

### D1：在 `SellerClient` 协议上新增 `refresh_local_sku_cache()` 方法

**决定**：在 `ec/seller_client.py:SellerClient` 协议上新增一个最小方法签名：

```python
def refresh_local_sku_cache(self) -> None:
    """从上游 ERP 全量拉取 SKU 列表并写入本地缓存（cookies/all_sku.json 等）。"""
```

`BigSellerAdapter` 实现：调用现有 `self._sku_manager.load_and_update_all_sku(self._client)`；
`UpSellerAdapter` 实现：调用现有 `self._sku_manager.load_and_update_all_sku(self._client)`（`UpSellerSkuManager` 已支持）。

`auto_sync_tools/sync_all_sku.py` 改为：

```python
from ec_erp_api.common.seller_util import build_seller_client
build_seller_client().refresh_local_sku_cache()
```

**替代方案**：

1. 让脚本自己 `if use_up_seller: ... else: ...` 分支构造 `BigSellerAdapter._sku_manager` —— 复制 `seller_util` 的判断，违反 DRY；
2. 在 `seller_util` 暴露 `build_sku_manager_for_current_seller()` 单独工厂 —— 多一层而无业务价值；
3. 把 `sku_manager` 作为 `SellerClient` 公开属性 —— 暴露过多内部状态。

**理由**：

- `SellerClient` 协议本就负责"屏蔽 BigSeller / UpSeller 在 SKU 操作上的差异"，"刷新本地 SKU 缓存"是它天然的职责；
- 实现是单行 delegate，工程成本低；
- 让脚本可以保持极简（一行调用），且后续如果 ERP 切换更多平台，只需在 adapter 加实现。

### D2：所有 SKU/库存查询统一走 `SkuDetail` / `InventoryDetail`

**决定**：`sync_sku_inventory.py` 不再访问 BigSeller 原生字段，使用：

```python
sku_detail = seller.query_sku_detail(sku_info.sku)         # SkuDetail
inv_detail = seller.query_sku_inventory_detail(sku_info.sku) # InventoryDetail

sku_info.inventory          = sku_detail.inventory_in_warehouse
sku_info.erp_sku_id         = sku_detail.erp_sku_id
sku_info.erp_sku_name       = sku_detail.title or inv_detail.title
sku_info.erp_sku_image_url  = sku_detail.image_url or inv_detail.image_url
```

并删除脚本中 `get_real_inventory` 函数（其逻辑已被 `BigSellerAdapter.query_sku_detail` 内化为 `inventory_in_warehouse` 计算）。

**替代方案**：保留 `get_real_inventory` —— 逻辑会在 BigSeller 与 UpSeller 出现两份各自访问原生字段的实现，重复且易腐化。

**理由**：消灭重复，所有字段差异处理收口在 adapter 层。

### D3：UpSeller 缺失 `avg_daily_sales` 时的兜底策略

**背景**：UpSeller `/api/warehouse-sku/list` 接口未返回 `avgDailySales`，`UpSellerAdapter.query_sku_inventory_detail` 固定返回 `avg_daily_sales=0.0`（见 `ec/up_seller_adapter.py` 注释）。

老脚本逻辑：

```python
sku_info.avg_sell_quantity = round(detail["avgDailySales"] * 1.1, 2)  # 一定写入
if sku_info.avg_sell_quantity > 0.01:
    sku_info.inventory_support_days = int(sku_info.inventory / sku_info.avg_sell_quantity)
else:
    sku_info.inventory_support_days = sku_info.inventory / 0.01
```

**决定**：

- BigSeller 项目（`avg_daily_sales > 0` 或 ERP 真实返回）：行为完全保持不变（按 `avg_daily_sales * 1.1` 落库，再算 `inventory_support_days`）；
- UpSeller 项目（`avg_daily_sales == 0` 且 ERP 不暴露该字段）：**保留 `sku_info.avg_sell_quantity` 数据库已有值，不再覆盖为 0**，`inventory_support_days` 在保留的 avg 基础上重算：
  - 若数据库已有 `avg_sell_quantity > 0.01`：`inventory_support_days = int(inventory / avg_sell_quantity)`；
  - 否则按"无销量"兜底分支：`inventory_support_days = inventory / 0.01`（与 BigSeller 老分支等价）。

实现上：UpSeller 路径下不向 `sku_info.avg_sell_quantity` 赋值，仅赋 `inventory_support_days`。

**替代方案**：

1. 直接写 0 → 抹掉运营人工维护的 avg 数据；
2. 让 UpSeller 自己提供一个 sales 估算接口 → 超出本变更范围（独立提案）；
3. 用本地 ES 销售估算 `t_sku_sale_estimate` 重算 → `sync_order_to_es.py` 还没 UpSeller 化，引入跨脚本依赖且数据未必齐全。

**理由**：以"不破坏现存数据"为优先级，等待后续 UpSeller 销量接口接入或 ES 数据齐全再补完整逻辑。

判定 ERP 类型仅在脚本内部用 `inv_detail.avg_daily_sales > 0` 做隐式判定（BigSeller 也可能返回 0；这种情况下两个 ERP 行为一致——都不破坏已有 avg），**无需读 `use_up_seller` 配置**。

### D4：仓库 ID 统一通过 `get_seller_warehouse_id()` 取

**决定**：脚本中删除 `warehouse_id = config["big_seller_warehouse_id"]`，改为：

```python
from ec_erp_api.common.seller_util import get_seller_warehouse_id
warehouse_id = get_seller_warehouse_id()  # 仅用于日志打印；同步本身不需要
```

事实上由于 `query_sku_detail` / `query_sku_inventory_detail` 内部已经使用 adapter 持有的 `_warehouse_id`，脚本本身可以**完全移除 `warehouse_id` 局部变量**。本设计选择**移除**该局部变量（D2 已删 `get_real_inventory`），保持调用面最小化。

**理由**：仓库 ID 是 adapter 的内部状态，脚本不需要关心。

### D5：保留 `sync_tool_project_id` 与 `build_backend` 的 BigSeller 路径

**决定**：`sync_sku_inventory.py` 继续从 `application.json` 读 `sync_tool_project_id` 用于初始化 `MysqlBackend`，`build_backend` 仍来自 `ec_erp_api.common.big_seller_util`（与 `seller_util.build_seller_client` 解耦——`build_backend` 与 ERP 无关，仅是数据库后端工厂）。

**替代方案**：把 `build_backend` 搬到 `seller_util` 或 `mysql_backend_util` —— 不属于本变更范畴（属于"工厂归位"重构），单独提案。

**理由**：限定本变更影响面；BigSeller / UpSeller 双 ERP 与 MySQL 后端工厂正交。

### D6：本地缓存路径在两个 ERP 下分别落盘

**事实**（已由 `seller_util` 实现）：

- BigSeller → `cookies/all_sku.json` + `cookies/all_variant_sku_mapping.json`（`SkuManager`）
- UpSeller → `cookies/all_up_seller_sku.json`（`UpSellerSkuManager`）

`sync_all_sku.py` 改造后无需关心路径——`refresh_local_sku_cache()` 内部委托 sku_manager；运维注意：如果同一台机器上跨 project 跑（理论上不会，但需在 spec 注释里写明），需要 `cookies_dir` 隔离。

### D7：`ec_erp_api.common.big_seller_util` 暂不删除

**决定**：

- `build_big_seller_client()` / `build_sku_manager()` / `build_shop_manager()` / `build_backend()` 保留；
- 仅本次涉及的 2 个脚本切换到 `build_seller_client()`；
- 其他 4 个 `auto_sync_tools` 脚本（`sync_order_to_es` / `sync_shop_statics_to_es` / `auto_preload_order` / `auto_return_refund_order_to_warehouse`）保持原状。

**理由**：缩小 blast radius；后续单独提案（"全自动同步任务 UpSeller 化"）逐个迁移。

## Risks / Trade-offs

| Risk | Mitigation |
| ---- | ---------- |
| `SellerClient` 协议新增 `refresh_local_sku_cache` 后，未来若有第三个 ERP 适配，必须同时实现 | 协议已经是"小而稳定"接口，新增项目自然知晓；在 design 中显式标注 |
| UpSeller 首次运行触发 selenium 登录，crontab 失败 | 接入前先在测试机手工跑一次 `sync_sku_inventory.py` 让 cookie 落地；后续依赖 cookie + 5 分钟登录续期；登录失败时 `print` 异常并退出，不污染数据库 |
| `inv_detail.avg_daily_sales == 0` 既可能是 UpSeller 缺字段也可能是 BigSeller 真无销量 | D3 决策对两种情况一致（保留旧 avg、重算 inventory_support_days），不引入差异 |
| 保留 `big_seller_util.build_big_seller_client` 与 `seller_util.build_seller_client` 双工厂时，未来误用 | `seller-sku-sync` spec 显式禁止本变更覆盖的脚本继续 import `big_seller_util`（PR review 拦截） |
| `SkuDetail.erp_sku_id` 类型在 BigSeller 是数值字符串、UpSeller 是 `idStr` | adapter 已统一为 `str`；MySQL `Ferp_sku_id` 列允许字符串，无影响 |

## Migration Plan

1. **代码改造**：
   - `ec/seller_client.py` 增加 `refresh_local_sku_cache` 方法签名；
   - `ec/big_seller_adapter.py`、`ec/up_seller_adapter.py` 各自实现该方法（一行 delegate）；
   - `auto_sync_tools/sync_all_sku.py`、`auto_sync_tools/sync_sku_inventory.py` 重写。
2. **本地静态校验**：`python3 -m py_compile` 通过；`grep -n big_seller_util auto_sync_tools/sync_all_sku.py auto_sync_tools/sync_sku_inventory.py` 应为空。
3. **测试机回归（BigSeller 项目）**：
   - 单跑 `python sync_all_sku.py`，比对 `cookies/all_sku.json` 大小与 SKU 行数与改造前相当；
   - 单跑 `python sync_sku_inventory.py`，抽样 1~3 个 SKU 比对 `t_sku_info` 中 `inventory / avg_sell_quantity / inventory_support_days / erp_sku_*` 与改造前一致。
4. **测试机回归（UpSeller 项目）**：
   - 单跑 `python sync_all_sku.py`，确认 `cookies/all_up_seller_sku.json` 写入；
   - 单跑 `python sync_sku_inventory.py`，确认：
     - SKU 行 `inventory / erp_sku_name / erp_sku_image_url` 来自 UpSeller；
     - `avg_sell_quantity` 与同步前一致（不被覆盖）；
     - `inventory_support_days` 已基于最新 inventory 重算。
5. **生产灰度**：
   - 先在 BigSeller 项目国家库的运维机执行一次手动 `python sync_sku_inventory.py`，确认无异常；
   - 再在 UpSeller 项目（首个国家）操作一次；
   - 最后恢复 crontab。
6. **回滚**：`git revert <PR>` 即可，无数据库变更。

## Open Questions

- UpSeller 是否有可作为 `avg_daily_sales` 等价信号的接口？需运营/产品确认；当前按 0 处理，且我们保留旧值——预计上线 1 个月内补充。
- 是否需要把 `build_backend` 也搬到 `seller_util` 形成"统一工厂"？倾向于另起 refactor 提案，本次不动。
