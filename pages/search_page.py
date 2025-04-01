from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from data.locators import SearchPageLocators


class SearchPage(BasePage):

    def __init__(self, driver, wait):
        super().__init__(driver, wait)
        self.url = "https://plataformavirtual.itla.edu.do"
        self.locator = SearchPageLocators

    def go_to_search_page(self):
        self.go_to_page(self.url)

    def make_a_login_fail(self, input_user, input_password):
        self.driver.find_element(*self.locator.SEARCH_INPUT_USER).send_keys(input_user)
        self.driver.find_element(*self.locator.SEARCH_INPUT_PASSWORD).send_keys(input_password)
        self.driver.find_element(*self.locator.SEARCH_BUTTON).click()
        self.wait.until(EC.presence_of_element_located(self.locator.BUTTON_RESULT))
        self.driver.save_screenshot("results/fail_login.png")

    def make_a_login_pass(self, input_user, input_password):
        self.driver.save_screenshot("results/intro_page.png")
        self.driver.find_element(*self.locator.SEARCH_INPUT_USER).send_keys(input_user)
        self.driver.save_screenshot("results/insert_user.png")
        self.driver.find_element(*self.locator.SEARCH_INPUT_PASSWORD).send_keys(input_password)
        self.driver.save_screenshot("results/password.png")
        self.driver.find_element(*self.locator.SEARCH_BUTTON).click()
        self.driver.save_screenshot("results/login.png")
        self.driver.find_element(*self.locator.RESULTS).click()
        self.driver.save_screenshot("results/droplist.png")
        self.wait.until(EC.presence_of_element_located(self.locator.BUTTON_LOGOUT))
        self.driver.find_element(*self.locator.BUTTON_LOGOUT).click()
        self.driver.save_screenshot("results/logout.png")


