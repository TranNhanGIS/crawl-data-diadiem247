# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv

class Diadiem247Pipeline:
    def open_spider(self, spider):
        self.file = open(file="locations.csv", mode="w", encoding="utf-8", newline="")
        fieldnames = ["lon", "lat", "location_name", "location_address", "row"]
        
        self.writer = csv.DictWriter(f=self.file, fieldnames=fieldnames)
        self.writer.writeheader()

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        try:
            self.writer.writerow(item)
        except Exception as e:
            spider.logger.error(f"Save the item failed: {e}")
        return item
