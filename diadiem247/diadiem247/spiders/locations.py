import scrapy
import math
import re
import pandas as pd
from scrapy.http import HtmlResponse, Request
from playwright.async_api import Page, Locator, FrameLocator
from scrapy_playwright.handler import PageMethod

ROOT_URL: str = "https://diadiem247.com"
PAGE_SIZE: int = 8
# file_path = 'D:/Tasks/scrapy-diadiem247/diadiem247/quan-an.csv'
# df = pd.read_csv(file_path)

class LocationsSpider(scrapy.Spider):
    name = "locations"
    allowed_domains = ["diadiem247.com"]
    start_urls = [f"{ROOT_URL}/index/get-province-list"]

    def parse(self, response: HtmlResponse):
        json_res: object = response.json()
        is_success: bool = json_res.get("success", False)

        if is_success:
            province_list = json_res.get("province_list", [])

            for province in province_list:
                province_link: str = province.get("href")
                province_name: str = province.get("name")
                meta = {
                    "province_name": province_name
                }
                yield scrapy.Request(
                    url=f"{ROOT_URL}{province_link}", callback=self.fetch_province_page, meta=meta
                )

        else:
            self.logger.error(f"Failed to fetch api: {response.url}")

    def fetch_province_page(self, response: HtmlResponse):
        navbar = response.xpath("//ul[contains(@class, 'nav')]")
        navbar_items = navbar.xpath(".//li[@class='dropdown']")
        meta = response.meta

        for navbar_item in navbar_items:
            dropdown_items = navbar_item.xpath("./ul[contains(@class,'dropdown-menu')]//li")

            for dropdown_item in dropdown_items:
                dropdown_link: str = dropdown_item.xpath("./a/@href").get()
                dropdown_title: str = dropdown_item.xpath("./a/span/text()").get()
                
                meta.update({
                    "category_name": dropdown_title,
                    "category_link": f"{ROOT_URL}{dropdown_link}",
                })
                yield scrapy.Request(
                    url=f"{ROOT_URL}{dropdown_link}", callback=self.fetch_category_page, meta=meta
                )
                    

    def fetch_category_page(self, response: HtmlResponse):
        data_column = response.xpath("//div[contains(@class, 'main-content')]/div[@class][1]")
        row_count = data_column.xpath(".//h2//b/text()").getall()[-1]
        more_location = response.xpath("//a[@id='more-location']")
        meta = response.meta

        total_rows: int = int(row_count.replace(",", "")) if "," in row_count else int(row_count)
        total_pages: int = math.ceil(total_rows / PAGE_SIZE)

        if total_pages > 1 and bool(more_location) is True:
            province_id: str = more_location.xpath("./@data-province-id").get()
            category_id: str = more_location.xpath("./@data-category-id").get()

            for page_index in range(1, total_pages + 1):
                formdata = {
                    'province_id': province_id,
                    'category_id': category_id,
                    'page': str(page_index),
                }
                yield scrapy.FormRequest(
                    url=f"{ROOT_URL}/index/get-location-ajax",
                    callback=self.fetch_more_category_page,
                    formdata=formdata,
                    meta=meta,
                )

        elif total_pages == 1 and bool(more_location) is False:
            rows = data_column.xpath("./div[@class='row']/div[@class='col-md-10 col-xs-9']")

            for row in rows:
                location_name: str = row.xpath("./a/div[@class='title-home']/text()").get()
                location_address: str = row.xpath("./div[@class='addr-list']/text()[2]").get()
                location_link: str = row.xpath("./a/@href").get()

                # if not df["row"].str.contains(f"{ROOT_URL}{location_link}", na=False).any():
                meta.update(
                    {
                        "location_name": location_name,
                        "location_address": location_address,
                        "location_link": f"{ROOT_URL}{location_link}",
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("evaluate", "window.scrollBy(0, document.getElementById('map_iframe').getBoundingClientRect().top + window.scrollY)"),
                            PageMethod("wait_for_selector", "iframe#map_iframe"),
                            PageMethod("wait_for_load_state", "networkidle"),
                        ],
                    }
                )
                yield scrapy.Request(
                    url=f"{ROOT_URL}{location_link}",
                    callback=self.fetch_location_page,
                    errback=self.errback,
                    meta=meta,
                    dont_filter=True,
                )

        else:
            self.logger.warning(f"This category is empty: {response.url}")

    def fetch_more_category_page(self, response: HtmlResponse):
        meta = response.meta
        json_res = response.json()
        is_success: bool = json_res.get("success", False)

        if is_success:
            location_list = json_res.get("location_list", [])

            for location in location_list:
                location_name: str = location.get("name")
                location_address: str = location.get("address")
                location_link: str = location.get("href")

                # if not df["row"].str.contains(f"{ROOT_URL}{location_link}", na=False).any():                
                meta.update(
                    {
                        "location_name": location_name,
                        "location_address": location_address,
                        "location_link": f"{ROOT_URL}{location_link}",
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("evaluate", "window.scrollBy(0, document.getElementById('map_iframe').getBoundingClientRect().top + window.scrollY)"),
                            PageMethod("wait_for_selector", "iframe#map_iframe"),
                            PageMethod("wait_for_load_state", "networkidle"),
                        ],
                    }
                )
                yield scrapy.Request(
                    url=f"{ROOT_URL}{location_link}",
                    callback=self.fetch_location_page,
                    errback=self.errback,
                    meta=meta,
                    dont_filter=True,
                )

        else:
            self.logger.error(f"Failed to fetch api: {response.url}")

    async def fetch_location_page(self, response: HtmlResponse):
        page: Page = response.meta['playwright_page']

        try:
            iframe: FrameLocator = page.frame_locator('iframe#map_iframe')
            ggm_tag: Locator = iframe.locator('//a[@aria-label="View larger map"]')
            ggm_link: str = await ggm_tag.get_attribute("href")

            pattern: re.Pattern[str] = r"ll=(-?\d+\.\d+),(-?\d+\.\d+)"
            match: re.Match[str] = re.search(pattern=pattern, string=ggm_link)

            print(f"{ggm_link}")

            latitude = match.group(1) if match else 0.0
            longitude = match.group(2) if match else 0.0
            meta = response.meta
            yield {
                "lat": latitude,
                "lng": longitude,
                "location_name": meta["location_name"],
                "location_address": meta["location_address"],
                "category_name": meta["category_name"],
                "province_name": meta["province_name"],
                "row": {
                    "location_link": meta["location_link"],
                    "category_link": meta["category_link"],
                },
            }
        except:
            self.logger.error(f"Failed to get location: {response.url}")
            request: Request = response.request
            yield request.copy()
        finally:
            await page.close()

    async def errback(self, failure):
        request: Request = failure.request
        self.logger.error(f'Retrying request: {request.url}')
        yield request.copy()