# t_supplier_info 供应商信息表

## 业务用途

存储所有供应商主数据，用于采购单关联与采购价格管理。

支持 **特殊占位供应商**：`Fsupplier_id == 10000000` 表示「线下销售」（用于 `t_purchase_order` 中 `Forder_type=2` 境外线下采购单）。

## 主键

`PRIMARY KEY (Fsupplier_id)` AUTO_INCREMENT

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS `t_supplier_info` (
  `Fsupplier_id` INT NOT NULL AUTO_INCREMENT COMMENT '供应商ID',
  `Fproject_id` VARCHAR(128) COMMENT '所属项目ID',
  `Fsupplier_name` VARCHAR(128) COMMENT '供应商名',
  `Fwechat_account` VARCHAR(128) COMMENT '供应商微信号',
  `Fdetail` VARCHAR(1024) COMMENT '详细信息',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fsupplier_id`),
  KEY `idx_project_id` (`Fproject_id`),
  KEY `idx_supplier_name` (`Fsupplier_name`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='供应商信息表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fsupplier_id` | INT | 是 | AUTO_INCREMENT | 供应商 ID |
| `Fproject_id` | VARCHAR(128) | 否 | NULL | 所属项目 ID |
| `Fsupplier_name` | VARCHAR(128) | 否 | NULL | 供应商名 |
| `Fwechat_account` | VARCHAR(128) | 否 | NULL | 供应商微信号 |
| `Fdetail` | VARCHAR(1024) | 否 | NULL | 详细信息（银行卡、联系方式等） |
| `Fis_delete` | INT | 是 | 0 | 逻辑删除 |
| `Fversion` | INT | 是 | 0 | 乐观锁版本 |
| `Fmodify_user` | VARCHAR(128) | 是 | `''` | 修改人 |
| `Fcreate_time` | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| `Fmodify_time` | DATETIME | 是 | CURRENT_TIMESTAMP ON UPDATE | 修改时间 |

## 索引

| 索引 | 列 | 类型 |
| ---- | -- | ---- |
| PRIMARY | `Fsupplier_id` | 主键 |
| `idx_project_id` | `Fproject_id` | 普通 |
| `idx_supplier_name` | `Fsupplier_name` | 普通 |
| `idx_create_time` | `Fcreate_time` | 普通 |
| `idx_modify_time` | `Fmodify_time` | 普通 |

## DTO 类

```python
class SupplierDto(DtoBase):
    __tablename__ = "t_supplier_info"
    __table_args__ = ({"mysql_default_charset": "utf8"})
    supplier_id: Mapped[int] = Column('Fsupplier_id', Integer, primary_key=True, autoincrement=True, comment="供应商ID")
    project_id: Mapped[str] = Column('Fproject_id', String(128), index=True, comment='所属项目ID')
    supplier_name: Mapped[str] = Column('Fsupplier_name', String(128), index=True, comment='供应商名')
    wechat_account: Mapped[str] = Column('Fwechat_account', String(128), comment='供应商微信号')
    detail: Mapped[str] = Column('Fdetail', String(1024), comment='详细信息')
    is_delete: Mapped[int] = Column('Fis_delete', Integer, default=0, server_default="0",
                                    comment='是否逻辑删除, 1: 删除')
    version: Mapped[int] = Column('Fversion', Integer, default=0, server_default="0",
                                  comment="记录版本号")
    modify_user: Mapped[str] = Column('Fmodify_user', String(128), default="", server_default="",
                                      comment="修改用户")
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='创建时间')
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, default=datetime.now(),
                                           server_default=sql.func.now(), comment='修改时间')
    columns = [
        "supplier_id", "project_id", "supplier_name", "wechat_account",
        "detail", "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]
```

## 特殊数据约定

- `Fsupplier_id == 10000000`：固定占位记录"线下销售"，由 [ec_erp_api/apis/supplier.py](../../../../ec_erp_api/apis/supplier.py) 中 `build_purchase_order_from_req` 在 `order_type==2` 时使用，`supplier_name = "线下销售"`

## CRUD 方法

| 方法 | 说明 |
| ---- | ---- |
| `store_supplier(supplier: SupplierDto)` | upsert 供应商 |
| `search_suppliers(offset, limit) -> (total, list)` | 分页查询当前 project 的供应商 |
| `get_supplier(supplier_id) -> Optional[SupplierDto]` | 按 ID 查询 |

## 关联表 / 模块

- [t_sku_purchase_price](./t_sku_purchase_price.md)：通过 `Fsupplier_id` 关联
- [t_purchase_order](./t_purchase_order.md)：通过 `Fsupplier_id` 关联
- [supplier_module_spec](../../supplier_module_spec.md)：供应商管理 API

## 工具脚本

- [tools/import_supplier_info.py](../../../../tools/import_supplier_info.py)：从 Excel 批量导入

## Change-Log

### 初始版本 - 供应商信息表创建

**变更类型**：新增表

**变更原因**：管理供应商主数据，支持采购订单流程。

**变更内容**：
- 新建 `t_supplier_info`
- 主键 `Fsupplier_id` AUTO_INCREMENT
- 索引 `idx_project_id`、`idx_supplier_name`

**新建库**：直接执行 `docs/ec_erp_db.sql`。

**存量库 ALTER 脚本**：

```sql
CREATE TABLE IF NOT EXISTS `t_supplier_info` (
  `Fsupplier_id` INT NOT NULL AUTO_INCREMENT COMMENT '供应商ID',
  `Fproject_id` VARCHAR(128) COMMENT '所属项目ID',
  `Fsupplier_name` VARCHAR(128) COMMENT '供应商名',
  `Fwechat_account` VARCHAR(128) COMMENT '供应商微信号',
  `Fdetail` VARCHAR(1024) COMMENT '详细信息',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fsupplier_id`),
  KEY `idx_project_id` (`Fproject_id`),
  KEY `idx_supplier_name` (`Fsupplier_name`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='供应商信息表';

-- 插入"线下销售"占位供应商（每个国家库分别执行）
INSERT IGNORE INTO `t_supplier_info` (`Fsupplier_id`, `Fproject_id`, `Fsupplier_name`)
VALUES (10000000, 'philipine', '线下销售');
```

**执行说明**：
- 在每个国家库分别执行
- "线下销售"占位记录的 `Fsupplier_id` 必须固定为 10000000
- 风险评估：低
- 回滚方式：`DROP TABLE IF EXISTS t_supplier_info;`

**关联代码改动**：
- ORM：`SupplierDto`
- API：[ec_erp_api/apis/supplier.py](../../../../ec_erp_api/apis/supplier.py) `search_supplier`
