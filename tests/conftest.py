import os
import warnings
from pathlib import Path

import pytest
from dotenv import load_dotenv
from py.xml import html  # type: ignore
from pytest_html import extras
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ServiceChrome
from selenium.webdriver.firefox.service import Service as ServiceFirefox
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from utils.config import load_settings

load_dotenv()
os.environ["WDM_LOG_LEVEL"] = "0"


@pytest.fixture(scope="session")
def settings():
    """Settings loaded once per session from data/config.yaml."""
    return load_settings()


@pytest.fixture(scope="session")
def credentials():
    """Credentials provided via environment variables."""
    return {
        "username": os.getenv("USERNAME", ""),
        "password": os.getenv("PASSWORD", ""),
        "invalid_password": os.getenv("FAIL_PASSWORD", "invalid-password"),
    }


def _build_driver(settings):
    browser = settings["browser"].lower()
    headless = settings.get("headless", False)

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
        return webdriver.Chrome(service=ServiceChrome(ChromeDriverManager().install()), options=options)

    if browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        if headless:
            options.add_argument("--headless")
        return webdriver.Firefox(service=ServiceFirefox(GeckoDriverManager().install()), options=options)

    raise ValueError(f"Unsupported browser: {browser}")


@pytest.fixture
def driver(settings):
    warnings.filterwarnings("ignore", category=ResourceWarning)
    browser_driver = _build_driver(settings)
    browser_driver.maximize_window()
    yield browser_driver
    browser_driver.quit()


@pytest.fixture
def wait(driver, settings):
    return WebDriverWait(driver, settings.get("wait_timeout", 10))


def pytest_configure(config):
    """Add useful metadata to the HTML report."""
    settings = load_settings()
    metadata = getattr(config, "_metadata", {})
    metadata.update(
        {
            "Base URL": settings["base_url"],
            "Browser": settings["browser"],
            "Headless": settings["headless"],
            "Wait timeout (s)": settings["wait_timeout"],
        }
    )
    config._metadata = metadata

    reports_dir = Path("results")
    reports_dir.mkdir(exist_ok=True)


def pytest_html_report_title(report):
    report.title = "Selenium UI Test Report"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach description and screenshots to the HTML report."""
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__ or "").strip()

    if report.when != "call":
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    extra = getattr(report, "extra", [])
    if report.failed:
        screenshot_base64 = driver.get_screenshot_as_base64()
        extra.append(extras.image(screenshot_base64, "base64", "Failure Screenshot"))
    report.extra = extra


def pytest_html_results_table_header(cells):
    cells.insert(1, html.th("Description"))


def pytest_html_results_table_row(report, cells):
    cells.insert(1, html.td(report.description))
