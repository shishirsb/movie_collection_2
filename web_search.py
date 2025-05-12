from selenium import webdriver
from flask import Flask, render_template, url_for,request
from selenium.common import ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from utils.database_connection import DatabaseConnection
import re
from asyncio import gather
# import async_timeout
import time
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, urlunparse
import requests
from playwright.async_api import async_playwright
from concurrent.futures import ThreadPoolExecutor

class WebSearch():
    def __init__(self):
        self.search_results = []
        self.media_info = []
        self.search_results_keywords = []

    def text_box_search_titles_playwrite(self, search_query):
        try:
            async def scrape_imdb():
                async with async_playwright() as p:
                    async with await p.chromium.launch() as browser:
                        page = await browser.new_page()
                        await page.set_extra_http_headers({
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                            "Accept-Language": "en-US,en;q=0.9",
                        })
                        await page.goto(f"https://www.imdb.com/find/?q={search_query}")
                        async def extract_all_titles(page):
                            movie_list = await page.query_selector_all(
                                "section[data-testid='find-results-section-title'] div.ipc-metadata-list-summary-item__tc"
                            )

                            return await asyncio.gather(*[
                                extract_playwright_title(i, el)
                                for i, el in enumerate(movie_list, 1)
                            ])

                        async def extract_playwright_title(index,  element):
                            title_element = await element.query_selector("a.ipc-metadata-list-summary-item__t")
                            details_elements = await element.query_selector_all("span.ipc-metadata-list-summary-item__li")

                            return {
                                'id': index,
                                'title': await title_element.text_content(),
                                'other_details': [await details_elements[0].text_content(), "", "", ""],
                                'url': "https://www.imdb.com" + await title_element.get_attribute('href')
                            }

                        return await extract_all_titles(page)
            return asyncio.run(scrape_imdb())
        except Exception as e:
            print(f"Error while searching movies by Title: {str(e)}")


    def text_box_search_keywords_playwrite(self, search_query):
        try:
            async def scrape_imdb():
                async with async_playwright() as p:
                    async with await p.chromium.launch() as browser:
                        page = await browser.new_page()
                        await page.set_extra_http_headers({
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                            "Accept-Language": "en-US,en;q=0.9",
                        })
                        await page.goto(f"https://www.imdb.com/find/?s=kw&q={search_query}")

                        async def extract_all_keywords(page):
                            keyword_list = await page.query_selector_all(
                                "section[data-testid='find-results-section-keyword'] div.ipc-metadata-list-summary-item__tc"
                            )

                            return await asyncio.gather(*[
                                extract_playwright_keyword(i, el)
                                for i, el in enumerate(keyword_list, 1)
                            ])

                        async def extract_playwright_keyword(index,  element):
                            keyword_element = await element.query_selector("a.ipc-metadata-list-summary-item__t")
                            details_element = await element.query_selector_all("span.ipc-metadata-list-summary-item__li")

                            return {
                                'id': index,
                                'name': await keyword_element.text_content(),
                                'details': [await d.text_content() for d in details_element],
                                'url': "https://www.imdb.com" + await keyword_element.get_attribute('href')
                            }

                        return await extract_all_keywords(page)
            return asyncio.run(scrape_imdb())
        except Exception as e:
            print(f"Error while searching movies by Keyword: {str(e)}")



    def get_movie_titles_for_keyword_playwrite(self, keyword_url):
        try:
            async def scrape_imdb():
                async with (async_playwright() as p):
                    async with await p.chromium.launch() as browser:
                        browser = await p.chromium.launch()
                        page = await browser.new_page()
                        await page.set_extra_http_headers({
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                            "Accept-Language": "en-US,en;q=0.9",
                        })
                        await page.goto(keyword_url + "&title_type=feature&count=250&sort=user_rating,desc")

                        async def extract_all_titles(page):
                            movie_list = await page.query_selector_all(
                                "div.ipc-metadata-list-summary-item__tc"
                            )
                            return await asyncio.gather(*[
                                extract_playwright_title(i, el)
                                for i, el in enumerate(movie_list, 1)
                            ])

                        async def extract_playwright_title(index,  element):
                            try:
                                title_element = await element.query_selector("a.ipc-title-link-wrapper")
                                details_element_list = await element.query_selector_all('span[class*="title-metadata-item"]')
                                rating_element = await element.query_selector('span.ipc-rating-star--rating')
                                other_details = [await d.text_content()
                                                 for d in details_element_list] if details_element_list else []
                                other_details = other_details + [""] * (3 - len(other_details))
                                if rating_element:
                                    other_details.append(await rating_element.text_content())

                                return {
                                    'id': index,
                                    'title': (await title_element.text_content()).split('. ', 1)[1],
                                    'other_details': other_details,
                                    'url': "https://www.imdb.com" + await title_element.get_attribute('href')
                                }
                            except Exception as e:
                                print(f"Error inside extract_playwright_title function: {str(e)}")

                        return await extract_all_titles(page)
            return asyncio.run(scrape_imdb())
        except Exception as e:
            print(f"Error when Search button is clicked: {str(e)}")



    def get_media_info_playwrite(self, movie):
        try:
            async def scrape_imdb():
                async with async_playwright() as p:
                    async with await p.chromium.launch() as browser:
                        browser = await p.chromium.launch()
                        context = await browser.new_context(
                            extra_http_headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                                "Accept-Language": "en-US,en;q=0.9"
                            }
                        )
                        async def extract_all_data(context):
                            return await asyncio.gather(*[
                                get_data(context, "images"),
                                get_data(context, "summary"),
                                get_data(context, "synopsis"),
                                get_data(context, "violence"),
                                get_data(context, "frightening"),
                                get_data(context, "parentalguide")
                            ])

                        async def get_data(context, option):
                            if option == "images":
                                return await self.get_img_urls(context, movie)
                            elif option == "summary":
                                return await self.get_summary(context, movie)
                            elif option == "synopsis":
                                return await self.get_synopsis(context, movie)
                            elif option == "violence":
                                return await self.get_violent_scenes_information(context, movie)
                            elif option == "frightening":
                                return await self.get_frightening_scenes_information(context, movie)
                            elif option == "parentalguide":
                                return await self.get_parentalguide_information(context, movie)
                        results = await extract_all_data(context)
                        return {'id': movie['id'], 'title': movie['title'], 'summaries': results[1], 'img_urls': results[0] , 'synopsis': results[2], 'parentalguide': results[5], 'violence': results[3], 'frightening': results[4]}
            return asyncio.run(scrape_imdb())
        except Exception as e:
            print(f"Error while extracting media data: {str(e)}")



    async def get_img_urls(self, context, movie):
        images_page = await context.new_page()  # New tab
        await images_page.goto(self.modify_imdb_url(movie['url'], 'mediaindex'))
        img_elements = await images_page.query_selector_all('img[data-testid="image-gallery-image"]')
        return [await img_element.get_attribute('src') for img_element in img_elements] if img_elements else [
            "No images available"]



    async def get_summary(self, context, movie):
        summary_page = await context.new_page()  # New tab
        await summary_page.goto(self.modify_imdb_url(movie['url'], 'plotsummary'))
        summary_elements = await summary_page.query_selector_all(
            "div[data-testid='sub-section-summaries'] div.ipc-html-content-inner-div div.ipc-html-content-inner-div")
        return [await summary_element.text_content() for summary_element in summary_elements] if summary_elements else [
            "No summaries available"]



    async def get_synopsis(self, context, movie):
        synopsis_page = await context.new_page()  # New tab
        await synopsis_page.goto(self.modify_imdb_url(movie['url'], 'plotsummary/#synopsis'))
        synopsis_elements = await synopsis_page.query_selector_all(
            "div[data-testid='sub-section-synopsis'] div.ipc-html-content-inner-div div.ipc-html-content-inner-div")
        return [re.sub(r'\.([A-Z])', r'.<br><br>\1', await synopsis_element.text_content()) for synopsis_element in
                synopsis_elements] if synopsis_elements else ["No synopsis available"]



    async def get_violent_scenes_information(self, context, movie):
        violence_page = await context.new_page()  # New tab
        await violence_page.goto(self.modify_imdb_url(movie['url'], 'parentalguide/#violence'))
        violence_elements = await violence_page.query_selector_all(
            "div[data-testid='sub-section-violence'] div.ipc-html-content-inner-div")
        return [await violence_element.text_content() for violence_element in
                violence_elements] if violence_elements else ["No information available"]



    async def get_frightening_scenes_information(self, context, movie):
        frightening_page = await context.new_page()  # New tab
        await frightening_page.goto(self.modify_imdb_url(movie['url'], 'parentalguide/#frightening'))
        frightening_elements = await frightening_page.query_selector_all(
            "div[data-testid='sub-section-frightening'] div.ipc-html-content-inner-div")
        return [await frightening_element.text_content() for frightening_element in
                frightening_elements] if frightening_elements else ["No information available"]



    async def get_parentalguide_information(self, context, movie):
        parentalguide_page = await context.new_page()  # New tab
        await parentalguide_page.goto(self.modify_imdb_url(movie['url'], 'parentalguide/#nudity'))
        parentalguide_elements = await parentalguide_page.query_selector_all(
            "div[data-testid='sub-section-nudity'] div.ipc-html-content-inner-div")
        return [await parentalguide_element.text_content() for parentalguide_element in
                parentalguide_elements] if parentalguide_elements else ["No information available"]


    def modify_imdb_url(self, url, page_name):
        try:
            """
            This function takes an IMDb URL and modifies it to include 'plotsummary/' after the title ID.
            """
            parsed = urlparse(url)
            # Insert 'plotsummary/' after the title ID
            new_path = parsed.path.rstrip('/') + f'/{page_name}/'
            # Reconstruct the full URL
            new_url = urlunparse(parsed._replace(path=new_path))
            return new_url
        except Exception as e:
            print(f"Exception while modifying url {url}")
















