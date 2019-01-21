# -*- coding: utf-8 -*-

# Define your item pipelines here

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs #打开写入文件避免编码问题
import json

from scrapy.pipelines.images import ImagesPipeline

import MySQLdb

conn = MySQLdb.connect(host='localhost', user='root',
                       passwd='123456', db='article_spider', charset='utf8')

cur = conn.cursor()

insert_sql = """
            insert into article_info(title, url, create_date, fav_nums)
            VALUES (%s, %s, %s, %s)
        """
item ={
    'title':['http://jbcdn2.b0.upaiyun.com/2015/02/591d8b55a524f825dd29a22b8df70000.jpg'],
    'url':'https:www.pypi.doubam.com/example',
    'create_date':'2018/10/24',
    'fav_nums':'12'
}
cur.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["fav_nums"]))
conn.commit()