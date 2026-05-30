# 搜索SKU采购价格

## 接口信息

- **接口路径**: `/erp_api/supplier/search_sku_purchase_price`
- **请求方法**: POST
- **接口描述**: 分页查询SKU的采购价格信息
- **权限要求**: 需要 `PMS_SUPPLIER` 权限

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_page | int | 是 | 当前页码，从1开始 |
| page_size | int | 是 | 每页记录数 |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 数据对象 |
| ∟ total | int | 总记录数 |
| ∟ list | array | SKU采购价格列表 |
| &nbsp;&nbsp;∟ sku | string | SKU编码 |
| &nbsp;&nbsp;∟ sku_group | string | SKU分组 |
| &nbsp;&nbsp;∟ sku_name | string | SKU名称 |
| &nbsp;&nbsp;∟ supplier_id | int | 供应商ID |
| &nbsp;&nbsp;∟ supplier_name | string | 供应商名称 |
| &nbsp;&nbsp;∟ purchase_price | int | 采购价格（单位：分） |
| &nbsp;&nbsp;∟ erp_sku_image_url | string | SKU图片URL |
| &nbsp;&nbsp;∟ project_id | string | 所属项目ID |
| &nbsp;&nbsp;∟ create_time | string | 创建时间 |
| &nbsp;&nbsp;∟ modify_time | string | 修改时间 |
| &nbsp;&nbsp;∟ modify_user | string | 修改人 |
| &nbsp;&nbsp;∟ is_delete | int | 是否删除 |
| &nbsp;&nbsp;∟ version | int | 版本号 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1008 | 权限不足 |

## 请求示例

```json
{
  "current_page": 1,
  "page_size": 10
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "list": [
      {
        "create_time": "2024-03-02 21:51:42",
        "erp_sku_image_url": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/20230706074750640dc2ad09607578d8b1546866c91cf7.jpg?imageView2/1/w/300/h/300",
        "is_delete": 0,
        "modify_time": "2024-03-02 21:51:42",
        "modify_user": "",
        "project_id": "philipine",
        "purchase_price": 30,
        "sku": "A-11-Beige Reed leaf",
        "sku_group": "藤条/芦苇叶",
        "sku_name": "米色芦苇叶",
        "supplier_id": 4,
        "supplier_name": "新草地厂家(麦森人造草坪）",
        "version": 0
      },
      {
        "create_time": "2024-03-02 21:51:42",
        "erp_sku_image_url": "https://bigseller-1251220924.cos.accelerate.myqcloud.com/album/279590/202401030650052d9b6760d759a189c5a7d3d72cd5a693.jpg?imageView2/1/w/300/h/300",
        "is_delete": 0,
        "modify_time": "2024-03-02 21:51:42",
        "modify_user": "",
        "project_id": "philipine",
        "purchase_price": 30,
        "sku": "A-11-Blue Reed leaf",
        "sku_group": "藤条/芦苇叶",
        "sku_name": "蓝色芦苇叶",
        "supplier_id": 4,
        "supplier_name": "新草地厂家(麦森人造草坪）",
        "version": 0
      }
    ],
    "total": 5
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991821760
}
```

## 业务逻辑说明

1. 验证用户权限
2. 根据分页参数查询SKU采购价格列表
3. 返回分页结果

## 注意事项

- 采购价格单位为"分"，显示时需要除以100转换为元
- 接口会根据当前项目ID自动过滤数据
- 同一个SKU可能有多个供应商的采购价格记录
- 价格信息在采购单确认时自动更新

