#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib

def get_md5(url):
    if isinstance(url, str):   #python3中没有unicode这个关键词了
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

# if __name__ == '__main__':
#     get_md5('http://jobbole.com'.encode("utf-8"))