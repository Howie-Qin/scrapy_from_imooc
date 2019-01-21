# -*- coding: utf-8 -*-

# Define your item pipelines here

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs #打开写入文件避免编码问题
import json

from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

# 采用同步的机制写入mysql
class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '123456', 'article_spider', charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article_info(title, url, create_date, fav_nums)
            VALUES (%s, %s, %s, %s)
        """
        #execute，commit代表同步执行，此句执行完了才会往下执行，当爬取速度大于插入速度时，commit就会堵塞，适合采用异步的方法
        self.cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["fav_nums"]))
        self.conn.commit()

#mysql插入异步化,使用twist提供的异步API
class MysqlTwistedPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool
    #可以用一个类方法,读取setting,类似于字典的读取
    #from_settings在初始化的时候会被scrapy调用
    @classmethod
    def from_settings(cls, settings):
        #将参数作为关键字参数dict一次性传入
        dpparms = dict(
            host = settings['MYSQL_HOST'],
            db = settings['MYSQL_DBNAME'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWORD'],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dpparms)
        #返回cls(dbpool),前面需要实例化
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        #添加错误处理
        query.addErrback(self.handle_error) #处理异常

    def handle_error(self,failure):
        #处理异步插入异常
        print(failure)

    def do_insert(self, cursor, item):
        #执行具体的插入
        insert_sql = """
                        insert into article_info(title, url, create_date, fav_nums)
                        VALUES (%s, %s, %s, %s)
                    """
        cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["fav_nums"]))




#新建一个保存json格式的pipeline,需要用到codecs
class JsonWithEncodeingPipeline(object):
    #初始化的时候打开这个文件
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')
    def process_item(self, item, spider):
        #写入需要以字符串的模式写入，用json方法，ensure_ascii=False避免乱码
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item
    def spider_closed(self, spider):
        self.file.close()


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value["path"]
            item["front_image_path"] = image_file_path
            return item
        pass

