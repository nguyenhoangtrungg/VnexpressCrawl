from asyncio.windows_events import NULL
from operator import ge
from re import X
from turtle import title
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "express"
    global block_list
    block_list = ['Menu-ThoiSu', 'Menu-GocNhin', 'Menu-TheGioi', 'Menu-Video', 'Menu-Podcasts',
                  'Menu-KinhDoanh', 'Menu-KhoaHoc', 'Menu-GiaiTri', 'Menu-TheThao', 'Menu-PhapLuat',
                  'Menu-GiaoDuc', 'Menu-SucKhoe', 'Menu-DoiSong', 'Menu-DuLich', 'Menu-SoHoa',
                  'Menu-Xe', 'Menu-YKien', 'Menu-TamSu', 'Menu-Hai', 'Menu-MoiNhat', 'Menu-Home']
    start_urls = [
        'https://vnexpress.net',
    ]
            
    cnt = 0        
            
    def parse(self, response):
        
        # yield scrapy.Request("https://vnexpress.net/thoi-su", callback=self.parseSmallList)
        
        for express in response.css('li a'):
        
            checkTitle = express.css('a::attr(title)').get()
            checkHref = express.css('a::attr(href)').get()
            
            if checkTitle == None: break
            if checkHref == "/": continue
            if 'vnexpress.net' in checkHref: continue
            
            # yield {
            #     'title': express.css('a::attr(title)').get(),
            #     'href' : express.css('a::attr(href)').get(),
            # }
            
            linkTo = response.urljoin(checkHref);
            
            yield scrapy.Request(linkTo, callback=self.parseSmallList)
                    
    def parseSmallList(self, response):
        
        for express in response.css('a'):
            
            checkTitle = express.css('a::attr(title)').get()
            checkDataMedium = express.css('a::attr(data-medium)').get()
            checkHref = express.css('a::attr(href)').get()
            
            if checkTitle == None: continue
            if checkDataMedium == None: continue
            if checkHref == None: continue
            
            if 'Menu' not in checkDataMedium: continue
            if checkDataMedium in block_list: continue
            if 'vnexpress.net' in checkHref: continue
            
            #print('1', checkTitle, checkDataMedium, checkHref)
            
            # yield {
            #     'href' : express.css('a::attr(href)').get(),
            #     'data-medium': express.css('a::attr(data-medium)').get(),
            #     'title': express.css('a::attr(title)').get(),
            # }
            
            self.cnt = 0
            
            linkTo = response.urljoin(checkHref);
            
            yield scrapy.Request(linkTo, callback=self.parsePaper)
    
    
    def parsePaper(self, response):
        
        pageHere = response.url.split(" ")[0]
        
        for express in response.css('h2.title-news a'):
            
            getTitle = express.css('a::attr(title)').get()
            getHref = express.css('a::attr(href)').get()
            # yield {
            #     'currentPage' : pageHere,
            #     'link' : getHref,
            #     'title': getTitle,
            # }
            yield scrapy.Request(getHref, callback=self.parseInfo, meta={'index' : pageHere})
            self.cnt += 1
            
            if self.cnt > 100: break
            
        nextPage = response.css('a.btn-page::attr(href)').getall()
        
        willNextPage = "Text!!"
        
        for page in nextPage:
            willNextPage = self.start_urls[0] + page
            if len(willNextPage) < len(pageHere): continue
            if len(willNextPage) > len(pageHere): break
            if willNextPage > pageHere: break
            
        print(willNextPage)
            
        if self.cnt <= 100:
            yield scrapy.Request(willNextPage, callback=self.parsePaper)
        
    def parseInfo(self, response):

        getPage = response.meta.get('index').split("/")[4]
        getPageReal = getPage.split("-")
        a = getPageReal.pop(-1)
        getPage = '-'.join(getPageReal)
        getTitle = getSub = getTag = "Hi"
        for express in response.css('meta'):
            name = express.css('::attr(name)').get()
            if name is None: continue
            content = express.css('::attr(content)').getall()
            if 'its_title' in name: getTitle = content
            if 'its_subsection' in name: getSub = content
            if 'its_tag' in name: getTag = content
            if 'twitter:url' in name: geturl = content
        yield {
                'page' : getPage,
                'title' : getTitle,
                'sub' : getSub,
                'tag': getTag,
                'url': geturl,
            }
            