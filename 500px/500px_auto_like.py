from selenium import webdriver
import time
import pickle

url_test = 'https://500px.me/fuxiao718'

def generate_cookie(url_test):
    browser = webdriver.Chrome()
    browser.get(url_test)
    # src = browser.page_source
    cookies2 = browser.get_cookies()
    print(cookies2)
    browser.delete_all_cookies()  # delete all cookies
    time.sleep(20)  # unfinished... add condition to auto process
    # 手动登录之后执行：
    cookies = browser.get_cookies()
    with open("cookies.pkl", 'wb') as f:
        pickle.dump(cookies, f)

def auto_login(url_test):
    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
    except:
        generate_cookie()
    browser = webdriver.Chrome()
    browser.get(url_test)
    for cookie in cookies:
        browser.add_cookie(cookie)
    browser.get(url_test)
    src = browser.page_source
    # browser.close()

    time.sleep(60)
    return src

if __name__ == '__main__':
    # generate_cookie(url_test)
    auto_login(url_test)
