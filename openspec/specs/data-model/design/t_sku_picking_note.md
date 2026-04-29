# t_sku_picking_note SKU 拣货备注表

## 业务用途

存储 SKU 的拣货单位与拣货 SKU 名称信息，用于订单打印流水线在面单 PDF 上叠加拣货备注 overlay，方便仓库人员按备注拣货。

支持普通拣货模式与 PKG 打包拣货模式（`Fsupport_pkg_picking`）。

## 主键

`PRIMARY KEY (Fproject_id, Fsku)`

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS `t_sku_picking_note` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` VARCHAR(512) NOT NULL COMMENT '商品SKU',
  `Fpicking_unit` FLOAT COMMENT '拣货单位（1个sku的换算）',
  `Fpicking_unit_name` VARCHAR(256) COMMENT '拣货单位名',
  `Fsupport_pkg_picking` TINYINT(1) COMMENT '支持pkg拣货打包模式',
  `Fpkg_picking_unit` FLOAT COMMENT 'pkg打包，拣货单位（1个sku的换算）',
  `Fpkg_picking_unit_name` VARCHAR(256) COMMENT 'pkg打包，拣货单位名',
  `Fpicking_sku_name` VARCHAR(256) COMMENT '拣货sku名',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Fsku`),
  KEY `idx_picking_sku_name` (`Fpicking_sku_name`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU拣货备注表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fproject_id` | VARCHAR(128) | 是 | - | 项目 ID |
| `Fsku` | VARCHAR(512) | 是 | - | 商品 SKU（注意：长度 512，比其他表的 256 更长） |
| `Fpicking_unit` | FLOAT | 否 | NULL | 拣货单位换算（1 个 SKU 等于多少拣货单位） |
| `Fpicking_unit_name` | VARCHAR(256) | 否 | NULL | 拣货单位名（如"卷"/"箱"） |
| `Fsupport_pkg_picking` | TINYINT(1) | 否 | NULL | 是否支持 PKG 打包拣货模式（0/1） |
| `Fpkg_picking_unit` | FLOAT | 否 | NULL | PKG 拣货单位换算 |
| `Fpkg_picking_unit_name` | VARCHAR(256) | 否 | NULL | PKG 拣货单位名 |
| `Fpicking_sku_name` | VARCHAR(256) | 否 | NULL | 拣货 SKU 名称（在 PDF 中标注） |
| `Fcreate_time` | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| `Fmodify_time` | DATETIME | 是 | CURRENT_TIMESTAMP ON UPDATE | 修改时间 |

> **历史例外**：本表**没有** `Fis_delete` / `Fversion` / `Fmodify_user` 字段（与其他业务表不同）。新增类似配置表时建议沿用此简化设计。

## 索引

| 索引 | 列 |
| ---- | -- |
| PRIMARY | `(Fproject_id, Fsku)` |
| `idx_picking_sku_name` | `Fpicking_sku_name` |
| `idx_create_time` | `Fcreate_time` |
| `idx_modify_time` | `Fmodify_time` |

## DTO 类

```python
class SkuPickingNote(DtoBase):
    __tablename__ = "t_sku_picking_note"
    __table_args__ = (PrimaryKeyConstraint(
        "Fproject_id", "Fsku"
    ), {"mysql_default_charset": "utf8"})
    project_id: Mapped[str] = Column('Fproject_id', String(128), comment='所属项目ID')
    sku: Mapped[str] = Column('Fsku', String(512), comment='商品SKU')
    picking_unit: Mapped[float] = Column('Fpicking_unit', Float, comment='拣货单位（1个sku的换算）')
    picking_unit_name: Mapped[str] = Column('Fpicking_unit_name', String(256), comment='拣货单位名')
    support_pkg_picking: Mapped[bool] = Column('Fsupport_pkg_picking', Boolean, comment='支持pkg拣货打包模式')
    pkg_picking_unit: Mapped[float] = Column('Fpkg_picking_unit', Float, comment='pkg打包，拣货单位（1个sku的换算）')
    pkg_picking_unit_name: Mapped[str] = Column('Fpkg_picking_unit_name', String(256), comment='pkg打包，拣货单位名')
    picking_sku_name: Mapped[str] = Column('Fpicking_sku_name', String(256), index=True, comment='拣货sku名')
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, ...)
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, ...)
    columns = [
        "project_id", "sku", "picking_unit", "picking_unit_name",
        "support_pkg_picking", "pkg_picking_unit", "pkg_picking_unit_name",
        "picking_sku_name", "create_time", "modify_time"
    ]
```

## CRUD 方法

| 方法 | 说明 |
| ---- | ---- |
| `store_sku_picking_note(note)` | upsert |
| `search_sku_picking_note(sku, offset, limit) -> (total, list)` | 模糊搜索 |
| `get_sku_picking_note(sku) -> Optional[SkuPickingNote]` | 精确查询 |
| `_get_sku_picking_note(session, sku)` (静态) | 内部查询 |

## 关联表 / 模块

- [t_sku_info](./t_sku_info.md)：通过 `(Fproject_id, Fsku)` 关联
- [warehouse_module_spec](../../warehouse_module_spec.md)：
  - `pre_submit_print_order` 检测缺失备注的 SKU
  - `submit_manual_mark_sku_picking_note` 批量补录
  - `PrintOrderThread._split_and_note_pdf` 在 PDF 上叠加备注
- 工具：[tools/import_picking_note.py](../../../../tools/import_picking_note.py) 从 Excel 批量导入

## Change-Log

### 初始版本 - SKU 拣货备注表创建

**变更类型**：新增表

**变更原因**：订单打印流水线需要在面单上标注拣货 SKU 与单位，便于仓库人员拣货。

**变更内容**：
- 新建 `t_sku_picking_note`
- 复合主键 `(Fproject_id, Fsku)`
- `Fsku` 长度 512（特殊，比通用 SKU 表 256 更长）
- 简化设计：无 `Fis_delete` / `Fversion` / `Fmodify_user`

**新建库**：直接执行 `docs/ec_erp_db.sql`。

**存量库 ALTER 脚本**：

```sql
CREATE TABLE IF NOT EXISTS `t_sku_picking_note` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` VARCHAR(512) NOT NULL COMMENT '商品SKU',
  `Fpicking_unit` FLOAT COMMENT '拣货单位（1个sku的换算）',
  `Fpicking_unit_name` VARCHAR(256) COMMENT '拣货单位名',
  `Fsupport_pkg_picking` TINYINT(1) COMMENT '支持pkg拣货打包模式',
  `Fpkg_picking_unit` FLOAT COMMENT 'pkg打包，拣货单位（1个sku的换算）',
  `Fpkg_picking_unit_name` VARCHAR(256) COMMENT 'pkg打包，拣货单位名',
  `Fpicking_sku_name` VARCHAR(256) COMMENT '拣货sku名',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Fsku`),
  KEY `idx_picking_sku_name` (`Fpicking_sku_name`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU拣货备注表';
```

**执行说明**：
- 在每个国家库分别执行
- 数据初始化：使用 [tools/import_picking_note.py](../../../../tools/import_picking_note.py) 从 Excel 批量导入
- 风险评估：低
- 回滚方式：`DROP TABLE IF EXISTS t_sku_picking_note;`

**关联代码改动**：
- ORM：`SkuPickingNote`
- API：[ec_erp_api/apis/warehouse.py](../../../../ec_erp_api/apis/warehouse.py)
- 业务：[ec_erp_api/business/order_printing.py](../../../../ec_erp_api/business/order_printing.py)
