from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pickle
import os

# from selenium.webdriver.common.keys import Keys
chrome_options = Options()
# chrome_options.headless = True
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')  # for Windows OS ...
chrome_options.add_argument("--mute-audio")

base_url = 'http://www.dianping.com/'
target_url = 'http://www.dianping.com/shop/110605626'

class DianPing(object):

    def __init__(self, target_url, use_cookie='cookies_bother_dp',chrome_options=None):
        self.target_url = target_url
        self.use_cookie = use_cookie
        self.chrome_options = chrome_options
        try:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        except:
            self.base_dir = os.getcwd()
        self.file_path = os.path.join(self.base_dir, f"{self.use_cookie}.pkl")


    def generate_cookie(self):
        browser = webdriver.Chrome()
        browser.get(self.target_url)
        cookies2 = browser.get_cookies()
        browser.delete_all_cookies()  # delete all cookies
        print(
            "ENTER YOUR USERID AND PASSWORD... COOKIES WILL BE SAVED IN 40s ..."
        )
        time.sleep(40)  # unfinished... add condition to auto process
        # enter your passwd and UserID manually ...
        cookies = browser.get_cookies()
        with open(self.file_path, 'wb') as f:
            pickle.dump(cookies, f)

    def auto_login(self):
        try:
            cookies = pickle.load(open(self.file_path, "rb"))
        except:
            self.generate_cookie()
            cookies = pickle.load(open(self.file_path, "rb"))
        browser = webdriver.Chrome(options=self.chrome_options)
        browser.get(self.target_url)
        time.sleep(1)
        for cookie in cookies:
            browser.add_cookie(cookie)
        time.sleep(1)
        browser.get(self.target_url)
        #         browser.implicsitly_wait(30)
        return browser

    def auto_likeBadComments(self):
        browser = self.auto_login()
        time.sleep(2)
        browser.get(target_url)
        
        return browser
#         time.sleep(60)


if __name__ == '__main__':
    dp = DianPing(target_url=base_url, use_cookie='cookies_bother_dp', chrome_options=None)
    brower = dp.auto_likeBadComments()
