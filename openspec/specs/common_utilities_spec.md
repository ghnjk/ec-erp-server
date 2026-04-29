# 公共工具与装饰器规约

## 模块概述

`ec_erp_api/common/` 提供 API 装饰器、请求/响应工具、加解密、上下文管理、限流与单例等基础能力，所有 API 与业务代码均依赖这些工具。

目录：[ec_erp_api/common/](../../ec_erp_api/common/)

## 文件清单

| 文件 | 主要内容 |
| ---- | -------- |
| `api_core.py` | `set_file_logger`、`api_post_request` 装饰器 |
| `request_util.py` | 从 `request.json["body"]` 取参的工具函数 |
| `response_util.py` | 标准化响应包装函数 |
| `codec_util.py` | SHA256、Base64 编解码 |
| `request_context.py` | Backend 上下文、用户/项目获取、权限校验 |
| `big_seller_util.py` | BigSeller / SkuManager / ShopManager / Backend 工厂 |
| `sku_sale_estimate.py` | SKU 销售估算聚合工具 |
| `rate_limiter.py` | 滑动窗口限流器 |
| `singleton.py` | 缓存型单例 holder |

## 1. api_core

### `set_file_logger(...)`

```python
set_file_logger(
    log_file_path: str,
    log_level=logging.DEBUG,
    max_file_size_mb: int = 100,
    max_file_count: int = 20,
    encoding: str = "UTF-8",
    logger: logging.Logger = None,
)
```

- 清空现有 handlers，挂载 `RotatingFileHandler`
- 默认 logger 为 root（除非显式传入）

### `@api_post_request()`

所有 `/erp_api/*` 接口的统一装饰器，行为：

1. 生成本地 `trace_id = f"TRACE_{time.time()}"`（用于日志与异常响应）
2. 从 `request.json` 序列化整个 `api_request` 写 ACC 日志
3. 调用业务 handler
4. 记录 `cost_time_ms` 与响应 body
5. 异常路径：返回 `{result: "1001", resultMsg: str(e), traceId: trace_id, data: None}`，并记录 ERROR 日志

> **注意**：装饰器内部 `trace_id` 仅用于日志与异常响应；正常响应中的 `traceId` 来自 `request_util.get_trace_id()`，即 `request.json["timestamp"]`，与 ACC 日志 trace_id **不同**。前端约定使用 `timestamp` 作为 traceId。

## 2. request_util

请求体结构（外层包装）：

```json
{
  "timestamp": "TRACE_xxx",
  "serviceName": "ec_erp_static",
  "apiUrl": "/erp_api/xxx",
  "traceId": "TRACE_xxx",
  "body": { /* 实际业务参数 */ }
}
```

所有 `get_*_param` 从 **`request.json["body"]`** 取值。

| 函数 | 签名 | 用途 |
| ---- | ---- | ---- |
| `get_trace_id()` | `() -> str` | 返回 `request.json["timestamp"]`（响应 traceId 来源） |
| `get_str_param(key, erase_empty_str=False)` | | 字符串；`erase_empty_str=True` 时空串转 None |
| `get_bool_param(key, default_value=None)` | | 布尔 |
| `get_int_param(key, default_value=None)` | | 整型；缺失/None/空串返回默认值 |
| `get_float_param(key, default_value=None)` | | 浮点 |
| `get_param(key, default_value=None)` | | 通用（dict/list/object） |
| `check_params(param_name_list)` | `(list) -> bool` | body 是否包含全部键 |
| `parse_url_query_string(query_str)` | `(str) -> dict` | `parse_qs` + 取每键首值（用于 token 登录解码） |

## 3. response_util

| 函数 | 结构 | 用途 |
| ---- | ---- | ---- |
| `pack_error_response(result=-1, result_msg="fail")` | `{result, resultMsg, traceId}` | 错误（无 data） |
| `pack_error_json_response(result, result_msg)` | 同上 | 错误（命名等价） |
| `pack_response(data, result=0, result_msg="success")` | `{result, resultMsg, traceId, data}` | 标准成功 |
| `pack_json_response(data, result=0, result_msg="success")` | 同上 | 命名等价 |
| `pack_simple_response(data=None)` | data 默认 `{}`，走 pack_response | 仅返回成功 |
| `pack_pagination_result(total, records)` | `data = {total, list: [DtoUtil.to_dict(r)...]}` | 分页响应 |

响应结构示例：

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": "TRACE_xxx",
  "data": {
    "total": 100,
    "list": [...]
  }
}
```

## 4. codec_util

| 函数 | 用途 |
| ---- | ---- |
| `calc_sha256(s, encoding="utf-8") -> str` | SHA256 16 进制字符串（用于密码哈希） |
| `base64_decode(s, encoding="utf-8") -> str` | Base64 解码后转字符串（用于 token 登录解码） |

约定：
- 密码存储：`Fpassword = calc_sha256(plain_password)`
- 不在日志中打印明文密码

## 5. request_context

### Backend 工厂

```python
get_backend() -> MysqlBackend
```

- 按 `session.get("project_id", "dev")` 缓存独立的 `MysqlBackend` 实例
- 使用 `CachedSingletonInstanceHolder` 缓存（timeout 1800 秒）
- DB 连接来自 `app_config["db_config"]`

### 用户上下文

| 函数 | 返回 |
| ---- | ---- |
| `get_current_user()` | `Optional[UserDto]`（基于 session 中 user_name + `get_backend().get_user`） |
| `get_current_project_id()` | `str`（缺省 `"dev"`） |

### 权限常量

| 常量 | 值 |
| ---- | -- |
| `PMS_SUPPLIER` | `"supply"` |
| `PMS_WAREHOUSE` | `"warehouse"` |
| `PMS_SALE` | `"sale"` |

### 权限校验

```python
validate_user_permission(permission_name: str) -> bool
```

校验顺序：
1. session 无 user_name → False
2. user.is_admin == True → True
3. roles 中 project_id == 当前 → 找 role_list 中 name == permission_name → True
4. 否则 False

## 6. big_seller_util（工厂）

| 函数 | 缓存 | 说明 |
| ---- | ---- | ---- |
| `build_big_seller_client()` | 300 秒 | BigSeller 登录态客户端 |
| `build_shop_manager()` | - | 读取 `cookies_dir/shop_group.json` |
| `build_sku_manager()` | 60 秒 | 加载 `cookies_dir/all_sku.json` |
| `build_backend(project_id)` | - | 创建无 session 耦合的 MysqlBackend |

## 7. sku_sale_estimate（销售估算聚合）

类：`SkuSaleEstimate(project_id, order_date, backend)`

| 方法 | 用途 |
| ---- | ---- |
| `add_sku_sale(sale_doc, var_count, var_cost_ratio)` | 累加 sku × shop_id 维度的销量、退款、取消、有效金额等 |
| `store()` | 遍历内部映射 `sku_est_data` 调用 `backend.store_sku_sale_estimate`（单条异常打印不中断） |
| `_get_sku_from_db(...)` | 惰性加载全 SKU 列表用于查找 |

主要在 `auto_sync_tools/sync_order_to_es.py` 使用。

## 8. rate_limiter

```python
RateLimiter(max_count_per_period: int, seconds_per_period: int)
```

| 方法 | 用途 |
| ---- | ---- |
| `try_acquire() -> bool` | 滑动窗口内可用则消耗 1 个配额返回 True |
| `acquire(timeout_sec: float)` | 循环 sleep 重试，超时打 logger 警告 |

`BigSellerClient.get_order_detail` 使用模块级 `GLOBAL_RATE_LIMITER` 控速。

## 9. singleton

```python
class CachedSingletonInstanceHolder:
    def __init__(self, timeout_sec: int)
    def get(self) -> Optional[Any]
    def set(self, instance) -> None
```

- `get()`：超时返回 None；未超时刷新 `last_access_time`
- 用于 BigSellerClient / SkuManager / Backend 等的进程内缓存

## 标准请求/响应示例

请求：

```json
{
  "timestamp": "TRACE_1714450000",
  "serviceName": "ec_erp_static",
  "apiUrl": "/erp_api/supplier/search_sku",
  "traceId": "TRACE_1714450000",
  "body": {
    "sku": "ABC",
    "current_page": 1,
    "page_size": 20
  }
}
```

成功响应：

```json
{
  "result": 0,
  "resultMsg": "success",
  "traceId": "TRACE_1714450000",
  "data": {
    "total": 1,
    "list": [{ "sku": "ABC", "sku_name": "..." }]
  }
}
```

错误响应：

```json
{
  "result": "1003",
  "resultMsg": "参数错误",
  "traceId": "TRACE_1714450000"
}
```

## 标准错误码

| 错误码 | 含义 |
| ------ | ---- |
| `0` | 成功 |
| `1001` | 系统异常（装饰器异常分支默认） |
| `1002` | 用户认证失败 |
| `1003` | 参数错误 |
| `1004` | 状态机/业务校验失败 |
| `1008` | 业务执行失败（DB / 第三方异常） |

## 添加新 API 的强制约定

- 必须使用 `@api_post_request()` 装饰
- 请求参数从 `body` 取，使用 `request_util.get_*_param`
- 响应使用 `response_util.pack_*_response`
- 业务必须使用 `request_context.get_backend()` 获取 backend
- 多 project 隔离：所有写库操作必须显式带 `project_id`（来自 `request_context.get_current_project_id()`）
- 操作前先调用 `validate_user_permission(...)` 校验权限（system 模块除外）
