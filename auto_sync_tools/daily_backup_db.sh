#!/usr/bin/env bash
set -euo pipefail

# Daily cron example:
# cd /data/ec-erp-server && /bin/bash auto_sync_tools/daily_backup_db.sh >> logs/daily_backup_db.log 2>&1

BACKUP_TABLES=(
  "t_project_info"
  "t_purchase_order"
  "t_sale_order"
  "t_sku_info"
  "t_sku_picking_note"
  "t_sku_purchase_price"
  "t_sku_sale_price"
  "t_supplier_info"
  "t_user_info"
)

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

die() {
  log "ERROR: $*"
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

find_project_dir() {
  local current_dir
  current_dir="$(pwd -P)"

  while [[ "$current_dir" != "/" ]]; do
    if [[ -f "$current_dir/ec_erp_app.py" && -d "$current_dir/conf" ]]; then
      printf '%s\n' "$current_dir"
      return 0
    fi
    current_dir="$(dirname "$current_dir")"
  done

  return 1
}

load_db_config() {
  local config_file="$1"

  [[ -f "$config_file" ]] || die "database config file not found: $config_file"

  eval "$(
    python3 - "$config_file" <<'PY'
import json
import shlex
import sys

config_file = sys.argv[1]
with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

db_config = config.get("db_config") or {}
required_keys = ["host", "port", "user", "password"]
missing_keys = [key for key in required_keys if db_config.get(key) in (None, "")]
if missing_keys:
    raise SystemExit("missing db_config fields: " + ", ".join(missing_keys))

values = {
    "DB_HOST": db_config["host"],
    "DB_PORT": str(db_config["port"]),
    "DB_USER": db_config["user"],
    "DB_PASSWORD": db_config["password"],
    "DB_NAME": db_config.get("db_name") or "ec_erp_db",
}

for key, value in values.items():
    print(f"{key}={shlex.quote(str(value))}")
PY
  )"
}

create_backup_dirs() {
  local data_dir="$1"
  local backup_dir="$2"

  mkdir -p "$data_dir" "$backup_dir"
}

backup_tables() {
  local backup_file="$1"

  log "start database backup: ${DB_NAME} -> ${backup_file}"

  MYSQL_PWD="$DB_PASSWORD" mysqldump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --user="$DB_USER" \
    --single-transaction \
    --routines=false \
    --triggers=false \
    "$DB_NAME" \
    "${BACKUP_TABLES[@]}" \
    > "$backup_file"

  log "database backup finished: ${backup_file}"
}

cleanup_old_backup_dirs() {
  local data_dir="$1"

  [[ -d "$data_dir" ]] || return 0

  python3 - "$data_dir" <<'PY'
import datetime
import os
import re
import shutil
import sys

data_dir = sys.argv[1]
today = datetime.date.today()
try:
    cutoff = today.replace(year=today.year - 2)
except ValueError:
    cutoff = today.replace(year=today.year - 2, day=28)
date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

for name in os.listdir(data_dir):
    path = os.path.join(data_dir, name)
    if not os.path.isdir(path) or not date_pattern.match(name):
        continue

    try:
        backup_date = datetime.date.fromisoformat(name)
    except ValueError:
        continue

    if backup_date < cutoff:
        shutil.rmtree(path)
        print(f"removed expired backup directory: {path}")
PY
}

cleanup_order_print_tasks() {
  log "start cleanup t_order_print_task records older than 3 days"

  MYSQL_PWD="$DB_PASSWORD" mysql \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --user="$DB_USER" \
    "$DB_NAME" \
    --execute="DELETE FROM t_order_print_task WHERE Fcreate_time < DATE_SUB(NOW(), INTERVAL 3 DAY);"

  log "cleanup t_order_print_task finished"
}

main() {
  local project_dir data_dir today backup_dir backup_file mode

  mode="${1:-run}"

  require_command "python3"

  project_dir="$(find_project_dir)" || die "project root not found from current path: $(pwd -P)"

  if [[ "$mode" == "--print-project-dir" ]]; then
    printf '%s\n' "$project_dir"
    return 0
  fi

  data_dir="${project_dir}/data"
  today="$(date '+%Y-%m-%d')"
  backup_dir="${data_dir}/${today}"
  backup_file="${backup_dir}/ec_erp_db.sql"

  create_backup_dirs "$data_dir" "$backup_dir"

  if [[ "$mode" == "--cleanup-backups-only" ]]; then
    cleanup_old_backup_dirs "$data_dir"
    log "backup directory cleanup finished"
    return 0
  fi

  [[ "$mode" == "run" ]] || die "unknown argument: $mode"

  require_command "mysqldump"
  require_command "mysql"

  load_db_config "${project_dir}/conf/application.json"
  backup_tables "$backup_file"
  cleanup_old_backup_dirs "$data_dir"
  cleanup_order_print_tasks

  log "daily backup job finished successfully"
}

main "$@"
