## 1. Script Foundation

- [x] 1.1 Implement `auto_sync_tools/daily_backup_db.sh` with strict shell options, timestamped logging, and non-zero exit on failures.
- [x] 1.2 Add project root detection based on `pwd -P`, walking upward until project markers `ec_erp_app.py` and `conf/` are found.
- [x] 1.3 Add creation of `${project_dir}/data` and `${project_dir}/data/<yyyy-mm-dd>`.

## 2. Database Configuration

- [x] 2.1 Parse `${project_dir}/conf/application.json` with Python standard library to extract `db_config.host`, `db_config.port`, `db_config.user`, `db_config.password`, and optional `db_config.db_name`.
- [x] 2.2 Validate required database config fields and fail clearly when config is missing or incomplete.
- [x] 2.3 Pass the MySQL password through `MYSQL_PWD` instead of command-line arguments.

## 3. Backup Implementation

- [x] 3.1 Define the fixed backup table list: `t_project_info`, `t_purchase_order`, `t_sale_order`, `t_sku_info`, `t_sku_picking_note`, `t_sku_purchase_price`, `t_sku_sale_price`, `t_supplier_info`, and `t_user_info`.
- [x] 3.2 Use `mysqldump` to export table structure and data for the fixed table list into `${project_dir}/data/<yyyy-mm-dd>/ec_erp_db.sql`.
- [x] 3.3 Ensure backup failure exits the script before cleanup is reported as successful.

## 4. Cleanup Implementation

- [x] 4.1 Delete only first-level `${project_dir}/data/YYYY-MM-DD` backup directories older than 2 years.
- [x] 4.2 Preserve non-date directories and date directories within the 2-year retention window.
- [x] 4.3 Use the `mysql` client to delete `t_order_print_task` rows where `Fcreate_time < DATE_SUB(NOW(), INTERVAL 3 DAY)`.

## 5. Verification

- [x] 5.1 Run shell syntax validation for `auto_sync_tools/daily_backup_db.sh`.
- [x] 5.2 Verify project root inference from the project root and from `auto_sync_tools/`.
- [x] 5.3 Verify directory cleanup behavior with temporary date and non-date directories under `data`.
- [x] 5.4 Document the expected cron invocation command or usage comment in the script.
