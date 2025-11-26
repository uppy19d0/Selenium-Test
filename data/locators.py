from selenium.webdriver.common.by import By


class SearchPageLocators:
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "loginbtn")
    REMEMBER_ME_CHECKBOX = (By.ID, "rememberusername")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "div[role='alert'], .alert-danger")

    USER_MENU_TOGGLE = (By.ID, "action-menu-toggle-1")
    USER_MENU = (By.CSS_SELECTOR, "[data-region='user-menu']")
    LOGOUT_BUTTON = (By.ID, "actionmenuaction-7")

