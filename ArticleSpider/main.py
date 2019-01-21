#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 让scrapy变得可调试
from scrapy.cmdline import execute
import sys
import os
# sys.path.append("D:\linuxShare\ArticleSpider")
# 获取当前文件的目录的父目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "jobbole"])
