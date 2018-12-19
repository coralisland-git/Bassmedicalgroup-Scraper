# from __future__ import unicode_literals
import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from chainxy.items import ChainItem

from scrapy import signals

from scrapy.xlib.pydispatch import dispatcher

from selenium import webdriver

from lxml import etree

from lxml import html

import time

import pdb


class bassmedicalgroup(scrapy.Spider):

	name = 'bassmedicalgroup'

	domain = 'https://www.bassmedicalgroup.com'

	history = []

	output = []

	def __init__(self):

		pass

	
	def start_requests(self):

		url = "https://www.bassmedicalgroup.com/our-doctors/?showall=1"

		yield scrapy.Request(url, callback=self.parse)
		

	def parse(self, response):

		doctor_list = response.xpath('//table[@class="table searchTable"]//tr')

		for doctor in doctor_list[1:]:

			link = doctor.xpath('.//td[1]//a[1]/@href').extract_first()

			yield scrapy.Request(link, callback=self.parse_detail)


	def parse_detail(self, response):

		item = ChainItem()

		detail = response.xpath('//div[contains(@class, "postContent")]')

		item['name'] = self.validate(detail.xpath('//h1//text()').extract_first())

		item['avatar'] = self.validate(detail.xpath('//div[@id="doctorContactInfo"]//img/@src').extract_first())

		item['description'] = self.validate('\n'.join(self.eliminate_space(detail.xpath('//div[@class="entry"]//p//text()').extract())))

		more_detail = detail.xpath('//div[@class="entry"]//div[@id="accordion"]//div[@class="card"]')

		if more_detail:

			for more in more_detail:

				temp = ''

				data = self.eliminate_space(more.xpath('.//div[contains(@class, "collapse")]//text()').extract())

				for dat in data:

					temp += dat

					if ':' not in dat:

						temp += ', '

				temp = self.validate(temp[:-2])

				if 'education' in ''.join(more.xpath('.//div[@class="card-header"]//text()').extract()).lower():

					item['education'] = temp

				if 'affiliation' in ''.join(more.xpath('.//div[@class="card-header"]//text()').extract()).lower():

					item['affiliation'] = temp

		item['specialty'] = self.validate(', '.join(self.eliminate_space(response.xpath('//div[@class="info_wrapper"]//ul[1]//text()').extract())))

		location_list = response.xpath('//div[@class="info_wrapper"]//ul[@id="locations-list"]//li')

		locations = ''

		for location in location_list:

			locations += ' '.join(self.eliminate_space(location.xpath('.//text()').extract())) + ' | '

		item['locations'] = self.validate(locations[:-2])

		item['website'] = self.validate(', '.join(self.eliminate_space(response.xpath('//div[@class="info_wrapper"]//ul')[-1].xpath('.//text()').extract())))

		yield item


	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t','').replace('\r', '').strip().encode('ascii','ignore')

		except:

			pass


	def eliminate_space(self, items):

	    tmp = []

	    for item in items:

	        if self.validate(item) != '':

	            tmp.append(self.validate(item))

	    return tmp