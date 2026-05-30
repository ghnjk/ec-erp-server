# 获取登录用户信息

## 接口信息

- **接口路径**: `/erp_api/system/get_login_user_info`
- **请求方法**: POST
- **接口描述**: 获取当前已登录用户的详细信息

## 请求参数

无需请求参数

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

## 请求示例

```json
{}
```

## 响应示例

### 成功响应

```json
{
  "data": {
    "admin": 1,
    "groupName": "",
    "project_id": "malaysia",
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
  "result": 1001,
  "resultMsg": "not login.",
  "traceId": 1709991728857
}
```

## 业务逻辑说明

1. 从session中获取当前登录用户信息
2. 如果用户未登录，返回错误
3. 获取用户的项目ID
4. 过滤用户角色，只返回当前项目下的角色
5. 返回用户信息

## 注意事项

- 此接口依赖session，需要先登录
- 返回的角色列表会根据当前project_id进行过滤
- 可用于前端判断用户登录状态和权限

