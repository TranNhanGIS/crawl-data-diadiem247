# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import csv


class Diadiem247CSVPipeline:
    def open_spider(self, spider):
        self.file = open(file="quan-an-1.csv", mode="w", encoding="utf-8", newline="")
        fieldnames = ["lat", "lng", "location_name", "location_address", "category_name", "province_name", "row"]

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


class Diadiem247MongoPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE"),
            mongo_collection=crawler.settings.get("MONGO_COLLECTION"),
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.db[self.mongo_collection].insert_one(item)
        except Exception as e:
            spider.logger.error(f"Save the item failed: {e}")
        return item
