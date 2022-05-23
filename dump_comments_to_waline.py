#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2020 Lucas Cimon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Dump isso comments to waline json format.
"""

import json
import sqlite3
from collections import defaultdict, namedtuple
from datetime import datetime

DB_PATH = 'comments.db'
ADMIN_NICK = "zhangnew"
# merge multi email to the first one
ADMIN_EMAIL = ["xxx@gmail.com", "xxx@qq.com"]
ADMIN_SITE = "https://zhangnew.com"
# isso doesn't have UA, so we use a fake one
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4882.197 Safari/537.36"

Comment = namedtuple('Comment', ('uri', 'id', 'remote_addr', 'parent', 'created', 'text', 'author', 'email', 'website', 'likes', 'dislikes', 'replies'))

QUERY = 'SELECT uri, comments.id, remote_addr, parent, created, text, author, email, website, likes, dislikes FROM comments INNER JOIN threads on comments.tid = threads.id'


def main():
    db = sqlite3.connect(DB_PATH)
    comments_per_uri = defaultdict(list)
    for result in db.execute(QUERY).fetchall():
        comment = Comment(*result, replies=[])
        comments_per_uri[comment.uri].append(comment)
    root_comments_per_sort_date = {}
    for comments in comments_per_uri.values():
        comments_per_id = {comment.id: comment for comment in comments}
        root_comments, sort_date = [], None
        for comment in comments:
            if comment.parent and comment.parent in comments_per_id:  # == this is a "reply" comment
                comments_per_id[comment.parent].replies.append(comment)
            else:
                root_comments.append(comment)
                if sort_date is None or comment.created > sort_date:
                    sort_date = comment.created
        root_comments_per_sort_date[sort_date] = root_comments
    final_list = []
    for _, root_comments in sorted(root_comments_per_sort_date.items(), key=lambda pair: pair[0]):
        for comment in root_comments:
            final_list.append(print_comment(comment))
            parent_author = comment.author or '匿名'
            for comment in comment.replies:
                final_list.append(print_comment(comment, parent_author))
    print(json.dumps(final_list, indent=4, ensure_ascii=False))


def print_comment(comment, parent_author=None):
    author = comment.author or '匿名'
    email = comment.email or ''
    website = comment.website or ''
    when = datetime.fromtimestamp(comment.created).strftime("%Y-%m-%d %H:%M:%S")

    # set me as admin
    if email in ADMIN_EMAIL:
        email = ADMIN_EMAIL[0]
        website = ADMIN_SITE
        author = ADMIN_NICK
        user_id = 1
    else:
        email = comment.email
        user_id = None
    if comment.parent:
        a = parent_author or '匿名'
        text = "[@" + a + "](#" + str(comment.parent) + "): " + comment.text
    else:
        text = comment.text
    waline_comment = {
        "user_id": user_id,
        "comment": text,
        "insertedAt": when,
        "ip": comment.remote_addr,
        "link": website,
        "mail": email,
        "nick": author,
        "rid": comment.parent,
        "pid": comment.parent,
        "sticky": None,
        "status": "approved",
        "like": comment.likes,
        "ua": UA,
        "url": comment.uri,
        "createdAt": "datetime('now', 'localtime')",
        "updatedAt": "datetime('now', 'localtime')",
        "objectId": comment.id
    }
    # print(comment)
    # print(waline_comment)
    return waline_comment

if __name__ == '__main__':
    main()
