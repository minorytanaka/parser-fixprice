from collections.abc import Iterable
from urllib.parse import urljoin
import json
import scrapy
from scrapy.http import Request
from fixprice.items import FixPriceProductItem
from typing import Generator
from time import time
from settings import CATEGORIES, ALLOWED_DOMAINS, BASE_URL_CLIENT, BASE_URL_API, PARAMS, HEADERS
from urllib.parse import urlencode
from w3lib.url import add_or_replace_parameter

class CategorySpider(scrapy.Spider):
    name = "categories"
    allowed_domains = ALLOWED_DOMAINS
    start_urls = CATEGORIES

    url_client = BASE_URL_CLIENT
    url_api = BASE_URL_API
    params = PARAMS
    headers = HEADERS

    def start_requests(self) -> Iterable[Request]:
        for category_link in self.start_urls:
            category_slug = category_link.split("/catalog/")[-1]
            url = f"{urljoin(self.url_api, category_slug)}?{urlencode(self.params)}"
            yield Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response) -> Generator[FixPriceProductItem, None, None]:
        products = response.json()

        for product in products:
            original_price = product.get("price", "")

            special_price = product.get("specialPrice", {}).get("price")

            current_price = special_price if special_price else original_price
            sale_tag = f"Скидка {round((original_price - special_price) / original_price * 100)}%" if special_price else "Нету скидки"
            
            yield FixPriceProductItem(
                title=product.get("title"),
                url=self.base_url_client + product.get("url", "отсутствует url"),
                RPC=product.get("sku"),
                timestamp=int(time()),
                # marketing_tags= TODO
                brand=product.get("brand", {}).get("title", ""),
                # section=
                price_data={"current": current_price, "original": original_price, "sale_tag": sale_tag},
                stock={"in_stock": 1, "count": 1},
            )
