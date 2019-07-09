"""
NEXT:
add md5 to avoid duplicated downloading...
"""

import time
import pickle
import re
import os
import logging
logging.basicConfig(level=logging.INFO)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.info(BASE_DIR)
import sys
sys.path.append(BASE_DIR)
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
from config.browser_config import chrome_options


fuxiao = 'https://500px.me/fuxiao718'
jkt = 'https://500px.me/community/user-details/e914f856b4b3f9d7dc9c82dfaac033703'
tms = 'https://500px.me/community/user-details/e0fca793f468a98473a1e86284aff4612'
lian = 'https://500px.me/community/user-details/1351a0c0e4c199afcbe9ff48d579d2047'
xiaokai = 'https://500px.me/community/user-details/7228ae6fd4cf2b0436b43bbf3a4da1423'
bother = 'https://500px.me/zhangqibot'

cookie_bo = 'cookies_500px_bother.pkl'
cookie_lz = 'cookies_500px_lukezhang.pkl'
zdk = 'https://500px.me/community/user-details/b122fef8a4d34865573287edd1f3f1137'


class Crawler_500px(object):
    def __init__(self,
                 target_url,
                 use_cookie=cookie_bo,
                 userID='ANONYMOUS',
                 chrome_options=None):
        self.target_url = target_url
        self.use_cookie = use_cookie
        try:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        except:
            self.base_dir = os.getcwd()
        self.cookie_path = os.path.join(self.base_dir, self.use_cookie)
        self.userID = userID
        self.chrome_options = chrome_options

    def mk_dir(self, file_path):
        folder = os.path.exists(file_path)
        if not folder:
            os.makedirs(file_path)

    def _progress_bar(self, total):
        _output = sys.stdout
        for count in range(0, total + 1):
            _second = 0.1
            time.sleep(_second)
            now_progress = count / total * 100
            _output.write(f'\rcomplete percent: {now_progress:.1f}%')
        _output.flush()

    def generate_cookie(self):
        browser = webdriver.Chrome()
        browser.get(self.target_url)
        cookies2 = browser.get_cookies()
        #         print(cookies2)
        browser.delete_all_cookies()  # delete all cookies
        print(
            "ENTER YOUR USERID AND PASSWORD... COOKIES WILL BE SAVED IN 60s ..."
        )
        time.sleep(60)  # unfinished... add condition to auto process
        # enter your passwd and UserID manually ...
        cookies = browser.get_cookies()
        with open(self.cookie_path, 'wb') as f:
            pickle.dump(cookies, f)

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
        return browser

    def auto_like(self):
        browser = self.auto_login()
        last_height = browser.execute_script(
            "return document.body.scrollHeight")
        time.sleep(1)
        while True:
            browser.execute_script(
                'document.body.scrollTop = document.documentElement.scrollTop = 9999999999999'
            )
            time.sleep(1)
            new_height = browser.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        all_like_button = browser.find_elements_by_class_name('like-button')
        for like_bt in all_like_button:
            try:
                flag = like_bt.find_element_by_class_name(
                    'button').get_attribute('class')
                if 'liked' not in flag:
                    like_bt.click()
            except Exception as exc:
                print(f"Error: {exc}")
        browser.close()
        logging.info('Auto like finished!')

    def get_url_lst(self):
        browser = self.auto_login()
        last_height = browser.execute_script(
            "return document.body.scrollHeight")
        time.sleep(1)
        while True:
            browser.execute_script(
                'document.body.scrollTop = document.documentElement.scrollTop = 9999999999999'
            )
            time.sleep(1)
            new_height = browser.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        src = browser.page_source
        pattern = r'https://img\.500px\.me/photo/[0-9a-zA-Z/]+\.jpg!p4'
        all_foto_lst = re.findall(pattern, src, re.S)
        browser.close()
        return all_foto_lst

    def _sub_downloader(self, iurl):

        if '.jpg!p5' in iurl:
            p5p7 = 'p5'
        elif '.jpg!p7' in iurl:
            p5p7 = 'p7'
        else:
            raise ValueError(f"Only p5 and p7 are supportable, got {iurl}")

        file_path = os.path.join(self.base_dir, '500px_fotos', self.userID,
                                 p5p7)
        self.mk_dir(file_path)
        r = requests.get(iurl, stream=True)
        file_name = str(time.time()).replace('.', '_') + \
            str(random.randint(0, 99999999)).zfill(8)+'.jpg'
        logging.info(f"{self.userID}/{p5p7} downloading...")
        file_to_download = os.path.join(file_path, file_name)
        with open(file_to_download, "wb") as file:
            for chunk in r.iter_content(chunk_size=1024):  # 1024 bytes
                if chunk:
                    file.write(chunk)

    def parallel_downloader(self, url_lst):
        error_lst = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(self._sub_downloader, iurl): iurl
                for iurl in url_lst
            }
            for future in as_completed(future_to_url):
                iurl = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    logging.info(f'Generated an exception({exc})! **{iurl}**')
                    error_lst.append(iurl)
                    logging.info(
                        "---------------------------------------------------")
                else:
                    logging.info(f'Finished with NO EXCEPTION! @@ {iurl} @@')
                    logging.info(
                        "---------------------------------------------------")
        self.error_lst = error_lst

    def downloader(self):
        p4_lst = self.get_url_lst()
        p5_lst = [iurl.replace('!p4', '!p5') for iurl in p4_lst]
        p7_lst = [iurl.replace('!p4', '!p7') for iurl in p4_lst]
        p5p7_lst = p5_lst + p7_lst
        self.parallel_downloader(url_lst=p5p7_lst)

        if self.error_lst:
            logging.warning(
                f"Error existing in {self.error_lst}, will be tried again...")
            self.parallel_downloader(url_lst=self.error_lst)
        else:
            logging.info("All pics successfully downloaded!")

    def add_pageview(self):
        browser = self.auto_login()
        while True:
            browser.refresh()
            # slp_time = random.random() + random.randint(0, 2)
            slp_time = random.random()
            time.sleep(slp_time)
        browser.close()

if __name__ == '__main__':
    cpx = Crawler_500px(
        target_url=bother,
        use_cookie=cookie_lz,
        userID='bother',
        chrome_options=chrome_options)
    #     cpx.auto_like()
    # cpx.auto_like()
    cpx.add_pageview()
