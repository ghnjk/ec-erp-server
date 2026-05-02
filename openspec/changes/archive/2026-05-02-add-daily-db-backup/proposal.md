## Why

当前 `daily_backup_db.sh` 尚未实现，核心业务表缺少按日自动备份和备份留存清理机制；同时打印任务表的过期任务数据也需要定期清理，避免数据目录和数据库持续膨胀。

## What Changes

- 新增每日数据库备份脚本能力，备份指定核心表的表结构和数据。
- 备份文件保存到 `${project_dir}/data/<yyyy-mm-dd>/`，其中 `project_dir` 由脚本运行时当前 shell 的绝对路径推断。
- 脚本运行时自动创建 `data` 目录和当天日期子目录。
- 新增备份留存清理逻辑，删除 `${project_dir}/data` 下日期超过 2 年的备份子目录。
- 新增数据库维护清理逻辑，删除 `t_order_print_task` 表中创建时间超过 3 天的记录。
- 不新增 HTTP API，不修改数据库表结构。

## Capabilities

### New Capabilities

- `database-backup-maintenance`: 定义每日数据库备份、备份目录留存清理、打印任务过期记录清理的运维脚本行为。

### Modified Capabilities

- 无。

## Impact

- 影响脚本：`auto_sync_tools/daily_backup_db.sh`
- 影响数据目录：`${project_dir}/data/<yyyy-mm-dd>/`
- 影响数据库表：`t_project_info`、`t_purchase_order`、`t_sale_order`、`t_sku_info`、`t_sku_picking_note`、`t_sku_purchase_price`、`t_sku_sale_price`、`t_supplier_info`、`t_user_info`、`t_order_print_task`
- 依赖系统命令：`mysqldump`、`mysql`、`date`、`find`、`pwd`
- 不影响前端、不新增接口、不要求数据库 schema 迁移。
