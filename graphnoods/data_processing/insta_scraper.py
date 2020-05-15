import json
import os
import urllib.request

import PIL
import requests
from bs4 import BeautifulSoup as bs
from PIL import Image

import matplotlib.pyplot as plt
from natebbcommon.logger import initialise_logger
from natebbwebcapture.webdriver_firefox import WebdriverFirefox
from webdriver_utils.common import timed_scroll
from config.webdriver_config import WebdriverConfig


class InstagramScraper:
    def __init__(self, config):
        self.config = config
        self.webdriver = WebdriverFirefox(
            page_load_timeout=config.page_load_timeout,
            browser_emulation=config.browser_emulation,
            viewport_size_h_w=config.viewport_size_h_w,
            headless=config.headless,
        )
        self.scroll_time = config.scroll_time
        self.scroll_pause_time = config.scroll_pause_time
        self.ins_explore_url = 'https://www.instagram.com/explore'
        self.image_save_path = './'

    def extract_links_of_posts_by_tag(self, hashtag='food'):
        self.webdriver.get(os.path.join(self.ins_explore_url, 'tags', hashtag))

        if self.scroll_time:
            timed_scroll(self.webdriver.driver, self.scroll_time, self.scroll_pause_time)

        url_shortcodes = []
        dom_string = self.webdriver.driver.page_source  # obtain DOM
        soup = bs(dom_string, 'html.parser')
        body = soup.find('body')
        script = body.find('script', text=lambda t: t.startswith('window._sharedData'))
        page_json = script.contents[0].split(' = ', 1)[1].replace(';', '')
        soup = json.loads(page_json)

        # Find elements by x-path maybe?
        for url in soup['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']:
            url_shortcodes.append(url['node']['shortcode'])

        print('Extracted {} post shortcodes for hashtag:{}'.format(len(url_shortcodes), hashtag))

        return url_shortcodes

    def save_images_by_url(self, list_url_shortcodes, image_save_path='./'):
        for short_code in list_url_shortcodes:
            image_url = os.path.join(self.ins_explore_url, 'p', short_code, 'media/?size=m')
            try:
                image = Image.open(requests.get(image_url, stream=True).raw)
                image.save(os.path.join(image_save_path + "{}.jpg".format(short_code)))
            except PIL.UnidentifiedImageError:
                print('Cannot load image for shortcode:{}'.format(short_code))


    def scrap_caption_by_url(self):
        pass

    def scrap_hashtags_by_url(self):
        pass

    def display_images_from_short_code(self, short_code, size='m'):
        assert size in ['s','m','l']
        image_url = os.path.join(self.ins_explore_url, 'p', short_code, 'media/?size={}'.format())
        image = Image.open(urllib.request.urlopen(image_url))
        image.show()

    def finish_extraction(self):
        # Maybe produce some sort of summary
        self.webdriver.driver.close()


if __name__ == '__main__':
    root_logger = initialise_logger()
    hashtag = 'food'
    ins_scraper = InstagramScraper(config=WebdriverConfig())
    url_shortcodes = ins_scraper.extract_links_of_posts_by_tag(hashtag)
    ins_scraper.display_images_from_short_code(url_shortcodes[0])
