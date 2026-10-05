-- MySQL dump 10.14  Distrib 5.5.68-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: ec_erp_db
-- ------------------------------------------------------
-- Server version	5.5.68-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `t_order_print_task`
--

DROP TABLE IF EXISTS `t_order_print_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_order_print_task` (
  `Fproject_id` varchar(128) NOT NULL COMMENT '所属项目ID',
  `Ftask_id` varchar(128) NOT NULL COMMENT '打印任务id',
  `Fpdf_file_url` varchar(256) DEFAULT NULL COMMENT '打印的pdf地址',
  `Fcurrent_step` varchar(1024) DEFAULT NULL COMMENT '当前任务步骤',
  `Fprogress` int(11) DEFAULT NULL COMMENT '当前进度0-100',
  `Forder_list` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '订单列表',
  `Flogs` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '处理日志',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`,`Ftask_id`),
  KEY `ix_t_order_print_task_Fmodify_time` (`Fmodify_time`),
  KEY `ix_t_order_print_task_Fcreate_time` (`Fcreate_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_project_info`
--

DROP TABLE IF EXISTS `t_project_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_project_info` (
  `Fproject_id` varchar(128) NOT NULL COMMENT '项目ID',
  `Fdoc` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '项目配置，对应ProjectConfig类',
  `Fis_delete` int(11) DEFAULT '0' COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` int(11) DEFAULT '0' COMMENT '记录版本号',
  `Fmodify_user` varchar(128) DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`),
  KEY `ix_t_project_info_Fmodify_time` (`Fmodify_time`),
  KEY `ix_t_project_info_Fcreate_time` (`Fcreate_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_purchase_order`
--

DROP TABLE IF EXISTS `t_purchase_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_purchase_order` (
  `Fpurchase_order_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '采购单id',
  `Fproject_id` varchar(128) DEFAULT NULL COMMENT '所属项目ID',
  `Forder_type` int(11) NOT NULL DEFAULT '1' COMMENT '采购单类型, 1: 境内进货采购单, 2: 境外线下采购单',
  `Fsupplier_id` int(11) DEFAULT NULL COMMENT '供应商id',
  `Fsupplier_name` varchar(128) DEFAULT NULL COMMENT '供应商名',
  `Fpurchase_step` varchar(128) DEFAULT NULL COMMENT '采购状态',
  `Fsku_summary` varchar(10240) DEFAULT '' COMMENT '货物概述',
  `Fsku_amount` int(11) DEFAULT '0' COMMENT 'sku采购金额',
  `Fpay_amount` int(11) DEFAULT '0' COMMENT '支付金额',
  `Fpay_state` int(11) DEFAULT '0' COMMENT '支付状态，0： 未支付， 1：已支付',
  `Fpurchase_date` varchar(128) DEFAULT NULL COMMENT '采购日期',
  `Fexpect_arrive_warehouse_date` varchar(128) DEFAULT NULL COMMENT '预计到货日期',
  `Fmaritime_port` varchar(128) DEFAULT NULL COMMENT '海运港口',
  `Fshipping_company` varchar(128) DEFAULT NULL COMMENT '货运公司',
  `Fshipping_fee` varchar(128) DEFAULT NULL COMMENT '海运费',
  `Farrive_warehouse_date` varchar(128) DEFAULT NULL COMMENT '入库日期',
  `Fremark` varchar(10240) DEFAULT '' COMMENT '备注',
  `Fpurchase_skus` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '采购的货品',
  `Fstore_skus` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '入库的货品',
  `op_log` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '操作记录',
  `Fis_delete` int(11) DEFAULT '0' COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` int(11) DEFAULT '0' COMMENT '记录版本号',
  `Fmodify_user` varchar(128) DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fpurchase_order_id`),
  KEY `ix_t_purchase_order_Fsupplier_name` (`Fsupplier_name`),
  KEY `ix_t_purchase_order_Fmodify_time` (`Fmodify_time`),
  KEY `ix_t_purchase_order_Fpurchase_step` (`Fpurchase_step`),
  KEY `ix_t_purchase_order_Fpurchase_date` (`Fpurchase_date`),
  KEY `ix_t_purchase_order_Fexpect_arrive_warehouse_date` (`Fexpect_arrive_warehouse_date`),
  KEY `ix_t_purchase_order_Fmaritime_port` (`Fmaritime_port`),
  KEY `ix_t_purchase_order_Fshipping_company` (`Fshipping_company`),
  KEY `ix_t_purchase_order_Farrive_warehouse_date` (`Farrive_warehouse_date`),
  KEY `ix_t_purchase_order_Fcreate_time` (`Fcreate_time`),
  KEY `idx_order_type` (`Forder_type`)
) ENGINE=InnoDB AUTO_INCREMENT=352 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sale_order`
--

DROP TABLE IF EXISTS `t_sale_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sale_order` (
  `Fproject_id` varchar(128) NOT NULL COMMENT '所属项目ID',
  `Forder_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `Forder_date` datetime DEFAULT NULL COMMENT '订单日期',
  `Fsale_sku_list` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '销售SKU列表，包含sku, sku_group, sku_name, erp_sku_image_url, unit_price, quantity, total_amount',
  `Ftotal_amount` float DEFAULT NULL COMMENT '订单总金额',
  `Fstatus` varchar(128) DEFAULT NULL COMMENT '订单状态，待同步、已同步',
  `Fis_delete` int(11) NOT NULL DEFAULT '0' COMMENT '是否逻辑删除, 1: 删除',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Forder_id`),
  KEY `idx_project_id` (`Fproject_id`),
  KEY `idx_order_date` (`Forder_date`),
  KEY `idx_status` (`Fstatus`),
  KEY `idx_is_delete` (`Fis_delete`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COMMENT='销售订单表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sku_info`
--

DROP TABLE IF EXISTS `t_sku_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sku_info` (
  `Fproject_id` varchar(64) NOT NULL COMMENT '所属项目ID',
  `Fsku` varchar(128) NOT NULL COMMENT '商品SKU',
  `Fsku_group` varchar(256) DEFAULT NULL COMMENT '商品SKU分组',
  `Fsku_name` varchar(1024) DEFAULT NULL COMMENT '商品名称',
  `Finventory` int(11) DEFAULT '0' COMMENT '库存量',
  `Ferp_sku_name` varchar(1024) DEFAULT NULL COMMENT 'ERP商品名称',
  `Ferp_sku_image_url` varchar(10240) DEFAULT NULL COMMENT '商品图片链接',
  `Ferp_sku_id` varchar(256) DEFAULT NULL COMMENT 'erp上sku id',
  `Ferp_sku_info` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'erp上商品扩展信息',
  `Fis_delete` int(11) DEFAULT '0' COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` int(11) DEFAULT '0' COMMENT '记录版本号',
  `Fmodify_user` varchar(128) DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  `Fsku_unit_name` varchar(256) DEFAULT '' COMMENT '采购单位',
  `Fsku_unit_quantity` int(11) DEFAULT '1' COMMENT '每个单位的sku数',
  `Fsku_pack_length` int(11) NOT NULL DEFAULT '0' COMMENT '打包长度（cm）',
  `Fsku_pack_width` int(11) NOT NULL DEFAULT '0' COMMENT '打包宽度（cm）',
  `Fsku_pack_height` int(11) NOT NULL DEFAULT '0' COMMENT '打包高度（cm）',
  `Favg_sell_quantity` float DEFAULT '0' COMMENT '平均每天销售量',
  `Fshipping_stock_quantity` int(11) DEFAULT '0' COMMENT '海运中的sku数',
  `Finventory_support_days` int(11) DEFAULT '0' COMMENT '库存支撑天数预估',
  PRIMARY KEY (`Fproject_id`,`Fsku`),
  KEY `ix_t_sku_info_Fsku_group` (`Fsku_group`(255)),
  KEY `ix_t_sku_info_Fsku_name` (`Fsku_name`(255)),
  KEY `ix_t_sku_info_Ferp_sku_name` (`Ferp_sku_name`(255)),
  KEY `ix_t_sku_info_Fcreate_time` (`Fcreate_time`),
  KEY `ix_t_sku_info_Fmodify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sku_picking_note`
--

DROP TABLE IF EXISTS `t_sku_picking_note`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sku_picking_note` (
  `Fproject_id` varchar(64) NOT NULL COMMENT '所属项目ID',
  `Fsku` varchar(128) NOT NULL COMMENT '商品SKU',
  `Fpicking_unit` float DEFAULT NULL COMMENT '拣货单位（1个sku的换算）',
  `Fpicking_unit_name` varchar(256) DEFAULT NULL COMMENT '拣货单位名',
  `Fsupport_pkg_picking` tinyint(1) DEFAULT NULL COMMENT '支持pkg拣货打包模式',
  `Fpkg_picking_unit` float DEFAULT NULL COMMENT 'pkg打包，拣货单位（1个sku的换算）',
  `Fpkg_picking_unit_name` varchar(256) DEFAULT NULL COMMENT 'pkg打包，拣货单位名',
  `Fpicking_sku_name` varchar(256) DEFAULT NULL COMMENT '拣货sku名',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`,`Fsku`),
  KEY `ix_t_sku_picking_note_Fcreate_time` (`Fcreate_time`),
  KEY `ix_t_sku_picking_note_Fpicking_sku_name` (`Fpicking_sku_name`(255)),
  KEY `ix_t_sku_picking_note_Fmodify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sku_purchase_price`
--

DROP TABLE IF EXISTS `t_sku_purchase_price`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sku_purchase_price` (
  `Fproject_id` varchar(64) NOT NULL COMMENT '所属项目ID',
  `Fsku` varchar(128) NOT NULL COMMENT '商品SKU',
  `Fsupplier_id` int(11) NOT NULL COMMENT '供应商id',
  `Fsupplier_name` varchar(128) DEFAULT NULL COMMENT '供应商名',
  `Fpurchase_price` int(11) DEFAULT NULL COMMENT '供应价',
  `Fsku_group` varchar(256) DEFAULT NULL COMMENT '商品SKU分组',
  `Fsku_name` varchar(1024) DEFAULT NULL COMMENT '商品名称',
  `Ferp_sku_image_url` varchar(10240) DEFAULT NULL COMMENT '商品图片链接',
  `Fis_delete` int(11) DEFAULT '0' COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` int(11) DEFAULT '0' COMMENT '记录版本号',
  `Fmodify_user` varchar(128) DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`,`Fsku`,`Fsupplier_id`),
  KEY `ix_t_sku_purchase_price_Fsupplier_name` (`Fsupplier_name`),
  KEY `ix_t_sku_purchase_price_Fsku_group` (`Fsku_group`(255)),
  KEY `ix_t_sku_purchase_price_Fsku_name` (`Fsku_name`(255)),
  KEY `ix_t_sku_purchase_price_Fcreate_time` (`Fcreate_time`),
  KEY `ix_t_sku_purchase_price_Fmodify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sku_sale_estimate`
--

DROP TABLE IF EXISTS `t_sku_sale_estimate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sku_sale_estimate` (
  `Fproject_id` varchar(64) NOT NULL COMMENT '所属项目ID',
  `Forder_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '订单日期',
  `Fsku` varchar(128) NOT NULL COMMENT '商品SKU',
  `Fshop_id` varchar(128) NOT NULL COMMENT '店铺id',
  `Fsku_class` varchar(256) DEFAULT NULL COMMENT '商品SKU大类',
  `Fsku_group` varchar(256) DEFAULT NULL COMMENT '商品SKU分组',
  `Fsku_name` varchar(1024) DEFAULT NULL COMMENT '商品名称',
  `Fshop_name` varchar(256) DEFAULT '' COMMENT '店铺名',
  `Fshop_owner` varchar(256) DEFAULT '' COMMENT '店铺运营人员',
  `Fsale_amount` int(11) DEFAULT '0' COMMENT '销售额',
  `Fsale_quantity` int(11) DEFAULT '0' COMMENT '销售的sku量',
  `Fcancel_amount` int(11) DEFAULT '0' COMMENT '取消的销售额',
  `Fcancel_quantity` int(11) DEFAULT '0' COMMENT '取消的sku量',
  `Fcancel_orders` int(11) DEFAULT '0' COMMENT '取消的订单数',
  `Frefund_amount` int(11) DEFAULT '0' COMMENT '退款的销售额',
  `Frefund_quantity` int(11) DEFAULT '0' COMMENT '退款的sku量',
  `Frefund_orders` int(11) DEFAULT '0' COMMENT '退款的订单数',
  `Fefficient_amount` int(11) DEFAULT '0' COMMENT '有效销售额',
  `Fefficient_quantity` int(11) DEFAULT '0' COMMENT '有效的sku量',
  `Fefficient_orders` int(11) DEFAULT '0' COMMENT '有效订单数',
  `Fis_delete` int(11) DEFAULT '0' COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` int(11) DEFAULT '0' COMMENT '记录版本号',
  `Fmodify_user` varchar(128) DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`,`Forder_date`,`Fsku`,`Fshop_id`),
  KEY `ix_t_sku_sale_estimate_Fshop_name` (`Fshop_name`(255)),
  KEY `ix_t_sku_sale_estimate_Fshop_owner` (`Fshop_owner`(255)),
  KEY `ix_t_sku_sale_estimate_Fsku_class` (`Fsku_class`(255)),
  KEY `ix_t_sku_sale_estimate_Fcreate_time` (`Fcreate_time`),
  KEY `ix_t_sku_sale_estimate_Fsku_group` (`Fsku_group`(255)),
  KEY `ix_t_sku_sale_estimate_Fmodify_time` (`Fmodify_time`),
  KEY `ix_t_sku_sale_estimate_Fsku_name` (`Fsku_name`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sku_sale_price`
--

DROP TABLE IF EXISTS `t_sku_sale_price`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sku_sale_price` (
  `Fproject_id` varchar(128) NOT NULL COMMENT '所属项目ID',
  `Fsku` varchar(128) NOT NULL COMMENT '商品SKU',
  `Funit_price` float DEFAULT NULL COMMENT '单价',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fproject_id`,`Fsku`),
  KEY `idx_create_time` (`Fcreate_time`),
  KEY `idx_modify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='SKU销售价格表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_supplier_info`
--

DROP TABLE IF EXISTS `t_supplier_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_supplier_info` (
  `Fsupplier_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '供应商ID',
  `Fproject_id` varchar(128) DEFAULT NULL COMMENT '所属项目ID',
  `Fsupplier_name` varchar(128) DEFAULT NULL COMMENT '供应商名',
  `Fwechat_account` varchar(128) DEFAULT NULL COMMENT '供应商微信号',
  `Fdetail` varchar(1024) DEFAULT NULL COMMENT '详细信息',
  `Fis_delete` int(11) DEFAULT '0' COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` int(11) DEFAULT '0' COMMENT '记录版本号',
  `Fmodify_user` varchar(128) DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fsupplier_id`),
  KEY `ix_t_supplier_info_Fmodify_time` (`Fmodify_time`),
  KEY `ix_t_supplier_info_Fproject_id` (`Fproject_id`),
  KEY `ix_t_supplier_info_Fcreate_time` (`Fcreate_time`),
  KEY `ix_t_supplier_info_Fsupplier_name` (`Fsupplier_name`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_user_info`
--

DROP TABLE IF EXISTS `t_user_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_user_info` (
  `Fuser_name` varchar(128) NOT NULL COMMENT '用户名',
  `Fdefault_project_id` varchar(128) DEFAULT NULL COMMENT '默认项目',
  `Fpassword` varchar(256) DEFAULT NULL COMMENT '用户密码',
  `Froles` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '用户角色列表',
  `Fis_admin` int(11) DEFAULT '0' COMMENT '是否管理员, 1: 管理员',
  `Fis_delete` int(11) DEFAULT '0' COMMENT '是否逻辑删除, 1: 删除',
  `Fversion` int(11) DEFAULT '0' COMMENT '记录版本号',
  `Fmodify_user` varchar(128) DEFAULT '' COMMENT '修改用户',
  `Fcreate_time` datetime DEFAULT NULL COMMENT '创建时间',
  `Fmodify_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`Fuser_name`),
  KEY `ix_t_user_info_Fcreate_time` (`Fcreate_time`),
  KEY `ix_t_user_info_Fmodify_time` (`Fmodify_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-05 16:29:26
