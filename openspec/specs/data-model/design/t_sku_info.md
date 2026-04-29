# t_sku_info SKU 商品信息表

## 业务用途

存储 SKU 主数据：基本信息、库存、销售估算、ERP 关联映射。是供应链与销售模块的核心表。

库存与销量字段（`Finventory`、`Favg_sell_quantity`、`Finventory_support_days`、`Fshipping_stock_quantity`）由 [auto_sync_tools/sync_sku_inventory.py](../../../../auto_sync_tools/sync_sku_inventory.py) 定时从 BigSeller 同步刷新。

## 主键

`PRIMARY KEY (Fproject_id, Fsku)`

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS `t_sku_info` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` VARCHAR(256) NOT NULL COMMENT '商品SKU',
  `Fsku_group` VARCHAR(256) COMMENT 'SKU分组',
  `Fsku_name` VARCHAR(1024) COMMENT '商品名称',
  `Fsku_unit_name` VARCHAR(256) NOT NULL DEFAULT '' COMMENT '采购单位',
  `Fsku_unit_quantity` INT NOT NULL DEFAULT 1 COMMENT '每个单位的sku数',
  `Finventory` INT NOT NULL DEFAULT 0 COMMENT '库存量',
  `Favg_sell_quantity` FLOAT NOT NULL DEFAULT 0.0 COMMENT '平均每天销售量',
  `Finventory_support_days` INT NOT NULL DEFAULT 0 COMMENT '库存支撑天数预估',
  `Fshipping_stock_quantity` INT NOT NULL DEFAULT 0 COMMENT '海运中的sku数',
  `Ferp_sku_name` VARCHAR(1024) COMMENT 'ERP商品名称',
  `Ferp_sku_image_url` VARCHAR(10240) COMMENT '商品图片链接',
  `Ferp_sku_id` VARCHAR(256) COMMENT 'erp上sku id',
  `Ferp_sku_info` JSON COMMENT 'erp上商品扩展信息',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Fsku`),
  KEY `idx_sku_group` (`Fsku_group`),
  KEY `idx_sku_name` (`Fsku_name`(255)),
  KEY `idx_erp_sku_name` (`Ferp_sku_name`(255)),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU商品信息表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fproject_id` | VARCHAR(128) | 是 | - | 所属项目 |
| `Fsku` | VARCHAR(256) | 是 | - | 商品 SKU 编码 |
| `Fsku_group` | VARCHAR(256) | 否 | NULL | SKU 分组（用于聚合显示） |
| `Fsku_name` | VARCHAR(1024) | 否 | NULL | 商品名称 |
| `Fsku_unit_name` | VARCHAR(256) | 是 | `''` | 采购单位名（"个"/"包"/"箱"） |
| `Fsku_unit_quantity` | INT | 是 | 1 | 每个采购单位包含的 SKU 数量 |
| `Finventory` | INT | 是 | 0 | 当前库存量 |
| `Favg_sell_quantity` | FLOAT | 是 | 0.0 | 平均每天销售量 |
| `Finventory_support_days` | INT | 是 | 0 | 库存支撑天数预估 |
| `Fshipping_stock_quantity` | INT | 是 | 0 | 海运中（在途）SKU 数 |
| `Ferp_sku_name` | VARCHAR(1024) | 否 | NULL | ERP 中的商品名称 |
| `Ferp_sku_image_url` | VARCHAR(10240) | 否 | NULL | ERP 商品图片 URL |
| `Ferp_sku_id` | VARCHAR(256) | 否 | NULL | ERP 上的 SKU ID |
| `Ferp_sku_info` | JSON | 否 | NULL | ERP 商品扩展信息（原始 JSON） |
| `Fis_delete` | INT | 是 | 0 | 逻辑删除 |
| `Fversion` | INT | 是 | 0 | 乐观锁版本 |
| `Fmodify_user` | VARCHAR(128) | 是 | `''` | 修改人 |
| `Fcreate_time` | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| `Fmodify_time` | DATETIME | 是 | CURRENT_TIMESTAMP ON UPDATE | 修改时间 |

## 索引

| 索引 | 列 | 类型 |
| ---- | -- | ---- |
| PRIMARY | `(Fproject_id, Fsku)` | 复合主键 |
| `idx_sku_group` | `Fsku_group` | 普通 |
| `idx_sku_name` | `Fsku_name(255)` | 前缀索引 |
| `idx_erp_sku_name` | `Ferp_sku_name(255)` | 前缀索引 |
| `idx_create_time` | `Fcreate_time` | 普通 |
| `idx_modify_time` | `Fmodify_time` | 普通 |

## DTO 类

```python
class SkuDto(DtoBase):
    __tablename__ = "t_sku_info"
    __table_args__ = (PrimaryKeyConstraint(
        "Fproject_id", "Fsku"
    ), {"mysql_default_charset": "utf8"})
    project_id: Mapped[str] = Column('Fproject_id', String(128), comment='所属项目ID')
    sku: Mapped[str] = Column('Fsku', String(256), comment='商品SKU')
    sku_group: Mapped[str] = Column('Fsku_group', String(256), index=True, comment='商品SKU分组')
    sku_name: Mapped[str] = Column('Fsku_name', String(1024), index=True, comment='商品名称')
    sku_unit_name: Mapped[str] = Column('Fsku_unit_name', String(256), default="", server_default="", comment='采购单位')
    sku_unit_quantity: Mapped[int] = Column('Fsku_unit_quantity', Integer, default=1, server_default="1",
                                            comment='每个单位的sku数')
    inventory: Mapped[int] = Column('Finventory', Integer, default=0, server_default="0", comment='库存量')
    avg_sell_quantity: Mapped[float] = Column('Favg_sell_quantity', Float, default=0.0, server_default="0.0",
                                              comment='平均每天销售量')
    inventory_support_days: Mapped[int] = Column('Finventory_support_days', Integer, default=0, server_default="0",
                                                 comment='库存支撑天数预估')
    shipping_stock_quantity: Mapped[int] = Column('Fshipping_stock_quantity', Integer, default=0, server_default="0",
                                                  comment='海运中的sku数')
    erp_sku_name: Mapped[str] = Column('Ferp_sku_name', String(1024), index=True, comment='ERP商品名称')
    erp_sku_image_url: Mapped[str] = Column('Ferp_sku_image_url', String(10240), comment='商品图片链接')
    erp_sku_id: Mapped[str] = Column('Ferp_sku_id', String(256), comment='erp上sku id')
    erp_sku_info: Mapped[dict] = Column('Ferp_sku_info', JSON, comment='erp上商品扩展信息')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0", comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0", comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="", comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, ...)
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, ...)
    columns = [
        "project_id", "sku", "sku_group",
        "sku_name", "inventory", "erp_sku_name", "erp_sku_image_url",
        "erp_sku_id", "erp_sku_info",
        "sku_unit_name", "sku_unit_quantity",
        "avg_sell_quantity", "shipping_stock_quantity", "inventory_support_days",
        "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]
```

## CRUD 方法

| 方法 | 说明 |
| ---- | ---- |
| `store_sku(sku: SkuDto)` | upsert SKU（校验 `project_id == self.project_id`） |
| `search_sku(sku_group, sku_name, sku, offset, limit, inventory_support_days=0, sort_types=None) -> (total, list)` | 多条件分页查询 |
| `get_sku(sku) -> Optional[SkuDto]` | 按 SKU 查询 |
| `_get_sku(session, sku)` (静态) | 内部查询 |

## 关联表 / 模块

- [t_sku_purchase_price](./t_sku_purchase_price.md)：通过 `(Fproject_id, Fsku)` 关联
- [t_sku_picking_note](./t_sku_picking_note.md)：通过 `(Fproject_id, Fsku)` 关联
- [t_sku_sale_estimate](./t_sku_sale_estimate.md)：通过 `(Fproject_id, Fsku)` 关联
- [supplier_module_spec](../../supplier_module_spec.md)：`save_sku` / `search_sku` / `add_sku` / `sync_all_sku` 接口

## 同步任务

- [auto_sync_tools/sync_sku_inventory.py](../../../../auto_sync_tools/sync_sku_inventory.py)：每天定时同步库存与销售估算
- [auto_sync_tools/sync_all_sku.py](../../../../auto_sync_tools/sync_all_sku.py)：同步本地 SKU 主数据 JSON

## Change-Log

### 初始版本 - SKU 商品信息表创建

**变更类型**：新增表

**变更原因**：建立 SKU 主数据，支撑供应链与销售业务。

**变更内容**：
- 新建 `t_sku_info`
- 复合主键 `(Fproject_id, Fsku)`
- 大字段索引使用前缀（255 字符）

**新建库**：直接执行 `docs/ec_erp_db.sql`。

**存量库 ALTER 脚本**：

```sql
CREATE TABLE IF NOT EXISTS `t_sku_info` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` VARCHAR(256) NOT NULL COMMENT '商品SKU',
  `Fsku_group` VARCHAR(256) COMMENT 'SKU分组',
  `Fsku_name` VARCHAR(1024) COMMENT '商品名称',
  `Fsku_unit_name` VARCHAR(256) NOT NULL DEFAULT '' COMMENT '采购单位',
  `Fsku_unit_quantity` INT NOT NULL DEFAULT 1 COMMENT '每个单位的sku数',
  `Finventory` INT NOT NULL DEFAULT 0 COMMENT '库存量',
  `Favg_sell_quantity` FLOAT NOT NULL DEFAULT 0.0 COMMENT '平均每天销售量',
  `Finventory_support_days` INT NOT NULL DEFAULT 0 COMMENT '库存支撑天数预估',
  `Fshipping_stock_quantity` INT NOT NULL DEFAULT 0 COMMENT '海运中的sku数',
  `Ferp_sku_name` VARCHAR(1024) COMMENT 'ERP商品名称',
  `Ferp_sku_image_url` VARCHAR(10240) COMMENT '商品图片链接',
  `Ferp_sku_id` VARCHAR(256) COMMENT 'erp上sku id',
  `Ferp_sku_info` JSON COMMENT 'erp上商品扩展信息',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Fsku`),
  KEY `idx_sku_group` (`Fsku_group`),
  KEY `idx_sku_name` (`Fsku_name`(255)),
  KEY `idx_erp_sku_name` (`Ferp_sku_name`(255)),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU商品信息表';
```

**执行说明**：
- 在每个国家库分别执行
- 数据导入：可使用 [tools/import_sku.py](../../../../tools/import_sku.py) 从 Excel 导入
- 风险评估：低
- 回滚方式：`DROP TABLE IF EXISTS t_sku_info;`

**关联代码改动**：
- ORM：`SkuDto`
- API：[ec_erp_api/apis/supplier.py](../../../../ec_erp_api/apis/supplier.py)
- 同步任务：`sync_sku_inventory.py`、`sync_all_sku.py`
