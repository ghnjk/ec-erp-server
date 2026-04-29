# t_project_info 项目信息表

## 业务用途

存储所有 project（国家/地区）的元数据与配置。每个 project 对应一个独立的业务运营单元，例如 `philipine`、`india`、`malaysia`、`thailand`。

`Fdoc` 字段保存项目级配置（JSON），可用于业务层自定义参数。

## 主键

`PRIMARY KEY (Fproject_id)`

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS `t_project_info` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '项目ID',
  `Fdoc` JSON COMMENT '项目配置，对应ProjectConfig类',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='项目信息表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fproject_id` | VARCHAR(128) | 是 | - | 项目 ID（philipine/india/malaysia/thailand/dev） |
| `Fdoc` | JSON | 否 | NULL | 项目级配置，对应 `ProjectConfig` 类 |
| `Fis_delete` | INT | 是 | 0 | 逻辑删除标记 |
| `Fversion` | INT | 是 | 0 | 乐观锁版本号 |
| `Fmodify_user` | VARCHAR(128) | 是 | `''` | 修改人 |
| `Fcreate_time` | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| `Fmodify_time` | DATETIME | 是 | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 修改时间 |

## 索引

| 索引 | 列 | 类型 |
| ---- | -- | ---- |
| PRIMARY | `Fproject_id` | 主键 |
| `idx_create_time` | `Fcreate_time` | 普通 |
| `idx_modify_time` | `Fmodify_time` | 普通 |

## DTO 类

文件：[ec_erp_api/models/mysql_backend.py](../../../../ec_erp_api/models/mysql_backend.py)

```python
class ProjectDto(DtoBase):
    """
    项目表
    """
    __tablename__ = "t_project_info"
    __table_args__ = {"mysql_default_charset": "utf8"}
    project_id: Mapped[str] = Column('Fproject_id', String(128), primary_key=True, comment='项目ID')
    doc: Mapped[dict] = Column('Fdoc', JSON, comment='项目配置，对应ProjectConfig类')
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
```

## 已知差异

> ⚠️ `ProjectDto` **未定义** `columns` 列表。直接调用 `DtoUtil.to_dict(project_dto)` 会因缺少 `columns` 属性而异常。使用时必须显式传入 `columns` 参数。

## CRUD 方法

`MysqlBackend` 提供：

| 方法 | 说明 |
| ---- | ---- |
| `store_project(project_id: str, project: dict)` | upsert 项目配置 |
| `_get_project(session, project_id)` (静态) | 内部查询 |

## 关联表 / 模块

- [t_user_info](./t_user_info.md)：`Fdefault_project_id` 引用 project_id
- 其他业务表：通过 `Fproject_id` 关联

## Change-Log

### 初始版本 - 项目信息表创建

**变更类型**：新增表

**变更原因**：建立多 project 数据隔离的根表。

**变更内容**：
- 新建 `t_project_info` 表
- 主键 `Fproject_id`
- JSON 字段 `Fdoc` 存储项目级配置

**新建库**：直接执行 [docs/ec_erp_db.sql](../../../../docs/ec_erp_db.sql) 即包含本表。

**存量库 ALTER 脚本**：

```sql
-- 创建项目信息表（已存在则跳过）
CREATE TABLE IF NOT EXISTS `t_project_info` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '项目ID',
  `Fdoc` JSON COMMENT '项目配置，对应ProjectConfig类',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='项目信息表';

-- 插入初始项目（按需）
INSERT IGNORE INTO `t_project_info` (`Fproject_id`, `Fdoc`)
VALUES ('philipine', JSON_OBJECT('project_name', '菲律宾'));
```

**执行说明**：
- 在每个国家库中执行：`ec_erp_db_philipine`、`ec_erp_db_india` 等
- 风险评估：低风险（新建表）
- 回滚方式：`DROP TABLE IF EXISTS t_project_info;`

**关联代码改动**：
- ORM：`ProjectDto`
