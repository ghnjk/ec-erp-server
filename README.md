# ec-erp-server

电商erp后台服务

## 国家搭建

```bash
create database ec_erp_db_ind;
CREATE USER 'ec_erp_ind'@'localhost' IDENTIFIED BY 'ec_erp_myr#2025';
GRANT ALL PRIVILEGES ON ec_erp_db_ind.* TO 'ec_erp_ind'@'localhost';
FLUSH PRIVILEGES;


mysqldump -u root  ec_erp_db_myr > ec_erp_db_myr.sql
mysql -u root  ec_erp_db_ind < ec_erp_db_myr.sql
# 修改和初始化商品等相关信息
# 修改和初始化商品等相关信息
update t_sku_info set Fproject_id = "thailand";
update t_sku_picking_note  set Fproject_id = "thailand";
update t_supplier_info  set Fproject_id = "thailand";
delete from t_user_info;
# 注册账户 
python add_user.py thailand  xx_user _xx_passwd

crontab:
20 5 * * *  cd /data/ec-erp-server_ind/static/print/  && find /data/ec-erp-server_ind/static/print/ -mtime +10 -exec rm -rf {} \;

30 8 * * * cd /data/ec-erp-server_ind/auto_sync_tools && /root/miniconda3/envs/ec_erp_env/bin/python3  sync_sku_inventory.py 2>&1 1>>std.log

```