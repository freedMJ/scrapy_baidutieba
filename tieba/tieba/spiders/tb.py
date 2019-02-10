# -*- coding: utf-8 -*-
import scrapy
import urllib
import requests
import re

class TbSpider(scrapy.Spider):
    name = 'tb'
    allowed_domains = ['tieba.baidu.com']
    start_urls = ['https://tieba.baidu.com/f?kw=%E6%9D%8E%E6%AF%85&ie=utf-8&pn=0']

    def parse(self, response):
        tie_list=response.xpath("//div[@class='post_list']//li[@class='tl_shadow tl_shadow_new ']")
        for tie in tie_list:
            item={}
            item['title']=tie.xpath(".//a/div[@class='ti_title']/span[1]/text()").extract_first()
            item['href']=tie.xpath("./a/@href").extract_first()
            if item['href'] is not None:
                item['href']=urllib.parse.urljoin(response.url,item['href'])
            yield scrapy.Request(
                item['href'],
                callback=self.parse_detail,
                meta={"item":item}
                )
        next_url="https://tieba.baidu.com/f?kw=%E6%9D%8E%E6%AF%85&ie=utf-8&pn="+str(((int(re.findall("&pn=(\\d)",response.url)[0])+1)*50))
        yield scrapy.Request(
            next_url,
            callback=self.parse
            )

            #贴子详情
    def parse_detail(self,response):
        item=response.meta['item']
        item['img_list']=re.findall("data-url='(.*?)'",response.body.decode())
        if item['img_list'] is not None:
            item['img_list']=[requests.utils.unquote(i).split("src=")[-1] for i in item['img_list']]
        item['next_detail']=response.xpath("//div[@class='l_thread_info']//a[text()='下一页']/@href").extract_first()

        yield item

