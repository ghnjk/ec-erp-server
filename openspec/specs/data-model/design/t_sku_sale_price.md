# t_sku_sale_price SKU 销售价格表

## 业务用途

存储 (project, SKU) 维度的销售单价，供销售订单创建与销售统计使用。

> ⚠️ **金额单位差异**：与采购价 `t_sku_purchase_price.Fpurchase_price`（INT 单位"分"）不同，本表 `Funit_price` 是 **FLOAT** 类型，单位为「元」（历史遗留），新增字段时不要沿用此差异。

## 主键

`PRIMARY KEY (Fproject_id, Fsku)`

## CREATE TABLE

```sql
CREATE TABLE `t_sku_sale_price` (
  `Fproject_id` varchar(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` varchar(128) NOT NULL COMMENT '商品SKU',
  `Funit_price` float DEFAULT NULL COMMENT '单价',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`,`Fsku`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU销售价格表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fproject_id` | VARCHAR(128) | 是 | - | 项目 ID |
| `Fsku` | VARCHAR(128) | 是 | - | 商品 SKU（**注意：长度 128，比通用 SKU 表的 256 短**） |
| `Funit_price` | FLOAT | 否 | NULL | 销售单价，**单位：元（与采购价的"分"不同）** |
| `Fcreate_time` | DATETIME | 否 | NULL | 创建时间（**未设置 NOT NULL，与其他表不同**） |
| `Fmodify_time` | DATETIME | 否 | NULL | 修改时间（**未设置 NOT NULL 与 ON UPDATE**，与其他表不同） |

> **历史例外**：
> - `Funit_price` 使用 FLOAT 而非 INT（分）
> - `Fsku` 长度仅 128
> - `Fcreate_time` / `Fmodify_time` 无 `NOT NULL DEFAULT` 与 `ON UPDATE` 自动管理（应用层手工赋值）
> - 无 `Fis_delete` / `Fversion` / `Fmodify_user`

## 索引

| 索引 | 列 |
| ---- | -- |
| PRIMARY | `(Fproject_id, Fsku)` |
| `idx_create_time` | `Fcreate_time` |
| `idx_modify_time` | `Fmodify_time` |

## DTO 类

```python
class SkuSalePrice(DtoBase):
    __tablename__ = "t_sku_sale_price"
    __table_args__ = (PrimaryKeyConstraint(
        "Fproject_id", "Fsku"
    ), {"mysql_default_charset": "utf8"})
    project_id: Mapped[str] = Column('Fproject_id', String(128), comment='所属项目ID')
    sku: Mapped[str] = Column('Fsku', String(128), comment='商品SKU')
    unit_price: Mapped[float] = Column('Funit_price', Float, comment='单价')
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, ...)
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, ...)
    columns = [
        "project_id", "sku", "unit_price", "create_time", "modify_time"
    ]
```

## CRUD 方法

| 方法 | 说明 |
| ---- | ---- |
| `store_sku_sale_price(sku_sale_price)` | upsert |
| `get_sku_sale_price(sku) -> Optional[SkuSalePrice]` | 精确查询 |
| `search_sku_sale_price(sku, offset, limit) -> (total, list)` | 模糊搜索（按 modify_time 降序） |
| `_get_sku_sale_price(session, sku)` (静态) | 内部查询 |

## 关联表 / 模块

- [t_sku_info](./t_sku_info.md)：通过 `(Fproject_id, Fsku)` 关联
- [t_sale_order](./t_sale_order.md)：销售订单创建时引用单价
- [sale_module_spec](../../sale_module_spec.md)：`save_sku_sale_price`、`search_sku_sale_price`

## Change-Log

### 初始版本 - SKU 销售价格表创建

**变更类型**：新增表

**变更原因**：销售订单需要单价数据。

**变更内容**：
- 新建 `t_sku_sale_price`
- 复合主键 `(Fproject_id, Fsku)`
- 历史例外：使用 FLOAT 元值；无审计字段；时戳列无默认值

**新建库**：直接执行 `docs/ec_erp_db.sql`。

**存量库 ALTER 脚本**：

```sql
CREATE TABLE IF NOT EXISTS `t_sku_sale_price` (
  `Fproject_id` varchar(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` varchar(128) NOT NULL COMMENT '商品SKU',
  `Funit_price` float DEFAULT NULL COMMENT '单价',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`,`Fsku`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU销售价格表';
```

**执行说明**：
- 在每个国家库分别执行
- 风险评估：低
- 回滚方式：`DROP TABLE IF EXISTS t_sku_sale_price;`

**关联代码改动**：
- ORM：`SkuSalePrice`
- API：[ec_erp_api/apis/sale.py](../../../../ec_erp_api/apis/sale.py) `save_sku_sale_price`、`search_sku_sale_price`

### 改进建议（待执行）

当前表存在以下技术债务，建议在后续迭代中规范化：

1. **金额类型对齐**：将 `Funit_price` 由 FLOAT 元改为 INT（分），需同步修改 ORM、API 入参、前端展示
2. **补充审计字段**：增加 `Fis_delete`、`Fversion`、`Fmodify_user`
3. **SKU 长度对齐**：将 `Fsku` 由 128 扩展到与 `t_sku_info` 一致的 256
4. **时戳自动化**：增加 `NOT NULL DEFAULT CURRENT_TIMESTAMP` 与 `ON UPDATE CURRENT_TIMESTAMP`

如需执行上述改造，参考通用 ALTER 模板：

```sql
-- 改造为 INT（分）单位（需先迁移数据）
ALTER TABLE t_sku_sale_price ADD COLUMN `Funit_price_cents` INT COMMENT '销售单价（单位：分）' AFTER `Fsku`;
UPDATE t_sku_sale_price SET Funit_price_cents = ROUND(Funit_price * 100) WHERE Funit_price IS NOT NULL;
-- 应用切换后再 DROP COLUMN Funit_price
```
