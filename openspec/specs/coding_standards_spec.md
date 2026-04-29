# 编码规范规约

## 概述

本规约汇总 EC-ERP-Server 项目的代码风格、命名约定、文件头格式、错误处理和日志规范，源自 [.cursorrules](../../.cursorrules) 与项目实际代码实践。

## 文件头格式

所有新增 Python 文件**必须**包含以下文件头：

```python
#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: filename
@author: jkguo
@create: YYYY/MM/DD
"""
```

约束：
- 第一行：shebang
- 第二行：编码声明（UTF-8）
- 文件级 docstring 至少包含 `@file`、`@author`、`@create`
- 所有源文件统一使用 UTF-8 编码

## 命名规范

### Python

| 类型 | 约定 | 示例 |
| ---- | ---- | ---- |
| 类 | PascalCase | `BigSellerClient`、`MysqlBackend` |
| 函数/方法 | snake_case | `get_app_config`、`login_user` |
| 私有方法 | 前缀单下划线 | `_get_login_user_info`、`_save_task` |
| 模块级常量 | UPPER_SNAKE_CASE | `CONFIG_DIR`、`__APP_CONFIG__` |
| Logger 名称 | UPPER_CASE 单词 | `ACC`、`INVOKER`、`ASYNC_TASK` |

### 数据库

| 类型 | 约定 | 示例 |
| ---- | ---- | ---- |
| 表名 | `t_` + snake_case | `t_user_info`、`t_purchase_order` |
| 字段名 | `F` + snake_case | `Fproject_id`、`Fcreate_time` |
| 索引名 | `idx_` + 字段 | `idx_supplier_name` |
| DTO 类 | PascalCase + `Dto` | `UserDto`、`SupplierDto`、`PurchaseOrder`（部分历史无 Dto 后缀） |

### URL / Blueprint

| 类型 | 约定 | 示例 |
| ---- | ---- | ---- |
| URL 前缀 | `/erp_api/<module>` | `/erp_api/supplier` |
| API 路径 | `/erp_api/<module>/<action>` | `/erp_api/supplier/search_sku` |

## 导入顺序

```python
# 1. 标准库
import os
import logging
from typing import Optional

# 2. 第三方库
import requests
from flask import Blueprint, request

# 3. 本地模块
from ec_erp_api.common import api_core
from ec_erp_api.models.mysql_backend import MysqlBackend
```

每组之间空一行；同组内部按字母顺序。

## API 路由规范

```python
from flask import Blueprint, request
from ec_erp_api.common.api_core import api_post_request
from ec_erp_api.common import request_util, response_util, request_context

xxx_apis = Blueprint("xxx_apis", __name__, url_prefix="/erp_api/xxx")

@xxx_apis.route("/some_action", methods=["POST"])
@api_post_request()
def some_action():
    # 1. 参数获取
    name = request_util.get_str_param("name")
    page = request_util.get_int_param("current_page", default_value=1)

    # 2. 参数校验 + 权限校验
    if not name:
        return response_util.pack_error_json_response(1003, "name 必填")
    if not request_context.validate_user_permission(request_context.PMS_XXX):
        return response_util.pack_error_json_response(1002, "无权限")

    # 3. 业务逻辑
    backend = request_context.get_backend()
    result = backend.do_something(name)

    # 4. 返回
    return response_util.pack_response({"detail": result})
```

强制约束：
1. **必须**使用 `@api_post_request()` 装饰器
2. **必须**通过 `request_util.get_*_param` 获取参数（不要直接 `request.json["body"]`）
3. **必须**通过 `response_util.pack_*_response` 返回响应
4. **必须**通过 `request_context.get_backend()` 获取数据库后端（不要直接 `MysqlBackend(...)`）
5. 业务模块（非 system）**必须**校验权限

## 响应格式（强制）

```json
{
  "result": "0",
  "resultMsg": "成功",
  "traceId": "TRACE_xxx",
  "data": {}
}
```

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `result` | string/int | 0 = 成功，其他为错误码 |
| `resultMsg` | string | 错误信息或 `"success"` |
| `traceId` | string | 透传请求 `timestamp` |
| `data` | object | 业务数据（错误时可省略） |

## 错误码规范

| 错误码 | 含义 |
| ------ | ---- |
| `0` | 成功 |
| `1001` | 系统异常 |
| `1002` | 用户认证失败 |
| `1003` | 参数错误 |
| `1004` | 状态机校验失败 |
| `1008` | 业务执行失败（DB / 第三方异常） |

新增错误码遵循 1xxx 编号，并在 `docs/erp_api/README.md` 全局错误码表中登记。

## 日志规范

### Logger 与文件对应（强制）

| Logger 名称 | 文件 | 用途 |
| ----------- | ---- | ---- |
| `ACC` | `logs/acc.log` | API 访问与响应（`@api_post_request()` 自动写入） |
| `ERROR` | `logs/error.log` | 应用错误 |
| `ASYNC_TASK` | `logs/async_task.log` | 异步业务任务 |
| `INVOKER` | `logs/invoker.log` | 第三方调用（BigSeller 等） |
| `sqlalchemy.engine` | `logs/sql.log` | SQLAlchemy 输出 |

### 日志级别

| 级别 | 场景 |
| ---- | ---- |
| `DEBUG` | 调试信息（默认只在文件中） |
| `INFO` | 正常业务流程节点 |
| `WARNING` | 业务异常但可继续（如限流超时） |
| `ERROR` | 业务/系统错误 |

### 内容约束

- 请求日志包含：trace_id、path、body
- 响应日志包含：trace_id、path、cost_time、body
- **绝对禁止**记录明文密码、`session_secret_key`、`ydm_token`
- BigSeller cookie 内容禁止全量记录

## 数据库规范

### Dto 定义

```python
class XxxDto(DtoBase):
    __tablename__ = "t_xxx"

    project_id = Column("Fproject_id", String(128), primary_key=True)
    name = Column("Fname", String(128), index=True)
    is_delete = Column("Fis_delete", Integer)
    version = Column("Fversion", Integer)
    modify_user = Column("Fmodify_user", String(128))
    create_time = Column("Fcreate_time", DateTime, index=True)
    modify_time = Column("Fmodify_time", DateTime, index=True)

    columns = [
        "project_id", "name",
        "is_delete", "version", "modify_user",
        "create_time", "modify_time",
    ]
```

### 强制约束

- 所有 Dto **必须**显式定义 `columns`
- 业务表**必须**包含 `Fproject_id`、`Fcreate_time`、`Fmodify_time`
- 删除采用**逻辑删除**（`Fis_delete`），不物理删除（拣货/打印任务表除外）
- 不使用外键约束，关联在应用层校验
- 金额字段优先使用 INT（**单位：分**），新表禁止使用 Float 表示金额

### 索引

- 频繁过滤字段加 `index=True`
- 复合主键使用 `PrimaryKeyConstraint`

## Session 与认证

| 操作 | 约定 |
| ---- | ---- |
| 登录 | `session["user_name"] = ...` 与 `session["project_id"] = ...` |
| 退出 | `session.clear()` |
| 密码 | `Fpassword = calc_sha256(plain)` |
| 获取当前用户 | `request_context.get_current_user()` |
| 获取当前项目 | `request_context.get_current_project_id()` |

## 第三方集成

| 约定 | 说明 |
| ---- | ---- |
| HTTP 调用 | 必须经过 `BigSellerClient.post/get/download` 等统一入口 |
| 日志 | 使用 `INVOKER` logger |
| 重试 | 验证码识别内置 10 次重试；其他场景由调用方决定 |
| Cookie | 持久化到 `cookies/big_seller.cookies`，使用原子写入 |
| 限流 | `BigSellerClient.get_order_detail` 必须经过 `GLOBAL_RATE_LIMITER` |

## 配置管理

- 应用配置文件 `conf/application.json` **不**入版本控制
- 模板文件 `conf/application_template.json` 入版本控制（仅作示例）
- 不同环境使用 `release_conf/application_{country}.json`
- 密码、Token 使用前先用 `codec_util.calc_sha256` 加密（password 字段）

## Git 规范

### 不入版本控制

- `conf/application.json`
- `*.pyc` 与 `__pycache__/`
- `logs/`、`data/pdf/`、`cookies/`
- 临时数据 / 本地实验

### 提交说明

- 提交代码时**同步更新相关文档**（API md / db.sql）
- 修改 API 时同步更新 `docs/erp_api/README.md`
- 新增数据表时同步更新 `docs/ec_erp_db.sql`

## 文档规范

### API 接口文档

每个 API 接口必须创建独立的 Markdown 文档（`docs/erp_api/<module>/<action>.md`），包含：

1. 接口路径、方法、描述、权限
2. 请求参数表（参数名、类型、必填、说明）
3. 响应参数结构
4. 错误码
5. 请求示例
6. 响应示例（基于 `docs/sample_response/`）
7. 业务逻辑说明
8. 注意事项

### 数据库文档

- 建表语句维护在 `docs/ec_erp_db.sql`
- 每个字段必须有中文注释
- 必须定义合适的索引

## 安全约束（强制）

- 密码使用 SHA256 加密（`calc_sha256`）
- Session secret_key 仅存放于 `application.json`，不入版本控制
- 第三方凭证（BigSeller、ydm）不硬编码
- API 必须做权限校验（`validate_user_permission`）
- 多 project 必须做数据隔离（所有写操作显式 `project_id`）

## 性能约束

- 大文件操作优先流式（如 BigSeller PDF 下载使用 `download` 流式接口）
- 第三方接口调用必须节流（`time.sleep(0.3)` 或 `RateLimiter`）
- DB 批量操作通过 session 内多条 commit 实现，避免单条循环 commit
- 长耗时业务（如订单打印）使用线程异步执行，HTTP 请求快速返回

## 测试规范

- 测试代码统一放 `tools/test.py`
- 不在生产环境执行测试代码
- 测试数据库与生产数据库分离
