ALTER TABLE t_purchase_order ADD COLUMN `Forder_type` INT NOT NULL DEFAULT 1 COMMENT '采购单类型, 1: 境内进货采购单, 2: 境外线下采购单' AFTER `Fproject_id`;
ALTER TABLE t_purchase_order ADD INDEX `idx_order_type` (`Forder_type`);
UPDATE t_purchase_order SET Forder_type = 1 WHERE Forder_type IS NULL;
