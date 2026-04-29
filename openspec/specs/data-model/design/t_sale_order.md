# t_sale_order 销售订单表

## 业务用途

存储销售订单数据，支持订单的创建、修改、删除（逻辑删除）、提交至 BigSeller 出库。状态字段记录订单生命周期。

## 主键

`PRIMARY KEY (Forder_id)` AUTO_INCREMENT

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS `t_sale_order` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Forder_id` INT NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `Forder_date` DATETIME COMMENT '订单日期',
  `Fsale_sku_list` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '销售SKU列表，包含sku, sku_group, sku_name, erp_sku_image_url, unit_price, quantity, total_amount',
  `Ftotal_amount` FLOAT COMMENT '订单总金额',
  `Fstatus` VARCHAR(128) COMMENT '订单状态，待同步、已同步',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fcreate_time` DATETIME DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` DATETIME DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Forder_id`),
  KEY `idx_project_id` (`Fproject_id`),
  KEY `idx_order_date` (`Forder_date`),
  KEY `idx_status` (`Fstatus`),
  KEY `idx_is_delete` (`Fis_delete`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='销售订单表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fproject_id` | VARCHAR(128) | 是 | - | 项目 ID |
| `Forder_id` | INT | 是 | AUTO_INCREMENT | 订单 ID |
| `Forder_date` | DATETIME | 否 | NULL | 订单日期 |
| `Fsale_sku_list` | LONGTEXT (utf8mb4_bin) | 否 | NULL | 销售 SKU 列表（JSON 序列化字符串） |
| `Ftotal_amount` | FLOAT | 否 | NULL | 订单总金额，**单位：元（Float）** |
| `Fstatus` | VARCHAR(128) | 否 | NULL | 状态：`新建` / `已同步` |
| `Fis_delete` | INT | 是 | 0 | 逻辑删除（0=有效，1=已删除） |
| `Fcreate_time` | DATETIME | 否 | NULL | 创建时间（**应用层赋值**，无 DEFAULT） |
| `Fmodify_time` | DATETIME | 否 | NULL | 修改时间（**应用层赋值**，无 ON UPDATE） |

> **历史差异**：
> - `Ftotal_amount` 使用 FLOAT 元值（与采购模块"分整数"约定不同）
> - `Fsale_sku_list` ORM 声明为 JSON，但 SQL 建表使用 `LONGTEXT utf8mb4_bin`（兼容更长内容）
> - 时戳无 DEFAULT 与 ON UPDATE，由应用层赋值
> - 无 `Fversion` / `Fmodify_user`

### `Fsale_sku_list` JSON 结构

```json
[
  {
    "sku": "G-2-grape leaves",
    "sku_group": "藤条",
    "sku_name": "葡萄叶",
    "erp_sku_image_url": "https://...",
    "unit_price": 1.5,
    "quantity": 30,
    "total_amount": 45.0
  }
]
```

## 状态机

```
新建 → 已同步
        ↑
   submit_sale_order
   (调用 BigSeller 出库)
```

## 索引

| 索引 | 列 |
| ---- | -- |
| PRIMARY | `Forder_id` |
| `idx_project_id` | `Fproject_id` |
| `idx_order_date` | `Forder_date` |
| `idx_status` | `Fstatus` |
| `idx_is_delete` | `Fis_delete` |
| `idx_create_time` | `Fcreate_time` |
| `idx_modify_time` | `Fmodify_time` |

## DTO 类

```python
class SaleOrder(DtoBase):
    __tablename__ = "t_sale_order"
    __table_args__ = {"mysql_default_charset": "utf8"}
    project_id: Mapped[str] = Column('Fproject_id', String(128), index=True, comment='所属项目ID')
    order_id: Mapped[int] = Column('Forder_id', Integer, primary_key=True, autoincrement=True, comment='订单ID')
    order_date: Mapped[datetime] = Column('Forder_date', DateTime, comment='订单日期')
    sale_sku_list: Mapped[str] = Column('Fsale_sku_list', JSON,
        comment='销售SKU列表，包含sku, sku_group, sku_name, erp_sku_image_url, unit_price, quantity, total_amount')
    total_amount: Mapped[float] = Column('Ftotal_amount', Float, comment='订单总金额')
    status: Mapped[str] = Column('Fstatus', String(128), comment='订单状态， 待同步、已同步')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, index=True, default=0, server_default='0', comment='是否逻辑删除, 1: 删除')
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, ...)
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, ...)
    columns = [
        "project_id", "order_id", "order_date", "sale_sku_list", "total_amount", "status", "is_delete",
        "create_time", "modify_time"
    ]
```

## CRUD 方法

| 方法 | 说明 |
| ---- | ---- |
| `create_sale_order(sale_order) -> order_id` | 创建（强制 `order_id=None`，由 DB autoincrement 生成）|
| `update_sale_order(sale_order)` | 更新（按 `order_id` 查找） |
| `delete_sale_order(order_id)` | 逻辑删除（`Fis_delete = 1`） |
| `get_sale_order(order_id) -> Optional[SaleOrder]` | 按 ID 查询 |
| `search_sale_order(status, begin_date, end_date, offset, limit) -> (total, list)` | 多条件分页查询，自动过滤 `Fis_delete == 0` |
| `_get_sale_order(session, order_id)` (静态) | 内部查询 |

## 关联表 / 模块

- [t_sku_sale_price](./t_sku_sale_price.md)：单价来源
- [t_sku_info](./t_sku_info.md)：SKU 主数据
- [sale_module_spec](../../sale_module_spec.md)：`create_sale_order` / `update_sale_order` / `delete_sale_order` / `submit_sale_order` / `search_sale_order`
- [BigSellerClient.add_stock_to_erp](../../bigseller_integration_spec.md)：`submit_sale_order` 出库时调用

## Change-Log

### 初始版本 - 销售订单表创建

**变更类型**：新增表

**变更原因**：管理销售订单全生命周期，并支持向 BigSeller ERP 同步出库。

**变更内容**：
- 新建 `t_sale_order`
- AUTO_INCREMENT 主键 `Forder_id`
- `Fsale_sku_list` 使用 LONGTEXT utf8mb4_bin（支持更长 JSON 内容与 emoji）
- 历史例外：`Ftotal_amount` 使用 FLOAT 元值；无 `Fversion`/`Fmodify_user`

**新建库**：直接执行 `docs/ec_erp_db.sql`。

**存量库 ALTER 脚本**：

```sql
CREATE TABLE IF NOT EXISTS `t_sale_order` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Forder_id` INT NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `Forder_date` DATETIME COMMENT '订单日期',
  `Fsale_sku_list` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '销售SKU列表',
  `Ftotal_amount` FLOAT COMMENT '订单总金额',
  `Fstatus` VARCHAR(128) COMMENT '订单状态',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fcreate_time` DATETIME DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` DATETIME DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Forder_id`),
  KEY `idx_project_id` (`Fproject_id`),
  KEY `idx_order_date` (`Forder_date`),
  KEY `idx_status` (`Fstatus`),
  KEY `idx_is_delete` (`Fis_delete`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='销售订单表';
```

**执行说明**：
- 在每个国家库分别执行
- 风险评估：低（新建表）
- 回滚方式：`DROP TABLE IF EXISTS t_sale_order;`

**关联代码改动**：
- ORM：`SaleOrder`
- API：[ec_erp_api/apis/sale.py](../../../../ec_erp_api/apis/sale.py)
- 业务：调用 BigSellerClient 出库

### 改进建议（待执行）

1. **金额类型对齐**：`Ftotal_amount` 由 FLOAT 元改为 INT（分）
2. **补充审计字段**：增加 `Fversion`、`Fmodify_user`
3. **时戳自动化**：增加 `NOT NULL DEFAULT CURRENT_TIMESTAMP` 与 `ON UPDATE CURRENT_TIMESTAMP`
4. **`Fstatus` 标准化**：当前实现中 status 字符串值与 SQL 注释存在差异（注释「待同步」/ 实现「新建」），需统一
