import datetime
import re

import scrapy
from scrapy.exceptions import CloseSpider

from scrapy.loader import ItemLoader

from ..items import CrcentoitItem
from itemloaders.processors import TakeFirst

base = 'https://www.crcento.it/ajax.htm?v_ajax_esegui=COMUNICATILISTA&v_input_comunicati_anno={}'

class CrcentoitSpider(scrapy.Spider):
	name = 'crcentoit'
	year = 2012
	start_urls = [base.format(year)]

	def parse(self, response):
		post_links = response.xpath('//a/@onclick').getall()
		for post in post_links:
			_id = re.findall(r'[A-Z]_\d+', post)[0]
			url = f'https://www.crcento.it/ajax.htm?v_ajax_esegui=NEWSCOMUNICATIVIEW&v_news_comunicati_view={_id}'
			yield response.follow(url, self.parse_post)

		if post_links:
			self.year += 1
			yield response.follow(base.format(self.year), self.parse)

	def parse_post(self, response):
		title = response.xpath('//div[@class="FrutigerNeueMedium_18 color_green align_left"]//text()').get()
		description = response.xpath('//div[@class="proximanova_16_light line_height_20"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		try:
			date = re.findall(r'\d{1,2}\s[a-z]{3,}\s\d{4}', description)[0]
		except:
			date = ''

		item = ItemLoader(item=CrcentoitItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
