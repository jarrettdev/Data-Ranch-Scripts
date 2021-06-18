#scrape products from armslist
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.item import Item, Field
from tqdm import tqdm 
import requests

torchestrator_host = "localhost"
tochestrator_port = 8080
torchestrator_api_path = "port"

class ArmslistSpider(scrapy.Spider):

    ip_list = []

    def fetch_proxy_port(self):
        response = requests.get(f'http://{torchestrator_host}:{tochestrator_port}/{torchestrator_api_path}')
        return response.text

    name = 'armslist'
    headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }
    base_url = 'https://www.armslist.com/classifieds/search?category=all&page={}&posttype=1&ispowersearch=0'
    # custom settings
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': './data/armslist/Armslist Listings.csv',
        'CONCURRENT_REQUESTS' : 64,
        'CONCURRENT_REQUESTS_PER_DOMAIN' : 64,
        'LOG_ENABLED' : 'True'
    }

    def start_requests(self):
        #1. collect video links
        for page in tqdm(range(1,3500)):
            #get proxy port each request
            proxy_port = self.fetch_proxy_port()
            proxy = f'https://{torchestrator_host}:{proxy_port}'
            next_page = self.base_url.format(page)
            yield scrapy.Request(url=next_page, headers=self.headers, callback=self.collect_links, meta={'proxy' : proxy})

    def collect_links(self, response):
        card_container = response.css('div[class="col-xs-12 col-md-8 img-rounded"]').get()
        cards = response.css('div[class="container-fluid"]').getall()
        for card in cards:
            gun_url = None
            card_inner = Selector(text=card).css('div[class="row"]')
            info_container = card_inner.css('div[class="col-md-7"]')
            h4_list = card_inner.css('h4').getall()
            item = {
                "URL" : None,
                "Title" : None,
                "Price" : None,
                "Location" : None,
                "Post_Date" : None
            }
            for i in range(len(h4_list)):
                h4_content = Selector(text=h4_list[i]).css('*::text').get().strip()
                print(h4_content)
                if i == 0:
                    #Get href
                    href = Selector(text=h4_list[i]).css('a ::attr(href)').get()
                    gun_url = f'https://armslist.com{href}'
                    item.update({"Title" : h4_content})
                    item.update({"URL" : gun_url})
                else:
                    item.update({"Price" : h4_content})
            proxy_port = self.fetch_proxy_port()
            proxy = f'{torchestrator_host}:{proxy_port}'
            print(f'proxy : {proxy}')
            if gun_url:
                yield response.follow(url=gun_url, headers=self.headers, callback=self.get_details, meta={'proxy' : proxy}, cb_kwargs=item)

    def get_details(self, response, URL, Title, Price, Location, Post_Date):
        item = {
            "URL" : URL,
            "Title" : Title,
            "Price" : Price,
            "Location" : Location,
            "Post_Date" : Post_Date
        }

        location_container = response.css('ul[class="location"]')
        location_containers = response.css('ul[class="location"]').getall()
        li_elements = location_container.css('li').getall()
        location = None
        shipping = None
        website = None
        phone_number = None
        for i in range(len(li_elements)):
            if i == 0:
                print(li_elements[i])
                print('')
                location = li_elements[i].split('<div class="col-sm-12 col-md-7">')[1].split('</div>')[0]
                print(f'location : {location}')
            elif i == 1:
                shipping = li_elements[i].split('<div class="col-sm-12 col-md-7">')[1].split('</div>')[0]
                if 'href="' in shipping:
                    website = shipping.split('href="')[1].split('">')[0]
                    phone_number = location
                    split_selector = location_containers[1].split('<div class="col-sm-12 col-md-7">')
                    location = split_selector[1].split('</div>')[0].strip()
                    shipping = split_selector[2].split('</div>')[0].strip()
                    
                
        item.update({'Location' : location})
        item.update({'Shipping' : shipping})
        item.update({'Phone_Number' : phone_number})
        item.update({'Website' : website})
        info_time = response.css('div[class="info-time"]')
        try:
            date = info_time.css('span[class="date"] ::text').get().split('Listed On: ')[1]
            print(date)
        except:
            date = None
        item['Post_Date'] = date
        yield item

# main driver
if __name__ == '__main__':
    # run scraper
    process = CrawlerProcess()
    process.crawl(ArmslistSpider)
    process.start()
