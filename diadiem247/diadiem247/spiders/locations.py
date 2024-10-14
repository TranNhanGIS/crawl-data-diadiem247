import scrapy
import math
import re

ROOT_URL = "https://diadiem247.com"
PAGE_SIZE = 8

class LocationsSpider(scrapy.Spider):
    name = "locations"
    allowed_domains = ["diadiem247.com"]
    start_urls = [f"{ROOT_URL}/index/get-province-list"]

    def parse(self, response):
        json_res = response.json()
        is_success = json_res.get("success", False)
        
        if is_success:
            province_list = json_res.get("province_list", [])
            
            for province in province_list:
                province_link = province.get("href")
                yield scrapy.Request(
                    url=f"{ROOT_URL}{province_link}", 
                    callback=self.fetch_province_page
                )

        else:
            self.logger.error(f"Failed to fetch api: {response.url}")

    def fetch_province_page(self, response):
        navbar = response.xpath("//ul[contains(@class, 'nav')]")
        navbar_items = navbar.xpath(".//li[@class='dropdown']")

        for navbar_item in navbar_items:
            dropdown_title = navbar_item.xpath("./a[@class='dropdown-toggle']/div/text()").get()
            dropdown_items = navbar_item.xpath("./ul[contains(@class,'dropdown-menu')]//li")

            for dropdown_item in dropdown_items:
                dropdown_link = dropdown_item.xpath("./a/@href").get()
                meta = {
                    "category_name": dropdown_title,
                    "category_link": f"{ROOT_URL}{dropdown_link}"
                }
                yield scrapy.Request(
                    url=f"{ROOT_URL}{dropdown_link}", 
                    callback=self.fetch_category_page,
                    meta=meta
                )
    
    def fetch_category_page(self, response):         
        main_content = response.xpath("//div[contains(@class, 'main-content')]")
        data_column = main_content.xpath("./div[@class][1]")
        row_count_str = data_column.xpath(".//h2//b/text()").getall()[-1] 
        row_count = int(row_count_str.replace(",", "")) if "," in row_count_str else int(row_count_str)
        meta = response.meta

        total_pages = math.ceil(row_count / PAGE_SIZE)
        more_location = response.xpath("//a[@id='more-location']")
        
        if total_pages > 1 and bool(more_location) is True:  
            province_id = more_location.xpath("./@data-province-id").get()
            category_id = more_location.xpath("./@data-category-id").get() 

            for page_index in range(1, total_pages + 1):
                formdata = {
                    'province_id': province_id, 
                    'category_id': category_id, 
                    'page': str(page_index)
                }
                yield scrapy.FormRequest(
                    url=f"{ROOT_URL}/index/get-location-ajax", 
                    callback=self.fetch_more_category_page, 
                    formdata=formdata,
                    meta=meta
                )

        elif total_pages == 1 and bool(more_location) is False:
            rows = data_column.xpath("./div[@class='row']")
            
            for row in rows:
                data_row = row.xpath("./div[@class='col-md-10 col-xs-9']")
                location_name = data_row.xpath("./a/div[@class='title-home']/text()").get()
                location_address = data_row.xpath("./div[@class='addr-list']/text()[2]").get()
                location_link = data_row.xpath("./a/@href").get()

                meta.update({
                    "location_name": str(location_name).strip(),
                    "location_address": str(location_address).strip(),
                    "location_link": f"{ROOT_URL}{location_link}"
                })
                yield scrapy.Request(
                    url=f"{ROOT_URL}{location_link}", 
                    callback=self.fetch_location_page, 
                    meta=meta,
                    dont_filter=True
                )

        else:
            self.logger.warning(f"This category is empty: {response.url}")

    def fetch_more_category_page(self, response):
        json_res = response.json()
        is_success = json_res.get("success", False)
        meta = response.meta
        
        if is_success:
            location_list = json_res.get("location_list", [])         

            for location in location_list:
                location_name = location.get("name")
                location_address = location.get("address")
                location_link = location.get("href")
                meta.update({
                    "location_name": str(location_name).strip(),
                    "location_address": str(location_address).strip(),
                    "location_link": f"{ROOT_URL}{location_link}"
                })
                yield scrapy.Request(
                    url=f"{ROOT_URL}{location_link}", 
                    callback=self.fetch_location_page, 
                    meta=meta,
                    dont_filter=True
                )
                
        else:
            self.logger.error(f"Failed to fetch api: {response.url}")
    
    def fetch_location_page(self, response):
        url = response.xpath("//div[@class='google-maps-link']/a/@href").get()
        pattern = r"https://maps.google.com/maps?ll=(-?\d+\.\d+),(-?\d+\.\d+)"
        match = re.search(pattern=pattern, string=str(url))

        location_lon = response.xpath("//input[@id='location_lon']/@value").get()
        location_lat = response.xpath("//input[@id='location_lat']/@value").get()
        meta = response.meta

        yield {
            "lon": location_lon,
            "lat": location_lat,
            "location_name": meta["location_name"],
            "location_address": meta["location_address"],
            "row": {
                "location_link": meta["location_link"],
                "category_link": meta["category_link"],
                "category_name": meta["category_name"],
            }
        }
