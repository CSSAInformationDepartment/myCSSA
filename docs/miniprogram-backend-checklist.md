# 校园小程序后端实施清单

版本：v1.0
日期：2026-08-25
状态：核心业务 API 已实现，等待小程序调用层及生产基础设施联调

## 0. 当前交付快照

- [x] 已创建 `miniprogram-api-v1` 分支。
- [x] 已新增 `MiniProgramAPI`、`/api/v1/` 路由、模型和迁移。
- [x] 已实现帖子、评论、回复、点赞、消息、个人中心、课程和评价接口。
- [x] 已实现统一响应、请求 ID、JWT、游标分页、幂等和限流边界。
- [x] 已实现对象存储直传签名和上传完成校验；真实环境配置仍待注入。
- [x] 已实现文本审核失败关闭和待审核重试命令；图片审核供应商调用仍待接入。
- [x] 已实现计数重建和孤儿上传清理命令。
- [x] 已完成全新 PostgreSQL 迁移验证和 API 自动化测试。
- [x] 已确认复用现有 CSSANet 邮箱/JWT 登录，不新建第二套登录体系。
- [x] 已实现 `/api/v1/auth/wechat-bind`，安全绑定内容审核所需微信身份。
- [x] 已在 `cssa-minprogram/miniprogram-api-v1` 增加统一 `/api/v1` 请求封装。
- [ ] 新页面完成后按需调用 `utils/apiV1.js` 并进行真机联调。
- [ ] 接入图片安全审核、生产对象存储、队列、域名和监控。
- [ ] 轮换启动资料中出现过的全部凭据后再进行远程环境联调。

## 1. 目标与范围

本清单用于完成校园小程序 v1 后端建设，范围包括：

- 个人中心
- 表白墙帖子、评论、回复
- 帖子、评论和课程评价点赞
- 互动消息与未读数
- 课程、课程评价
- 图片直传
- 微信内容安全审核
- `/api/v1` 统一接口规范
- 自动测试、联调、发布与监控

实施原则：

- 保留现有 `/api/community/`，并行新增 `/api/v1/`，避免破坏旧客户端。
- 优先复用 `CommunityAPI` 的帖子、评论、图片、通知和审核能力。
- 课程评价单独建立领域模型。
- 新接口必须有自动测试和 OpenAPI 文档，不接受只完成代码、没有契约和测试的交付。

## 1.1 启动资料确认的基础设施基线

根据现有启动资料和当前仓库配置，本项目暂按以下基础设施开展：

- 本地开发使用 Python 3.8 环境，可不使用 Docker。
- `CSSANet.settings.dev` 通过被 Git 忽略的 `local.py` 加载开发配置。
- 开发数据来自共享 CSSADev PostgreSQL；其中可能包含未完全匿名化的用户数据。
- 静态文件和媒体文件使用 DigitalOcean 上的 S3 兼容对象存储/CDN。
- 生产镜像由 `RYYYY.MM.DD.NUMBER` 格式的 tag 触发 GitHub Actions 构建。
- 生产服务历史上通过 DigitalOcean Kubernetes 和外部维护的部署 YAML 发布。
- 本地 API 文档入口为 `/swagger/`。

安全边界：

- 启动资料中出现过明文数据库、对象存储和生产接入凭据，全部按“可能已泄露”处理。
- 新文档、代码、聊天记录和截图中不得再次复制这些凭据。
- 在凭据轮换完成前，不使用资料中的旧凭据连接任何远程服务。
- 共享开发数据只允许用于获批的项目开发，不下载、传播或用于与任务无关的分析。
- 普通开发不得通过临时开放生产数据库公网访问的方式操作数据。

## 2. P0：开发前必须确认

- [x] 确认小程序代码仓库为 `cssa-uom/cssa-minprogram`。
- [x] 确认继续使用 `/api/token/` 和 `/api/refresh/` 签发、刷新 JWT。
- [x] 使用 `/api/v1/auth/wechat-bind` 将 `openid` 服务端绑定到当前 `UserProfile`。
- [ ] 确认未登录浏览时是否完全不下发 JWT。
- [ ] 确认继续使用现有 DigitalOcean S3 兼容对象存储/CDN，并获取已轮换的新凭据。
- [ ] 轮换启动资料中出现的开发数据库、生产数据库、对象存储和 DigitalOcean 凭据。
- [ ] 检查相关凭据是否在其他文档、聊天记录、日志或历史提交中重复出现。
- [ ] 确认 CSSADev 数据访问审批、最小权限账户和允许的开发人员名单。
- [ ] 确认本地开发通过 VPN、SSH Tunnel 或 IP Allowlist 访问共享数据，不开放生产数据库公网入口。
- [ ] 确认 `cssanet-service.yaml` 的当前维护位置、负责人和变更审计方式。
- [ ] 确认 GitHub Actions 当前镜像仓库地址仍可用，并完成一次非生产构建验证。
- [ ] 确认匿名内容对普通用户隐藏身份、对管理员保留审计身份。
- [ ] 确认“我的点赞”在 UI 中区分“收到的赞”和“我点赞的内容”。
- [ ] 确认课程学院使用固定枚举还是自由输入。
- [ ] 确认课程热门排序公式。
- [ ] 确认审核失败时是允许编辑重提，还是只能删除后重新发布。
- [ ] 确认小程序正式、测试和开发环境的 API 域名。
- [ ] 冻结 `/api/v1` 字段、错误码和分页规范。

## 3. P0：现有工程基线修复

- [ ] 保留 `local.py` 本地覆盖机制，但改为只读取环境变量，不保存明文凭据。
- [ ] 增加不含秘密的 `local.example.py` 或统一 `.env.example`。
- [ ] 为无共享数据库权限的开发者提供本地 PostgreSQL 配置和脱敏 fixture。
- [ ] 补齐开发环境的 `STATIC_URL`、`STATIC_ROOT`、`MEDIA_URL`、`MEDIA_ROOT`。
- [ ] 把数据库密码、Django Secret Key、存储密钥移入环境变量。
- [ ] 修复 `REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES` 单元素元组配置。
- [ ] 缩短 JWT Access Token 有效期，定义 Refresh Token 轮换策略。
- [ ] 移除容器启动时自动执行 `makemigrations` 的行为。
- [ ] 确认 Docker Compose 可以从全新数据卷一键启动。
- [ ] 增加 `.env.example`，不包含真实凭据。
- [ ] 建立 pytest 或 Django TestCase 测试运行命令。
- [ ] CI 增加 `manage.py check`、迁移检查和自动测试。

完成标准：

- [ ] 新开发者根据 README 可以启动项目。
- [ ] CI 在全新数据库上能够执行迁移并通过测试。
- [ ] 仓库中没有生产密钥或可复用密码。

## 4. P0：`/api/v1` 公共基础层

- [ ] 新建 `MiniProgramAPI` Django app。
- [ ] 注册 `/api/v1/` 根路由。
- [ ] 实现统一成功响应 `{code, message, data}`。
- [ ] 实现统一异常处理器和业务错误码映射。
- [ ] 保留正确 HTTP 状态码，不把所有错误返回为 HTTP 200。
- [ ] 实现毫秒时间戳序列化。
- [ ] 所有 ID 在 JSON 中按字符串输出。
- [ ] 实现不透明游标分页 `cursor + size`。
- [ ] `size` 默认 20，最大 50。
- [ ] 实现可选 JWT 认证：公共 GET 可匿名访问，携带 token 时返回 `isLiked`、`isMine`。
- [ ] 写操作统一要求 JWT。
- [ ] 支持 `X-Request-Id`，响应中回传请求 ID。
- [ ] POST 创建接口支持 `Idempotency-Key`。
- [ ] 为接口增加 Swagger/OpenAPI Schema。
- [ ] 新增 `/api/v1/health` 健康检查。

## 5. P0：数据库模型和迁移

### 5.1 用户信息

- [ ] 确认复用 `CommunityAPI.UserInformation` 或建立 `MiniProgramProfile`。
- [ ] 补充昵称、头像、学院字段。
- [ ] 建立用户与微信身份的服务端关联。
- [ ] 为昵称、头像缺失定义默认值。

### 5.2 帖子和评论

- [ ] 在现有 `Post` 增加 `section`。
- [ ] 增加 `is_anonymous`。
- [ ] 增加 `audit_status`：`PENDING/APPROVED/REJECTED`。
- [ ] 增加 `like_count`、`comment_count` 缓存字段。
- [ ] 增加 `deleted_at`，保留现有软删除兼容逻辑。
- [ ] 标题业务限制改为最多 30 字。
- [ ] 正文业务限制改为 1–2000 字。
- [ ] 评论业务限制改为 1–500 字。
- [ ] 单帖图片上限由 3 张调整为 9 张。
- [ ] 为公开列表常用条件建立组合索引。
- [ ] 编写旧数据默认值和数据迁移。

### 5.3 点赞

- [ ] 新建 `PostLike(user, post)` 唯一约束。
- [ ] 新建 `CourseReviewLike(user, review)` 唯一约束。
- [ ] 确认现有 `FavouritePost` 是否迁移为 `PostLike`。
- [ ] 编写收藏到点赞的数据迁移和回滚方案。
- [ ] 使用事务和 `F()` 表达式更新点赞计数。

### 5.4 互动消息

- [ ] 扩展现有 `Notification`，增加标准消息类型。
- [ ] 支持 `LIKE_POST`。
- [ ] 支持 `LIKE_COMMENT`。
- [ ] 支持 `LIKE_REVIEW`。
- [ ] 支持 `COMMENT_POST`。
- [ ] 支持 `REPLY_COMMENT`。
- [ ] 支持 `AUDIT_REJECTED`。
- [ ] 增加 `root_post_id`，便于客户端统一跳转。
- [ ] 增加摘要、封面快照，避免目标删除后消息完全不可读。
- [ ] 为 `recipient + is_read + id` 建立索引。

### 5.5 课程评价

- [ ] 新建 `Course`。
- [ ] 新建 `CourseReview`。
- [ ] 增加课程名、教师标准化字段。
- [ ] 建立课程名和教师查重键。
- [ ] 增加 `rating_sum`、`review_count`。
- [ ] 评价增加 `is_anonymous`、`audit_status`、`like_count`。
- [ ] 同一用户对同一课程只保留一条评价。
- [ ] 删除后的评价允许恢复并重新审核。
- [ ] 使用事务保证修改、删除评价后的均分一致。
- [ ] 提供评价计数和均分重建管理命令。

## 6. P0：图片上传

- [ ] 实现 `GET /api/v1/upload/token`。
- [ ] 上传签名有效期不超过 10 分钟。
- [ ] 对象路径限制在当前用户目录。
- [ ] 限制 MIME 类型为允许的图片格式。
- [ ] 限制单文件大小，建议不超过 10 MB。
- [ ] 实现 `POST /api/v1/uploads/complete`。
- [ ] 上传完成时校验对象存在、大小、类型和归属。
- [ ] 创建 `PostImage` 并返回 `imageId`。
- [ ] 帖子接口只接受 `imageId`，不接受任意外部 URL。
- [ ] 清理上传后长期未绑定内容的孤儿图片。
- [ ] 为图片生成列表缩略图。

## 7. P0：内容安全审核

- [ ] 从服务端登录身份取得 `openid`，禁止客户端提交或覆盖 `openid`。
- [ ] 重构现有微信文本审核封装，设置连接和读取超时。
- [ ] 新内容默认保存为 `PENDING`。
- [ ] `PENDING` 内容不进入公共列表。
- [ ] 文本审核通过后更新为 `APPROVED`。
- [ ] 审核拒绝后更新为 `REJECTED` 并生成消息。
- [ ] 微信接口故障时保持 `PENDING`，禁止失败放行。
- [ ] 接入图片安全审核。
- [ ] 启用 Celery Worker 和 Redis 队列处理重试及异步图片审核。
- [ ] 实现带退避的有限次数重试。
- [ ] 记录审核请求 ID、结果、时间和失败原因。
- [ ] 提供管理员重新审核操作。

## 8. P0：接口开发清单

### 8.1 登录和上传

- [x] 复用 `POST /api/token/` 和 `POST /api/refresh/`：现有 CSSANet 登录。
- [x] `POST /api/v1/auth/wechat-bind`：绑定当前微信身份用于内容审核。
- [ ] `GET /api/v1/upload/token`：获取图片直传签名。
- [ ] `POST /api/v1/uploads/complete`：确认上传并获得 `imageId`。

### 8.2 个人中心

- [ ] `GET /api/v1/users/me`
- [ ] `GET /api/v1/users/me/posts`
- [ ] `GET /api/v1/users/me/comments`
- [ ] `GET /api/v1/users/me/likes/received`
- [ ] `GET /api/v1/users/me/likes/given`
- [ ] `GET /api/v1/users/me/reviews`

### 8.3 消息

- [ ] `GET /api/v1/messages`
- [ ] `GET /api/v1/messages/unread-count`
- [ ] `POST /api/v1/messages/read`

### 8.4 帖子

- [ ] `GET /api/v1/posts`
- [ ] `POST /api/v1/posts`
- [ ] `GET /api/v1/posts/{postId}`
- [ ] `DELETE /api/v1/posts/{postId}`

### 8.5 评论和回复

- [ ] `GET /api/v1/posts/{postId}/comments`
- [ ] `POST /api/v1/posts/{postId}/comments`
- [ ] `GET /api/v1/comments/{commentId}/replies`
- [ ] `DELETE /api/v1/comments/{commentId}`

### 8.6 点赞

- [ ] `POST /api/v1/likes/toggle`

### 8.7 课程

- [ ] `GET /api/v1/courses`
- [ ] `POST /api/v1/courses`
- [ ] `GET /api/v1/courses/{courseId}`

### 8.8 课程评价

- [ ] `GET /api/v1/courses/{courseId}/reviews`
- [ ] `POST /api/v1/courses/{courseId}/reviews`
- [ ] `PUT /api/v1/reviews/{reviewId}`
- [ ] `DELETE /api/v1/reviews/{reviewId}`

## 9. P0：权限与业务规则

- [ ] 未登录用户只能调用公开 GET 接口。
- [ ] 发布、评论、回复、点赞、评价均要求登录。
- [ ] 用户只能删除自己的帖子。
- [ ] 评论作者可删除自己的评论。
- [ ] 帖主可删除自己帖子下的评论。
- [ ] 用户只能修改或删除自己的课程评价。
- [ ] 匿名内容在公共响应中不得返回真实用户 ID、昵称或头像。
- [ ] 管理员审核日志保留真实发布者。
- [ ] 同一用户发帖间隔至少 60 秒。
- [ ] 点赞操作在并发和网络重试下保持一致。
- [ ] 删除均为软删除。
- [ ] 软删除目标不能通过详情接口绕过访问。

## 10. P1：查询和性能

- [ ] 列表查询使用 `select_related` / `prefetch_related`。
- [ ] 消除帖子列表、评论列表和评价列表的 N+1 查询。
- [ ] 为最新排序使用 `created_at + id` 游标。
- [ ] 为热门排序使用 `hot_score + created_at + id` 游标。
- [ ] 明确热门分数计算规则。
- [ ] 课程搜索第一版支持名称和老师模糊搜索。
- [ ] 数据量增长后评估 PostgreSQL `pg_trgm`。
- [ ] Redis 只缓存可重建数据。
- [ ] 缓存点赞数、评论数、未读数时设计失效策略。
- [ ] 提供计数对账和修复命令。

## 11. P0：自动测试

### 11.1 通用层

- [ ] 成功和失败响应格式测试。
- [ ] HTTP 状态和业务错误码映射测试。
- [ ] 游标分页无重复、无遗漏测试。
- [ ] JWT 缺失、过期和非法 token 测试。
- [ ] Idempotency-Key 重放测试。

### 11.2 帖子与评论

- [ ] 未登录浏览测试。
- [ ] 发布、详情、删除权限测试。
- [ ] 匿名信息不泄露测试。
- [ ] 字数和 9 张图片限制测试。
- [ ] 60 秒限流测试。
- [ ] 两级评论结构测试。
- [ ] 帖主删除评论权限测试。
- [ ] 软删除过滤测试。

### 11.3 点赞与消息

- [ ] 点赞、取消、重复请求测试。
- [ ] 并发点赞唯一约束测试。
- [ ] 点赞计数一致性测试。
- [ ] 消息创建和自赞不通知测试。
- [ ] 未读数和批量已读竞态测试。

### 11.4 课程评价

- [ ] 课程查重测试。
- [ ] 同一用户重复评价测试。
- [ ] 评价修改和删除权限测试。
- [ ] 均分和评分分布测试。
- [ ] 并发评价计数测试。
- [ ] 匿名评价测试。

### 11.5 审核与上传

- [ ] 审核通过、拒绝、超时和重试测试。
- [ ] 审核异常时内容不可见测试。
- [ ] 非本人上传对象绑定测试。
- [ ] 非图片和超大文件测试。
- [ ] 上传签名过期测试。

## 12. P0：小程序联调

- [ ] 提供测试环境 Base URL。
- [ ] 提供测试用户和 JWT 获取方式。
- [ ] 导出 OpenAPI JSON。
- [ ] 提供 Postman/Apifox 集合。
- [ ] 对齐 ID 为字符串的处理。
- [ ] 对齐毫秒时间戳。
- [ ] 对齐匿名作者展示。
- [ ] 对齐审核中、通过、拒绝的 UI。
- [ ] 对齐 token 过期刷新流程。
- [ ] 对齐上传签名和上传确认流程。
- [ ] 对齐下拉刷新和游标清空逻辑。
- [ ] 对齐上拉加载的 `nextCursor` 和 `hasMore`。
- [ ] 对齐 401、409、422、429 的用户提示。
- [ ] 完成帖子完整链路联调。
- [ ] 完成课程评价完整链路联调。
- [ ] 完成消息红点联调。

## 13. P0：发布与回滚

- [ ] 迁移前备份生产数据库。
- [ ] 在生产数据副本上演练迁移。
- [ ] 确认迁移时间和锁表影响。
- [ ] 新 API 使用功能开关控制。
- [ ] 使用 `RYYYY.MM.DD.NUMBER` 规则创建发布 tag。
- [ ] 验证 tag 能触发 GitHub Actions 镜像构建和 Smoke Test。
- [ ] 确认镜像仓库、Kubernetes 集群和部署 YAML 中引用同一版本号。
- [ ] 将部署 YAML 放入受控且可审计的位置，避免依赖个人临时文件。
- [ ] Kubernetes 配置文件、证书 ID 和 DigitalOcean Token 不进入仓库。
- [ ] 发布前检查负载均衡证书仍然有效。
- [ ] 先发布后端，再灰度开启小程序入口。
- [ ] 保留旧 API 至少一个完整版本周期。
- [ ] 准备数据库迁移回滚或前滚修复方案。
- [ ] 配置错误率、延迟、审核积压、消息积压监控。
- [ ] 配置 401、409、422、429 分布监控。
- [ ] 发布后核对点赞数、评论数和课程均分。

## 14. 完成定义（Definition of Done）

每个接口只有同时满足以下条件才算完成：

- [ ] 接口代码已合并。
- [ ] 数据迁移已编写并验证。
- [ ] 权限和业务校验完整。
- [ ] 自动测试通过。
- [ ] OpenAPI 文档已更新。
- [ ] 请求和响应示例已验证。
- [ ] 小程序测试环境联调通过。
- [ ] 日志中可通过 Request ID 定位问题。
- [ ] 没有明显 N+1 查询。
- [ ] 错误提示可以直接用于前端展示或映射。

## 15. 建议里程碑

### M1：基础可用

- `/api/v1` 公共层
- 登录接入
- 图片上传
- 帖子列表、发布、详情、删除
- 评论和回复

### M2：互动闭环

- 帖子/评论点赞
- 互动消息
- 未读红点
- 个人中心
- 匿名和内容审核

### M3：课程评分

- 课程搜索和创建
- 课程查重
- 评价新增、修改、删除
- 评价点赞
- 均分和评分分布

### M4：上线

- 全量自动测试
- 性能测试
- 小程序验收
- 数据迁移演练
- 灰度发布和监控
