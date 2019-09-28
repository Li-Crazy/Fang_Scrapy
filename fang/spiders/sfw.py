# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy_demo.fang.fang.items import NewHouseItem,ESFHouseItem
from scrapy_redis.spiders import RedisSpider

class SfwSpider(RedisSpider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    # start_urls = ['https://www.fang.com/SoufunFamily.htm']
    redis_key = "fang:start_urls"

    def parse(self, response):
        trs = response.xpath("//div[@class='outCont']//tr")
        for tr in trs:
            tds = tr.xpath(".//td[not(@class)]")
            province_td = tds[0]
            province_text = province_td.xpath(".//text()").get()
            province_text = re.sub(r"\s","",province_text)
            if province_text:
                province = province_text
            #不爬取海外的城市的房源
            if province == '其它':
                continue

            city_td = tds[1]
            city_links = city_td.xpath(".//a")
            for city_link in city_links:
                city = city_link.xpath(".//text()").get()
                city_url = city_link.xpath(".//@href").get()
                # print("省份：",province)
                # print("城市：",city)
                # print("城市链接：",city_link)
                # break
                # 构建新房的链接
                url_module = city_url.split(".")
                scheme = url_module[0]
                domain = url_module[1] + "." + url_module[2]

                if 'bj' in scheme:
                    newhouse_url = "https://newhouse.fang.com/house/s/"
                    esf_url = "https://esf.fang.com/"
                    self.newhouse_url = newhouse_url
                else:
                    newhouse_url = scheme + ".newhouse." + domain + "house/s/"
                    # 构建二手房的链接
                    esf_url = scheme + ".esf." + domain
                    self.newhouse_url = newhouse_url
                # print("城市：%s%s"%(province,city))
                # print("新房链接：%s"%newhouse_url)
                # print("二手房链接：%s"%esf_url)
                yield scrapy.Request(url = newhouse_url,callback=self.parse_newhouse,meta = {"info":(province,city)})
                yield scrapy.Request(url=esf_url,callback=self.parse_esf,
                                     meta={"info": (province, city)})
                break
            break

    def parse_newhouse(self,response):
        province,city = response.meta.get('info')
        lis = response.xpath("//div[contains(@class,'nl_con')]/ul/li")
        for li in lis:
            # h3 = li.xpath(".//div[@class='clearfix']/h3")
            # print(h3)
            if li.xpath(".//div[@class='clearfix']/h3"):
                continue
            name = li.xpath(".//div[@class='nlcd_name']/a/text()").get()
            name = re.sub(r"\s", "", name)
            # print(name)
            house_type_list = li.xpath(".//div[contains(@class,"
                                       "'house_type')]/a//text()").getall()
            house_type_list = list(map(lambda x:re.sub(r"\s","",x),house_type_list))
            rooms = list(filter(lambda x:x.endswith("居"),house_type_list))
            # print(rooms)
            area = "".join(li.xpath(".//div[contains(@class,'house_type')]/text("
                               ")").getall())
            area = re.sub(r"\s|－|/","",area)
            # print(area)
            address = li.xpath(".//div[@class='address']/a/@title").get()
            # print(address)
            district_text = "".join(li.xpath(".//div[@class='address']/a//text("
                                        ")").getall())
            district = re.search(r".*\[(.+)\].*",district_text).group(1)
            # print(district)
            sale = li.xpath(".//div[contains(@class,'fangyuan')]/span/text("
                            ")").get()
            # print(sale)
            price = "".join(li.xpath(".//div[@class='nhouse_price']//text("
                                ")").getall())
            price = re.sub(r"\s|广告","",price)
            # print(price)
            origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()
            origin_url = "https:" + origin_url
            # print(origin_url)

            item = NewHouseItem(name=name,rooms=rooms,area=area,city=city,
                                address=address,district=district,sale=sale,
                                price=price,origin_url=origin_url,province=province)
            yield item

        next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").get()
        url = next_url.split("/")
        # print(url)
        next_url = self.newhouse_url + url[-2]
        print(next_url)
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url),callback=self.parse_newhouse,meta = {"info":(province,city)})

    def parse_esf(self,response):
        province,city = response.meta.get('info')
        item = ESFHouseItem(province=province,city=city)
        dls = response.xpath("//div[@class='shop_list shop_list_4']/dl")
        for dl in dls:
            name = dl.xpath(".//p[@class='mt10']/a/span/text()").gett()
            print(name)
            infos = dl.xpath(".//p[@class='tel_shop']/text()").getall()
            infos = list(map(lambda  x:re.sub(r"\s","",x),infos))
            print(infos)
            for info in infos:
                if "厅" in info:
                    item['rooms'] = info
                elif '层' in info:
                    item['floor'] = info
                elif '向' in info:
                    item['toward'] = info
                else:
                    item['year'] = info.replace("建筑年代：","")
                print(item)
            address = dl.xpath(".//p[@class='add_shop']/span/@title").get()
            item['address'] = address
            item['area'] = dl.xpath(".//div[contains(@class,'area')]/p/text("
                                    ")").get()
            item['price'] = "".join(dl.xpath(".//div[@class='moreInfo']/p["
                                             "1]//text()").getall())
            item['unit'] = "".join(dl.xpath(".//div[@class='moreInfo']/p[2"
                                         "]//text()").getall())
            detail_url = dl.xpath(".//p[@class='title']/a/@href").get()
            item['origin_url'] = response.urljoin(detail_url)
            yield item
        next_url = response.xpath("//a[@id=PageControll_hlk_next']/@href").get()
        yield scrapy.Request(url=response.urljoin(next_url),
                             callback=self.parse_esf,meta = {"info":(
                province,city)})