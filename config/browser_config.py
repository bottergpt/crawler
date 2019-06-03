from selenium.webdriver.chrome.options import Options

chrome_options = Options()
# chrome_options.headless = True
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')  # for Windows OS ...
chrome_options.add_argument("--mute-audio")
