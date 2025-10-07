-- EC-ERP 数据库建表语句
-- 数据库: ec_erp_db
-- 字符集: utf8
-- 生成时间: 2024-10

-- ========================================
-- 1. 项目信息表
-- ========================================
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

-- ========================================
-- 2. 用户信息表
-- ========================================
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

-- ========================================
-- 3. 供应商信息表
-- ========================================
CREATE TABLE IF NOT EXISTS `t_supplier_info` (
  `Fsupplier_id` INT NOT NULL AUTO_INCREMENT COMMENT '供应商ID',
  `Fproject_id` VARCHAR(128) COMMENT '所属项目ID',
  `Fsupplier_name` VARCHAR(128) COMMENT '供应商名',
  `Fwechat_account` VARCHAR(128) COMMENT '供应商微信号',
  `Fdetail` VARCHAR(1024) COMMENT '详细信息',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fsupplier_id`),
  KEY `idx_project_id` (`Fproject_id`),
  KEY `idx_supplier_name` (`Fsupplier_name`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='供应商信息表';

-- ========================================
-- 4. SKU商品信息表
-- ========================================
CREATE TABLE IF NOT EXISTS `t_sku_info` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` VARCHAR(256) NOT NULL COMMENT '商品SKU',
  `Fsku_group` VARCHAR(256) COMMENT 'SKU分组',
  `Fsku_name` VARCHAR(1024) COMMENT '商品名称',
  `Fsku_unit_name` VARCHAR(256) NOT NULL DEFAULT '' COMMENT '采购单位',
  `Fsku_unit_quantity` INT NOT NULL DEFAULT 1 COMMENT '每个单位的sku数',
  `Finventory` INT NOT NULL DEFAULT 0 COMMENT '库存量',
  `Favg_sell_quantity` FLOAT NOT NULL DEFAULT 0.0 COMMENT '平均每天销售量',
  `Finventory_support_days` INT NOT NULL DEFAULT 0 COMMENT '库存支撑天数预估',
  `Fshipping_stock_quantity` INT NOT NULL DEFAULT 0 COMMENT '海运中的sku数',
  `Ferp_sku_name` VARCHAR(1024) COMMENT 'ERP商品名称',
  `Ferp_sku_image_url` VARCHAR(10240) COMMENT '商品图片链接',
  `Ferp_sku_id` VARCHAR(256) COMMENT 'erp上sku id',
  `Ferp_sku_info` JSON COMMENT 'erp上商品扩展信息',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Fsku`),
  KEY `idx_sku_group` (`Fsku_group`),
  KEY `idx_sku_name` (`Fsku_name`(255)),
  KEY `idx_erp_sku_name` (`Ferp_sku_name`(255)),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU商品信息表';

-- ========================================
-- 5. SKU采购价格表
-- ========================================
CREATE TABLE IF NOT EXISTS `t_sku_purchase_price` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` VARCHAR(256) NOT NULL COMMENT '商品SKU',
  `Fsupplier_id` INT NOT NULL COMMENT '供应商id',
  `Fsupplier_name` VARCHAR(128) COMMENT '供应商名',
  `Fpurchase_price` INT COMMENT '供应价',
  `Fsku_group` VARCHAR(256) COMMENT 'SKU分组',
  `Fsku_name` VARCHAR(1024) COMMENT '商品名称',
  `Ferp_sku_image_url` VARCHAR(10240) COMMENT '商品图片链接',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Fsku`, `Fsupplier_id`),
  KEY `idx_supplier_name` (`Fsupplier_name`),
  KEY `idx_sku_group` (`Fsku_group`),
  KEY `idx_sku_name` (`Fsku_name`(255)),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU采购价格表';

-- ========================================
-- 6. 采购单表
-- ========================================
CREATE TABLE IF NOT EXISTS `t_purchase_order` (
  `Fpurchase_order_id` INT NOT NULL AUTO_INCREMENT COMMENT '采购单id',
  `Fproject_id` VARCHAR(128) COMMENT '所属项目ID',
  `Fsupplier_id` INT COMMENT '供应商id',
  `Fsupplier_name` VARCHAR(128) COMMENT '供应商名',
  `Fpurchase_step` VARCHAR(128) COMMENT '采购状态: 草稿/供应商捡货中/待发货/海运中/已入库/完成/废弃',
  `Fsku_summary` VARCHAR(10240) NOT NULL DEFAULT '' COMMENT '货物概述',
  `Fsku_amount` INT NOT NULL DEFAULT 0 COMMENT 'sku采购金额',
  `Fpay_amount` INT NOT NULL DEFAULT 0 COMMENT '支付金额',
  `Fpay_state` INT NOT NULL DEFAULT 0 COMMENT '支付状态，0: 未支付， 1：已支付',
  `Fpurchase_date` VARCHAR(128) COMMENT '采购日期',
  `Fexpect_arrive_warehouse_date` VARCHAR(128) COMMENT '预计到货日期',
  `Fmaritime_port` VARCHAR(128) COMMENT '海运港口',
  `Fshipping_company` VARCHAR(128) COMMENT '货运公司',
  `Fshipping_fee` VARCHAR(128) COMMENT '海运费',
  `Farrive_warehouse_date` VARCHAR(128) COMMENT '入库日期',
  `Fremark` VARCHAR(10240) NOT NULL DEFAULT '' COMMENT '备注',
  `Fpurchase_skus` JSON COMMENT '采购的货品',
  `Fstore_skus` JSON COMMENT '入库的货品',
  `op_log` JSON COMMENT '操作记录',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fpurchase_order_id`),
  KEY `idx_supplier_name` (`Fsupplier_name`),
  KEY `idx_purchase_step` (`Fpurchase_step`),
  KEY `idx_purchase_date` (`Fpurchase_date`),
  KEY `idx_expect_arrive_warehouse_date` (`Fexpect_arrive_warehouse_date`),
  KEY `idx_maritime_port` (`Fmaritime_port`),
  KEY `idx_shipping_company` (`Fshipping_company`),
  KEY `idx_arrive_warehouse_date` (`Farrive_warehouse_date`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='采购单表';

-- ========================================
-- 7. SKU销售数据统计表
-- ========================================
CREATE TABLE IF NOT EXISTS `t_sku_sale_estimate` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Forder_date` DATETIME NOT NULL COMMENT '订单日期',
  `Fsku` VARCHAR(256) NOT NULL COMMENT '商品SKU',
  `Fshop_id` VARCHAR(256) NOT NULL COMMENT '店铺id',
  `Fsku_class` VARCHAR(256) COMMENT 'SKU大类',
  `Fsku_group` VARCHAR(256) COMMENT 'SKU分组',
  `Fsku_name` VARCHAR(1024) COMMENT '商品名称',
  `Fshop_name` VARCHAR(256) NOT NULL DEFAULT '' COMMENT '店铺名',
  `Fshop_owner` VARCHAR(256) NOT NULL DEFAULT '' COMMENT '店铺运营人员',
  `Fsale_amount` INT NOT NULL DEFAULT 0 COMMENT '销售额',
  `Fsale_quantity` INT NOT NULL DEFAULT 0 COMMENT '销售的sku量',
  `Fcancel_amount` INT NOT NULL DEFAULT 0 COMMENT '取消的销售额',
  `Fcancel_quantity` INT NOT NULL DEFAULT 0 COMMENT '取消的sku量',
  `Fcancel_orders` INT NOT NULL DEFAULT 0 COMMENT '取消的订单数',
  `Frefund_amount` INT NOT NULL DEFAULT 0 COMMENT '退款的销售额',
  `Frefund_quantity` INT NOT NULL DEFAULT 0 COMMENT '退款的sku量',
  `Frefund_orders` INT NOT NULL DEFAULT 0 COMMENT '退款的订单数',
  `Fefficient_amount` INT NOT NULL DEFAULT 0 COMMENT '有效销售额',
  `Fefficient_quantity` INT NOT NULL DEFAULT 0 COMMENT '有效的sku量',
  `Fefficient_orders` INT NOT NULL DEFAULT 0 COMMENT '有效订单数',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` INT NOT NULL DEFAULT 0 COMMENT '记录版本号',
  `Fmodify_user` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Forder_date`, `Fsku`, `Fshop_id`),
  KEY `idx_sku_class` (`Fsku_class`),
  KEY `idx_sku_group` (`Fsku_group`),
  KEY `idx_sku_name` (`Fsku_name`(255)),
  KEY `idx_shop_name` (`Fshop_name`),
  KEY `idx_shop_owner` (`Fshop_owner`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU销售数据统计表';

-- ========================================
-- 8. SKU拣货备注表
-- ========================================
CREATE TABLE IF NOT EXISTS `t_sku_picking_note` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` VARCHAR(512) NOT NULL COMMENT '商品SKU',
  `Fpicking_unit` FLOAT COMMENT '拣货单位（1个sku的换算）',
  `Fpicking_unit_name` VARCHAR(256) COMMENT '拣货单位名',
  `Fsupport_pkg_picking` TINYINT(1) COMMENT '支持pkg拣货打包模式',
  `Fpkg_picking_unit` FLOAT COMMENT 'pkg打包，拣货单位（1个sku的换算）',
  `Fpkg_picking_unit_name` VARCHAR(256) COMMENT 'pkg打包，拣货单位名',
  `Fpicking_sku_name` VARCHAR(256) COMMENT '拣货sku名',
  `Fcreate_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `Fmodify_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`, `Fsku`),
  KEY `idx_picking_sku_name` (`Fpicking_sku_name`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU拣货备注表';

-- ========================================
-- 9. 订单打印任务表
-- ========================================
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

-- ========================================
-- 10. SKU销售价格表
-- ========================================
CREATE TABLE `t_sku_sale_price` (
  `Fproject_id` varchar(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` varchar(128) NOT NULL COMMENT '商品SKU',
  `Funit_price` float DEFAULT NULL COMMENT '单价',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`,`Fsku`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU销售价格表'
-- ========================================
-- 11. 销售订单表
-- ========================================
CREATE TABLE IF NOT EXISTS `t_sale_order` (
  `Fproject_id` VARCHAR(128) NOT NULL COMMENT '所属项目ID',
  `Forder_id` INT NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `Forder_date` DATETIME COMMENT '订单日期',
  `Fsale_sku_list` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '销售SKU列表，包含sku, sku_group, sku_name, erp_sku_image_url, unit_price, quantity, total_amount',
  `Ftotal_amount` FLOAT COMMENT '订单总金额',
  `Fstatus` VARCHAR(128) COMMENT '订单状态，待同步、已同步',
  `Fis_delete` INT NOT NULL DEFAULT 0 COMMENT '是否逻辑删除, 1: 删除',
  `Fcreate_time` DATETIME DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` DATETIME DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Forder_id`),
  KEY `idx_project_id` (`Fproject_id`),
  KEY `idx_order_date` (`Forder_date`),
  KEY `idx_status` (`Fstatus`),
  KEY `idx_is_delete` (`Fis_delete`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='销售订单表';

-- ========================================
-- 索引说明
-- ========================================
-- 1. 所有表都有 create_time 和 modify_time 的索引，用于按时间查询
-- 2. 包含 project_id 的表都会在查询时加上项目过滤条件
-- 3. 经常用于搜索的字段（如 name、group）都添加了索引
-- 4. 复合主键表的主键顺序按照查询频率设计

-- ========================================
-- 字段命名规范
-- ========================================
-- 1. 表名：t_ 前缀 + 功能描述（下划线分隔）
-- 2. 字段名：F 前缀 + 字段描述（下划线分隔）
-- 3. 所有字段都有注释说明

-- ========================================
-- 数据类型说明
-- ========================================
-- 1. 金额字段使用 INT 类型，单位为"分"，避免浮点数精度问题
-- 2. JSON 类型用于存储复杂结构数据（如角色列表、SKU列表等）
-- 3. 日期字段根据需要使用 DATETIME 或 VARCHAR(128)
-- 4. 布尔字段使用 TINYINT(1) 或 INT（0/1）

-- ========================================
-- 使用示例
-- ========================================
-- 创建数据库：
-- CREATE DATABASE IF NOT EXISTS ec_erp_db DEFAULT CHARACTER SET utf8;
-- USE ec_erp_db;

-- 执行本脚本创建所有表：
-- source ec_erp_db.sql;

