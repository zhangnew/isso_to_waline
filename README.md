# dump_comments_to_waline

把 isso 的数据库导出为 waline 的 json 格式

## Usage

修改脚本开头的变量：

- DB_PATH = ''
- ADMIN_NICK = ""
- ADMIN_EMAIL = ""
- ADMIN_SITE = ""
- UA = ""

```shell
python3 dump_comments_to_waline.py > comments.json
```

- 初始化 waline 之后访问 ui 页面，导出数据得到 waline.json
- 把 comments.json 文件里面的 List 替换到 waline.json 的 Comment 中
- 把 waline.json 重新导入到 waline 中。

## 限制

isso 只支持二级回复，所以导出评论中的二级回复，回复@的都是一级回复的人(也就是层主)
