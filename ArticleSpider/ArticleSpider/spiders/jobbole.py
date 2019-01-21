# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
from scrapy.http import Request
from urllib import parse  #将域名拼接

from ArticleSpider.items import JobboleArticleItem
from utils.common import get_md5

'''
爬取所有文章内容，定义两个函数，首先定义start_urls首页爬取完列表页所有内用，
再定义下一页循环调用parse传入request的网址
'''

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://python.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2.获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        """
        #解析列表页中所有文章url并交给scrapy下载后并进行解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            #Request(url = post_url, callback = self.parse_detail)
            #域名拼接方法
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url":image_url}, callback=self.parse_detail, dont_filter=True)
            print(post_url)

        #提取下一页并交给scrapy进行下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        article_item = JobboleArticleItem()
        #提取文章的具体字段
        front_images_url = response.meta.get("front_image_url","") #文章封面图
        title = response.xpath('//*[@id="archive"]/div[1]/div[2]/p[1]/a[1]/text()').extract_first()
        #time = response.xpath('//*[@id="post-89331"]/div[2]/p').extract()[0].strip().replace('·', "").strip()
        create_date = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace('·', "").strip()
        #vote_post = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract()
        fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract()[0]
        content = response.xpath('//*[@class="entry"]//*/text()').extract()
        match_re = re.match(".*(\d+).*", fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0
        desc = response.xpath('//*[@id="post-89331"]/div[2]/p/a/text()').extract()
        descString = ','.join(desc)

        article_item["url_object_id"] = get_md5(response.url)
        #因为取出来的日期是字符串，存到数据库中要转换为日期格式
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()

        article_item['create_date'] = create_date

        article_item["title"] = title
        article_item["url"] = response.url
        article_item["front_images_url"] = [front_images_url]
        article_item['fav_nums'] = fav_nums
        article_item['content'] = content
        yield article_item
        print(title)
        pass
