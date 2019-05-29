import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle


class Downloader(object):
    def __init__(self, dict_0=None, url_info_lst=None):
        self.dict_0 = dict_0
        if url_info_lst is not None:
            self.url_info_lst = url_info_lst
        else:
            self.dict2list()

    def dict2list(self):
        """ for parallel computing """
        url_info_lst = []
        for topic, sub_topic_dict in self.dict_0.items():
            for sub_topic_nm, sub_topic_lst in sub_topic_dict.items():
                for iurl in sub_topic_lst:
                    if not iurl.startswith('https://'):
                        print(topic, ' || ', sub_topic_nm, ' || ', iurl)
                    else:
                        info_tuple = (topic, sub_topic_nm, iurl)
                        url_info_lst.append(info_tuple)
        self.url_info_lst = url_info_lst
        return url_info_lst

    def mk_dir(self, file_path):
        folder = os.path.exists(file_path)
        if not folder:
            os.makedirs(file_path)

    def _sub_downloader(self, info_tuple):

        topic, sub_topic_nm, iurl = info_tuple
        file_path = os.path.join(BASE_DIR, 'tableau_tutorials', topic,
                                 sub_topic_nm)
        self.mk_dir(file_path)
        r = requests.get(iurl, stream=True)
        if '.mp4' in iurl:  # or 'videoId' in iurl):
            file_nm = '%s.mp4' % sub_topic_nm
        else:
            file_nm = iurl.split('/')[-1]
#         try:
        print(f"{topic}/{sub_topic_nm} downloading...")
        file_to_download = os.path.join(file_path, file_nm)
        with open(file_to_download, "wb") as file:
            for chunk in r.iter_content(chunk_size=1024):  # 1024 bytes
                if chunk:
                    file.write(chunk)


#         except Exception as e:
#             print(f"{topic}/{sub_topic_nm} downloading failed ...{e}")
#             self.error_files.append(info_tuple)

    def parallel_downloader(self):
        error_lst = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(self._sub_downloader, url_tuple): url_tuple
                for url_tuple in self.url_info_lst
            }
            for future in as_completed(future_to_url):
                url_tuple = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print(f'Generated an exception({exc})! **{url_tuple}**')
                    error_lst.append(url_tuple)
                    print(
                        "---------------------------------------------------")
                else:
                    print(f'Finished with NO EXCEPTION! @@ {url_tuple} @@')
                    print(
                        "---------------------------------------------------")
        self.error_lst = error_lst

if __name__ == '__main__':
    # BASE_DIR = os.getcwd()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(BASE_DIR)
    dict_0 = pickle.load(open(os.path.join(BASE_DIR, "tableau.pkl"), "rb"))
    DLD = Downloader(dict_0=dict_0, url_info_lst=None)
    DLD.parallel_downloader()
