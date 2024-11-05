# Scrapy settings for diadiem247 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "diadiem247"

SPIDER_MODULES = ["diadiem247.spiders"]
NEWSPIDER_MODULE = "diadiem247.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "diadiem247 (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 2

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8,fr-FR;q=0.7,fr;q=0.6",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "diadiem247.middlewares.Diadiem247SpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "diadiem247.middlewares.Diadiem247DownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {"diadiem247.pipelines.Diadiem247CSVPipeline": 300}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Enable save logging to file and diasble logging in terminal
LOG_LEVEL = 'DEBUG'
LOG_FILE = 'quan-an-1.txt'
LOG_ENABLED = True

# MongoDB Configuration
# MONGO_URI = "mongodb+srv://nhantt:12345@trannhangtel.enilf.mongodb.net/"
MONGO_URI = 'mongodb://mongodb:27017'
MONGO_DATABASE = 'scrapy_db'
MONGO_COLLECTION = 'diadiem247'

# Set Playwright as a downloader handler for Scrapy
DOWNLOAD_HANDLERS = {
    'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
    'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
}

# Enable Playwright in your project
PLAYWRIGHT_BROWSER_TYPE = 'chromium'
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Playwright settings
PLAYWRIGHT_LAUNCH_OPTIONS = {
    'headless': True,
    "timeout": 20 * 1000,
}

# Max concurrent Playwright pages per browser context (set according to your needs)
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 8

# Define a default timeout for Playwright actions (like waiting for elements)
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 20 * 1000
DOWNLOAD_TIMEOUT = 20
RETRY_ENABLED = True
RETRY_TIMES = 3

def should_abort_request(request):
    return (
        request.resource_type in ["image", "font", "media"]
        or any(ext in request.url for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico"])
        or any(ext in request.url for ext in [".mp3", ".mp4", ".avi", ".mov", ".wav", ".flv", ".mkv", ".webm"])
        or any(ext in request.url for ext in [".woff", ".woff2", ".ttf", ".eot", ".otf"])
    )

PLAYWRIGHT_ABORT_REQUEST = should_abort_request