# 搜索供应商

## 接口信息

- **接口路径**: `/erp_api/supplier/search_supplier`
- **请求方法**: POST
- **接口描述**: 分页查询供应商列表
- **权限要求**: 需要 `PMS_SUPPLIER` 权限
- **Handler**: [ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `search_supplier`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_page | int | 是 | 当前页码，从 1 开始 |
| page_size | int | 是 | 每页记录数 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪 ID |
| data | object | 数据对象 |
| ∟ total | int | 总记录数 |
| ∟ list | array | 供应商列表（按 supplier_id 升序） |
| &nbsp;&nbsp;∟ supplier_id | int | 供应商 ID |
| &nbsp;&nbsp;∟ supplier_name | string | 供应商名称 |
| &nbsp;&nbsp;∟ wechat_account | string | 微信账号 |
| &nbsp;&nbsp;∟ detail | string | 详细信息（银行卡、联系方式等） |
| &nbsp;&nbsp;∟ project_id | string | 所属项目 |
| &nbsp;&nbsp;∟ create_time | string | 创建时间 |
| &nbsp;&nbsp;∟ modify_time | string | 修改时间 |
| &nbsp;&nbsp;∟ modify_user | string | 修改人 |
| &nbsp;&nbsp;∟ is_delete | int | 0=有效 |
| &nbsp;&nbsp;∟ version | int | 版本号 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "body": {
    "current_page": 1,
    "page_size": 10
  }
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "list": [
      {
        "create_time": "2024-02-24 21:05:51",
        "detail": "6212260408009471538 中国工商银行 宗子龙\n18531712555",
        "is_delete": 0,
        "modify_time": "2024-02-24 21:05:51",
        "modify_user": "",
        "project_id": "philipine",
        "supplier_id": 1,
        "supplier_name": "草地厂家(子龙)",
        "version": 0,
        "wechat_account": "-zilong"
      }
    ],
    "total": 2
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1708844000800
}
```

## 业务逻辑说明

1. 校验 `PMS_SUPPLIER` 权限
2. 计算 `offset = (current_page - 1) * page_size`
3. 调用 `backend.search_suppliers(offset, page_size)`，按 `supplier_id ASC` 排序
4. 通过 `pack_pagination_result(total, records)` 返回

## 关联

- 数据表：[t_supplier_info](../../../data-model/design/t_supplier_info.md)
- 模块 spec：[supplier_module_spec.md](../../../supplier_module_spec.md)
- 业务文档：[docs/erp_api/supplier/search_supplier.md](../../../../../docs/erp_api/supplier/search_supplier.md)

## 注意事项

- 自动按当前 session 的 `project_id` 过滤
- 返回的 `supplier_id == 10000000` 是占位"线下销售"

## Change-Log

### 初始版本 - 搜索供应商接口

**变更类型**：新增接口

**变更原因**：供应商管理基础查询。

**变更内容**：
- 新增 `POST /erp_api/supplier/search_supplier`

**前端影响**：供应商列表页使用。

**关联代码改动**：
- handler：[ec_erp_api/apis/supplier.py](../../../../../ec_erp_api/apis/supplier.py) `search_supplier`
- 数据表：[t_supplier_info](../../../data-model/design/t_supplier_info.md)
