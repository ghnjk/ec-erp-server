## Requirements

### Requirement: Daily backup script determines project directory

`daily_backup_db.sh` SHALL determine `project_dir` from the current shell absolute path at runtime and SHALL write all backup output under that project directory.

#### Scenario: Run from project root

- **WHEN** the script is executed while the current shell directory is the EC-ERP server project root
- **THEN** `project_dir` SHALL resolve to that project root
- **AND** backup output SHALL be written under `${project_dir}/data/<yyyy-mm-dd>/`.

#### Scenario: Run from project subdirectory

- **WHEN** the script is executed while the current shell directory is a subdirectory of the EC-ERP server project
- **THEN** `project_dir` SHALL resolve to the nearest parent directory containing project markers such as `ec_erp_app.py` and `conf/`
- **AND** backup output SHALL still be written under `${project_dir}/data/<yyyy-mm-dd>/`.

### Requirement: Daily backup script creates backup directories

`daily_backup_db.sh` SHALL create `${project_dir}/data` and `${project_dir}/data/<yyyy-mm-dd>` automatically when they do not exist.

#### Scenario: Backup directories are missing

- **WHEN** `${project_dir}/data` or today's date directory does not exist
- **THEN** the script SHALL create the missing directories before running database backup.

### Requirement: Daily backup script backs up selected core tables

`daily_backup_db.sh` SHALL back up both table structures and data for the following tables: `t_project_info`, `t_purchase_order`, `t_sale_order`, `t_sku_info`, `t_sku_picking_note`, `t_sku_purchase_price`, `t_sku_sale_price`, `t_supplier_info`, and `t_user_info`.

#### Scenario: Backup succeeds

- **WHEN** the database is reachable and all selected tables exist
- **THEN** the script SHALL create a SQL dump file in `${project_dir}/data/<yyyy-mm-dd>/`
- **AND** the dump SHALL contain CREATE TABLE statements and INSERT data for all selected tables.

#### Scenario: Backup command fails

- **WHEN** the selected table backup fails
- **THEN** the script MUST exit with a non-zero status
- **AND** the script MUST NOT report the run as successful.

### Requirement: Daily backup script uses project database configuration

`daily_backup_db.sh` SHALL read MySQL connection information from `${project_dir}/conf/application.json` and SHALL use `db_config.db_name` when present, otherwise `ec_erp_db`.

#### Scenario: Application config contains database name

- **WHEN** `conf/application.json` contains `db_config.host`, `db_config.port`, `db_config.user`, `db_config.password`, and `db_config.db_name`
- **THEN** the script SHALL connect to the configured host, port, user, password, and database name.

#### Scenario: Application config omits database name

- **WHEN** `conf/application.json` contains database connection fields but omits `db_config.db_name`
- **THEN** the script SHALL use `ec_erp_db` as the database name.

### Requirement: Daily backup script removes expired local backups

`daily_backup_db.sh` SHALL delete backup subdirectories under `${project_dir}/data` whose directory names are dates older than 2 years.

#### Scenario: Backup directory is older than retention period

- **WHEN** `${project_dir}/data` contains a first-level subdirectory named in `YYYY-MM-DD` format and that date is older than 2 years
- **THEN** the script SHALL remove that subdirectory.

#### Scenario: Data directory contains non-date directory

- **WHEN** `${project_dir}/data` contains a first-level subdirectory whose name is not in `YYYY-MM-DD` format
- **THEN** the script MUST NOT delete that subdirectory as part of backup retention cleanup.

### Requirement: Daily backup script removes expired print task records

`daily_backup_db.sh` SHALL delete records from `t_order_print_task` whose `Fcreate_time` is earlier than 3 days before the script run time.

#### Scenario: Print task is older than 3 days

- **WHEN** `t_order_print_task` contains a record with `Fcreate_time < NOW() - INTERVAL 3 DAY`
- **THEN** the script SHALL delete that record.

#### Scenario: Print task is within 3 days

- **WHEN** `t_order_print_task` contains a record with `Fcreate_time >= NOW() - INTERVAL 3 DAY`
- **THEN** the script MUST NOT delete that record.
