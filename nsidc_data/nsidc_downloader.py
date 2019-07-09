# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import logging
import pickle

# try:
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# except:
#     BASE_DIR = !pwd
#     BASE_DIR = BASE_DIR[0]


def get_sub_dir_path(url=RAW_URL, headers=HEADERS):
    resp = requests.get(url, headers=headers).text
    soup = BeautifulSoup(resp, 'lxml')
    linklst = soup.find_all(class_='indexcolname')
    link_all_day = []
    for i in linklst:
        a = i.find('a').get('href')
        if a[0] == '2':
            link_all_day.append(RAW_URL + a)
    return link_all_day


def parse_daily(url, headers=HEADERS):
    resp = requests.get(url, headers=HEADERS).text
    h5_pattern = re.compile(r'href="(ATL06_201.*?\.h5)"')
    result = re.findall(h5_pattern, resp)
    daily_url_lst = list(set(result))
    daily_full_url_lst = []
    for i_url in daily_url_lst:
        if url[-1] == '/':
            new_url = url + i_url
        else:
            new_url = url + '/' + i_url
        daily_full_url_lst.append(new_url)
    return daily_full_url_lst


def mk_dir(file_path):
    folder = os.path.exists(file_path)
    if not folder:
        os.makedirs(file_path)


def get_all_file_url(link_all_day):
    all_url_list = []
    error_url = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_url = {
            executor.submit(parse_daily, url): url
            for url in link_all_day
        }
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                print('%r page is %d elements' % (url, len(data)))
                if len(data) == 0:
                    print(url)
                    error_url.append(url)
                else:
                    all_url_list.extend(data)
    return all_url_list, error_url


def _sub_downloader(iurl):
    file_nm = iurl.split('/')[-1]
    file_path = os.path.join(BASE_DIR, 'nsidc_data')
    mk_dir(file_path)
    r = requests.get(iurl, stream=True, headers=HEADERS)
    file_to_download = os.path.join(file_path, file_nm)
    with open(file_to_download, "wb") as file:
        for chunk in r.iter_content(chunk_size=1024):  # 1024 bytes
            if chunk:
                file.write(chunk)


def parallel_downloader(all_url_list):
    error_lst = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(_sub_downloader, iurl): iurl
            for iurl in all_url_list
        }
        for future in as_completed(future_to_url):
            iurl = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f'Generated an exception({exc})! **{iurl}**')
                error_lst.append(iurl)
                print("---------------------------------------------------")
            else:
                print(f'Finished with NO EXCEPTION! @@ {iurl} @@')
                print("---------------------------------------------------")
    return error_lst


def main():
    if not os.path.exists(os.path.join(BASE_DIR, 'all_url_list.pkl')):
        logging.info("No pickle file exsitin ... ")
        logging.info("Generating ... ")
        link_all_day = get_sub_dir_path()
        all_url_list, error_url = get_all_file_url(link_all_day)
        if not error_url:
            logging.warning(f"error_url is not none!")
        with open('all_url_list.pkl', 'wb') as f:
            pickle.dump(all_url_list, f)
    logging.info("loading pickle file...")
    with open(os.path.join(BASE_DIR, 'all_url_list.pkl'), 'rb') as f:
        all_url_list = pickle.load(f)
    error_lst = parallel_downloader(all_url_list)
    if not error_lst:
        error_lst2 = parallel_downloader(error_lst)
    if not error_lst2:
        logging.warning("error_lst2 is not none:")
        logging.warning(f"{error_lst2}")


if __name__ == '__main__':
    CookieInfo = "f5_cspm=1234; _ga=GA1.2.1789903767.1557988093; CIsForCookie_OPS=XSQ9S8jdokai31SvASdvsQAAADg; f5avr0039763557aaaaaaaaaaaaaaaa=JBIILLKNBOBNNKKHPKLCMKEDIHJEKABNCKMFLPOKDODJDMLPOIEFKNONINACBPOAJDCCPDFDELAIHKPDJKEAEILOAFDFFECEDHKGHCIJELCHINDDJPELAFJMGFPHFNFG"
    UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    HEADERS = {'Cookie': CookieInfo, 'User-Agent': UserAgent}
    RAW_URL = "https://n5eil01u.ecs.nsidc.org/ATLAS/ATL06.001/"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logging.info(BASE_DIR)
    main()
