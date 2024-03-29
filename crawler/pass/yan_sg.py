from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


class yan_sgSpider(BaseSpider):
    name = 'yan_sg'
    website_id = 1639
    language_id = 2005
    allowed_domains = ['yan.sg']
    start_urls = ['https://www.yan.sg/all/']  # https://targetlaos.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        if self.time is not None:
            t = soup.find(class_='td-ss-main-content td_block_template_1').find_all(class_='td_module_10 td_module_wrap td-animation-stack')[0]
            last_time = t.select_one('.td-post-date').text.replace('年', '-').replace('月', '-').replace('日','') + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            print(last_time,'\n',self.time)
            articles = soup.find(class_='td-ss-main-content td_block_template_1').find_all(class_='td_module_10 td_module_wrap td-animation-stack')
            for article in articles:
                article_url = article.select_one('.td-module-thumb a').get('href')
                title = article.select_one('.item-details').find(class_='entry-title td-module-title').text
                yield Request(url=article_url, callback=self.parse_item,
                              meta={'category1': None, 'category2': None,
                                    'title': title,
                                    'abstract': article.select_one('.td-excerpt').text.strip(),
                                    'images': article.select_one('.td-module-thumb a img').get('src'),
                                    'time': article.select_one('.td-post-date').text.replace('年', '-').replace('月', '-').replace('日','') + ' 00:00:00'})
        else:
            flag = False
            self.logger.info("时间截止")

        if flag:
            if soup.find(class_='page-nav td-pb-padding-side') is not None:
                next_page = soup.find(class_='page-nav td-pb-padding-side').select('a')[-1].get('href')
                yield Request(url=next_page, callback=self.parse, meta=response.meta)
            else:
                self.logger.info("no more pages")


    # def parse_page(self, response):
    #     soup = BeautifulSoup(response.text, 'lxml')
    #     flag = True
    #     if self.time is not None:
    #         t = soup.select('div.post-listing > article > p > span')[-1].text.split('/')
    #         last_time = "{}-{}-{}".format(t[2], t[1], t[0]) + ' 00:00:00'
    #     if self.time is None or DateUtil.time_now_formate(last_time) >= int(self.time):
    #         articles = soup.select('#main-content > div.content-wrap > div > div.post-listing h2 > a')
    #         for article in articles:
    #             article_url = article.get('href')
    #             title = article.text
    #             yield Request(url=article_url, callback=self.parse_item,meta={'title': title, 'category1': response.meta['category1'], 'category2': response.meta['category2']})
    #     else:
    #         flag = False
    #         self.logger.info("时间截止")
    #     if flag:
    #         if soup.select_one('#tie-next-page a') is not None:
    #             next_page = soup.select_one('#tie-next-page a').get('href')
    #             yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
    #         else:
    #             self.logger.info("no more pages")


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = soup.select_one('.td-category').select('li a')[0].text
        item['category2'] = soup.select_one('.td-category').select('li a')[1].text
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        item['images'] = [response.meta['images']]
        item['abstract'] = response.meta['abstract']
        p_list = []
        if soup.select('.td-post-content section'):
            all_p = soup.select('.td-post-content section')
            for paragraph in all_p:
                try:
                    p_list.append(paragraph.select_one('span').text.strip())
                except:
                    continue
            body = '\n'.join(p_list)
            item['body'] = body
        return item