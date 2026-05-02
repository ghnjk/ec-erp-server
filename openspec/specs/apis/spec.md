# API 接口规约

## 模块概述

本规约定义 EC-ERP-Server 全部 HTTP API 的统一接入约定、请求/响应格式、错误码体系，以及**接口变更管理流程**。

每个具体接口的详细定义（参数、响应字段、示例、业务逻辑）见 [design/](./design/) 子目录，按业务模块（system/supplier/warehouse/sale）分组。

## 接口接入约定（强制）

### 通用规则

| 项 | 约定 |
| -- | ---- |
| 接口前缀 | `/erp_api/` |
| 请求方法 | **统一 POST** |
| Content-Type | `application/json` |
| 鉴权方式 | Flask Session（先经 `/erp_api/system/login_user*` 登录） |
| 多 project 隔离 | Session 中 `project_id` 决定数据范围 |
| 装饰器 | 所有 handler 必须使用 `@api_post_request()` |

### Blueprint 与 URL Prefix

| Blueprint | url_prefix | 文件 |
| --------- | ---------- | ---- |
| `system_apis` | `/erp_api/system` | [ec_erp_api/apis/system.py](../../../ec_erp_api/apis/system.py) |
| `supplier_apis` | `/erp_api/supplier` | [ec_erp_api/apis/supplier.py](../../../ec_erp_api/apis/supplier.py) |
| `warehouse_apis` | `/erp_api/warehouse` | [ec_erp_api/apis/warehouse.py](../../../ec_erp_api/apis/warehouse.py) |
| `sale_apis` | `/erp_api/sale` | [ec_erp_api/apis/sale.py](../../../ec_erp_api/apis/sale.py) |

## 请求格式（强制）

前端外层包装：

```json
{
  "timestamp": "TRACE_xxx",
  "serviceName": "ec_erp_static",
  "apiUrl": "/erp_api/<module>/<action>",
  "traceId": "TRACE_xxx",
  "body": {
    "/* 业务参数 */": "..."
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
| ---- | ---- | ---- | ---- |
| `timestamp` | string | 是 | 前端生成的 trace 标识，会作为响应 `traceId` 透传 |
| `serviceName` | string | 是 | 固定值 `"ec_erp_static"` |
| `apiUrl` | string | 是 | 当前请求的接口路径 |
| `traceId` | string | 是 | 同 `timestamp`，用于跨系统追踪 |
| `body` | object | 是 | 实际业务参数，所有 `request_util.get_*_param` 都从这里读取 |

> **关键**：服务端通过 `request_util.get_*_param("xxx")` 取值时，等价于读取 `request.json["body"]["xxx"]`。**直接访问 `request.json["xxx"]` 是错误用法**。

## 响应格式（强制）

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991728857,
  "data": { /* 业务数据 */ }
}
```

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `result` | int / string | 0 = 成功；其他为错误码（见下） |
| `resultMsg` | string | 成功为 `"success"`，错误时为可读消息 |
| `traceId` | string / number | 来自请求 `timestamp`（由 `request_util.get_trace_id()` 透传）；异常路径下为装饰器生成的 `TRACE_<time>` |
| `data` | object | 业务数据，错误时可省略 |

### 标准包装函数（`response_util`）

| 函数 | 用法 |
| ---- | ---- |
| `pack_response(data, result=0, result_msg="success")` | 标准成功 |
| `pack_json_response(data)` | 与 `pack_response` 等价（命名差异） |
| `pack_simple_response(data=None)` | 仅返回成功（data 默认 `{}`） |
| `pack_pagination_result(total, records)` | 分页响应：`data = {total, list: [DtoUtil.to_dict(r)...]}` |
| `pack_error_response(result=-1, result_msg="fail")` | 错误（无 data） |
| `pack_error_json_response(result, result_msg)` | 错误（命名等价） |

## 标准错误码

| 错误码 | 含义 | 触发场景 |
| ------ | ---- | -------- |
| `0` | 成功 | - |
| `1001` | 系统异常 / 用户未登录 | `@api_post_request()` 装饰器异常分支默认；`request_context.get_current_user()` 返回 None |
| `1002` | 用户认证失败 | 密码错误、Token 无效 |
| `1003` | 参数错误 | 缺失必填字段、类型/取值非法 |
| `1004` | 业务逻辑错误 | 状态机校验失败（如重复同步、不可跳过的步骤） |
| `1008` | 权限不足 | `validate_user_permission(...)` 返回 False |

> 新增错误码必须 **使用 1xxx 编号**，并在本规约表格与 [docs/erp_api/README.md](../../../docs/erp_api/README.md) 中同步登记。

## 接口编写模板（强制）

新增接口必须遵循以下结构：

```python
@xxx_apis.route("/<action>", methods=["POST"])
@api_post_request()
def <action>():
    # 1. 权限校验（system 模块除外）
    if not request_context.validate_user_permission(request_context.PMS_XXX):
        return response_util.pack_error_json_response(1008, "权限不足")

    # 2. 参数获取
    name = request_util.get_str_param("name")
    page = request_util.get_int_param("current_page", default_value=1)
    size = request_util.get_int_param("page_size", default_value=20)

    # 3. 参数校验
    if not name:
        return response_util.pack_error_json_response(1003, "name 必填")

    # 4. 业务逻辑
    backend = request_context.get_backend()
    total, records = backend.search_xxx(name, (page - 1) * size, size)

    # 5. 返回
    return response_util.pack_pagination_result(total, records)
```

## 多 project 数据隔离（强制）

- 所有业务接口必须通过 `request_context.get_backend()` 获取 backend，不要直接 `MysqlBackend(...)`
- backend 内部按 `session["project_id"]` 进行数据过滤
- 写库操作必须显式校验 `data.project_id == backend.project_id`（已在 backend 大部分写方法中内置）
- 跨 project 查询禁止

## 接口模块索引

| 模块 | 接口数 | 设计文档 |
| ---- | ------ | -------- |
| system | 4 | [design/system/](./design/system/) |
| supplier | 10 | [design/supplier/](./design/supplier/) |
| warehouse | 7 | [design/warehouse/](./design/warehouse/) |
| sale | 7 | [design/sale/](./design/sale/) |
| **合计** | **28** | - |

完整接口列表见 [config.yaml](../config.yaml) 中的 `apis.routes` 节，以及各模块对应的 spec 文档：

- [system_module_spec.md](../system_module_spec.md)
- [supplier_module_spec.md](../supplier_module_spec.md)
- [warehouse_module_spec.md](../warehouse_module_spec.md)
- [sale_module_spec.md](../sale_module_spec.md)

## System API Requirements

### Requirement: System API exposes backend ERP status
The API layer SHALL expose a POST endpoint under the system module for querying backend ERP status, following the standard `/erp_api/system/*` route convention and `@api_post_request()` response wrapping.

#### Scenario: Authenticated user queries ERP status
- **WHEN** an authenticated user calls `POST /erp_api/system/get_backend_erp_status`
- **THEN** the API SHALL return `result=0` with the backend ERP status data.

#### Scenario: Unauthenticated user queries ERP status
- **WHEN** a request without a valid Flask session calls `POST /erp_api/system/get_backend_erp_status`
- **THEN** the API SHALL return the same not-login error behavior used by existing system user-info APIs.

#### Scenario: API response shape
- **WHEN** the endpoint succeeds
- **THEN** the response `data` SHALL contain `erp_type`, `email`, `warehouse_id`, `is_login`, `auto_login`, and `message` fields.

#### Scenario: Documentation is synchronized
- **WHEN** the API is implemented
- **THEN** `openspec/specs/apis/design/system/get_backend_erp_status.md`, `docs/erp_api/system/get_backend_erp_status.md`, and API indexes SHALL be updated to document the route, request, response fields, examples, and business logic.

---

# 接口变更管理规约（API Change Management）

## 总则

EC-ERP-Server 是前后端分离架构（后端 ec-erp-server / 前端 ec-erp-static），所有接口契约都是**前后端共享资产**。任何接口变更（新增 / 修改 / 删除）必须严格遵循以下流程，确保：

- **可追溯**：每次变更有明确记录
- **可回滚**：避免破坏生产环境
- **同步性**：代码、规约、文档、前端调用一致

## 变更场景

涵盖以下所有调整：

| 场景 | 触发条件 | 风险 |
| ---- | -------- | ---- |
| 新增接口 | 新业务需求 | 低 |
| 删除接口 | 业务下线 | **高（破坏前端调用）** |
| 修改请求参数（字段名/类型/必填） | 入参语义变化 | **高（破坏前端调用）** |
| 修改响应结构 | 出参语义变化 | **高（破坏前端调用）** |
| 修改错误码 | 错误处理变化 | 中 |
| 修改业务逻辑（不变契约） | 内部重构 | 低 |
| 调整权限要求 | 权限收紧/放开 | 中 |
| URL 路径变更 | 路径重命名 | **高（破坏前端调用）** |

## 变更流程（强制）

每次接口调整必须**同步**完成以下 6 项更新：

### 1. 修改 API 实现代码

文件：`ec_erp_api/apis/<module>.py`

- 新增/修改路由 handler
- 必须使用 `@api_post_request()` 装饰器
- 必须使用 `request_util.get_*_param` 取参，`response_util.pack_*_response` 返回
- 必须经过权限校验（system 模块除外）

### 2. 修改/新增 OpenSpec 设计文档

文件：[openspec/specs/apis/design/<module>/<action>.md](./design/)

- **新增接口**：创建新文件，按 [接口设计文档模板](#接口设计文档模板) 编写
- **修改接口**：更新对应字段表、示例、业务逻辑章节
- **删除接口**：保留文件并在文件头部加上 `> ⚠️ 已下线（YYYY-MM-DD）` 醒目提示，**不要直接删除**

### 3. 同步对应模块 spec

文件：`openspec/specs/<module>_module_spec.md`

- 新增/删除接口时更新 "接口清单" 表格
- 修改接口语义时同步说明
- 状态机或业务流程变化时更新对应章节

### 4. 同步 docs/erp_api/ 业务文档

文件：`docs/erp_api/<module>/<action>.md`

历史业务文档目录，保持与 design 同步以便业务方查阅。

> **二者关系**：`openspec/specs/apis/design/` 是规约性文档（含接口定义、handler 引用、Change-Log）；`docs/erp_api/` 是业务文档（更易读、含示例）。两者必须同步。

### 5. 在 design 文档末尾追加 Change-Log

design 文件**必须**在文末包含 `## Change-Log` 章节，按时间倒序记录变更。

### 6. 更新 [config.yaml](../config.yaml)

- 新增/删除接口时更新 `apis.routes.<module>` 列表与 `apis.total_count`
- 修改路径时同步路径

### 7.（可选）更新前端 API 客户端

文件：`ec-erp-static/src/apis/*Apis.ts`

- 修改前端 API 类型定义
- 修改请求/响应 DTO

> 后端发版前需要确保前端版本与新接口契约对齐，避免线上报错。

## 接口设计文档模板

每个 `design/<module>/<action>.md` **必须**包含以下章节：

```markdown
# 接口标题

## 接口信息

- **接口路径**: `/erp_api/<module>/<action>`
- **请求方法**: POST
- **接口描述**: 一句话描述
- **权限要求**: PMS_XXX / 仅登录态 / 无
- **Handler**: [ec_erp_api/apis/<module>.py](../../../../../ec_erp_api/apis/<module>.py) `<func_name>`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| ... | | | |

（嵌套对象使用 `∟` 表达层级）

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| ... | | |

## 错误码

| 错误码 | 说明 |
|--------|------|

## 请求示例

```json
{ ... }
```

## 响应示例

### 成功响应

```json
{ ... }
```

### 错误响应（如有）

```json
{ ... }
```

## 业务逻辑说明

1. ...
2. ...

## 关联

- 数据表：[t_xxx](../../../data-model/design/t_xxx.md)
- 模块 spec：[xxx_module_spec.md](../../../xxx_module_spec.md)
- 业务文档：[docs/erp_api/<module>/<action>.md](../../../../../docs/erp_api/<module>/<action>.md)

## 注意事项

- ...

## Change-Log

### YYYY-MM-DD - <一句话描述>

**变更类型**：新增接口 / 修改请求参数 / 修改响应结构 / 修改错误码 / 修改业务逻辑 / 删除接口

**变更原因**：业务背景

**变更内容**：
- ...

**前端影响**：是否需要前端同步改动
- 是：列出 `ec-erp-static` 需要修改的文件 / 字段
- 否：纯后端兼容变更

**回滚方式**：如何快速回滚

**关联代码改动**：
- handler：`ec_erp_api/apis/<module>.py:func_name`
- 数据表：`t_xxx`（如有 schema 变更）
- 前端：`ec-erp-static/src/apis/<module>Apis.ts`（如有）
```

## Change-Log 章节模板

```markdown
## Change-Log

### 2026-04-29 - 新增 inventory_support_days 过滤参数

**变更类型**：修改请求参数（向后兼容）

**变更原因**：供应链运营需要按库存支撑天数筛选 SKU。

**变更内容**：
- 新增可选参数 `inventory_support_days` (int, 默认 0)
- 当 > 0 时过滤 `inventory_support_days <= <值>` 的 SKU

**前端影响**：可选改动
- 前端可以新增筛选 UI；不传该字段时行为不变

**回滚方式**：移除该参数处理代码即可，DB 字段保留（已有数据无影响）

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `search_sku`
- 数据表：[t_sku_info](../../../data-model/design/t_sku_info.md)
- 前端：`ec-erp-static/src/apis/supplierApis.ts`
```

## 兼容性约束（强制）

### 向后兼容变更（推荐）

可在生产环境直接发布，无需前端同步：

- 新增**可选**请求参数（带默认值）
- 新增响应字段
- 新增可选错误码（不影响已有路径）
- 内部业务逻辑重构（不变契约）

### 不兼容变更（高风险）

**必须**先升级前端再发布后端，并准备回滚预案：

- 新增**必填**请求参数
- 修改请求参数名称/类型/必填性
- 删除请求参数
- 修改响应字段名称/类型
- 删除响应字段
- 修改 URL 路径
- 修改错误码语义

**不兼容变更建议先采用「双版本并行」策略**：
1. 新建 v2 接口 `/<action>_v2`，完成切换后再下线旧版

## 强制约束清单

| 约束 | 说明 |
| ---- | ---- |
| 任何接口变更必须同步更新代码、design 文档、模块 spec、docs/erp_api/、config.yaml | 缺一不可 |
| 每次变更必须在 design/<module>/<action>.md 追加 Change-Log 条目 | 时间倒序 |
| 新增接口必须使用 `@api_post_request()` | - |
| 新增接口必须用 `request_util.get_*_param` 取参 | 不允许直接 `request.json[...]` |
| 新增接口必须用 `response_util.pack_*_response` 返回 | - |
| 业务接口必须做权限校验 | system 模块除外 |
| 新增错误码使用 1xxx 编号 | 在错误码表中登记 |
| URL 路径不允许中划线 / 大写 | 仅 snake_case |
| 删除接口不要物理删除 design 文件 | 标注下线日期保留 |
| 不兼容变更前必须先升级前端 | 防止线上故障 |

## 变更审查检查清单

提交代码评审前，作者必须确认：

- [ ] 实现代码使用了 `@api_post_request()`
- [ ] 参数取值通过 `request_util.get_*_param`
- [ ] 响应通过 `response_util.pack_*_response`
- [ ] 已校验权限（system 模块除外）
- [ ] 已创建/更新 `openspec/specs/apis/design/<module>/<action>.md`
- [ ] 已在 design 文件追加 Change-Log
- [ ] 已更新 `openspec/specs/<module>_module_spec.md` 接口清单（如新增/删除）
- [ ] 已更新 `docs/erp_api/<module>/<action>.md`
- [ ] 已更新 `openspec/specs/config.yaml`
- [ ] 是否兼容变更已识别，不兼容变更有前端同步计划
- [ ] 已加入测试用例（如有测试体系）

## 与 OpenSpec 提案流程的关系

涉及接口变更的需求，建议通过 OpenSpec 提案管理：

```bash
openspec propose "<接口变更描述>"
# 提案中包含：
# - design/<module>/<action>.md 的 diff
# - 影响范围（前端 / 第三方调用方 / 定时任务）
# - 兼容性分析

openspec apply <change-id>
openspec archive <change-id>
```
