# 小程序“圈子”模块

## 通知的返回类型
这一部分不好弄到swagger文档里，所以我就用markdown来写文档了。

目前通知有 2 个类型。

### `REPLY` ： 表示回复的通知类型。

返回的数据中， `targetPost` 为回复的目标的id。由于这里无法判断目标具体是主贴、一级回复还是二级回复，
前端不需要使用此字段。

`sender` 相关的两个字段为回复者的信息。

`data` 字段中包含了前端可以使用的数据，其格式如下：

```python
{
  'main_post_id': '这个回复属于哪个主贴',
  'main_post_tag_id': '这个回复的主贴的tag id',
  'main_post_title': '这个回复的主贴的标题',
  'reply_content_summary': '这个回复的正文的前20个字',
  'comment_id': '这个回复属于的一级回复的id，方便前端做跳转用',
}
```

### `CENSOR` ： 表示被封禁的通知类型。

返回的数据中， `targetPost` 为回复的目标的id。可根据data中'type'字段来分辨是主贴、一级回复还是二级回复

`sender` 相关的信息为 null。

`data` 字段中包含了前端可以使用的数据，其格式如下：

```python
{
  'type': '返回帖子的类型可以为：main_post 或 comment 或 subcomment'
  'main_post_id': '属于的主贴的id,若被封禁的是主贴，则为本身id'
  'main_post_tag_id': '属于的主贴的tag id',
  'main_post_title': '属于的主贴的title'
  'content_summary': '被封禁的帖子或评论的正文的前20个字',
  'reason': '封禁的理由',
}
```

### 'FAVOURITE' 被收藏的通知
回的数据中， `targetPost` 为收藏的目标的id。

`data` 字段中包含了前端可以使用的数据，其格式如下：

```python
{
  "target_post_tag": 被收藏帖子的的tag
  'target_post_title': 被收藏帖子的title
}