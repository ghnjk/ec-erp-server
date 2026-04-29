# 工具脚本规约

## 模块概述

`tools/` 目录存放一次性运维与导入工具，用于初始化数据库、用户管理、批量导入业务数据。

目录：[tools/](../../tools/)

## 脚本清单

| 脚本 | 入口 | CLI 参数 | 功能 |
| ---- | ---- | -------- | ---- |
| `init_db.py` | `init_db()` | 无 | 创建库表与初始 project（philipine） |
| `add_user.py` | `add_user()` | `project_id user password` | 添加用户并设置默认角色 |
| `import_sku.py` | `import_sku()` | `<excel_path>` | 从 Excel 导入 SKU 主数据 |
| `import_supplier_info.py` | `import_suppliers()` | `<excel_path>` | 从 Excel 导入供应商 |
| `import_picking_note.py` | `import_picking_notes()` | `<excel_path>` | 从 Excel 导入拣货备注 |
| `test.py` | - | - | 临时测试脚本（不入流水线） |

## 各脚本说明

### 1. `init_db.py`

- 用途：建库 + 建表 + 创建初始 project
- 流程：
  1. 读取 `application.json` 配置
  2. 创建 `MysqlBackend("philipine", host, port, user, password)`
  3. 调用 `init_db()` 执行 `DtoBase.metadata.create_all`
  4. 调用 `store_project("philipine", {...})` 写入项目元信息
- 替代方式：直接执行 `mysql -u username -p < docs/ec_erp_db.sql`

### 2. `add_user.py`

- 命令：`python tools/add_user.py <project_id> <user_name> <password>`
- 流程：
  1. SHA256 加密密码
  2. 构造 `UserDto`，默认 `is_admin=0`，`roles=[{project_id, role_list: [{name: "supply"}, {name: "warehouse"}]}]`
  3. `backend.store_user(user)`

### 3. `import_sku.py`

- 命令：`python tools/import_sku.py <excel_path>`
- 流程：
  1. `MysqlBackend("philipine")` + `BigSellerClient.login`
  2. `SkuManager.load_and_update_all_sku(client)` 全量同步本地 SKU
  3. 读取 Excel sheet `SKU信息`
  4. 对每行 `query_sku_detail` 累加库存
  5. 构造 `SkuDto` 并 `store_sku`
- 注意：脚本文件头错误标注为 `import_supplier_info`，实际功能是导入 SKU
- project_id 写死为 `philipine`

### 4. `import_supplier_info.py`

- 命令：`python tools/import_supplier_info.py <excel_path>`
- 流程：
  1. 通过 `sync_tool_project_id` 配置创建 backend
  2. 读 Excel sheet `供应商信息`
  3. 对已存在 supplier 合并 ID 后 `store_supplier`

### 5. `import_picking_note.py`

- 命令：`python tools/import_picking_note.py <excel_path>`
- 流程：
  1. 读 Excel sheet `pick_note`
  2. 构造 `SkuPickingNote`
  3. `store_sku_picking_note`

## 共同约定

- 所有脚本从 `conf/application.json` 读取配置
- 不依赖 Flask Session，需通过显式 project_id 创建 backend
- 批量导入时单条异常应捕获并继续，不中断整体
- 工具脚本应从项目根目录执行，确保相对路径正确

## 安全注意

- `add_user.py` 的密码以明文形式作为 CLI 参数传入，shell 历史可能泄漏：建议改为交互式输入或环境变量
- 导入工具会**覆盖**已有数据，操作前必须备份

## 与 backend 的交互模式

工具脚本属于"非 Web 上下文"，不能使用 `request_context.get_backend()`，应直接：

```python
from ec_erp_api.app_config import get_app_config
from ec_erp_api.models.mysql_backend import MysqlBackend

config = get_app_config()
db_config = config["db_config"]
backend = MysqlBackend(
    project_id=config.get("sync_tool_project_id", "philipine"),
    host=db_config["host"],
    port=db_config["port"],
    user=db_config["user"],
    password=db_config["password"],
    db_name=db_config.get("db_name", "ec_erp_db"),
)
```

## 注意事项

- `tools/test.py` 是开发临时测试代码，**不应**在生产环境执行
- 工具脚本输出统一 `print` + `>> std.log 2>&1` 重定向
- 多 project 部署时，导入脚本需按项目轮流执行，并明确传入 `sync_tool_project_id`
