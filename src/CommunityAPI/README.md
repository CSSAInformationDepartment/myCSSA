# 小程序“圈子”模块

## 通知的返回类型
这一部分不好弄到swagger文档里，所以我就用markdown来写文档了。

目前通知有 1 个类型。

### `REPLY` ： 表示回复的通知类型。

返回的数据中， `targetPost` 为回复的目标的id。由于这里无法判断目标具体是主贴、一级回复还是二级回复，
前端不需要使用此字段。

`data` 字段中包含了前端可以使用的数据，其格式如下：

```python
{
  'replier_username': '给我回复的人的用户名',
  'replier_avatar': '给我回复的人的头像',
  'main_post_id': '这个回复属于哪个主贴',
  'main_post_tag_id': '这个回复的主贴的tag id',
  'main_post_title': '这个回复的主贴的标题',
  'reply_content_summary': '这个回复的正文的前20个字',
  'comment_id': '这个回复属于的一级回复的id，方便前端做跳转用',
}
```