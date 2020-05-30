import ipdb
from selenium import webdriver

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

CAPS = DesiredCapabilities.CHROME
CAPS['loggingPrefs'] = {'performance': 'ALL'}

# set a headless browser
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument('headless')
OPTIONS.add_experimental_option('w3c', False)

browser = webdriver.Chrome(
    executable_path="/home/ben/repos/us_zip_codes/selenium/chrome/chromedriver",
    chrome_options=OPTIONS,
    desired_capabilities=CAPS,
)

browser.get(
    "https://www.grubhub.com/"
)
logs = browser.get_log("performance")
ipdb.set_trace()

print(browser)
