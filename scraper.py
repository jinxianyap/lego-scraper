import scrapy
import csv

visited = ['/sets/year-2016']
file = open('lego.csv', 'w')
fnames = ['year', 'page', 'name', 'pieces', 'minifigs', 'rrp', 'image']
writer = csv.DictWriter(file, fieldnames=fnames)
writer.writeheader()

def processRRP(rrp):
    # if type(rrp) is not str:
    #     return ''
    # if (',' in rrp):
    #     return rrp[1:].split(',')[0]
    # else:
    #     return rrp[1:].split(' ')[0]
    return rrp
        

class BrickSetSpider(scrapy.Spider):
    name = "spider"
    start_urls = ['http://brickset.com/sets/year-2016']
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
    
    def parse(self, res):
        SET_SELECTOR = '.set'
        year_page = res.request.url.split('/')[4:]
        curr_year = year_page[0].split('-')[1]
        curr_page = year_page[1].split('-')[-1] if len(year_page) > 1 else '1'

        for each in res.css(SET_SELECTOR):
            NAME_SELECTOR = 'h1 ::text'
            PCS_SELECTOR = './/dl[dt/text() = "Pieces"]/dd[1]/text() | .//dl[dt/text() = "Pieces"]/dd[1]/a/text()'
            MINIFIGS_SELECTOR = './/dl[dt/text() = "Minifigs"]/dd[2]/a/text()'
            IMG_SELECTOR = 'img ::attr(src)'
            RRP_SELECTOR = './/dl[dt/text() = "Pieces" and dt/text() = "Minifigs" and dt/text() = "RRP"]/dd[3]/text() | .//dl[dt/text() = "Pieces" and dt/text() = "RRP"] /dd[2]/text() | .//dl[dt/text() = "RRP"] /dd[1]/text()'
            brickset = {
                'year': curr_year,
                'page': curr_page,
                'name': each.css(NAME_SELECTOR).extract_first(),
                'pieces': each.xpath(PCS_SELECTOR).extract_first(),
                'minifigs': each.xpath(MINIFIGS_SELECTOR).extract_first(),
                'rrp': processRRP(each.xpath(RRP_SELECTOR).extract_first()),
                'image': each.css(IMG_SELECTOR).extract_first(),
            }
            writer.writerow(brickset)

        NEXT_PAGE_SELECTOR = '.next a ::attr(href)'
        next_page = res.css(NEXT_PAGE_SELECTOR).extract_first()
        if next_page:
            yield scrapy.Request(
                res.urljoin(next_page),
                callback=self.parse
            )

        NEXT_YEAR_SELECTOR = '//*[@id="body"]/div[1]/div/div/aside[1]/div[1]/div[1]/form/select/option'
        for year in res.xpath(NEXT_YEAR_SELECTOR):
            YEAR_SELECTOR = 'option ::attr(value)'
            year_url = year.css(YEAR_SELECTOR).extract_first()
            if year_url and not (year_url in visited):
                # print(res.urljoin(year_url))
                visited.append(year_url)
                yield scrapy.Request(
                    res.urljoin(year_url),
                    headers=headers,
                    callback=self.parse
                )

