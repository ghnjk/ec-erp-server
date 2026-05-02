# UpSeller Client 集成测试报告

- 生成时间：2026-05-02 06:32:26
- Python：`/Users/jkguo/miniforge3/envs/ec-data-mining/bin/python`
- Cookie 文件：`/Users/jkguo/workspace/ec-erp-server/test/up_test/up_seller.cookies`（存在=False）

## 结论

未登录，后续接口未执行。

### 登录结果

- 登录：失败，账号密码登录失败：argument of type 'NoneType' is not iterable

### 已验证接口（未登录也可访问）

| 接口 | 结果 |
|------|------|
| GET /api/is-login | 可达 |
| GET /api/getCountryCode | 可达 |
| GET /api/vcode | 可达 |