from selenium.webdriver.common.by import By


class SearchPageLocators:
    SEARCH_INPUT_USER = (By.XPATH, "//*[@id='username']")
    SEARCH_INPUT_PASSWORD = (By.XPATH, "//*[@id='password']")
    SEARCH_BUTTON = (By.XPATH, "//*[@id='loginbtn']")
    CHECKBOX_REMEMBERME = (By.XPATH, "//*[@id='rememberusername']")
    BUTTON_RESULT = SEARCH_BUTTON
    RESULTS = (By.XPATH, "//*[@id='action-menu-toggle-1']")
    BUTTON_LOGOUT = (By.XPATH, "//*[@id='actionmenuaction-7']")
    # TEST_EMAIL = (By.XPATH, "//*[@id='element-0']")
    # TEST_PASSWORD = (By.XPATH, "//*[@id='element-4']")
    # TEST_BUTTON = (By.XPATH, "//*[@class='nFxHGeI S7Jh9YX _8313bd46 _7a4dbd5f _95951888 _2a3b75a1 _8c75067a']")


