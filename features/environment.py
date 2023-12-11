"""
Environment for Behave Testing
"""
from os import getenv
from selenium import webdriver
from behave import fixture, use_fixture
import requests


WAIT_SECONDS = int(getenv("WAIT_SECONDS", "60"))
BASE_URL = getenv("BASE_URL", "http://localhost:8000")
DRIVER = getenv("DRIVER", "chrome").lower()


def before_all(context):
    """Executed once before all tests"""
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS
    context.WAIT_SECONDS = WAIT_SECONDS
    # Select either Chrome or Firefox
    if "firefox" in DRIVER:
        context.driver = get_firefox()
    else:
        context.driver = get_chrome()
    context.driver.implicitly_wait(context.wait_seconds)
    context.config.setup_logging()


def after_all(context):
    """Executed after all tests"""
    context.driver.quit()


@fixture
def setup_custom_session(context):
    """Create a custom session for requests"""
    context.custom_session = requests.Session()
    context.custom_session.allow_redirects = True
    yield context.custom_session
    context.custom_session.close()


def before_feature(context, feature):
    """Executed before each feature"""
    use_fixture(setup_custom_session, context)


######################################################################
# Utility functions to create web drivers
######################################################################


def get_chrome():
    """Creates a headless Chrome driver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)


def get_firefox():
    """Creates a headless Firefox driver"""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)
