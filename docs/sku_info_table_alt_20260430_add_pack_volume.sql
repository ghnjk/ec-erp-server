-- ========================================================================
-- 变更：t_sku_info 新增打包体积字段（长 / 宽 / 高，单位 cm）
-- 日期：2026-04-30
-- 关联 OpenSpec change：openspec/changes/add-sku-pack-volume
-- ------------------------------------------------------------------------
-- 业务背景：
--   SKU 主数据缺少"每个采购单位"的打包尺寸，导致海运费 / 装柜 / 货架占用
--   等场景无法基于 SKU 主数据推算。本次新增 3 个 INT 字段（cm，默认 0）。
--
-- 风险评估：低
--   - 单表 ADD COLUMN，MySQL 8 默认 INSTANT/INPLACE，不锁表或锁表时间极短
--   - 字段 NOT NULL DEFAULT 0，存量行 0 不影响读路径
--   - sync_all_sku 与 sync_sku_inventory.py 不会覆盖体积字段
--
-- 执行说明：
--   * 4 个国家库分别执行：philipine / india / malaysia / thailand
--   * 推荐业务低峰期执行
--   * 本脚本幂等：已存在字段时通过 INFORMATION_SCHEMA 检查跳过
--
-- 回滚方式（仅回滚字段，不回滚业务数据）：
--   ALTER TABLE t_sku_info
--     DROP COLUMN Fsku_pack_length,
--     DROP COLUMN Fsku_pack_width,
--     DROP COLUMN Fsku_pack_height;
-- ========================================================================

-- ------------------------------------------------------------------------
-- 1. Fsku_pack_length（打包长度，cm）
-- ------------------------------------------------------------------------
SET @col_exists := (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 't_sku_info'
    AND COLUMN_NAME = 'Fsku_pack_length'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE t_sku_info ADD COLUMN `Fsku_pack_length` INT NOT NULL DEFAULT 0 COMMENT ''打包长度（cm）'' AFTER `Fsku_unit_quantity`;',
  'SELECT ''Fsku_pack_length already exists, skip'' AS msg;'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ------------------------------------------------------------------------
-- 2. Fsku_pack_width（打包宽度，cm）
-- ------------------------------------------------------------------------
SET @col_exists := (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 't_sku_info'
    AND COLUMN_NAME = 'Fsku_pack_width'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE t_sku_info ADD COLUMN `Fsku_pack_width` INT NOT NULL DEFAULT 0 COMMENT ''打包宽度（cm）'' AFTER `Fsku_pack_length`;',
  'SELECT ''Fsku_pack_width already exists, skip'' AS msg;'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ------------------------------------------------------------------------
-- 3. Fsku_pack_height（打包高度，cm）
-- ------------------------------------------------------------------------
SET @col_exists := (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 't_sku_info'
    AND COLUMN_NAME = 'Fsku_pack_height'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE t_sku_info ADD COLUMN `Fsku_pack_height` INT NOT NULL DEFAULT 0 COMMENT ''打包高度（cm）'' AFTER `Fsku_pack_width`;',
  'SELECT ''Fsku_pack_height already exists, skip'' AS msg;'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ------------------------------------------------------------------------
-- 4. 数据回填：存量行的 3 个字段值为 NULL 时（理论上 NOT NULL 不会出现）兜底为 0
-- ------------------------------------------------------------------------
UPDATE t_sku_info SET Fsku_pack_length = 0 WHERE Fsku_pack_length IS NULL;
UPDATE t_sku_info SET Fsku_pack_width  = 0 WHERE Fsku_pack_width  IS NULL;
UPDATE t_sku_info SET Fsku_pack_height = 0 WHERE Fsku_pack_height IS NULL;

-- ------------------------------------------------------------------------
-- 5. 验证（可选，手动执行查看输出）
-- ------------------------------------------------------------------------
-- SHOW CREATE TABLE t_sku_info;
-- SELECT Fsku, Fsku_pack_length, Fsku_pack_width, Fsku_pack_height FROM t_sku_info LIMIT 5;
