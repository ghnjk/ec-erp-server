# t_user_info 用户信息表

## 业务用途

存储登录用户的认证信息、权限角色、默认所属项目。

- 密码使用 SHA256 (`codec_util.calc_sha256`) 加密存入 `Fpassword`
- 通过 `Froles` JSON 字段表达多 project 下的角色权限
- `Fdefault_project_id` 是用户登录时默认进入的 project

## 主键

`PRIMARY KEY (Fuser_name)`

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS `t_user_info` (
  `Fuser_name` VARCHAR(128) NOT NULL COMMENT '用户名',
  `Fdefault_project_id` VARCHAR(128) COMMENT '默认项目',
  `Fpassword` VARCHAR(256) COMMENT '用户密码',
  `Froles` JSON COMMENT '用户角色列表',
  `Fis_admin` INT NOT NULL DEFAULT 0 COMMENT '是否管理员, 1: 管理员',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fuser_name`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户信息表';
```

## 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| ---- | ---- | ---- | ------ | ---- |
| `Fuser_name` | VARCHAR(128) | 是 | - | 用户名（主键） |
| `Fdefault_project_id` | VARCHAR(128) | 否 | NULL | 默认项目（登录后写入 session） |
| `Fpassword` | VARCHAR(256) | 否 | NULL | SHA256 加密后的密码（hex 字符串） |
| `Froles` | JSON | 否 | NULL | 用户角色列表（见下方结构） |
| `Fis_admin` | INT | 是 | 0 | 1=管理员，全部权限放行 |
| `Fis_delete` | INT | 是 | 0 | 逻辑删除标记 |
| `Fversion` | INT | 是 | 0 | 乐观锁版本号 |
| `Fmodify_user` | VARCHAR(128) | 是 | `''` | 修改人 |
| `Fcreate_time` | DATETIME | 是 | CURRENT_TIMESTAMP | 创建时间 |
| `Fmodify_time` | DATETIME | 是 | CURRENT_TIMESTAMP ON UPDATE | 修改时间 |

### `Froles` JSON 结构

```json
[
  {
    "project_id": "philipine",
    "name": "supply",
    "memo": "供应链管理",
    "level": 1
  },
  {
    "project_id": "philipine",
    "name": "warehouse",
    "memo": "仓库管理",
    "level": 1
  }
]
```

`name` 取值参考权限常量：
- `supply` → `PMS_SUPPLIER`
- `warehouse` → `PMS_WAREHOUSE`
- `sale` → `PMS_SALE`

## 索引

| 索引 | 列 | 类型 |
| ---- | -- | ---- |
| PRIMARY | `Fuser_name` | 主键 |
| `idx_create_time` | `Fcreate_time` | 普通 |
| `idx_modify_time` | `Fmodify_time` | 普通 |

## DTO 类

```python
class UserDto(DtoBase):
    __tablename__ = "t_user_info"
    __table_args__ = {"mysql_default_charset": "utf8"}
    user_name: Mapped[str] = Column('Fuser_name', String(128), primary_key=True, comment='用户名')
    default_project_id: Mapped[str] = Column('Fdefault_project_id', String(128), comment='默认项目')
    password: Mapped[str] = Column('Fpassword', String(256), comment='用户密码')
    roles: Mapped[list] = Column('Froles', JSON, comment='用户角色列表')
    is_admin: Mapped[int] = Column('Fis_admin', Integer, default=0, server_default="0",
                                   comment='是否管理员, 1: 管理员')
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
        "user_name", "default_project_id", "password", "roles",
        "is_admin", "is_delete", "version",
        "modify_user", "create_time", "modify_time"
    ]
```

## 多 Project 关系

`t_user_info` 是 **跨 project** 的全局用户表：
- 表中**不**包含 `Fproject_id` 字段
- 通过 `Fdefault_project_id` 表达默认所属
- 通过 `Froles` 表达多 project 角色

## CRUD 方法

| 方法 | 说明 |
| ---- | ---- |
| `store_user(user: UserDto)` | upsert 用户 |
| `get_user(user_name) -> Optional[UserDto]` | 按用户名查询 |
| `_get_user(session, user_name)` (静态) | 内部查询 |

## 关联表 / 模块

- [t_project_info](./t_project_info.md)：`Fdefault_project_id` 引用 project_id
- [system_module_spec](../../system_module_spec.md)：登录与用户信息接口

## 工具脚本

- [tools/add_user.py](../../../../tools/add_user.py)：CLI 添加用户

## Change-Log

### 初始版本 - 用户信息表创建

**变更类型**：新增表

**变更原因**：建立用户认证与权限管理基础。

**变更内容**：
- 新建 `t_user_info` 表
- 主键 `Fuser_name`
- 密码使用 SHA256 加密存储
- `Froles` JSON 字段表达多 project 角色

**新建库**：直接执行 `docs/ec_erp_db.sql`。

**存量库 ALTER 脚本**：

```sql
CREATE TABLE IF NOT EXISTS `t_user_info` (
  `Fuser_name` VARCHAR(128) NOT NULL COMMENT '用户名',
  `Fdefault_project_id` VARCHAR(128) COMMENT '默认项目',
  `Fpassword` VARCHAR(256) COMMENT '用户密码',
  `Froles` JSON COMMENT '用户角色列表',
  `Fis_admin` INT NOT NULL DEFAULT 0 COMMENT '是否管理员, 1: 管理员',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fuser_name`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户信息表';
```

**执行说明**：
- 用户表是**跨 project** 的全局表，多国部署只需选择一个主库执行（建议 `ec_erp_db_philipine`），其他国家库共用此用户体系或独立维护
- 风险评估：低风险（新建表）
- 回滚方式：`DROP TABLE IF EXISTS t_user_info;`

**关联代码改动**：
- ORM：`UserDto`
- API：[ec_erp_api/apis/system.py](../../../../ec_erp_api/apis/system.py)
- 工具：[tools/add_user.py](../../../../tools/add_user.py)
