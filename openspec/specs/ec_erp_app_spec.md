# 应用入口与全局配置规约

## 模块概述

`ec_erp_app.py` 是 EC-ERP-Server 的 Flask 应用主入口，负责：

- Flask 应用初始化（应用名、静态资源、Session）
- 注册 4 个业务 Blueprint（system / supplier / warehouse / sale）
- 初始化日志体系（5 个独立 logger，使用 RotatingFileHandler）
- 启动 Web 服务

## 技术栈

| 项 | 版本 / 说明 |
| -- | ----------- |
| 语言 | Python 3 |
| Web 框架 | Flask |
| ORM | SQLAlchemy 1.4.51 + PyMySQL |
| 搜索引擎 | Elasticsearch 7.14.2 |
| 第三方集成 | BigSeller（电商 ERP）、jfbym（验证码识别） |
| 运行模式 | 单进程 + threaded=True |

## 目录结构（核心）

| 路径 | 职责 |
| ---- | ---- |
| `ec_erp_app.py` | 应用入口 |
| `ec_erp_api/apis/` | 4 个 API Blueprint |
| `ec_erp_api/common/` | 公共工具与装饰器 |
| `ec_erp_api/business/` | 业务逻辑（订单打印） |
| `ec_erp_api/models/mysql_backend.py` | 数据模型与 MysqlBackend |
| `ec_erp_api/app_config.py` | 配置文件加载 |
| `ec/` | 第三方电商集成（BigSeller、SKU/Shop 管理、验证码） |
| `auto_sync_tools/` | 定时同步任务脚本 |
| `tools/` | 一次性工具脚本（初始化 / 导入） |
| `conf/application.json` | 应用配置（不入版本控制） |
| `static/` | Flask 静态资源（含订单打印 PDF） |
| `data/pdf/`, `cookies/`, `logs/` | 运行期数据目录 |

## Blueprint 注册（必须遵循）

| 变量 | url_prefix | 文件 |
| ---- | ---------- | ---- |
| `system_apis` | `/erp_api/system` | [ec_erp_api/apis/system.py](../../ec_erp_api/apis/system.py) |
| `supplier_apis` | `/erp_api/supplier` | [ec_erp_api/apis/supplier.py](../../ec_erp_api/apis/supplier.py) |
| `warehouse_apis` | `/erp_api/warehouse` | [ec_erp_api/apis/warehouse.py](../../ec_erp_api/apis/warehouse.py) |
| `sale_apis` | `/erp_api/sale` | [ec_erp_api/apis/sale.py](../../ec_erp_api/apis/sale.py) |

新增 Blueprint 时：
1. 在 `ec_erp_api/apis/<module>.py` 用 `Blueprint(name, __name__, url_prefix='/erp_api/<module>')` 创建
2. 在 `ec_erp_app.py` 的 `create_app()` 中 `app.register_blueprint(...)`
3. 路由统一前缀 `/erp_api/<module>/<function_name>`

## 日志规范（必须遵循）

`create_app()` 中通过 `set_file_logger(...)` 配置以下 5 个 logger：

| logger 名称 | 日志文件 | 用途 |
| ----------- | -------- | ---- |
| `ACC` | `logs/acc.log` | API 访问与响应（由 `@api_post_request()` 写入） |
| `ERROR` | `logs/error.log` | 应用错误日志 |
| `ASYNC_TASK` | `logs/async_task.log` | 异步业务任务（如订单打印线程） |
| `INVOKER` | `logs/invoker.log` | 第三方调用（BigSeller HTTP 请求/响应） |
| `sqlalchemy.engine` | `logs/sql.log` | SQLAlchemy 执行日志 |

约束：
- 单文件最大 100MB，备份数量上限 20，编码 UTF-8（由 `set_file_logger` 默认值给出）。
- 业务代码必须使用上述 logger 名称，不得新增同名功能不同名的 logger。
- 异常路径下的 trace 信息打 `ERROR`；正常请求/响应打 `ACC`。

## Session 与静态资源

- `app.secret_key = app_config["session_secret_key"]`（来自 `conf/application.json`）
- `Flask(app_config["application"], static_url_path='')`
- `app.static_folder = "./static"`（相对于运行目录）
- 订单打印输出文件路径：`static/print/{task_id}/{task_id}.all.pdf`，对应 URL `/print/{task_id}/{task_id}.all.pdf`

## 启动方式

```bash
python ec_erp_app.py
# 或使用
./restart.sh
```

启动参数来源：
- `listen_host`：缺省 `127.0.0.1`，可在 `application.json` 覆盖
- `listen_port`：必填，由配置提供
- `debug=False, threaded=True`

## 配置文件（`conf/application.json`）

由 [ec_erp_api/app_config.py](../../ec_erp_api/app_config.py) 加载：

```python
CONFIG_DIR = <项目根>/conf
get_config_file(file_name) -> os.path.join(CONFIG_DIR, file_name)
get_app_config() -> dict     # 模块级单例懒加载（__APP_CONFIG__）
get_static_dir() -> str      # 项目根/static
```

### 必填配置键

| 键 | 类型 | 说明 |
| -- | ---- | ---- |
| `application` | string | Flask 应用名 |
| `session_secret_key` | string（secret） | Flask Session 加密 |
| `listen_port` | int | Web 监听端口 |
| `db_config.host` | string | MySQL 主机 |
| `db_config.port` | int | MySQL 端口 |
| `db_config.user` | string | MySQL 用户名 |
| `db_config.password` | string（secret） | MySQL 密码 |
| `ydm_token` | string（secret） | jfbym 打码平台 Token |
| `big_seller_mail` | string | BigSeller 登录邮箱 |
| `big_seller_encoded_passwd` | string（secret） | BigSeller 编码后的密码 |
| `big_seller_warehouse_id` | int | BigSeller 仓库 ID |
| `big_seller_shelf_id` | int | BigSeller 货架 ID |
| `big_seller_shelf_name` | string | BigSeller 货架名称 |

### 可选配置键

| 键 | 类型 | 默认 | 说明 |
| -- | ---- | ---- | ---- |
| `listen_host` | string | `127.0.0.1` | Web 监听 IP |
| `db_config.db_name` | string | `ec_erp_db` | 数据库名 |
| `cookies_dir` | string | `../cookies` | Cookie/SKU 缓存目录（相对运行 cwd） |
| `sync_tool_project_id` | string | 部分脚本必填，`sync_sku_inventory` 默认 `philipine` | 同步任务对应 project_id |
| `es_hosts` | array<string> | - | Elasticsearch 主机列表（ES 同步任务必填） |
| `es_user` | string | - | ES Basic Auth 账号 |
| `es_passwd` | string（secret） | - | ES Basic Auth 密码 |

### 安全约束

- `application.json` 不入版本控制，仅 `application_template.json` 在仓库内
- 密码、token、`session_secret_key` 不得记录在日志中
- 不同环境使用 `release_conf/application_{country}.json`

## 多项目（多国家/地区）支持

应用通过 Session 中的 `project_id` 区分不同国家/地区的数据：

| project_id | 国家/地区 |
| ---------- | --------- |
| `philipine` | 菲律宾 |
| `india` | 印度 |
| `malaysia` | 马来西亚 |
| `thailand` | 泰国 |

- 所有核心业务表必须包含 `Fproject_id` 字段
- 后端通过 `request_context.get_backend()` 按项目缓存独立的 `MysqlBackend` 实例（缓存 1800 秒）
- Session 中无 `project_id` 时默认为 `dev`

## 启动检查清单

- [ ] `conf/application.json` 已配置且包含上表所有必填项
- [ ] 数据库 `ec_erp_db` 已存在并执行过 `docs/ec_erp_db.sql`
- [ ] `cookies/` 与 `logs/` 目录可写
- [ ] BigSeller 账号可用，`ydm_token` 有效
