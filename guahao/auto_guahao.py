import os
import time
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(BASE_DIR)
    print(os.chdir(BASE_DIR))
except:
    pass
import sys
sys.path.append('..')
from crawler_base.base import BaseCrawler
import logging
from pyquery import PyQuery as pq
from config.browser_config import chrome_options


class Auto_114(BaseCrawler):
    def __init__(self,
                 target_url,
                 cookie_nm='cookie_default',
                 chrome_options=None):
        super().__init__(
            target_url, cookie_nm=cookie_nm, chrome_options=chrome_options)

    def __show_info(self, hospital_department, available_date):
        logging.info(hospital_department)
        if not available_date:
            logging.info("No available registration for the coming 7 days!")
        else:
            for ava in available_date:
                logging.info(ava)

    def parse_html(self):
        browser = self.auto_login()
        time.sleep(2)
        self.html_raw = browser.page_source
        doc = pq(self.html_raw)
        a = doc.find('.sourceNoShow').find('li').items()
        available_date = []
        hospital_department = doc.find('.ksorder_box_top_p').text()
        #         print(hospital_department)
        for il in a:
            if il.attr['class'] != 'full':  # 有号是''（空字符串）
                #         print(il.attr['data-id'])
                available_date.append(il.text())
        self.__show_info(hospital_department, available_date)


if __name__ == '__main__':

    url_1 = 'http://www.114yygh.com/dpt/appoints/91,NFM.htm?departmentName=%E5%86%85%E5%88%86%E6%B3%8C%E7%A7%91&deptSpec=%E5%86%85%E5%88%86%E6%B3%8C%E3%80%81%E7%B3%96%E5%B0%BF%E7%97%85%E3%80%81%E7%94%B2%E7%8A%B6%E8%85%BA'
    url_2 = 'http://www.114yygh.com/dpt/appoints/91,JZX.htm?departmentName=%E7%94%B2%E7%8A%B6%E8%85%BA%E9%A2%88%E9%83%A8%E5%A4%96%E7%A7%91&deptSpec=%E7%94%B2%E7%8A%B6%E8%85%BA%E3%80%81%E7%94%B2%E7%8A%B6%E6%97%81%E8%85%BA%E6%B6%8E%E8%85%BA%E8%82%BF%E7%98%A4'
    auto_114 = Auto_114(target_url=url_1, chrome_options=chrome_options)
    browser = auto_114.parse_html()
