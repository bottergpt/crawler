from selenium import webdriver
from bs4 import BeautifulSoup
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
# chrome_options.headless = True
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')  # for Windows OS ...
chrome_options.add_argument("--mute-audio")

class CrawlTableau(object):
    def __init__(self, url_lst):
        try:
            self.url_lst = url_lst
            if not url_lst:
                raise
        except:
            self.get_all_url()
        self.dict_all = {}
        self.url_test = url_test = 'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/distributing-and-publishing?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=getting_started'

    def get_all_url(self):
        url_all = []
        base_url = 'https://www.tableau.com/zh-cn/learn/training'
        browser = webdriver.Chrome()
        browser.get(base_url)
        src_0 = browser.page_source
        browser.close()
        soup = BeautifulSoup(src_0, 'lxml')
        for class_doc in soup.find_all(class_='accordion__item'):
            for link in class_doc.find_all('a'):
                url = link.get('href')
                if url is not None:
                    url_all.append(url)
        a = []
        for i in soup.find_all(class_='text--label'):
            if '视频' in i.text:
                a.append(int(i.text[:-2]))
        assert len(url_all) == sum(a)
        self.url_lst = url_all

    def generate_cookie(self):
        browser = webdriver.Chrome()
        browser.get(self.url_test)
        # src = browser.page_source
        cookies2 = browser.get_cookies()
        print(cookies2)
        browser.delete_all_cookies()  # delete all cookies
        time.sleep(20)  # unfinished... add condition to auto process
        # 手动登录之后执行：
        cookies = browser.get_cookies()
        with open("../test/cookies.pkl", 'wb') as f:
            pickle.dump(cookies, f)

    def get_src(self, url_test):
        try:
            cookies = pickle.load(open("../test/cookies.pkl", "rb"))
        except:
            self.generate_cookie()

        browser = webdriver.Chrome(options=chrome_options)
        browser.get(url_test)
        for cookie in cookies:
            browser.add_cookie(cookie)
        browser.get(url_test)
        try:
            # 点击播放视频：
            bt = browser.find_element_by_css_selector('#edit-gain-access')
            bt.click()
        except:
            pass
        finally:
            # 获得源码
            src = browser.page_source
            browser.close()

        return src

    def get_download_link(self, src):
        soup = BeautifulSoup(src, 'lxml')
        sub_link_all = []
        for link in soup.find_all(
                class_='mp4-download-link link link--download'):
            sub_link_all.append(link.get('href'))
        nb_pdf_link = []
        for link in soup.find_all(class_='link link--download'):
            sub_link_all.append(link.get('href'))

        topic_str = soup.find_all(
            class_="video-playlist-sidebar__topic")[0].string.strip()
        sub_topic_str = soup.find_all('h4')[0].string
        if topic_str in self.dict_all:
            self.dict_all[topic_str][sub_topic_str] = sub_link_all
        else:
            dict_sub = {}
            dict_sub[sub_topic_str] = sub_link_all
            self.dict_all[topic_str] = dict_sub

    def _wrapper_for_parellel(self, url):
        src = self.get_src(url)
        self.get_download_link(src)

    def get_all_download_link(self):
        error_lst = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(self._wrapper_for_parellel, url): url
                for url in self.url_lst
            }
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
                    error_lst.append(url)
                else:
                    print('%r page finished with NO EXCEPTION! ' % url)
        self.error_lst = error_lst

    @staticmethod
    def test():
        url_test = 'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/input-step?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=tableau_prep'
        try:
            cookies = pickle.load(open("../test/cookies.pkl", "rb"))
        except:
            self.generate_cookie()
        browser = webdriver.Chrome()
        browser.get(url_test)
        for cookie in cookies:
            browser.add_cookie(cookie)
        browser.get(url_test)
        try:
            # 点击播放视频：
            bt = browser.find_element_by_css_selector('#edit-gain-access')
            bt.click()
        except:
            pass
        finally:
            # 获得源码
            src = browser.page_source
            browser.close()
        soup = BeautifulSoup(src, 'lxml')
        sub_link_all = []
        for link in soup.find_all(
                class_='mp4-download-link link link--download'):
            sub_link_all.append(link.get('href'))


if __name__ == '__main__':
    # url_all = pickle.load(open("../test/url_all.pkl", "rb"))
    CT = CrawlTableau(url_lst=None)
    CT.get_all_download_link()
    dict_0 = CT.dict_all
    error_lst = CT.error_lst
    if not error_lst:
        CT2 = CrawlTableau(url_lst=error_lst)
        CT2.get_all_download_link()
        dict_1 = CT2.dict_all
#     error_lst2 = CT2.error_lst  # for further checking

    for topic, sub_topic_dict in dict_1.items():
        if topic in dict_0:
            for kv, vv in sub_topic_dict.items():
                dict_0[sub_topic_dict][kv] = vv
        else:
            dict_0[topic] = sub_topic_dict

    # check dict_0: if there are some useless urls existing..
    for topic, sub_topic_dict in dict_0.items():
        for sub_topic_nm, sub_topic_lst in sub_topic_dict.items():
            for iurl in sub_topic_lst:
                if not iurl.startswith('https://'):
                    print(topic, ' || ', sub_topic_nm, ' || ', iurl)

    # add manully ... (for further improvement)
    fault_url_lst = [
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/input-step?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=tableau_prep',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/cleaning-step?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=tableau_prep',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/managing-metadata?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=connecting_data',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/managing-extracts?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=connecting_data',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/parameters?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=visual_analytics',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/working-sets?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=visual_analytics',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/additional-filtering-topics?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=visual_analytics',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/intro-table-calculations?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=calculations',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/cloned-filtering-top-across-panes?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=why_tableau_doing',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/using-parameter-change-fields?product=tableau_desktop%2Btableau_prep&version=10_0%2Btableau_prep_2018_1_1&topic=how',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/interacting-content-tableau-online?product=tableau_server%2Btableau_online&version=10_0%2Btableau_prep_2018_1_1&topic=collaborate_tableau_online',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/navigating-tableau-mobile-app?product=tableau_server%2Btableau_online&version=10_0%2Btableau_prep_2018_1_1&topic=collaborate_tableau_online',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/web-authoring-online-10?product=tableau_server%2Btableau_online&version=10_0%2Btableau_prep_2018_1_1&topic=collaborate_tableau_online',
        'https://www.tableau.com/zh-cn/learn/tutorials/on-demand/interacting-content-tableau-mobile-app?product=tableau_server%2Btableau_online&version=10_0%2Btableau_prep_2018_1_1&topic=collaborate_tableau_online'
    ]

    CT3 = CrawlTableau(url_lst=fault_url_lst)
    CT3.get_all_download_link()

    dict_3 = CT3.dict_all

    for topic, sub_topic_dict in dict_3.items():
        if topic in dict_0:
            for kv, vv in sub_topic_dict.items():
                dict_0[sub_topic_dict][kv] = vv
        else:
            dict_0[topic] = sub_topic_dict

    with open('tableau.pkl', 'wb') as f:
        pickle.dump(dict_0, f)