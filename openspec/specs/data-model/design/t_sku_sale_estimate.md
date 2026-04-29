# t_sku_sale_estimate SKU 销售数据统计表

## 业务用途

按 (project, 订单日期, SKU, 店铺) 四元维度聚合的销售估算数据，覆盖销售额、销量、取消、退款、有效金额等多维度指标，是数据看板的核心表之一。

由 [auto_sync_tools/sync_order_to_es.py](../../../../auto_sync_tools/sync_order_to_es.py) 定时从 BigSeller 同步生成。

## 主键

`PRIMARY KEY (Fproject_id, Forder_date, Fsku, Fshop_id)`

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS `t_sku_sale_estimate` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Forder_date` DATETIME NOT NULL COMMENT '订单日期',
  `Fsku` VARCHAR(256) NOT NULL COMMENT '商品SKU',
  `Fshop_id` VARCHAR(256) NOT NULL COMMENT '店铺id',
  `Fsku_class` VARCHAR(256) COMMENT 'SKU大类',
  `Fsku_group` VARCHAR(256) COMMENT 'SKU分组',
  `Fsku_name` VARCHAR(1024) COMMENT '商品名称',
  `Fshop_name` VARCHAR(256) NOT NULL DEFAULT '' COMMENT '店铺名',
  `Fshop_owner` VARCHAR(256) NOT NULL DEFAULT '' COMMENT '店铺运营人员',
  `Fsale_amount` INT NOT NULL DEFAULT 0 COMMENT '销售额',
  `Fsale_quantity` INT NOT NULL DEFAULT 0 COMMENT '销售的sku量',
  `Fcancel_amount` INT NOT NULL DEFAULT 0 COMMENT '取消的销售额',
  `Fcancel_quantity` INT NOT NULL DEFAULT 0 COMMENT '取消的sku量',
  `Fcancel_orders` INT NOT NULL DEFAULT 0 COMMENT '取消的订单数',
  `Frefund_amount` INT NOT NULL DEFAULT 0 COMMENT '退款的销售额',
  `Frefund_quantity` INT NOT NULL DEFAULT 0 COMMENT '退款的sku量',
  `Frefund_orders` INT NOT NULL DEFAULT 0 COMMENT '退款的订单数',
  `Fefficient_amount` INT NOT NULL DEFAULT 0 COMMENT '有效销售额',
  `Fefficient_quantity` INT NOT NULL DEFAULT 0 COMMENT '有效的sku量',
  `Fefficient_orders` INT NOT NULL DEFAULT 0 COMMENT '有效订单数',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Forder_date`, `Fsku`, `Fshop_id`),
  KEY `idx_sku_class` (`Fsku_class`),
  KEY `idx_sku_group` (`Fsku_group`),
  KEY `idx_sku_name` (`Fsku_name`(255)),
  KEY `idx_shop_name` (`Fshop_name`),
  KEY `idx_shop_owner` (`Fshop_owner`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU销售数据统计表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fproject_id` | VARCHAR(128) | 是 | - | 项目 ID |
| `Forder_date` | DATETIME | 是 | - | 订单日期（日粒度） |
| `Fsku` | VARCHAR(256) | 是 | - | 商品 SKU |
| `Fshop_id` | VARCHAR(256) | 是 | - | 店铺 ID |
| `Fsku_class` | VARCHAR(256) | 否 | NULL | SKU 大类 |
| `Fsku_group` | VARCHAR(256) | 否 | NULL | SKU 分组（由 `SkuGroupMatcher` 推断） |
| `Fsku_name` | VARCHAR(1024) | 否 | NULL | 商品名称 |
| `Fshop_name` | VARCHAR(256) | 是 | `''` | 店铺名 |
| `Fshop_owner` | VARCHAR(256) | 是 | `''` | 店铺运营人员（来自 `ShopManager`） |
| `Fsale_amount` | INT | 是 | 0 | 销售额，**单位：分** |
| `Fsale_quantity` | INT | 是 | 0 | 销售的 SKU 数量 |
| `Fcancel_amount` | INT | 是 | 0 | 取消的销售额，**单位：分** |
| `Fcancel_quantity` | INT | 是 | 0 | 取消的 SKU 数量 |
| `Fcancel_orders` | INT | 是 | 0 | 取消的订单数 |
| `Frefund_amount` | INT | 是 | 0 | 退款的销售额，**单位：分** |
| `Frefund_quantity` | INT | 是 | 0 | 退款的 SKU 数量 |
| `Frefund_orders` | INT | 是 | 0 | 退款的订单数 |
| `Fefficient_amount` | INT | 是 | 0 | 有效销售额（销售-取消-退款），**单位：分** |
| `Fefficient_quantity` | INT | 是 | 0 | 有效 SKU 数量 |
| `Fefficient_orders` | INT | 是 | 0 | 有效订单数 |
| `Fis_delete` | INT | 是 | 0 | 逻辑删除 |
| `Fversion` | INT | 是 | 0 | 乐观锁版本 |
| `Fmodify_user` | VARCHAR(128) | 是 | `''` | 修改人 |
| `Fcreate_time` | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| `Fmodify_time` | DATETIME | 是 | CURRENT_TIMESTAMP ON UPDATE | 修改时间 |

> **金额单位**：所有 `*_amount` 字段为 INT，单位「分」。

## 索引

| 索引 | 列 |
| ---- | -- |
| PRIMARY | `(Fproject_id, Forder_date, Fsku, Fshop_id)` |
| `idx_sku_class` | `Fsku_class` |
| `idx_sku_group` | `Fsku_group` |
| `idx_sku_name` | `Fsku_name(255)` |
| `idx_shop_name` | `Fshop_name` |
| `idx_shop_owner` | `Fshop_owner` |
| `idx_create_time` | `Fcreate_time` |
| `idx_modify_time` | `Fmodify_time` |

## DTO 类

```python
class SkuSaleEstimateDto(DtoBase):
    __tablename__ = "t_sku_sale_estimate"
    __table_args__ = (PrimaryKeyConstraint(
        "Fproject_id", "Forder_date", "Fsku", "Fshop_id"
    ), {"mysql_default_charset": "utf8"})
    project_id: Mapped[str] = Column('Fproject_id', String(128), comment='所属项目ID')
    order_date: Mapped[datetime] = Column('Forder_date', DateTime, default=datetime.now(),
                                          server_default=sql.func.now(), comment='订单日期')
    sku: Mapped[str] = Column('Fsku', String(256), comment='商品SKU')
    shop_id: Mapped[str] = Column('Fshop_id', String(256), comment='店铺id')
    sku_class: Mapped[str] = Column('Fsku_class', String(256), index=True, comment='商品SKU大类')
    sku_group: Mapped[str] = Column('Fsku_group', String(256), index=True, comment='商品SKU分组')
    sku_name: Mapped[str] = Column('Fsku_name', String(1024), index=True, comment='商品名称')
    shop_name: Mapped[str] = Column('Fshop_name', String(256), index=True, default="", server_default="", comment='店铺名')
    shop_owner: Mapped[str] = Column('Fshop_owner', String(256), index=True, default="", server_default="",
                                     comment='店铺运营人员')
    sale_amount: Mapped[int] = Column('Fsale_amount', Integer, default=0, server_default="0", comment='销售额')
    sale_quantity: Mapped[int] = Column('Fsale_quantity', Integer, default=0, server_default="0", comment='销售的sku量')
    cancel_amount: Mapped[int] = Column('Fcancel_amount', Integer, default=0, server_default="0", comment='取消的销售额')
    cancel_quantity: Mapped[int] = Column('Fcancel_quantity', Integer, default=0, server_default="0", comment='取消的sku量')
    cancel_orders: Mapped[int] = Column('Fcancel_orders', Integer, default=0, server_default="0", comment='取消的订单数')
    refund_amount: Mapped[int] = Column('Frefund_amount', Integer, default=0, server_default="0", comment='退款的销售额')
    refund_quantity: Mapped[int] = Column('Frefund_quantity', Integer, default=0, server_default="0", comment='退款的sku量')
    refund_orders: Mapped[int] = Column('Frefund_orders', Integer, default=0, server_default="0", comment='退款的订单数')
    efficient_amount: Mapped[int] = Column('Fefficient_amount', Integer, default=0, server_default="0", comment='有效销售额')
    efficient_quantity: Mapped[int] = Column('Fefficient_quantity', Integer, default=0, server_default="0", comment='有效的sku量')
    efficient_orders: Mapped[int] = Column('Fefficient_orders', Integer, default=0, server_default="0", comment='有效订单数')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0", comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0", comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="", comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, ...)
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, ...)
    columns = [
        "project_id", "order_date", "sku", "shop_id",
        "sku_class", "sku_group", "sku_name", "shop_name",
        "shop_owner", "sale_amount", "sale_quantity", "cancel_amount", "cancel_quantity",
        "refund_amount", "refund_quantity", "efficient_amount", "efficient_quantity",
        "cancel_orders", "refund_orders", "efficient_orders",
        "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]
```

## CRUD 方法

| 方法 | 说明 |
| ---- | ---- |
| `store_sku_sale_estimate(est)` | upsert 销售估算 |
| `search_sku_sale_estimate(begin_date, end_date, sku) -> List` | 按日期区间查询某 SKU 的所有店铺销售记录 |
| `_get_sku_sale_estimate(session, order_date, sku, shop_id)` (静态) | 内部查询 |

## 关联表 / 模块

- [t_sku_info](./t_sku_info.md)：通过 `(Fproject_id, Fsku)` 关联
- ES 索引 `ec_analysis_sku`：双写（每条记录同时写 MySQL 与 ES）
- [auto_sync_tools_spec](../../auto_sync_tools_spec.md)：`sync_order_to_es.py`
- [common_utilities_spec](../../common_utilities_spec.md)：`sku_sale_estimate.SkuSaleEstimate` 聚合工具

## Change-Log

### 初始版本 - SKU 销售数据统计表创建

**变更类型**：新增表

**变更原因**：销售数据看板与库存预测的基础聚合表。

**变更内容**：
- 新建 `t_sku_sale_estimate`
- 复合主键 `(Fproject_id, Forder_date, Fsku, Fshop_id)`
- 所有金额字段单位：分

**新建库**：直接执行 `docs/ec_erp_db.sql`。

**存量库 ALTER 脚本**：

```sql
CREATE TABLE IF NOT EXISTS `t_sku_sale_estimate` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Forder_date` DATETIME NOT NULL COMMENT '订单日期',
  `Fsku` VARCHAR(256) NOT NULL COMMENT '商品SKU',
  `Fshop_id` VARCHAR(256) NOT NULL COMMENT '店铺id',
  `Fsku_class` VARCHAR(256) COMMENT 'SKU大类',
  `Fsku_group` VARCHAR(256) COMMENT 'SKU分组',
  `Fsku_name` VARCHAR(1024) COMMENT '商品名称',
  `Fshop_name` VARCHAR(256) NOT NULL DEFAULT '' COMMENT '店铺名',
  `Fshop_owner` VARCHAR(256) NOT NULL DEFAULT '' COMMENT '店铺运营人员',
  `Fsale_amount` INT NOT NULL DEFAULT 0 COMMENT '销售额',
  `Fsale_quantity` INT NOT NULL DEFAULT 0 COMMENT '销售的sku量',
  `Fcancel_amount` INT NOT NULL DEFAULT 0 COMMENT '取消的销售额',
  `Fcancel_quantity` INT NOT NULL DEFAULT 0 COMMENT '取消的sku量',
  `Fcancel_orders` INT NOT NULL DEFAULT 0 COMMENT '取消的订单数',
  `Frefund_amount` INT NOT NULL DEFAULT 0 COMMENT '退款的销售额',
  `Frefund_quantity` INT NOT NULL DEFAULT 0 COMMENT '退款的sku量',
  `Frefund_orders` INT NOT NULL DEFAULT 0 COMMENT '退款的订单数',
  `Fefficient_amount` INT NOT NULL DEFAULT 0 COMMENT '有效销售额',
  `Fefficient_quantity` INT NOT NULL DEFAULT 0 COMMENT '有效的sku量',
  `Fefficient_orders` INT NOT NULL DEFAULT 0 COMMENT '有效订单数',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Forder_date`, `Fsku`, `Fshop_id`),
  KEY `idx_sku_class` (`Fsku_class`),
  KEY `idx_sku_group` (`Fsku_group`),
  KEY `idx_sku_name` (`Fsku_name`(255)),
  KEY `idx_shop_name` (`Fshop_name`),
  KEY `idx_shop_owner` (`Fshop_owner`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU销售数据统计表';
```

**执行说明**：
- 在每个国家库分别执行
- 风险评估：低（新建表，初始为空，由定时任务回填）
- 回滚方式：`DROP TABLE IF EXISTS t_sku_sale_estimate;`

**关联代码改动**：
- ORM：`SkuSaleEstimateDto`
- 同步任务：`sync_order_to_es.py`、`sku_sale_estimate.SkuSaleEstimate`
