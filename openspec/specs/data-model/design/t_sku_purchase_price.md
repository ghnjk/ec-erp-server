# t_sku_purchase_price SKU 采购价格表

## 业务用途

存储 (project, SKU, supplier) 三元组的采购单价。一个 SKU 可由多个供应商提供，价格各不相同；同一供应商对同一 SKU 在不同 project 也可能有不同价格。

## 主键

`PRIMARY KEY (Fproject_id, Fsku, Fsupplier_id)`

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS `t_sku_purchase_price` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` VARCHAR(256) NOT NULL COMMENT '商品SKU',
  `Fsupplier_id` INT NOT NULL COMMENT '供应商id',
  `Fsupplier_name` VARCHAR(128) COMMENT '供应商名',
  `Fpurchase_price` INT COMMENT '供应价',
  `Fsku_group` VARCHAR(256) COMMENT 'SKU分组',
  `Fsku_name` VARCHAR(1024) COMMENT '商品名称',
  `Ferp_sku_image_url` VARCHAR(10240) COMMENT '商品图片链接',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Fsku`, `Fsupplier_id`),
  KEY `idx_supplier_name` (`Fsupplier_name`),
  KEY `idx_sku_group` (`Fsku_group`),
  KEY `idx_sku_name` (`Fsku_name`(255)),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU采购价格表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fproject_id` | VARCHAR(128) | 是 | - | 所属项目 |
| `Fsku` | VARCHAR(256) | 是 | - | 商品 SKU |
| `Fsupplier_id` | INT | 是 | - | 供应商 ID |
| `Fsupplier_name` | VARCHAR(128) | 否 | NULL | 供应商名（冗余，便于检索） |
| `Fpurchase_price` | INT | 否 | NULL | 采购单价，**单位：分** |
| `Fsku_group` | VARCHAR(256) | 否 | NULL | SKU 分组（冗余） |
| `Fsku_name` | VARCHAR(1024) | 否 | NULL | 商品名（冗余） |
| `Ferp_sku_image_url` | VARCHAR(10240) | 否 | NULL | 商品图片 URL（冗余） |
| `Fis_delete` | INT | 是 | 0 | 逻辑删除 |
| `Fversion` | INT | 是 | 0 | 乐观锁版本 |
| `Fmodify_user` | VARCHAR(128) | 是 | `''` | 修改人 |
| `Fcreate_time` | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| `Fmodify_time` | DATETIME | 是 | CURRENT_TIMESTAMP ON UPDATE | 修改时间 |

> **金额单位**：`Fpurchase_price` 是 INT，单位为「分」（避免浮点精度问题）。

## 索引

| 索引 | 列 | 类型 |
| ---- | -- | ---- |
| PRIMARY | `(Fproject_id, Fsku, Fsupplier_id)` | 复合主键 |
| `idx_supplier_name` | `Fsupplier_name` | 普通 |
| `idx_sku_group` | `Fsku_group` | 普通 |
| `idx_sku_name` | `Fsku_name(255)` | 前缀索引 |
| `idx_create_time` | `Fcreate_time` | 普通 |
| `idx_modify_time` | `Fmodify_time` | 普通 |

## DTO 类

```python
class SkuPurchasePriceDto(DtoBase):
    __tablename__ = "t_sku_purchase_price"
    __table_args__ = (PrimaryKeyConstraint(
        "Fproject_id", "Fsku", "Fsupplier_id"
    ), {"mysql_default_charset": "utf8"})
    project_id: Mapped[str] = Column('Fproject_id', String(128), comment='所属项目ID')
    sku: Mapped[str] = Column('Fsku', String(256), comment='商品SKU')
    supplier_id: Mapped[int] = Column('Fsupplier_id', Integer, comment='供应商id')
    supplier_name: Mapped[str] = Column('Fsupplier_name', String(128), index=True, comment='供应商名')
    purchase_price: Mapped[int] = Column('Fpurchase_price', Integer, comment='供应价')
    sku_group: Mapped[str] = Column('Fsku_group', String(256), index=True, comment='商品SKU分组')
    sku_name: Mapped[str] = Column('Fsku_name', String(1024), index=True, comment='商品名称')
    erp_sku_image_url: Mapped[str] = Column('Ferp_sku_image_url', String(10240), comment='商品图片链接')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0", comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0", comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="", comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, ...)
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, ...)
    columns = [
        "project_id", "sku", "supplier_id", "supplier_name", "sku_group",
        "sku_name", "erp_sku_image_url", "purchase_price",
        "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]
```

## CRUD 方法

| 方法 | 说明 |
| ---- | ---- |
| `store_sku_purchase_price(...)` | upsert |
| `search_sku_purchase_price(offset, limit) -> (total, list)` | 分页查询 |
| `get_sku_purchase_price(supplier_id, sku) -> Optional[SkuPurchasePriceDto]` | 三元组查询 |

## 关联表 / 模块

- [t_sku_info](./t_sku_info.md)：通过 `(Fproject_id, Fsku)` 关联
- [t_supplier_info](./t_supplier_info.md)：通过 `Fsupplier_id` 关联
- [supplier_module_spec](../../supplier_module_spec.md)：`search_sku_purchase_price`、`query_sku_purchase_price` 接口

## Change-Log

### 初始版本 - SKU 采购价格表创建

**变更类型**：新增表

**变更原因**：管理 SKU × 供应商维度的采购价格。

**变更内容**：
- 新建 `t_sku_purchase_price`
- 复合主键 `(Fproject_id, Fsku, Fsupplier_id)`
- 金额字段 `Fpurchase_price` 单位：分

**新建库**：直接执行 `docs/ec_erp_db.sql`。

**存量库 ALTER 脚本**：

```sql
CREATE TABLE IF NOT EXISTS `t_sku_purchase_price` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` VARCHAR(256) NOT NULL COMMENT '商品SKU',
  `Fsupplier_id` INT NOT NULL COMMENT '供应商id',
  `Fsupplier_name` VARCHAR(128) COMMENT '供应商名',
  `Fpurchase_price` INT COMMENT '供应价',
  `Fsku_group` VARCHAR(256) COMMENT 'SKU分组',
  `Fsku_name` VARCHAR(1024) COMMENT '商品名称',
  `Ferp_sku_image_url` VARCHAR(10240) COMMENT '商品图片链接',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Fsku`, `Fsupplier_id`),
  KEY `idx_supplier_name` (`Fsupplier_name`),
  KEY `idx_sku_group` (`Fsku_group`),
  KEY `idx_sku_name` (`Fsku_name`(255)),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU采购价格表';
```

**执行说明**：
- 在每个国家库分别执行
- 风险评估：低
- 回滚方式：`DROP TABLE IF EXISTS t_sku_purchase_price;`

**关联代码改动**：
- ORM：`SkuPurchasePriceDto`
- API：[ec_erp_api/apis/supplier.py](../../../../ec_erp_api/apis/supplier.py)
