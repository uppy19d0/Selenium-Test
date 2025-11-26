from pathlib import Path
from typing import Optional, Union

from selenium.common.exceptions import TimeoutException # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore


class BasePage:
    def __init__(self, driver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def go_to_page(self, url: str):
        self.driver.get(url)

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        return element

    def fill(self, locator, value: str, clear_first: bool = True):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        if clear_first:
            element.clear()
        element.send_keys(value)
        return element

    def is_visible(self, locator, timeout: Optional[int] = None) -> bool:
        custom_wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            custom_wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def save_screenshot(self, file_path: Union[Path, str]):
        target_path = Path(file_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        self.driver.save_screenshot(str(target_path))
