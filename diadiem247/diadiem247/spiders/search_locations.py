import scrapy
import re
from scrapy.http import HtmlResponse, Request
from playwright.async_api import Page, Locator, FrameLocator
from scrapy_playwright.handler import PageMethod

ROOT_URL: str = "https://diadiem247.com"
PAGE_SIZE: int = 8
search_term: str = "bảo+hiểm"
category_name: str = "Công ty bảo hiểm"
page_index: int = 1

class SearchLocationsSpider(scrapy.Spider):
    name = "search_locations"
    allowed_domains = ["diadiem247.com"]
    start_urls = [f"{ROOT_URL}/index/get-location-ajax"]

    def start_requests(self):
        global page_index
        while page_index > 0:
            formdata = {
                'search': search_term,
                'page': str(page_index),
            }
            yield scrapy.FormRequest(
                url=self.start_urls[0],
                callback=self.fetch_more_category_page,
                formdata=formdata,
            )

    def fetch_more_category_page(self, response: HtmlResponse):
        meta = response.meta
        json_res = response.json()
        is_success: bool = json_res.get("success", False)
        global page_index

        if is_success:
            location_list = json_res.get("location_list", [])

            if len(location_list) > 0:
                page_index += 1

                for location in location_list:
                    location_name: str = location.get("name")
                    location_address: str = location.get("address")
                    location_link: str = location.get("href")
                    meta = {
                        "location_name": location_name.strip(),
                        "location_address": location_address.strip(),
                        "location_link": f"{ROOT_URL}{location_link}",
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("evaluate", "window.scrollBy(0, document.getElementById('map_iframe').getBoundingClientRect().top + window.scrollY)"),
                            PageMethod("wait_for_selector", "iframe#map_iframe"),
                        ],
                    }
                    yield scrapy.Request(
                        url=f"{ROOT_URL}{location_link}",
                        callback=self.fetch_location_page,
                        errback=self.errback,
                        meta=meta,
                        dont_filter=True,
                    )
            else: 
                page_index = 0
                self.logger.warning(f"Completed to get data, stopping at a: {response.url}")

        else:
            self.logger.error(f"Failed to fetch api: {response.url}")

    async def fetch_location_page(self, response):
        page: Page = response.meta['playwright_page']

        try:
            iframe: FrameLocator = page.frame_locator('iframe#map_iframe')
            ggm_tag: Locator = iframe.locator('//a[@aria-label="View larger map"]')
            ggm_link: str = await ggm_tag.get_attribute("href")

            pattern: re.Pattern[str] = r"ll=(-?\d+\.\d+),(-?\d+\.\d+)"
            match: re.Match[str] = re.search(pattern=pattern, string=ggm_link)

            print(f"{ggm_link}")

            latitude = match.group(1) if match else 0
            longitude = match.group(2) if match else 0
            meta = response.meta
            yield {
                "lat": latitude,
                "lng": longitude,
                "location_name": meta["location_name"],
                "location_address": meta["location_address"],
                "category_name": category_name,
                "province_name": None,
                "row": {
                    "location_link": meta["location_link"],
                    "category_link": f"{ROOT_URL}/index/search?q={search_term}",
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

