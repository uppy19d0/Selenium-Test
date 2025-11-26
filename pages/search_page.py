from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from data.locators import SearchPageLocators
from pages.base_page import BasePage


class SearchPage(BasePage):
    def __init__(self, driver, wait, base_url: str):
        super().__init__(driver, wait)
        self.url = base_url.rstrip("/")
        self.locator = SearchPageLocators

    def open(self):
        self.go_to_page(self.url)

    def login(self, username: str, password: str, remember_me: bool = False):
        self.fill(self.locator.USERNAME_INPUT, username)
        self.fill(self.locator.PASSWORD_INPUT, password)
        self.set_remember_me(remember_me)
        self.click(self.locator.LOGIN_BUTTON)

    def set_remember_me(self, enable: bool) -> WebElement:
        checkbox = self.wait.until(EC.element_to_be_clickable(self.locator.REMEMBER_ME_CHECKBOX))
        if checkbox.is_selected() != enable:
            checkbox.click()
        return checkbox

    def is_login_error_displayed(self, timeout: int = 5) -> bool:
        return self.is_visible(self.locator.ERROR_MESSAGE, timeout)

    def is_login_form_visible(self) -> bool:
        return self.is_visible(self.locator.LOGIN_BUTTON, timeout=5)

    def is_logged_in(self) -> bool:
        return self.is_visible(self.locator.USER_MENU_TOGGLE, timeout=10)

    def open_user_menu(self):
        return self.click(self.locator.USER_MENU_TOGGLE)

    def logout(self):
        self.open_user_menu()
        self.click(self.locator.LOGOUT_BUTTON)

    def get_validation_message(self, locator) -> str:
        try:
            element = self.wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            return ""
        return element.get_attribute("validationMessage") or ""
