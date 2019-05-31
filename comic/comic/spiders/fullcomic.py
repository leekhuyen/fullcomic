# -*- coding: utf-8 -*-
import sys
sys.path.append('../comic_lib')
import scrapy
from model.base import Base
from model.category import Category
from model.chapter import Chapter
from model.comic import Comic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utility.utility import generate_url_name, remove_special_character

engine = create_engine('sqlite:///../fullcomic.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()

class FullcomicSpider(scrapy.Spider):
    name = 'fullcomic'
    allowed_domains = ['truyenfull.vn']
    start_urls = ['https://truyenfull.vn/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 100,
        'DOWNLOAD_DELAY': 0.25
    }

    def parse(self, response):
        for categoryCss in response.css('div.col-md-4 ul li a'):
            next_page = categoryCss.css('::attr(href)').get()
            yield scrapy.Request(next_page, callback=self.parse_category)

    def parse_category(self, response):
        if 'isFirstRequest' not in response.meta:
            name = response.css('ol.breadcrumb h1 a::attr(title)').get()
            description = response.css('div.container div.text-left div.panel-body::text').get()
            if name == 'Trinh Thám':
                description = ''
            if name == 'Tiên Hiệp':
                description = response.css('div.container div.text-left div.panel-body p::text').get()

            if not Category.find_by_name(name, session):
                new_category = Category(name, description)
            else:
                new_category = Category.find_by_name(name, session)
                new_category.name = name
                new_category.description = description
            new_category.save_to_db(session)

        for title in response.css('div.list-truyen h3.truyen-title a'):
            comic_request_url = title.css('::attr(href)').get()
            yield scrapy.Request(comic_request_url, callback=self.parse_comic)

        for pagination in response.css('ul.pagination li'):
            if pagination.css('a span.sr-only') is not None:
                next_page = response.css('a::attr(href)').get()
                next_request = scrapy.Request(next_page, callback=self.parse_category)
                next_request.meta['isFirstRequest'] = 'true'
                yield next_request

    def parse_comic(self, response):
        if 'comic' not in response.meta:
            name = response.css('div.container h3.title::text').get()
            description = ''
            writer = ''
            source = ''
            status = ''
            categories = []
            flag = False
            for des in response.xpath('//div[@class="desc-text"]/*|//div[@class="desc-text"]/text()|\
                                      //div[@class="desc-text desc-text-full"]/*|\
                                      //div[@class="desc-text desc-text-full"]/text()|\
                                      //div[@class="desc-text"]/p/text()|\
                                      //div[@class="desc-text"]/span/text()'):
                if des.xpath('name()').get() is None:
                    if not flag:
                        description += des.get() + '\n'
                elif des.xpath('name()').get() == 'b':
                    flag = True
                elif des.xpath('name()').get() == 'br':
                    if flag:
                        flag = False
            for info in response.css('div.info div'):
                if info.css('h3::text').get() == 'Tác giả:':
                    writer = info.css('a::text').get()
                elif info.css('h3::text').get() == 'Nguồn:':
                    source = info.css('span.source::text').get()
                elif info.css('h3::text').get() == 'Trạng thái:':
                    status = info.css('span::text').get()
                elif info.css('h3::text').get() == 'Thể loại:':
                    for category in info.css('a'):
                        category_name = category.css('::text').get()
                        if Category.find_by_name(category_name, session) is not None:
                            categories.append(Category.find_by_name(category_name, session))

            image_link = response.css('div.book img::attr(src)').get()
            rating_value = 0
            rating_number = 0
            for tmpRating in response.css('div.small strong span'):
                if tmpRating.css('::attr(itemprop)').get() == 'ratingValue':
                    rating_value = tmpRating.css('::text').get()
                elif tmpRating.css('::attr(itemprop)').get() == 'ratingCount':
                    rating_number = tmpRating.css('::text').get()

            if not Comic.find_by_name(name, session):
                new_comic = Comic(name, description, writer, source, status, rating_value, rating_number,\
                                  image_link, generate_url_name(name))
                new_comic.categories = categories
            else:
                new_comic = Comic.find_by_name(name, session)
                new_comic.description = description
                new_comic.writer = writer
                new_comic.source = source
                new_comic.status = status
                new_comic.rating = rating_value
                new_comic.ratingNumber = rating_number
                new_comic.imageLink = image_link
                new_comic.linkName = generate_url_name(name)

            new_comic.save_to_db(session)
        else:
            new_comic = response.meta['comic']

        for chapter in response.css('ul.list-chapter li a::attr(href)'):
            chapter_url = chapter.get()
            chapter_request = scrapy.Request(chapter_url, callback=self.parse_chapter)
            chapter_request.meta['comic'] = new_comic
            yield chapter_request

        for page in response.css('ul.pagination a'):
            if page.css('span.sr-only::text').get() is not None and page.css('span.sr-only::text').get() == 'Trang tiếp':
                next_chapter_list_url = page.css('a::attr(href)').get()
                next_chapter_list_request = scrapy.Request(next_chapter_list_url, callback=self.parse_comic)
                next_chapter_list_request.meta['comic'] = new_comic
                yield  next_chapter_list_request

    def parse_chapter(self, response):
        comic = response.meta['comic']
        if len(response.css('a.chapter-title::text')) == 2:
            book = response.css('a.chapter-title::text')[0].get()
            book = remove_special_character(book)
            book = book.replace(' ', '')

            chapter = response.css('a.chapter-title::text')[1].get()
            index = chapter.find(':')
            if index != -1:
                chapter_number = chapter[0:index]
                chapter_name = chapter[index + 1:len(chapter)]
            else:
                chapter_number = chapter
                chapter_name = ''
        else:
            book = ''
            chapter = response.css('a.chapter-title::text')[0].get()
            index = chapter.find(':')
            if index != -1:
                chapter_number = chapter[0:index]
                chapter_name = chapter[index + 1:len(chapter)]
            else:
                chapter_number = chapter
                chapter_name = ''

        if Chapter.find_by_number(comic.id, chapter_number, session) is None:
            content = ''
            for text in response.css('div.chapter-c::text'):
                content = content + text.get() + '\n'
            content = content[0:len(content) - 1]
            if book:
                nameLink = 'quyen-' + book + "-chuong-"+chapter_number
            else:
                nameLink = "chuong-"+chapter_number
            chapter = Chapter(chapter_number, chapter_name, content, nameLink, book)
            chapter.comic = comic
            chapter.comicId = comic.id
            chapter.save_to_db(session)
