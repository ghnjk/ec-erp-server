# ec-erp-server

电商erp后台服务

## UpSeller 自动登录（保存 cookies）

用于在 Linux 服务器上自动登录 UpSeller 并写入 `cookies/up_seller.cookies`，**不依赖 Chrome / Selenium**。

### 环境要求

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.x | 建议使用项目 conda 环境，如 `ec-data-mining` |
| Node.js | **>= 18**（建议 18 / 20 / 22 LTS） | 仅 CN 出口解腾讯验证码时需要；`jsdom@24` 要求 Node >= 18 |
| npm | 随 Node 安装即可 | 安装 `tools/` 下的 `jsdom` |

```bash
node -v   # 需 >= v18
```

若本机 Node 过旧，可用 nvm 安装：

```bash
nvm install 22
nvm use 22
```

### 首次准备

```bash
cd tools
npm install
```

需要可用的云码 `ydm_token`，以及 UpSeller 账号密码（也可写在环境变量里）。

### 使用方法

```bash
# 自动登录并保存 cookies（优先复用仍有效的 cookies）
python tools/up_seller_cookie.py \
  --email 'xxx@xx.com' \
  --password '***' \
  --ydm-token '***'

# 强制重新登录
python tools/up_seller_cookie.py \
  --email 'xxx@xx.com' \
  --password '***' \
  --ydm-token '***' \
  --force
```

环境变量（可替代部分参数）：

- `UPSELLER_EMAIL` / `UPSELLER_PASSWORD` / `UPSELLER_YDM_TOKEN`
- `UPSELLER_COOKIE_FILE`（默认 `cookies/up_seller.cookies`）
- `UPSELLER_EMAIL_CODE`（邮箱二次验证码）
- `UPSELLER_NODE_BIN`（默认 `node`）

### 登录流程说明

1. 云码识别图片验证码（`/api/vcode`）
2. 人机校验：
   - **CN 出口**：Node + jsdom 调用腾讯云 `TencentCaptcha`（脚本 `tools/upseller_tencent_captcha.js`）
   - **非 CN**：云码 funnel `type=40012` 解 Cloudflare Turnstile
3. 提交 `/api/login`；若风控 `score < 0.7`，会自动调用 `/api/send-code` 发送邮箱验证码

收到邮箱验证码后：

```bash
python tools/up_seller_cookie.py \
  --email 'xxx@xx.com' \
  --password '***' \
  --ydm-token '***' \
  --email-code '123456' \
  --force
```

或交互输入：

```bash
python tools/up_seller_cookie.py \
  --email 'xxx@xx.com' \
  --password '***' \
  --ydm-token '***' \
  --force \
  --prompt-email-code
```

人工浏览器登录（可选备选）：`python tools/up_seller_selenium_cookie.py`

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