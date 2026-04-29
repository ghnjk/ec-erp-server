# t_order_print_task 订单打印任务表

## 业务用途

记录订单打印任务（异步流水线）的状态、订单列表、当前步骤、进度、处理日志、最终 PDF URL。前端通过轮询 `query_print_order_task` 查询任务进度。

订单打印流水线由 [PrintOrderThread](../../../../ec_erp_api/business/order_printing.py) 异步执行。

## 主键

`PRIMARY KEY (Fproject_id, Ftask_id)`

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS `t_order_print_task` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Ftask_id` VARCHAR(256) NOT NULL COMMENT '打印任务id',
  `Fpdf_file_url` VARCHAR(256) COMMENT '打印的pdf地址',
  `Fcurrent_step` VARCHAR(1024) COMMENT '当前任务步骤',
  `Fprogress` INT COMMENT '当前进度0-100',
  `Forder_list` JSON COMMENT '订单列表',
  `Flogs` JSON COMMENT '处理日志',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Ftask_id`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='订单打印任务表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fproject_id` | VARCHAR(128) | 是 | - | 项目 ID |
| `Ftask_id` | VARCHAR(256) | 是 | - | 任务 ID（UUID 字符串） |
| `Fpdf_file_url` | VARCHAR(256) | 否 | NULL | 完成后的 PDF 访问 URL（如 `/print/{task_id}/{task_id}.all.pdf`） |
| `Fcurrent_step` | VARCHAR(1024) | 否 | NULL | 当前任务步骤的中文文案 |
| `Fprogress` | INT | 否 | NULL | 进度 0-100 |
| `Forder_list` | JSON | 否 | NULL | 订单列表（来自 BigSeller 订单 JSON 数组） |
| `Flogs` | JSON | 否 | NULL | 处理日志（带时戳的字符串列表） |
| `Fcreate_time` | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| `Fmodify_time` | DATETIME | 是 | CURRENT_TIMESTAMP ON UPDATE | 修改时间 |

> **历史例外**：本表**没有** `Fis_delete` / `Fversion` / `Fmodify_user`。

> **大字段**：`Forder_list` 可能很大（千订单级），查询时应使用 `get_order_print_task_summary`（不返回 `order_list`）。

## 步骤定义

`Fcurrent_step` 取值：

| 步骤 ID | 文案（中文） |
| ------- | ------------ |
| `parsed_all_order_info` | 已解析订单信息 |
| `downloading_order_pdf` | 下载面单中 |
| `merging_pdf` | 合并 PDF 中 |
| `marking_printed` | 标记已打印 |
| `compressing_pdf` | 压缩中 |
| `pdf_ready` | 已就绪 |

## 索引

| 索引 | 列 |
| ---- | -- |
| PRIMARY | `(Fproject_id, Ftask_id)` |
| `idx_create_time` | `Fcreate_time` |
| `idx_modify_time` | `Fmodify_time` |

## DTO 类

```python
class OrderPrintTask(DtoBase):
    __tablename__ = "t_order_print_task"
    __table_args__ = (PrimaryKeyConstraint(
        "Fproject_id", "Ftask_id"
    ), {"mysql_default_charset": "utf8"})
    project_id: Mapped[str] = Column('Fproject_id', String(128), comment='所属项目ID')
    task_id: Mapped[str] = Column('Ftask_id', String(256), comment='打印任务id')
    pdf_file_url: Mapped[str] = Column('Fpdf_file_url', String(256), comment='打印的pdf地址')
    current_step: Mapped[str] = Column('Fcurrent_step', String(1024), comment='当前任务步骤')
    progress: Mapped[int] = Column('Fprogress', Integer, comment='当前进度0-100')
    order_list: Mapped[list] = Column('Forder_list', JSON, comment='订单列表')
    logs: Mapped[list] = Column('Flogs', JSON, comment='处理日志')
    create_time: Mapped[datetime] = Column('Fcreate_time', DateTime, index=True, ...)
    modify_time: Mapped[datetime] = Column('Fmodify_time', DateTime, index=True, ...)
    columns = [
        "project_id", "task_id", "current_step", "progress", "order_list", "pdf_file_url",
        "logs", "create_time", "modify_time"
    ]
```

## CRUD 方法

| 方法 | 说明 |
| ---- | ---- |
| `store_order_print_task(task)` | upsert |
| `get_order_print_task(task_id) -> Optional[OrderPrintTask]` | 完整查询（含 `order_list`） |
| `get_order_print_task_summary(task_id)` | 摘要查询（**不含 `order_list`**），用于前端轮询 |
| `update_order_print_task_without_order_list(task)` | 更新进度，不写 `order_list`（避免大字段反复写入） |
| `_get_order_print_task(session, task_id)` (静态) | 内部查询 |

## 文件存储

任务执行过程中产生的临时与最终 PDF 路径：
- 工作目录：`static/print/{task_id}/`
- 中间面单：`{static_dir}/print/{task_id}/{order_id}.pdf`
- 最终合并：`{static_dir}/print/{task_id}/{task_id}.all.pdf`
- 访问 URL：`/print/{task_id}/{task_id}.all.pdf`

定时清理：每天 5:20 删除 10 天前的打印文件（crontab 自定义）。

## 关联表 / 模块

- [t_sku_picking_note](./t_sku_picking_note.md)：在生成 PDF overlay 时引用
- [warehouse_module_spec](../../warehouse_module_spec.md)：`pre_submit_print_order`、`start_run_print_order_task`、`query_print_order_task`
- [PrintOrderThread](../../../../ec_erp_api/business/order_printing.py)：异步线程

## Change-Log

### 初始版本 - 订单打印任务表创建

**变更类型**：新增表

**变更原因**：订单打印需要长耗时异步执行，需要状态持久化与进度追踪。

**变更内容**：
- 新建 `t_order_print_task`
- 复合主键 `(Fproject_id, Ftask_id)`
- 简化设计：无 `Fis_delete` / `Fversion` / `Fmodify_user`

**新建库**：直接执行 `docs/ec_erp_db.sql`。

**存量库 ALTER 脚本**：

```sql
CREATE TABLE IF NOT EXISTS `t_order_print_task` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Ftask_id` VARCHAR(256) NOT NULL COMMENT '打印任务id',
  `Fpdf_file_url` VARCHAR(256) COMMENT '打印的pdf地址',
  `Fcurrent_step` VARCHAR(1024) COMMENT '当前任务步骤',
  `Fprogress` INT COMMENT '当前进度0-100',
  `Forder_list` JSON COMMENT '订单列表',
  `Flogs` JSON COMMENT '处理日志',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Ftask_id`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='订单打印任务表';
```

**执行说明**：
- 在每个国家库分别执行
- 表数据可能持续增长（每个打印任务一条），建议每月归档历史数据
- 风险评估：低
- 回滚方式：`DROP TABLE IF EXISTS t_order_print_task;`

**关联代码改动**：
- ORM：`OrderPrintTask`
- API：[ec_erp_api/apis/warehouse.py](../../../../ec_erp_api/apis/warehouse.py)
- 业务：[ec_erp_api/business/order_printing.py](../../../../ec_erp_api/business/order_printing.py) `PrintOrderThread`
