## Context

`auto_sync_tools/daily_backup_db.sh` 目前为空文件。项目已有 `conf/application.json` / `conf/application_template.json` 中的 `db_config` 约定，Python 代码通过该配置连接 MySQL；本次变更应复用同一配置来源，避免在脚本中硬编码数据库账号、密码或数据库名。

脚本将作为 cron 类定时任务每天运行一次，主要职责是：

- 对核心业务表执行结构和数据备份。
- 清理 2 年以前的本地备份目录。
- 清理 `t_order_print_task` 中 3 天以前的打印任务记录。

## Goals / Non-Goals

**Goals:**

- 提供一个可重复执行的 `daily_backup_db.sh` 运维脚本。
- 根据当前 shell 所在绝对路径推断项目根目录，并把备份写入项目根目录下的 `data/<yyyy-mm-dd>/`。
- 使用 `mysqldump` 备份指定表的表结构和数据。
- 自动创建 `data` 和日期目录。
- 删除日期超过 2 年的备份子目录。
- 删除 `t_order_print_task` 中创建时间超过 3 天的记录。
- 脚本失败时尽早退出，避免静默跳过备份或清理失败。

**Non-Goals:**

- 不新增 Flask API 或前端入口。
- 不修改数据库表结构、ORM 或建表 SQL。
- 不负责配置 cron；仅提供可被 cron 调用的脚本。
- 不实现远端对象存储、压缩上传或加密归档。

## Decisions

1. **项目目录推断**

   脚本从 `pwd -P` 获取当前 shell 的物理绝对路径，并向上查找包含 `ec_erp_app.py` 与 `conf/` 的最近目录作为 `project_dir`。这样既支持在项目根目录执行，也支持在子目录中执行脚本。

   替代方案是使用脚本文件所在目录反推项目根目录，但用户明确要求根据当前 shell 绝对路径推断，因此以 `PWD` 为主。

2. **数据库配置来源**

   优先读取 `${project_dir}/conf/application.json` 的 `db_config`，并通过 Python 标准库解析 JSON 输出 shell 可消费的连接参数。`db_name` 缺省时沿用现有 `MysqlBackend` 约定使用 `ec_erp_db`。

   替代方案是在 shell 中通过 `sed`/`grep` 解析 JSON，风险是对格式敏感且容易误读密码中特殊字符。

3. **备份方式**

   使用 `mysqldump --single-transaction --routines=false --triggers=false` 一次性导出指定表的结构和数据，写入 `${project_dir}/data/<yyyy-mm-dd>/ec_erp_db.sql`。指定表清单固定在脚本中，避免误备份临时表或日志表。

   替代方案是每张表生成一个 SQL 文件，便于单表恢复，但会增加文件数量和恢复顺序管理。当前需求只要求保存到日期目录，单文件更便于整体恢复。

4. **备份留存清理**

   只删除 `${project_dir}/data` 下名称形如 `YYYY-MM-DD` 且日期早于 2 年前的一级子目录，避免误删非备份数据。清理逻辑在备份目录创建后执行。

5. **打印任务清理**

   使用 `mysql` 客户端执行：

   ```sql
   DELETE FROM t_order_print_task WHERE Fcreate_time < DATE_SUB(NOW(), INTERVAL 3 DAY);
   ```

   这里按“创建时间超过 3 天”理解为早于当前时间 3 天的记录。若实现阶段发现表字段名与规约不一致，应先确认实际字段后再调整。

## Risks / Trade-offs

- [Risk] `mysqldump` 或 `mysql` 未安装会导致脚本失败 → Mitigation：脚本启动时检查命令存在，不满足则退出并打印错误。
- [Risk] `conf/application.json` 缺失或没有 `db_config` 会导致无法连接数据库 → Mitigation：启动时校验配置文件和必填字段，失败时退出。
- [Risk] 数据库密码包含特殊字符时 shell 参数展开出错 → Mitigation：通过 `MYSQL_PWD` 环境变量传递密码，避免出现在命令行参数中。
- [Risk] 从子目录推断项目根目录可能失败 → Mitigation：向上查找项目标记文件，找不到时退出并提示当前路径。
- [Risk] 误删非备份目录 → Mitigation：只清理 `data` 下符合 `YYYY-MM-DD` 命名且超过留存期的一级目录。
