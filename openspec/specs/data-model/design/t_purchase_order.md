# t_purchase_order 采购单表

## 业务用途

记录采购订单的全生命周期数据，覆盖境内进货（`Forder_type=1`）与境外线下（`Forder_type=2`）两种类型，包含状态机推进、SKU 明细、入库明细、操作日志。

## 主键

`PRIMARY KEY (Fpurchase_order_id)` AUTO_INCREMENT

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS `t_purchase_order` (
  `Fpurchase_order_id` INT NOT NULL AUTO_INCREMENT COMMENT '采购单id',
  `Fproject_id` VARCHAR(128) COMMENT '所属项目ID',
  `Forder_type` INT NOT NULL DEFAULT 1 COMMENT '采购单类型, 1: 境内进货采购单, 2: 境外线下采购单',
  `Fsupplier_id` INT COMMENT '供应商id',
  `Fsupplier_name` VARCHAR(128) COMMENT '供应商名',
  `Fpurchase_step` VARCHAR(128) COMMENT '采购状态: 类型1(草稿/供应商捡货中/待发货/海运中/已入库/完成/废弃) 类型2(草稿/境外拣货/已出库/完成/废弃)',
  `Fsku_summary` VARCHAR(10240) NOT NULL DEFAULT '' COMMENT '货物概述',
  `Fsku_amount` INT NOT NULL DEFAULT 0 COMMENT 'sku采购金额',
  `Fpay_amount` INT NOT NULL DEFAULT 0 COMMENT '支付金额',
  `Fpay_state` INT NOT NULL DEFAULT 0 COMMENT '支付状态，0: 未支付， 1：已支付',
  `Fpurchase_date` VARCHAR(128) COMMENT '采购日期',
  `Fexpect_arrive_warehouse_date` VARCHAR(128) COMMENT '预计到货日期',
  `Fmaritime_port` VARCHAR(128) COMMENT '海运港口',
  `Fshipping_company` VARCHAR(128) COMMENT '货运公司',
  `Fshipping_fee` VARCHAR(128) COMMENT '海运费',
  `Farrive_warehouse_date` VARCHAR(128) COMMENT '入库日期',
  `Fremark` VARCHAR(10240) NOT NULL DEFAULT '' COMMENT '备注',
  `Fpurchase_skus` JSON COMMENT '采购的货品',
  `Fstore_skus` JSON COMMENT '入库的货品',
  `op_log` JSON COMMENT '操作记录',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fpurchase_order_id`),
  KEY `idx_order_type` (`Forder_type`),
  KEY `idx_supplier_name` (`Fsupplier_name`),
  KEY `idx_purchase_step` (`Fpurchase_step`),
  KEY `idx_purchase_date` (`Fpurchase_date`),
  KEY `idx_expect_arrive_warehouse_date` (`Fexpect_arrive_warehouse_date`),
  KEY `idx_maritime_port` (`Fmaritime_port`),
  KEY `idx_shipping_company` (`Fshipping_company`),
  KEY `idx_arrive_warehouse_date` (`Farrive_warehouse_date`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='采购单表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fpurchase_order_id` | INT | 是 | AUTO_INCREMENT | 采购单 ID |
| `Fproject_id` | VARCHAR(128) | 否 | NULL | 所属项目 |
| `Forder_type` | INT | 是 | 1 | 1=境内进货，2=境外线下 |
| `Fsupplier_id` | INT | 否 | NULL | 供应商 ID（type=2 时为 10000000 占位） |
| `Fsupplier_name` | VARCHAR(128) | 否 | NULL | 供应商名 |
| `Fpurchase_step` | VARCHAR(128) | 否 | NULL | 采购状态（见下方状态机） |
| `Fsku_summary` | VARCHAR(10240) | 是 | `''` | 货物概述 |
| `Fsku_amount` | INT | 是 | 0 | SKU 采购金额，**单位：分** |
| `Fpay_amount` | INT | 是 | 0 | 支付金额，**单位：分** |
| `Fpay_state` | INT | 是 | 0 | 0=未支付，1=已支付 |
| `Fpurchase_date` | VARCHAR(128) | 否 | NULL | 采购日期 |
| `Fexpect_arrive_warehouse_date` | VARCHAR(128) | 否 | NULL | 预计到货日期 |
| `Fmaritime_port` | VARCHAR(128) | 否 | NULL | 海运港口 |
| `Fshipping_company` | VARCHAR(128) | 否 | NULL | 货运公司 |
| `Fshipping_fee` | VARCHAR(128) | 否 | NULL | 海运费（字符串保留原始格式） |
| `Farrive_warehouse_date` | VARCHAR(128) | 否 | NULL | 实际入库日期 |
| `Fremark` | VARCHAR(10240) | 是 | `''` | 备注 |
| `Fpurchase_skus` | JSON | 否 | NULL | 采购 SKU 列表（结构见下方） |
| `Fstore_skus` | JSON | 否 | NULL | 入库 SKU 列表（结构见下方） |
| `op_log` | JSON | 否 | NULL | 操作记录列表（**列名无 F 前缀，历史例外**） |
| `Fis_delete` | INT | 是 | 0 | 逻辑删除 |
| `Fversion` | INT | 是 | 0 | 乐观锁版本 |
| `Fmodify_user` | VARCHAR(128) | 是 | `''` | 修改人 |
| `Fcreate_time` | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| `Fmodify_time` | DATETIME | 是 | CURRENT_TIMESTAMP ON UPDATE | 修改时间 |

> ⚠️ **历史例外**：`op_log` 列名缺少 `F` 前缀，是历史遗留。后续表禁止再次出现此类例外。

### `Fpurchase_skus` JSON 结构

```json
[
  {
    "sku": "G-2-grape leaves",
    "sku_group": "藤条",
    "sku_name": "葡萄叶",
    "unit_price": 1200,
    "sku_unit_quantity": 1,
    "quantity": 30
  }
]
```

### `Fstore_skus` JSON 结构

```json
[
  {
    "sku": "G-2-grape leaves",
    "sku_group": "藤条",
    "sku_name": "葡萄叶",
    "quantity": 30,
    "sku_unit_quantity": 1,
    "check_in_quantity": 30
  }
]
```

### `op_log` JSON 结构

```json
[
  { "time": "2026-04-29 17:30:00", "user": "alice", "action": "提交并推进至 海运中" }
]
```

## 状态机

### 类型 1（境内进货）

```
草稿 → 供应商捡货中 → 待发货 → 海运中 → 已入库 → 完成 / 废弃
```

### 类型 2（境外线下）

```
草稿 → 境外拣货 → 已出库 → 完成 / 废弃
```

## 索引

| 索引 | 列 |
| ---- | -- |
| PRIMARY | `Fpurchase_order_id` |
| `idx_order_type` | `Forder_type` |
| `idx_supplier_name` | `Fsupplier_name` |
| `idx_purchase_step` | `Fpurchase_step` |
| `idx_purchase_date` | `Fpurchase_date` |
| `idx_expect_arrive_warehouse_date` | `Fexpect_arrive_warehouse_date` |
| `idx_maritime_port` | `Fmaritime_port` |
| `idx_shipping_company` | `Fshipping_company` |
| `idx_arrive_warehouse_date` | `Farrive_warehouse_date` |
| `idx_create_time` | `Fcreate_time` |
| `idx_modify_time` | `Fmodify_time` |

## DTO 类

```python
class PurchaseOrder(DtoBase):
    __tablename__ = "t_purchase_order"
    __table_args__ = ({"mysql_default_charset": "utf8"})
    purchase_order_id: Mapped[int] = Column('Fpurchase_order_id', Integer, primary_key=True, autoincrement=True, comment="采购单id")
    project_id: Mapped[str] = Column('Fproject_id', String(128), comment='所属项目ID')
    order_type: Mapped[int] = Column('Forder_type', Integer, default=1, server_default="1", index=True,
                                     comment='采购单类型, 1: 境内进货采购单, 2: 境外线下采购单')
    supplier_id: Mapped[int] = Column('Fsupplier_id', Integer, comment='供应商id')
    supplier_name: Mapped[str] = Column('Fsupplier_name', String(128), index=True, comment='供应商名')
    purchase_step: Mapped[str] = Column('Fpurchase_step', String(128), index=True, comment='采购状态')
    sku_summary: Mapped[str] = Column('Fsku_summary', String(10240), default="", server_default="", comment='货物概述')
    sku_amount: Mapped[int] = Column('Fsku_amount', Integer, default=0, server_default="0", comment='sku采购金额')
    pay_amount: Mapped[int] = Column('Fpay_amount', Integer, default=0, server_default="0", comment='支付金额')
    pay_state: Mapped[int] = Column('Fpay_state', Integer, default=0, server_default="0", comment='支付状态')
    purchase_date: Mapped[str] = Column('Fpurchase_date', String(128), index=True, comment='采购日期')
    expect_arrive_warehouse_date: Mapped[str] = Column('Fexpect_arrive_warehouse_date', String(128), index=True, comment='预计到货日期')
    maritime_port: Mapped[str] = Column('Fmaritime_port', String(128), index=True, comment='海运港口')
    shipping_company: Mapped[str] = Column('Fshipping_company', String(128), index=True, comment='货运公司')
    shipping_fee: Mapped[str] = Column('Fshipping_fee', String(128), comment='海运费')
    arrive_warehouse_date: Mapped[str] = Column('Farrive_warehouse_date', String(128), index=True, comment='入库日期')
    remark: Mapped[str] = Column('Fremark', String(10240), default="", server_default="", comment='备注')
    purchase_skus: Mapped[list] = Column('Fpurchase_skus', JSON, comment='采购的货品')
    store_skus: Mapped[list] = Column('Fstore_skus', JSON, comment='入库的货品')
    op_log: Mapped[list] = Column('op_log', JSON, comment='操作记录')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0", comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0", comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="", comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, ...)
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, ...)
    columns = [
        "purchase_order_id", "project_id", "order_type", "supplier_id", "supplier_name",
        "purchase_step", "sku_summary", "sku_amount", "pay_amount", "pay_state", "purchase_date",
        "expect_arrive_warehouse_date", "maritime_port", "shipping_company",
        "shipping_fee", "arrive_warehouse_date",
        "remark", "purchase_skus", "store_skus", "op_log",
        "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]
```

## CRUD 方法

| 方法 | 说明 |
| ---- | ---- |
| `store_purchase_order(purchase_order)` | upsert |
| `search_purchase_order(offset, limit, order_type=None) -> (total, list)` | 分页查询，按类型过滤 |
| `load_shipping_purchase_order() -> List[PurchaseOrder]` | 加载在途订单（待发货/海运中/已入库/境外拣货/已出库） |
| `_get_purchase_order(session, purchase_order_id)` (静态) | 内部查询 |

## 关联表 / 模块

- [t_supplier_info](./t_supplier_info.md)：通过 `Fsupplier_id` 关联
- [t_sku_info](./t_sku_info.md)：`Fpurchase_skus` / `Fstore_skus` 中的 `sku` 字段
- [supplier_module_spec](../../supplier_module_spec.md)：`save_purchase_order`、`submit_purchase_order_and_next_step`、`search_purchase_order`

## Change-Log

### 2024-10 - 添加 `Forder_type` 字段（历史变更）

**变更类型**：新增字段 + 新增索引

**变更原因**：支持境外线下采购单类型，与境内进货采购单区分。

**变更内容**：
- 新增字段 `Forder_type INT NOT NULL DEFAULT 1`，1=境内进货，2=境外线下
- 新增索引 `idx_order_type`
- 已有数据回填 `Forder_type = 1`

**新建库**：直接执行 [docs/ec_erp_db.sql](../../../../docs/ec_erp_db.sql) 已包含本次变更。

**存量库 ALTER 脚本**（已固化在 [docs/purchase_order_table_alt.sql](../../../../docs/purchase_order_table_alt.sql)）：

```sql
-- 1. 新增字段
ALTER TABLE t_purchase_order
  ADD COLUMN `Forder_type` INT NOT NULL DEFAULT 1
  COMMENT '采购单类型, 1: 境内进货采购单, 2: 境外线下采购单'
  AFTER `Fproject_id`;

-- 2. 添加索引
ALTER TABLE t_purchase_order ADD INDEX `idx_order_type` (`Forder_type`);

-- 3. 回填默认值
UPDATE t_purchase_order SET Forder_type = 1 WHERE Forder_type IS NULL;
```

**执行说明**：
- 在每个国家库分别执行
- 预估耗时：< 1 秒
- 风险评估：低（新增字段，向下兼容）
- 回滚方式：`ALTER TABLE t_purchase_order DROP INDEX idx_order_type, DROP COLUMN Forder_type;`

**关联代码改动**：
- ORM：`PurchaseOrder.order_type`
- API：[ec_erp_api/apis/supplier.py](../../../../ec_erp_api/apis/supplier.py) `search_purchase_order`、`build_purchase_order_from_req`、`_submit_purchase_order_type1`、`_submit_purchase_order_type2`

### 初始版本 - 采购单表创建

**变更类型**：新增表

**变更原因**：管理采购单全生命周期。

**变更内容**：
- 新建 `t_purchase_order`
- AUTO_INCREMENT 主键
- JSON 字段：`Fpurchase_skus`、`Fstore_skus`、`op_log`

**新建库**：执行 `docs/ec_erp_db.sql`。

**存量库 ALTER 脚本**：

```sql
CREATE TABLE IF NOT EXISTS `t_purchase_order` (
  `Fpurchase_order_id` INT NOT NULL AUTO_INCREMENT COMMENT '采购单id',
  `Fproject_id` VARCHAR(128) COMMENT '所属项目ID',
  `Forder_type` INT NOT NULL DEFAULT 1 COMMENT '采购单类型, 1: 境内进货采购单, 2: 境外线下采购单',
  `Fsupplier_id` INT COMMENT '供应商id',
  `Fsupplier_name` VARCHAR(128) COMMENT '供应商名',
  `Fpurchase_step` VARCHAR(128) COMMENT '采购状态',
  `Fsku_summary` VARCHAR(10240) NOT NULL DEFAULT '' COMMENT '货物概述',
  `Fsku_amount` INT NOT NULL DEFAULT 0 COMMENT 'sku采购金额',
  `Fpay_amount` INT NOT NULL DEFAULT 0 COMMENT '支付金额',
  `Fpay_state` INT NOT NULL DEFAULT 0 COMMENT '支付状态',
  `Fpurchase_date` VARCHAR(128) COMMENT '采购日期',
  `Fexpect_arrive_warehouse_date` VARCHAR(128) COMMENT '预计到货日期',
  `Fmaritime_port` VARCHAR(128) COMMENT '海运港口',
  `Fshipping_company` VARCHAR(128) COMMENT '货运公司',
  `Fshipping_fee` VARCHAR(128) COMMENT '海运费',
  `Farrive_warehouse_date` VARCHAR(128) COMMENT '入库日期',
  `Fremark` VARCHAR(10240) NOT NULL DEFAULT '' COMMENT '备注',
  `Fpurchase_skus` JSON COMMENT '采购的货品',
  `Fstore_skus` JSON COMMENT '入库的货品',
  `op_log` JSON COMMENT '操作记录',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fpurchase_order_id`),
  KEY `idx_order_type` (`Forder_type`),
  KEY `idx_supplier_name` (`Fsupplier_name`),
  KEY `idx_purchase_step` (`Fpurchase_step`),
  KEY `idx_purchase_date` (`Fpurchase_date`),
  KEY `idx_expect_arrive_warehouse_date` (`Fexpect_arrive_warehouse_date`),
  KEY `idx_maritime_port` (`Fmaritime_port`),
  KEY `idx_shipping_company` (`Fshipping_company`),
  KEY `idx_arrive_warehouse_date` (`Farrive_warehouse_date`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='采购单表';
```

**关联代码改动**：
- ORM：`PurchaseOrder`
- API：[ec_erp_api/apis/supplier.py](../../../../ec_erp_api/apis/supplier.py)
