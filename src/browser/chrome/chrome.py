from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class HeadlessChrome(webdriver.Chrome):

    CAPS = DesiredCapabilities.CHROME
    CAPS['loggingPrefs'] = {'performance': 'ALL'}

    # set a headless browser
    OPTIONS = webdriver.ChromeOptions()
    OPTIONS.add_argument('headless')
    OPTIONS.add_experimental_option('w3c', False)

    def __init__(self, proxy=None):
        if proxy:
            self.OPTIONS.add_argument(f"--proxy-server={proxy.host}:{proxy.port}")

        super().__init__(
            chrome_options=self.OPTIONS,
            desired_capabilities=self.CAPS,
        )
