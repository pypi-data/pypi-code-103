import os
from os.path import dirname
import pytest
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType, os_type
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
import time
from pathlib import Path


class SE:
    driver = webdriver.Chrome
    remote = False
    huburl = None
    browser = ""
    browserversion = None
    os = None
    osversion = None
    device = None
    deviceorientation = None
    environmentURL = ''

    # def __init__(self, attr):
    # self.driver = attr

    @staticmethod
    def FrameworkInitialize():
        SE.GetExecutionDetails()

    @staticmethod
    def LaunchDriver(navigateToDefaultURL=True, desiredCap=None, driverOptions=None,headLess=False):
        # SelEx.GetExecutionDetails()
        if not SE.remote:
            if SE.browser.lower() == "chrome":
                if driverOptions is None:
                    driverOptions = webdriver.ChromeOptions()
                    prefs = {'download.prompt_for_download': False}
                    driverOptions.add_experimental_option("prefs", prefs)
                    driverOptions.add_argument('disable-web-security')
                    driverOptions.add_argument('ignore-certificate-errors')
                    driverOptions.add_argument('disable-infobars')
                else:
                    prefs = {'download.prompt_for_download': False}
                    driverOptions.add_experimental_option("prefs", prefs)
                    driverOptions.add_argument('disable-web-security')
                    driverOptions.add_argument('ignore-certificate-errors')
                if desiredCap is None:
                    desiredCap = webdriver.DesiredCapabilities.CHROME.copy()
                    desiredCap['acceptSslCerts'] = True
                else:
                    desiredCap['acceptSslCerts'] = True

                if headLess is True:
                    driverOptions.add_argument('--headless')
                SE.driver = webdriver.Chrome(ChromeDriverManager().install(),
                                             desired_capabilities=desiredCap, chrome_options=driverOptions)
            elif SE.browser.lower() == "firefox":
                if driverOptions is None:
                    driverOptions = Options()
                if desiredCap is None:
                    desiredCap = webdriver.DesiredCapabilities.FIREFOX.copy()
                    desiredCap['marionette'] = True
                else:
                    desiredCap['marionette'] = True

                SE.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),
                                              desired_capabilities=desiredCap, options=driverOptions)
            elif SE.browser.lower() == "edge":
                if desiredCap is None:
                    desiredCap = webdriver.DesiredCapabilities.EDGE.copy()
                    desiredCap['acceptSslCerts'] = True
                    desiredCap['javascriptEnabled'] = True
                    # SelEx.driver =
                else:
                    desiredCap['acceptSslCerts'] = True
                    desiredCap['javascriptEnabled'] = True
                    SE.driver = webdriver.Edge(executable_path=EdgeChromiumDriverManager().install(),
                                               capabilities=desiredCap)
            SE.driver.maximize_window()
        else:
            if 'browserstack' in SE.huburl:
                desiredCap = SE.ConstructBrowserStackCapabilities(SE.os, SE.browser, SE.browserversion,
                                                                  SE.osversion, 'false', SE.device,
                                                                  SE.deviceorientation)
            elif 'pcloudy.com' in SE.huburl:
                desiredCap = SE.ConstructPCloudyCapabilities("", "", SE.os, SE.browser, SE.device,
                                                             SE.browserversion, SE.osversion)

            if desiredCap is None:
                if SE.browser.lower() == "chrome":
                    desiredCap = webdriver.DesiredCapabilities.CHROME
                    desiredCap['acceptSslCerts'] = True
                elif SE.browser.lower() == "firefox":
                    desiredCap = webdriver.DesiredCapabilities.FIREFOX
                elif SE.browser.lower() == "safari":
                    desiredCap = webdriver.DesiredCapabilities.SAFARI
                elif SE.browser.lower() == "edge":
                    desiredCap = webdriver.DesiredCapabilities.EDGE
            if driverOptions is None:
                if SE.browser.lower() == "chrome":
                    driverOptions = webdriver.ChromeOptions()
                    driverOptions.add_argument('disable-web-security')
                    driverOptions.add_argument('ignore-certificate-errors')
                elif SE.browser.lower() == "firefox":
                    driverOptions = webdriver.FirefoxOptions
            SE.driver = webdriver.Remote(SE.huburl, desired_capabilities=desiredCap)
        if SE.environmentURL is not '':
            if navigateToDefaultURL:
                SE.driver.get(SE.environmentURL)
        return SE.driver

    @staticmethod
    def WaitForPageLoad(timeOut=50):
        wait = WebDriverWait(SE.driver, 2)
        start_time = time.time()
        state = SE.driver.execute_script('return document.readyState') == 'complete'
        while not state:
            current_time = time.time()
            elapsed_time = current_time - start_time
            state = SE.driver.execute_script('return document.readyState') == 'complete'
            if elapsed_time > timeOut | state:
                break

    @staticmethod
    def WaitForElement(element, visibility=True):
        wait = WebDriverWait(SE.driver, 2)
        if visibility:
            wait.until(EC.visibility_of_element_located(element))
        else:
            wait.until(EC.invisibility_of_element_located(element))

    @staticmethod
    def GetProjectPath():
        return SE.prjpth(os.getcwd())

    def prjpth(path=''):
        lst = path.split('\\')
        if lst[-1] == 'Test':
            return dirname(path)
        else:
            lst = lst[:-1]
            # print(lst)
            SE.prjpth('\\'.join(lst))

    @staticmethod
    def GetWorkingDirectory():
        return os.path.dirname(__file__)

    @staticmethod
    def GetExecutionDetails():
        dir = SE.GetProjectPath()
        executionenvironmentpath = os.path.join(dir, 'TestData\executionenvironment.txt')
        environmentURLFilePath = os.path.join(dir, 'TestData\environmentURL.txt')

        environmentURLFile = open(environmentURLFilePath, 'r')
        SE.environmentUR = environmentURLFile.readlines()[0].strip('\n')
        environmentURLFile.close()

        file = open(executionenvironmentpath, 'r')
        executiondetails = file.readlines()
        for str in executiondetails:
            command = str.split('|')[0]
            value = str.split('|')[1].strip('\n')
            if value.lower() is 'none':
                value = None
            elif value is '':
                value = None
            if command == 'remote':
                if value == 'true':
                    SE.remote = True
                else:
                    SE.remote = False
            elif command == 'huburl':
                SE.huburl = value
            elif command == 'browser':
                SE.browser = value
            elif command == 'browserversion':
                SE.browserversion = value
            elif command == 'os':
                SE.os = value
            elif command == 'osversion':
                SE.osversion = value
            elif command == 'device':
                SE.device = value
            elif command == 'orientation':
                SE.deviceorientation = value

        file.close()

    @staticmethod
    def ConstructBrowserStackCapabilities(OS, browser, browserVersion=None, OSVersion=None, browserStackLocal='false',
                                          device=None, deviceOrientation=None):
        desiredCap = {
            "OS": OS,
            "browser": browser,
            "browserstack.local": browserStackLocal
        }

        if OSVersion != 'None':
            desiredCap['os_version'] = OSVersion
        if browserVersion != 'None':
            desiredCap['browser_version'] = browserVersion
        if device != 'None':
            desiredCap['device'] = device
            desiredCap['real_mobile'] = "true"
        if deviceOrientation is not None:
            desiredCap['deviceOrientation'] = deviceOrientation

        return desiredCap

    @staticmethod
    def ConstructPCloudyCapabilities(userName, apiKey, OS, browser, deviceName, browserVersion=None, OSVersion=None):
        desiredCap = {
            "pCloudy_Username": userName,
            "pCloudy_ApiKey": apiKey,
            "browser": browser,
            "pCloudy_DeviceFullName": deviceName,
            "platformName": OS,
            "pCloudy_DurationInMinutes": "60",
            "pCloudy_WildNet": "true",
            "pCloudy_EnableVideo": "true",
            "pCloudy_EnablePerformanceData": "true",
            "pCloudy_EnableDeviceLogs": "true"
        }
        if OSVersion != 'None':
            desiredCap['os_version'] = OSVersion
        if browserVersion != 'None':
            desiredCap['browser_version'] = browserVersion

        return desiredCap

    @staticmethod
    def GetCurrentTestName():
        return os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(item, call):
        pytest_html = item.config.pluginmanager.getplugin("html")
        outcome = yield
        report = outcome.get_result()
        extra = getattr(report, "extra", [])
        if report.when == "call":
            # always add url to report
            extra.append(pytest_html.extras.url("http://www.example.com/"))
            xfail = hasattr(report, "wasxfail")
            if (report.skipped and xfail) or (report.failed and not xfail):
                # only add additional html on failure
                report_directory = os.path.dirname(item.config.option.htmlpath)
                file_name = report.nodeid.replace("::", "_") + ".png"
                destinationFile = os.path.join(report_directory, file_name)
                SE.driver.save_screenshot(destinationFile)
                if file_name:
                    html = '<div><img src="%s" alt="screenshot" style="width:300px;height=200px" ' \
                           'onclick="window.open(''this.src)" align="right"/></div' % file_name
                extra.append(pytest_html.extras.html(html))
            report.extra = extra

    def pytest_html_report_title(report):
        report.title = "Test Automation Report - Customer Analytics"
    """
    @staticmethod
    def HighlightElement(element):
        script = r"arguments[0].style.cssText = ""border-width: 4px; border-style: solid; border-color: red""; "
        SelEx.driver.execute_script(script, element)
        time.sleep(2)
        clearscript = r"arguments[0].style.cssText = ""border-width: 0px; border-style: solid; border-color: red""; "
        SelEx.driver.execute_script(clearscript, element)"""

    '''DesiredCapabilities capabilities = new DesiredCapabilities();
capabilities.setCapability("pCloudy_Username", "radhakrishnan.j@customeranalytics.com");
capabilities.setCapability("pCloudy_ApiKey", "gvz7zb6y63tsqkxhs7b68mrf");
capabilities.setCapability("pCloudy_DurationInMinutes", 60);
capabilities.setCapability("newCommandTimeout", 600);
capabilities.setCapability("launchTimeout", 90000);
capabilities.setCapability("pCloudy_DeviceFullName", "APPLE_iPhoneXS_iOS_13.6.1_d7aff");
capabilities.setCapability("platformVersion", "13.6.1");
capabilities.setCapability("platformName", "ios");
capabilities.setCapability("acceptAlerts", true);
capabilities.setCapability("automationName", "XCUITest");
capabilities.setBrowserName("Safari");
capabilities.setCapability("pCloudy_WildNet", "true");
capabilities.setCapability("pCloudy_EnableVideo", "true");
capabilities.setCapability("pCloudy_EnablePerformanceData", "true");
capabilities.setCapability("pCloudy_EnableDeviceLogs", "true");
IOSDriver<WebElement> driver = new IOSDriver<WebElement>(new URL("https://device.pcloudy.com/appiumcloud/wd/hub"), capabilities);'''
