# 通过Token登录

## 接口信息

- **接口路径**: `/erp_api/system/login_user_with_token`
- **请求方法**: POST
- **接口描述**: 通过Base64编码的token进行用户登录，或获取当前登录用户信息

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| token | string | 否 | Base64编码的token字符串，格式为: `user_name=xxx&password=xxx`。如果为空，则返回当前登录用户信息 |

### Token格式说明

token需要先按照URL query string格式拼接：
```
user_name=账号&password=密码
```

然后进行Base64编码后传入。

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
| 1001 | 用户未登录 |
| 1002 | 用户不存在或密码错误 |

## 请求示例

```json
{
  "token": "dXNlcl9uYW1lPWprJnBhc3N3b3JkPTEyMzQ1Ng=="
}
```

或者不传token获取当前用户信息：
```json
{
  "token": ""
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

1. 如果token参数为空或不传，则返回当前登录用户信息
2. 如果传入token，则：
   - 对token进行Base64解码
   - 解析为query string格式的键值对
   - 提取user_name和password
   - 对password进行SHA256加密
   - 验证用户名和密码
   - 登录成功后保存session
   - 返回用户信息

## 注意事项

- 密码需要经过SHA256加密后存储和比对
- 登录成功后，会在session中保存`user_name`和`project_id`
- 角色信息中的memo字段为Unicode编码，前端需要解码显示

