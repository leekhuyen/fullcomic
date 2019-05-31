# -*- coding: utf-8 -*-
import scrapy
import sys
sys.path.append('../comic_lib')
from utility.utility import remove_special_character


class TestComicSpider(scrapy.Spider):
    name = 'test_comic'
    allowed_domains = ['truyenfull.vn']
    start_urls = ['https://truyenfull.vn/niem-tien-quyet/chuong-1/']

    def parse(self, response):
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
            book =''
            chapter = response.css('a.chapter-title::text')[0].get()
            index = chapter.find(':')
            if index != -1:
                chapter_number = chapter[0:index]
                chapter_name = chapter[index + 1:len(chapter)]
            else:
                chapter_number = chapter
                chapter_name = ''

        if book:
            nameLink = 'quyen-' + book + "-chuong-" + chapter_number
        else:
            nameLink = "chuong-" + chapter_number

        print(f'link {nameLink}')
        print(f'chapter {chapter_number}')
        print(f'name {chapter_name}')
