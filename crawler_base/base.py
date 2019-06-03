import time
import pickle
import re
import os
import sys
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from selenium import webdriver

import logging
logging.basicConfig(level=logging.INFO)


class BaseCrawler(object):
    def __init__(self,
                 target_url,
                 cookie_nm='cookie_default',
                 chrome_options=None):
        self.__get_base_dir()
        self.chrome_options = chrome_options
        self.cookie_nm = cookie_nm
        self.cookie_path = os.path.join(self.base_dir,
                                        '%s.pkl' % self.cookie_nm)

    def __get_base_dir(self):
        try:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        except:
            self.base_dir = os.getcwd()

    def __mk_dir(self, file_path):
        folder = os.path.exists(file_path)
        if not folder:
            os.makedirs(file_path)

    def generate_cookie(self):
        logging.info("No Cookies! It will be generated ...")
        browser = webdriver.Chrome()
        browser.get(self.target_url)
        cookies2 = browser.get_cookies()
        #         print(cookies2)
        browser.delete_all_cookies()  # delete all cookies
        logging.info(
            "ENTER YOUR USERID AND PASSWORD... COOKIES WILL BE SAVED IN 40s ..."
        )
        time.sleep(40)  # unfinished... add condition to auto process
        # enter your passwd and UserID manually ...
        cookies = browser.get_cookies()
        with open(self.cookie_path, 'wb') as f:
            pickle.dump(cookies, f)
        logging.info("Successfully dump cookies!")

    def auto_login(self):

        try:
            cookies = pickle.load(open(self.cookie_path, "rb"))
        except:
            self.generate_cookie()
            cookies = pickle.load(open(self.cookie_path, "rb"))
        browser = webdriver.Chrome(options=self.chrome_options)
        browser.get(self.target_url)
        for cookie in cookies:
            browser.add_cookie(cookie)
        browser.get(self.target_url)
        #         browser.implicsitly_wait(30)
        logging.info("Successfully login!")

        return browser
