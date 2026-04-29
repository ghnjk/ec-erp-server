# BigSeller 第三方集成规约

## 模块概述

BigSeller 是 EC-ERP-Server 对接的核心电商 ERP 平台。集成涉及登录鉴权、Cookie 持久化、验证码识别、SKU/订单/库存/退单等多类业务接口。

- 主类：[ec/bigseller/big_seller_client.py](../../ec/bigseller/big_seller_client.py) → `BigSellerClient`
- 辅助类：
  - [ec/shop_manager.py](../../ec/shop_manager.py) → `ShopManager`
  - [ec/sku_manager.py](../../ec/sku_manager.py) → `SkuManager`
  - [ec/sku_group_matcher.py](../../ec/sku_group_matcher.py) → `SkuGroupMatcher`
- 验证码：[ec/verifycode/ydm_verify.py](../../ec/verifycode/ydm_verify.py) → `YdmVerify`
- 工厂：[ec_erp_api/common/big_seller_util.py](../../ec_erp_api/common/big_seller_util.py)
- 接口文档参考：[docs/big_seller_apis/bigseller接口.md](../../docs/big_seller_apis/bigseller接口.md)

## BigSellerClient

### 构造

```python
BigSellerClient(ydm_token: str, cookies_file_path: str = "cookies/big_seller.cookies")
```

- 内部持有 `requests.Session()`
- 内部持有 `YdmVerify(ydm_token)` 用于验证码识别
- Logger：`logging.getLogger("INVOKER")`，所有 HTTP 请求/响应均记录
- 接口基地址：`https://www.bigseller.com/api/...`

### 登录与 Cookie 持久化

| 方法 | 行为 |
| ---- | ---- |
| `login(email, encoded_password)` | 优先 `load_cookies` + `is_login` 复用；否则走 `__login` |
| `__login` | 新 Session → 拉登录页 → 拉验证码图 → `get_valid_verify_code` → POST 登录 → 成功后 `save_cookies` |
| `load_cookies()` | 从 `cookies_file_path` 读 JSON 更新 `session.cookies` |
| `save_cookies()` | 临时文件 + `os.replace` 原子写入 |
| `is_login()` | GET `check_login_url`，看响应 `data` 字段 |

### 验证码识别

`get_valid_verify_code()`：
1. GET `gen_verify_code_url`，解析 `base64Image`（去掉 `data:image/png;base64,` 前缀）
2. 调用 `YdmVerify.common_verify(image_base64, "10110")`
3. `code == 10000` 时返回 `(accessCode, verify_code)`
4. 失败 sleep 3 秒重试，最多 10 次

### HTTP 工具方法

| 方法 | 用途 |
| ---- | ---- |
| `post(url, data=..., json=..., timeout=...)` | 统一打 INVOKER 日志，返回 `requests.Response` |
| `get(url, ...)` | 同上 |
| `download(url, file_path)` | Session 流式下载到本地 |

> **注意**：所有外部 HTTP 调用必须经过 `post`/`get`/`download` 走统一日志。

### 主要业务 API

| 方法 | 关键参数 | 用途 |
| ---- | -------- | ---- |
| `load_all_sku()` | 内部分页 `pageSize=300` | 拉取商户全部 SKU |
| `load_sku_estimate_by_date(begin_date, end_date)` | 日期区间 | SKU 销售统计 |
| `load_all_sku_class()` | - | SKU 分类列表 |
| `query_sku_detail(sku_id, is_group=0)` | - | SKU 详情 |
| `query_sku_inventory_detail(sku, warehouse_id)` | - | 仓库维度库存 + 预测 |
| `add_stock_to_erp(req)` | 入库 JSON | ERP 库存入库/出库 |
| `query_shop_group()` | - | 店铺分组 |
| `query_all_shop_info()` | - | 全部店铺基本信息 |
| `query_shop_sell_static(begin_date, end_date)` | - | 店铺销售统计（按天） |
| `query_not_op_refund_order_tracking_no_list(refund_date)` | - | 退货待处理列表 |
| `query_refund_order_info_by_tracking_no(tracking_no, warehouse_id)` | - | 按运单查退款详情 |
| `return_refund_order_to_warehouse(refund_order, warehouse_id)` | - | 退货入库提交 |
| `get_wait_print_order_ship_provider_list(warehouse_id)` | - | 待打印订单按物流商分组 |
| `search_new_order(warehouse_id, begin_time, end_time, ...)` | 分页 | 新订单 |
| `set_new_order_to_wait_print(order_id)` | - | 新单标待打印（pack） |
| `search_wait_print_order_by_warehouse_id(warehouse_id, ...)` | 分页 | 仓库维度待打印 |
| `search_wait_print_order(shipping_provider_id, ...)` | 分页 | 物流商维度待打印 |
| `download_order_mask_pdf_file(order_id, mark_id, platform, local_path)` | - | 触发打印并轮询 fileUrl 下载 |
| `get_order_detail(order_id)` | - | 订单详情（**全局限流 GLOBAL_RATE_LIMITER**） |
| `mark_order_printed(order_id)` | - | 标记已打印 |
| `get_more_sku_mapping(sku_id)` | - | **deprecated** 额外 SKU 映射 |

### 限流

`get_order_detail` 使用模块级 `GLOBAL_RATE_LIMITER`（`RateLimiter` 实例）控速，避免触发 BigSeller 风控。

## YdmVerify（验证码识别）

平台：jfbym（云码）

| 方法 | 用途 | 验证码类型 |
| ---- | ---- | ---------- |
| `common_verify(image_base64, verify_type="60000")` | 通用 | BigSeller 用 `"10110"` 数英 |
| `slide_verify` / `sin_slide_verify` / `traffic_slide_verify` | 滑块 | - |
| `click_verify` | 点选 | - |
| `rotate` | 旋转 | - |
| `google_verify` | Google reCAPTCHA | 创建任务 + 轮询 `funnelApiResult` |
| `fun_captcha_verify` / `hcaptcha_verify` | FunCaptcha / hCaptcha | - |

接口端点：
- 通用：`http://api.jfbym.com/api/YmServer/customApi`
- Google 类：`122.9.52.147` + `funnelApi` / `funnelApiResult`

Token 来源：`application.json:ydm_token`

## ShopManager

文件：`cookies/shop_group.json`

| 方法 | 用途 |
| ---- | ---- |
| `__init__(file_path=...)` | 加载本地 JSON |
| `get_shop_platform(shop_id)` | 查询店铺所属平台 |
| `get_shop_owner(shop_id)` | 查询店铺负责人 |
| `load_an_update_sm(client: BigSellerClient)` | 调用 `query_shop_group` + `query_all_shop_info` 更新本地缓存 |
| `dump()` | 保存到本地 JSON |

仅依赖 BigSellerClient，**不直接访问 MySQL**。

## SkuManager

文件：
- `cookies/all_sku.json`
- `cookies/all_variant_sku_mapping.json`

数据结构：
- `sku_map`：SKU code → SKU 详情
- `sku_id_map`：SKU id → SKU code
- `platform_sku_map`：平台 SKU → 内部 SKU
- `sku_group_attr`：SKU 组合属性

| 方法 | 用途 |
| ---- | ---- |
| `add(sku_dict)` | 增加 SKU 到本地缓存 |
| `dump()` / `load()` | 落盘 / 加载 |
| `get_sku_id(sku_code)` | - |
| `get_sku_name_by_shop_sku(platform_sku)` | - |
| `get_sku_name_by_sku_id(sku_id)` | - |
| `get_sku_group_attr(sku_id)` | 获取组合 SKU 属性 |
| `load_and_update_all_sku(client)` | 全量同步：遍历 `client.load_all_sku()` 填充 `sku_detail_variant`，再 `add` + `dump` |

## SkuGroupMatcher

读取规则文件，对 product_name 子串匹配返回分组标签：
- 规则格式：`label` / `matches` 成对，`matches` 用 `|` 分隔关键词
- 未命中返回 `"UNKNOWN"`

主要在 ES 同步任务中给销售统计加分组标签。

## 工厂方法（big_seller_util）

| 方法 | 缓存 | 说明 |
| ---- | ---- | ---- |
| `build_big_seller_client()` | 单例 holder 300s | 首次创建并 `login`；超过 `__BIG_SELLER_LOGIN_TIMEOUT_SEC__ = 60` 秒强制重新登录；否则 `load_cookies` |
| `build_shop_manager()` | - | 读取 `cookies_dir/shop_group.json` |
| `build_sku_manager()` | holder 60s | 读取 `cookies_dir/all_sku.json` 并 `load()` |
| `build_backend(project_id)` | - | 创建无 session 耦合的 `MysqlBackend`（与 `request_context.get_backend` 区别） |

## 错误处理与重试

- 登录失败抛异常，由调用方决定是否重试
- 请求级失败：上游业务接口需在自身实现重试或返回 `1008` 业务异常码
- 验证码识别失败时 `get_valid_verify_code` 内部已做 10 次重试

## Cookie 与凭证目录

- 默认 `cookies_dir`：`../cookies`（相对运行 cwd），可配置覆盖
- 主要文件：
  - `big_seller.cookies`：登录会话
  - `shop_group.json`：店铺信息
  - `all_sku.json`：SKU 主数据
  - `all_variant_sku_mapping.json`：变体 SKU 映射
  - `order_cache/{order_id}.json`：订单详情缓存（`auto_preload_order` 写入）

## 注意事项

- `cookies/` 目录不入版本控制（已在 `.gitignore`）
- BigSeller 风控较敏感，`get_order_detail` 必须经过 `GLOBAL_RATE_LIMITER`
- 验证码识别的 `ydm_token` 是按调用次数计费，长时间死循环重试会产生费用
- BigSeller 接口签名/参数可能随版本更新，文档以代码实现为准
