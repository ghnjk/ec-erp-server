# 用户登录

## 接口信息

- **接口路径**: `/erp_api/system/login_user`
- **请求方法**: POST
- **接口描述**: 通过用户名和密码进行登录

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| account | string | 是 | 用户账号 |
| password | string | 是 | 用户密码（明文） |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| result | int | 响应码，0表示成功，其他表示失败 |
| resultMsg | string | 响应消息 |
| traceId | long | 追踪ID |
| data | object | 用户信息对象 |
| ∟ userName | string | 用户名 |
| ∟ groupName | string | 用户组名称（当前为空） |
| ∟ roles | array | 用户角色列表 |
| &nbsp;&nbsp;∟ name | string | 角色名称 |
| &nbsp;&nbsp;∟ level | int | 角色等级 |
| &nbsp;&nbsp;∟ memo | string | 角色说明（Unicode编码） |
| &nbsp;&nbsp;∟ project_id | string | 所属项目ID |
| ∟ admin | int | 是否管理员，1表示是，0表示否 |
| ∟ project_id | string | 当前项目ID |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 1002 | 用户不存在或密码错误 |

## 请求示例

```json
{
  "account": "jk",
  "password": "123456"
}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "admin": 1,
    "groupName": "",
    "roles": [
      {
        "level": 1,
        "memo": "u4f9bu5e94u94feu7ba1u7406",
        "name": "supply",
        "project_id": "philipine"
      },
      {
        "level": 1,
        "memo": "u4ed3u5e93u7ba1u7406",
        "name": "storehouse",
        "project_id": "philipine"
      }
    ],
    "userName": "jk"
  },
  "result": 0,
  "resultMsg": "success",
  "traceId": 1709991728857
}
```

### 错误响应

```json
{
  "result": 1002,
  "resultMsg": "用户不存在或者密码异常",
  "traceId": 1709991728857
}
```

## 业务逻辑说明

1. 接收用户名和明文密码
2. 对密码进行SHA256加密
3. 从数据库查询用户信息
4. 验证用户是否存在、是否删除、密码是否正确
5. 验证通过后，在session中保存`user_name`和`project_id`
6. 返回用户信息，包含用户的所有角色

## 注意事项

- 前端传入的password为明文，后端会进行SHA256加密后比对
- 登录成功后会建立session
- 返回的角色列表会根据当前project_id进行过滤
- 角色信息中的memo字段为Unicode编码

