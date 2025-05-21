from collections.abc import Iterable
from urllib.parse import urljoin
import json
import scrapy
from scrapy.http import Request
from fixprice.items import FixPriceProductItem
from typing import Generator
from time import time

class CategorySpider(scrapy.Spider):
    name = "categories"
    start_urls = [
        "https://fix-price.com/catalog/kosmetika-i-gigiena/ukhod-za-polostyu-rta",
        "https://fix-price.com/catalog/igrushki",
        "https://fix-price.com/catalog/produkty-i-napitki/zakuski",
    ]
    base_url_client = "https://fix-price.com/"
    base_api_url = "https://api.fix-price.com/buyer/v1/product/in/"
    default_params = {
        "page": 1,
        "limit": 24,
        "sort": "sold",
    }
    default_headers = {
        "x-city": 809,
        "x-language": "ru",
    }

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            category_slug = url.split("/catalog/")[-1]
            url = urljoin(self.base_api_url, category_slug)
            yield Request(url, callback=self.parse)

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
