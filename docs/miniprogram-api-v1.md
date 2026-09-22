# 校园小程序 API v1 对接文档

版本：v1.0-draft
日期：2026-08-25
状态：业务 API 已实现，等待小程序调用层与基础设施联调
Base Path：`/api/v1`

## 0. 本分支实现状态

实现分支：`miniprogram-api-v1`

已实现并纳入自动化测试：

- `/api/v1` 统一响应、HTTP 业务错误码、JWT、请求 ID、签名游标和创建幂等。
- 复用小程序现有 CSSANet 邮箱/JWT 登录，并提供微信身份安全绑定接口。
- 图片直传签名与上传完成确认（依赖部署环境提供 S3 兼容对象存储配置）。
- 个人中心、我的帖子/评论/点赞/评价。
- 帖子、评论、回复、软删除、内容可见性和计数一致性。
- 帖子/评论/课程评价的状态式点赞和互动消息。
- 课程、查重、课程评价、评分聚合和评价软删除。
- 文本审核失败关闭、待审核重试命令、计数重建和孤儿上传清理命令。
- 全新 PostgreSQL 数据库迁移及旧社区帖子/收藏数据迁移。

尚未开放或配置：

- 图片安全审核供应商调用。生产开启图片审核时，图片保持 `PENDING`，不会失败放行。
- 对象存储、微信 AppID/Secret、队列和正式域名必须通过部署环境注入，本分支不包含任何真实凭据。

## 1. 文档说明

本文档是校园小程序与 myCSSA Django 后端的正式对接契约，覆盖：

- 既有 CSSANet 登录与微信身份绑定
- 图片上传
- 个人中心
- 表白墙帖子、评论、回复
- 点赞与互动消息
- 课程和课程评价

小程序继续使用既有 CSSANet 邮箱/JWT 登录，不新建第二套用户体系。登录后通过一次 `wx.login` 将当前微信身份绑定到已登录 CSSANet 账号，仅用于内容安全审核。

小程序代码仓库：[cssa-uom/cssa-minprogram](https://github.com/cssa-uom/cssa-minprogram)。其 `miniprogram-api-v1` 分支已新增 `miniprogram/utils/apiV1.js`，统一封装本文件中的 `/api/v1` 调用，避免新页面继续直接写死域名和旧 `/api/community/` 路径。

基础设施约束：

- 后端部署在现有 CSSANet/DigitalOcean 基础设施中。
- 图片上传使用现有 S3 兼容对象存储/CDN，不绑定阿里云 OSS 专有字段。
- `/upload/token` 返回通用的 `host + method + fields + objectKey`，小程序按返回内容直传。
- 本地和生产环境使用相同 API 契约，只允许域名、凭据和存储桶不同。
- 开发、测试、生产凭据仅由服务端环境配置管理，任何接口不得返回数据库或长期对象存储密钥。

## 2. 通用约定

### 2.1 请求地址

不同环境使用不同域名：

| 环境 | Base URL |
|---|---|
| 开发 | `http://localhost:8000/api/v1` |
| 测试 | 待配置 |
| 生产 | 待配置 |

本文档中的路径均省略域名，例如 `GET /posts` 表示：

```text
GET {Base URL}/posts
```

### 2.2 Content-Type

除对象存储直传外，所有接口使用：

```http
Content-Type: application/json
Accept: application/json
```

### 2.3 鉴权

登录成功后，小程序保存 Access Token，并在需要鉴权的请求中携带：

```http
Authorization: Bearer <accessToken>
```

规则：

- 帖子、课程和评价的 GET 接口允许匿名浏览。
- 匿名浏览时 `isLiked=false`、`isMine=false`、`myReviewId=null`。
- 登录后浏览应携带 token，以获得当前用户相关状态。
- 发布、评论、回复、点赞、创建课程、评价、删除等写操作必须登录。
- 收到 `10002` 或 HTTP 401 时，客户端尝试刷新 token；刷新失败则重新登录。

### 2.4 ID 类型

所有 ID 均按 JSON 字符串传输，包括数据库中使用整数的 ID：

```json
{
  "postId": "5001",
  "userId": "550e8400-e29b-41d4-a716-446655440000"
}
```

客户端不得使用 `Number()` 强制转换 ID。

### 2.5 时间

所有时间字段使用 Unix 毫秒时间戳：

```json
{
  "createdAt": 1787644800000
}
```

客户端按本地时区格式化显示。

### 2.6 请求追踪

客户端可以发送：

```http
X-Request-Id: <UUID>
```

服务端响应头会返回相同或新生成的 `X-Request-Id`。联调报错时应同时提供 Request ID。

### 2.7 幂等键

发布帖子、评论、课程和评价时建议发送：

```http
Idempotency-Key: <UUID>
```

同一用户在有效期内使用相同 Key 重试时，服务端返回第一次操作结果，不重复创建数据。

## 3. 统一响应格式

### 3.1 成功响应

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

### 3.2 失败响应

```json
{
  "code": 10001,
  "message": "标题不能超过30个字符",
  "data": {
    "field": "title"
  }
}
```

### 3.3 HTTP 状态和业务错误码

| HTTP | code | 含义 | 客户端处理 |
|---:|---:|---|---|
| 400 | 10001 | 参数错误 | 展示字段提示 |
| 401 | 10002 | 未登录或 token 过期 | 刷新 token 或重新登录 |
| 403 | 10003 | 无权限 | 展示无权限提示 |
| 404 | 10004 | 内容不存在或已删除 | 返回上一页并刷新 |
| 409 | 10005 | 重复操作或重复数据 | 根据 `data` 跳转已有内容 |
| 422 | 10006 | 内容审核未通过 | 展示审核原因 |
| 429 | 10007 | 操作过于频繁 | 按 `retryAfter` 倒计时 |
| 500 | 20000 | 服务端错误 | 提示稍后重试并记录 Request ID |
| 503 | 20001 | 依赖服务暂不可用 | 稍后重试 |

字段校验错误示例：

```json
{
  "code": 10001,
  "message": "参数错误",
  "data": {
    "errors": {
      "title": ["标题不能超过30个字符"],
      "imageIds": ["单帖最多上传9张图片"]
    }
  }
}
```

## 4. 分页约定

请求参数：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---:|---:|---|
| `cursor` | string | 否 | - | 首页不传，下一页使用上次响应值 |
| `size` | integer | 否 | 20 | 最小 1，最大 50 |

分页响应统一放在 `data` 中：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "list": [],
    "nextCursor": "opaque-cursor-value",
    "hasMore": true
  }
}
```

客户端规则：

- 下拉刷新：清空列表，不传 `cursor`。
- 上拉加载：传入上一页的 `nextCursor`。
- `hasMore=false` 后停止加载。
- 客户端不得解析或修改 `nextCursor`。
- 切换搜索词、排序或筛选条件后必须清空旧 cursor。

## 5. 公共对象结构

### 5.1 UserSummary

非匿名：

```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "nickname": "小明",
  "avatar": "https://cdn.example.com/avatar.jpg",
  "isAnonymous": false
}
```

匿名：

```json
{
  "userId": null,
  "nickname": "匿名用户",
  "avatar": null,
  "isAnonymous": true
}
```

匿名内容不得通过其他返回字段泄露真实身份。

### 5.2 审核状态

| 值 | 含义 | 公共列表可见 |
|---|---|---:|
| `PENDING` | 审核中 | 否 |
| `APPROVED` | 审核通过 | 是 |
| `REJECTED` | 审核未通过 | 否 |

本人在“我的帖子/评论/评价”中可以看到全部状态。

### 5.3 消息类型

| type | 含义 |
|---|---|
| `LIKE_POST` | 赞了帖子 |
| `LIKE_COMMENT` | 赞了评论或回复 |
| `LIKE_REVIEW` | 赞了课程评价 |
| `COMMENT_POST` | 评论了帖子 |
| `REPLY_COMMENT` | 回复了评论 |
| `AUDIT_REJECTED` | 内容审核未通过 |

## 6. 接口总览

| 模块 | 方法 | 路径 | 鉴权 |
|---|---|---|---|
| 既有账号登录 | POST | `/api/token/` | 否 |
| 既有 Token 刷新 | POST | `/api/refresh/` | 否 |
| 微信身份绑定 | POST | `/auth/wechat-bind` | 是 |
| 上传 | GET | `/upload/token` | 是 |
| 上传 | POST | `/uploads/complete` | 是 |
| 个人 | GET | `/users/me` | 是 |
| 个人 | GET | `/users/me/posts` | 是 |
| 个人 | GET | `/users/me/comments` | 是 |
| 个人 | GET | `/users/me/likes/received` | 是 |
| 个人 | GET | `/users/me/likes/given` | 是 |
| 个人 | GET | `/users/me/reviews` | 是 |
| 消息 | GET | `/messages` | 是 |
| 消息 | GET | `/messages/unread-count` | 是 |
| 消息 | POST | `/messages/read` | 是 |
| 帖子 | GET | `/posts` | 可选 |
| 帖子 | POST | `/posts` | 是 |
| 帖子 | GET | `/posts/{postId}` | 可选 |
| 帖子 | DELETE | `/posts/{postId}` | 是 |
| 评论 | GET | `/posts/{postId}/comments` | 可选 |
| 评论 | POST | `/posts/{postId}/comments` | 是 |
| 评论 | GET | `/comments/{commentId}/replies` | 可选 |
| 评论 | DELETE | `/comments/{commentId}` | 是 |
| 点赞 | POST | `/likes/toggle` | 是 |
| 课程 | GET | `/courses` | 可选 |
| 课程 | POST | `/courses` | 是 |
| 课程 | GET | `/courses/{courseId}` | 可选 |
| 评价 | GET | `/courses/{courseId}/reviews` | 可选 |
| 评价 | POST | `/courses/{courseId}/reviews` | 是 |
| 评价 | PUT | `/reviews/{reviewId}` | 是 |
| 评价 | DELETE | `/reviews/{reviewId}` | 是 |

## 7. 登录与微信身份绑定

### 7.1 CSSANet 账号登录（既有接口）

```http
POST /api/token/
```

注意：该接口不在 `/api/v1` Base Path 下，小程序现有 `utils/user.js` 已调用此接口。

请求：

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

响应沿用现有 SimpleJWT 字段：

```json
{
  "refresh": "jwt-refresh-token",
  "access": "jwt-access-token"
}
```

Token 刷新继续调用：

```http
POST /api/refresh/
Content-Type: application/json

{"refresh": "jwt-refresh-token"}
```

### 7.2 绑定微信身份

CSSANet 登录成功后，小程序调用 `wx.login` 获取一次性 code，再调用：

```http
POST /auth/wechat-bind
Authorization: Bearer <token>
```

请求：

```json
{
  "code": "wx.login 返回的一次性 code"
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "wechatBound": true,
    "updatedAt": 1787644800000
  }
}
```

规则：

- `openid` 不返回给客户端，也不由业务接口接收。
- 后端使用 AppID/Secret 向微信换取 `openid`，并绑定到当前 JWT 对应的 CSSANet 账号。
- 同一微信身份不能绑定两个 CSSANet 账号，冲突返回 HTTP 409 / `10005`。
- code 无效或已使用时返回 HTTP 400 / `10001`。
- 微信接口或服务端配置不可用时返回 HTTP 503 / `20001`。
- `/users/me` 的 `wechatBound` 可用于决定是否需要重新绑定。

## 8. 图片上传

### 8.1 获取直传签名

```http
GET /upload/token?filename=photo.jpg&contentType=image/jpeg&size=123456
Authorization: Bearer <token>
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "method": "POST",
    "host": "https://storage.example.com",
    "objectKey": "community/user-id/2026/08/uuid.jpg",
    "fields": {
      "key": "community/user-id/2026/08/uuid.jpg",
      "policy": "...",
      "signature": "...",
      "accessId": "..."
    },
    "expire": 1787645400000
  }
}
```

小程序使用 `wx.uploadFile` 将文件及 `fields` 直传到 `host`。当前实现目标是兼容 CSSANet 使用的 DigitalOcean S3/CDN；客户端不得依赖某一家云厂商的固定字段名，只应透传服务端返回的 `fields`。

限制：

- 支持 JPEG、PNG、WebP；最终格式以服务端配置为准。
- 单文件最大 10 MB。
- 签名只允许写入当前用户目录。
- 签名有效期不超过 10 分钟。

### 8.2 确认上传完成

```http
POST /uploads/complete
Authorization: Bearer <token>
```

请求：

```json
{
  "objectKey": "community/user-id/2026/08/uuid.jpg",
  "contentType": "image/jpeg",
  "size": 123456
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "imageId": "0ad75fec-3db0-43db-91e6-ad4a29b839be",
    "url": "https://cdn.example.com/community/user-id/2026/08/uuid.jpg",
    "thumbnailUrl": "https://cdn.example.com/community/user-id/2026/08/uuid-thumb.jpg",
    "auditStatus": "PENDING"
  }
}
```

发布帖子时传 `imageId`，不要传 URL。

## 9. 个人中心

### 9.1 获取个人中心头部

```http
GET /users/me
Authorization: Bearer <token>
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "nickname": "小明",
    "avatar": "https://cdn.example.com/avatar.jpg",
    "college": "Faculty of Engineering and Information Technology",
    "postCount": 12,
    "commentCount": 31,
    "likeReceivedCount": 86,
    "unreadCount": 5
  }
}
```

### 9.2 我的帖子

```http
GET /users/me/posts?auditStatus=all&cursor=...&size=20
```

`auditStatus`：`all`、`PENDING`、`APPROVED`、`REJECTED`，默认 `all`。

列表项：

```json
{
  "postId": "5001",
  "title": "标题",
  "summary": "内容摘要",
  "images": [
    {
      "imageId": "0ad75fec-3db0-43db-91e6-ad4a29b839be",
      "thumbnailUrl": "https://cdn.example.com/thumb.jpg"
    }
  ],
  "likeCount": 12,
  "commentCount": 3,
  "isAnonymous": true,
  "auditStatus": "APPROVED",
  "auditMessage": null,
  "createdAt": 1787644800000
}
```

### 9.3 我的评论

```http
GET /users/me/comments?cursor=...&size=20
```

列表项：

```json
{
  "commentId": "7001",
  "content": "评论内容",
  "postId": "5001",
  "postTitle": "帖子标题",
  "likeCount": 5,
  "auditStatus": "APPROVED",
  "createdAt": 1787644800000
}
```

### 9.4 收到的赞

```http
GET /users/me/likes/received?type=all&cursor=...&size=20
```

`type`：`all`、`post`、`comment`、`review`。

列表项与消息结构一致，但只包含 `LIKE_*` 类型。

### 9.5 我点赞的内容

```http
GET /users/me/likes/given?type=all&cursor=...&size=20
```

列表项：

```json
{
  "likeId": "91001",
  "targetType": 1,
  "targetId": "5001",
  "postId": "5001",
  "title": "帖子标题",
  "snippet": "内容摘要",
  "cover": "https://cdn.example.com/thumb.jpg",
  "createdAt": 1787644800000
}
```

### 9.6 我的课程评价

```http
GET /users/me/reviews?cursor=...&size=20
```

列表项：

```json
{
  "reviewId": "8001",
  "courseId": "3001",
  "courseName": "数据结构与算法",
  "teacher": "张老师",
  "rating": 5,
  "content": "评价内容",
  "isAnonymous": false,
  "auditStatus": "APPROVED",
  "createdAt": 1787644800000,
  "updatedAt": 1787644800000
}
```

## 10. 消息

### 10.1 消息列表

```http
GET /messages?type=all&read=all&cursor=...&size=20
```

参数：

| 参数 | 可选值 |
|---|---|
| `type` | `all`、`like`、`comment`、`audit` |
| `read` | `all`、`true`、`false` |

列表项：

```json
{
  "messageId": "90001",
  "type": "LIKE_POST",
  "typeText": "赞了你的帖子",
  "sender": {
    "userId": "550e8400-e29b-41d4-a716-446655440001",
    "nickname": "小红",
    "avatar": "https://cdn.example.com/avatar2.jpg",
    "isAnonymous": false
  },
  "postId": "5001",
  "commentId": null,
  "reviewId": null,
  "courseId": null,
  "snippet": "被赞内容摘要",
  "cover": "https://cdn.example.com/thumb.jpg",
  "isRead": false,
  "createdAt": 1787644800000
}
```

如果发送者对应的是匿名内容，互动接收者仍不得通过消息看到其真实身份。

### 10.2 未读数

```http
GET /messages/unread-count
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "total": 5,
    "like": 3,
    "comment": 2,
    "audit": 0
  }
}
```

### 10.3 标记已读

```http
POST /messages/read
```

请求：

```json
{
  "type": "all",
  "maxId": "90001"
}
```

`type`：`all`、`like`、`comment`、`audit`。

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "updatedCount": 5
  }
}
```

## 11. 帖子

### 11.1 帖子列表

```http
GET /posts?section=1&sort=latest&cursor=...&size=20
Authorization: Bearer <token>  # 可选
```

参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `section` | integer | 否 | 当前固定为 1，表示表白墙 |
| `sort` | string | 否 | `latest` 或 `hot`，默认 `latest` |
| `cursor` | string | 否 | 分页游标 |
| `size` | integer | 否 | 默认 20，最大 50 |

列表项：

```json
{
  "postId": "5001",
  "author": {
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "nickname": "小明",
    "avatar": "https://cdn.example.com/avatar.jpg",
    "isAnonymous": false
  },
  "title": "标题",
  "summary": "正文前80字",
  "images": [
    {
      "imageId": "0ad75fec-3db0-43db-91e6-ad4a29b839be",
      "url": "https://cdn.example.com/image.jpg",
      "thumbnailUrl": "https://cdn.example.com/thumb.jpg"
    }
  ],
  "likeCount": 12,
  "commentCount": 3,
  "isLiked": false,
  "isMine": false,
  "createdAt": 1787644800000
}
```

只返回审核通过且未软删除的帖子。

### 11.2 发布帖子

```http
POST /posts
Authorization: Bearer <token>
Idempotency-Key: <UUID>
```

请求：

```json
{
  "section": 1,
  "title": "标题",
  "content": "正文",
  "imageIds": [
    "0ad75fec-3db0-43db-91e6-ad4a29b839be"
  ],
  "isAnonymous": false
}
```

校验：

- 标题 1–30 字。
- 正文 1–2000 字。
- 图片最多 9 张。
- 图片必须属于当前用户且上传有效。
- 距离当前用户上次发帖至少 60 秒。

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "postId": "5001",
    "auditStatus": "PENDING",
    "visible": false,
    "createdAt": 1787644800000
  }
}
```

限流响应：

```json
{
  "code": 10007,
  "message": "发布过于频繁，请稍后再试",
  "data": {
    "retryAfter": 37
  }
}
```

### 11.3 帖子详情

```http
GET /posts/{postId}
Authorization: Bearer <token>  # 可选
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "postId": "5001",
    "author": {
      "userId": null,
      "nickname": "匿名用户",
      "avatar": null,
      "isAnonymous": true
    },
    "title": "标题",
    "content": "完整正文",
    "images": [],
    "likeCount": 12,
    "commentCount": 3,
    "isLiked": false,
    "isMine": true,
    "createdAt": 1787644800000
  }
}
```

本人访问自己的待审核内容时，响应额外包含：

```json
{
  "auditStatus": "PENDING",
  "auditMessage": null
}
```

### 11.4 删除帖子

```http
DELETE /posts/{postId}
Authorization: Bearer <token>
```

仅作者本人可删除，执行软删除。

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": null
}
```

## 12. 评论和回复

### 12.1 评论列表

```http
GET /posts/{postId}/comments?sort=latest&cursor=...&size=20
Authorization: Bearer <token>  # 可选
```

`sort`：`latest` 或 `hot`。

列表项：

```json
{
  "commentId": "7001",
  "user": {
    "userId": "550e8400-e29b-41d4-a716-446655440001",
    "nickname": "小红",
    "avatar": "https://cdn.example.com/avatar2.jpg",
    "isAnonymous": false
  },
  "isAuthor": false,
  "content": "评论内容",
  "likeCount": 5,
  "isLiked": false,
  "isMine": false,
  "replyCount": 4,
  "createdAt": 1787644800000,
  "replies": [
    {
      "commentId": "7002",
      "user": {
        "userId": "550e8400-e29b-41d4-a716-446655440000",
        "nickname": "小明",
        "avatar": "https://cdn.example.com/avatar.jpg",
        "isAnonymous": false
      },
      "isAuthor": true,
      "replyToUser": {
        "userId": "550e8400-e29b-41d4-a716-446655440001",
        "nickname": "小红"
      },
      "content": "回复内容",
      "likeCount": 0,
      "isLiked": false,
      "isMine": true,
      "createdAt": 1787644900000
    }
  ]
}
```

每条一级评论默认只带时间最早的前 2 条有效回复；其余回复通过展开接口获取。

### 12.2 发表评论或回复

```http
POST /posts/{postId}/comments
Authorization: Bearer <token>
Idempotency-Key: <UUID>
```

评论帖子：

```json
{
  "content": "评论内容",
  "rootId": null,
  "replyToCommentId": null
}
```

回复一级评论：

```json
{
  "content": "回复内容",
  "rootId": "7001",
  "replyToCommentId": "7001"
}
```

回复楼中楼：

```json
{
  "content": "回复内容",
  "rootId": "7001",
  "replyToCommentId": "7002"
}
```

服务端校验 `rootId`、`replyToCommentId` 均属于 URL 中的帖子。

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "commentId": "7003",
    "auditStatus": "PENDING",
    "visible": false,
    "createdAt": 1787645000000
  }
}
```

### 12.3 展开全部回复

```http
GET /comments/{commentId}/replies?cursor=...&size=20
```

返回标准分页结构，列表项与评论列表中的 `replies` 元素一致。

### 12.4 删除评论

```http
DELETE /comments/{commentId}
Authorization: Bearer <token>
```

允许删除者：

- 评论或回复作者本人。
- 该评论所属帖子的作者。

删除为软删除。删除一级评论时，回复保留但前台整体不再展示。

## 13. 点赞

### 13.1 点赞或取消点赞

```http
POST /likes/toggle
Authorization: Bearer <token>
```

请求：

```json
{
  "targetType": 1,
  "targetId": "5001",
  "liked": true
}
```

`targetType`：

| 值 | 目标 |
|---:|---|
| 1 | 帖子 |
| 2 | 评论或回复 |
| 3 | 课程评价 |

`liked` 表示客户端期望的最终状态：

- `true`：确保已点赞。
- `false`：确保已取消。
- 为兼容旧客户端可以省略；省略时服务端执行反转，但新客户端必须传递。

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "liked": true,
    "likeCount": 13
  }
}
```

规则：

- 给自己的内容点赞可以计数，但不生成互动消息。
- 重复提交相同 `liked` 状态不重复计数。
- 已删除、待审核或审核拒绝的目标不能点赞。

## 14. 课程

### 14.1 课程列表和搜索

```http
GET /courses?keyword=数据结构&sort=hot&cursor=...&size=20
```

参数：

| 参数 | 可选值/说明 |
|---|---|
| `keyword` | 同时搜索课程名、课程代码和老师 |
| `sort` | `hot`、`rating`、`latest`，默认 `hot` |
| `cursor` | 分页游标 |
| `size` | 默认 20，最大 50 |

列表项：

```json
{
  "courseId": "3001",
  "name": "数据结构与算法",
  "code": "COMP20003",
  "teacher": "张老师",
  "college": "Faculty of Engineering and Information Technology",
  "credit": "12.5",
  "ratingAvg": "4.35",
  "reviewCount": 128
}
```

金额和小数类字段统一用字符串输出，避免浮点误差。

### 14.2 创建课程

```http
POST /courses
Authorization: Bearer <token>
Idempotency-Key: <UUID>
```

请求：

```json
{
  "name": "分布式系统",
  "code": "COMP90015",
  "teacher": "李老师",
  "college": "Faculty of Engineering and Information Technology",
  "credit": "12.5"
}
```

成功响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "courseId": "3002"
  }
}
```

重复课程响应：

```json
{
  "code": 10005,
  "message": "课程已存在",
  "data": {
    "courseId": "3001",
    "name": "分布式系统",
    "teacher": "李老师"
  }
}
```

前端收到 `10005` 后应提示并跳转到已有课程详情。

### 14.3 课程详情

```http
GET /courses/{courseId}
Authorization: Bearer <token>  # 可选
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "courseId": "3001",
    "name": "数据结构与算法",
    "code": "COMP20003",
    "teacher": "张老师",
    "college": "Faculty of Engineering and Information Technology",
    "credit": "12.5",
    "ratingAvg": "4.35",
    "reviewCount": 128,
    "ratingDistribution": {
      "1": 2,
      "2": 4,
      "3": 19,
      "4": 48,
      "5": 55
    },
    "myReviewId": "8001"
  }
}
```

未登录或未评价时 `myReviewId=null`。

## 15. 课程评价

### 15.1 评价列表

```http
GET /courses/{courseId}/reviews?sort=latest&cursor=...&size=20
Authorization: Bearer <token>  # 可选
```

`sort`：`latest` 或 `hot`。

列表项：

```json
{
  "reviewId": "8001",
  "user": {
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "nickname": "小明",
    "avatar": "https://cdn.example.com/avatar.jpg",
    "isAnonymous": false
  },
  "rating": 5,
  "content": "评价内容",
  "likeCount": 9,
  "isLiked": false,
  "isMine": true,
  "createdAt": 1787644800000,
  "updatedAt": 1787644800000
}
```

### 15.2 发表评价

```http
POST /courses/{courseId}/reviews
Authorization: Bearer <token>
Idempotency-Key: <UUID>
```

请求：

```json
{
  "rating": 5,
  "content": "评价内容",
  "isAnonymous": false
}
```

校验：

- `rating` 必须是 1、2、3、4、5。
- 评价正文 1–500 字；最终限制可在产品确认后调整。
- 同一用户对同一课程只能有一条有效评价。

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "reviewId": "8001",
    "auditStatus": "PENDING",
    "visible": false,
    "createdAt": 1787644800000
  }
}
```

重复评价：

```json
{
  "code": 10005,
  "message": "你已经评价过该课程",
  "data": {
    "reviewId": "8001"
  }
}
```

### 15.3 修改评价

```http
PUT /reviews/{reviewId}
Authorization: Bearer <token>
```

请求：

```json
{
  "rating": 4,
  "content": "修改后的评价",
  "isAnonymous": true
}
```

修改后重新进入 `PENDING`，公共列表暂时隐藏；课程均分只统计审核通过的评价。

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "reviewId": "8001",
    "auditStatus": "PENDING",
    "updatedAt": 1787645800000
  }
}
```

### 15.4 删除评价

```http
DELETE /reviews/{reviewId}
Authorization: Bearer <token>
```

仅本人可删除，执行软删除，并同步更新课程均分、评价数和评分分布。

## 16. 客户端关键流程

### 16.1 启动和登录

1. 继续使用现有 `POST /api/token/` 完成 CSSANet 邮箱登录。
2. 保存 `access` 和 `refresh`。
3. 调用 `wx.login` 获取临时 code。
4. 携带 Access Token 调用 `POST /auth/wechat-bind`。
5. 后续请求通过统一 request 封装添加 Authorization。
6. 401 时只允许一次 `/api/refresh/` 刷新和原请求重放，避免刷新死循环。

### 16.2 发布带图片的帖子

1. 对每张图片调用 `GET /upload/token`。
2. 使用 `wx.uploadFile` 直传对象存储。
3. 每张图片调用 `POST /uploads/complete`，得到 `imageId`。
4. 调用 `POST /posts`，传递 `imageIds`。
5. 响应为 `PENDING` 时展示“审核中”。
6. 通过“我的帖子”刷新审核结果。

### 16.3 评论和回复

1. 一级评论传 `rootId=null`、`replyToCommentId=null`。
2. 回复一级评论时两个字段都是一级评论 ID。
3. 回复楼中楼时 `rootId` 是一级评论 ID，`replyToCommentId` 是目标回复 ID。
4. 发布成功后先显示审核中状态，不直接插入公共评论列表。

### 16.4 点赞

1. 客户端立即更新本地 UI。
2. 请求必须传期望状态 `liked`。
3. 服务端响应后以返回的 `liked` 和 `likeCount` 覆盖本地状态。
4. 请求失败时回滚 UI。

### 16.5 消息红点

1. 进入个人中心时调用 `/messages/unread-count`。
2. 进入消息列表后分页加载 `/messages`。
3. 页面已展示到某条消息后，调用 `/messages/read` 并传当前最大消息 ID。
4. 使用接口返回的未读数更新红点，不在客户端自行推算。

### 16.6 课程评价

1. 进入课程页调用课程详情和评价列表。
2. `myReviewId=null` 显示新增按钮，否则显示编辑入口。
3. 搜索无结果后才展示创建课程入口。
4. 创建课程返回 `10005` 时跳转到已有课程。
5. 新增或修改评价后展示审核中状态。

## 17. 限制和默认值

| 项目 | 限制 |
|---|---|
| 帖子标题 | 1–30 字 |
| 帖子正文 | 1–2000 字 |
| 评论/回复 | 1–500 字 |
| 课程评价 | 1–500 字，待产品最终确认 |
| 帖子图片 | 最多 9 张 |
| 单张图片 | 最大 10 MB |
| 发帖频率 | 同一用户至少间隔 60 秒 |
| 默认分页 | 20 条 |
| 最大分页 | 50 条 |
| 上传签名 | 最长有效 10 分钟 |

## 18. 联调验收清单

- [ ] 登录后 token 能访问写接口。
- [ ] CSSANet 登录后能完成微信身份绑定，响应中不出现 `openid`。
- [ ] 未登录可浏览帖子和课程。
- [ ] token 过期能刷新或重新登录。
- [ ] 所有 ID 均作为字符串处理。
- [ ] 所有时间均按毫秒时间戳处理。
- [ ] 下拉刷新不携带旧 cursor。
- [ ] 上拉加载使用服务端 `nextCursor`。
- [ ] 匿名帖子和评价不泄露真实身份。
- [ ] 上传完成后使用 `imageId` 发布帖子。
- [ ] 第 10 张图片在客户端和服务端均被拒绝。
- [ ] 待审核内容不出现在公共列表。
- [ ] 点赞重试不会反转成错误状态。
- [ ] 评论回复跳转到正确帖子和楼层。
- [ ] 收到互动后未读红点增加。
- [ ] 批量标记已读后红点正确减少。
- [ ] 重复创建课程能跳转已有课程。
- [ ] 同一课程不能重复评价。
- [ ] 修改、删除评价后课程均分正确。
- [ ] 404、409、422、429 均有明确 UI 提示。
- [ ] 联调问题均能提供 `X-Request-Id`。

## 19. 待双方冻结的字段

以下项目在正式编码前必须由后端和小程序负责人共同确认：

1. 测试、预发布和生产 API 域名。
2. DigitalOcean S3/CDN 的测试与生产域名，以及 `upload/token` 最终字段。
3. 用户学院字段的枚举值。
4. 课程热门排序算法。
5. 课程评价最大字数。
6. 审核拒绝原因是否直接向用户展示。
7. 匿名用户的统一默认头像。
8. 是否需要消息实时推送；v1 默认采用进入页面主动拉取。
9. 旧 `/api/community/` 的下线时间。
