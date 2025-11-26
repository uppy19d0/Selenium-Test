from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from data.locators import SearchPageLocators


class SearchPage(BasePage):

    def __init__(self, driver, wait):
        super().__init__(driver, wait)
        self.url = "https://plataformavirtual.itla.edu.do"
        self.locator = SearchPageLocators

# daniel
        # //agregar inventario
        # //editar inventario
        #//notificacion
        # 5/3 HISTORIAS DE USUARIOS

        # //10 HOSTORIAS DE USUARIOS

    def go_to_search_page(self):
        self.go_to_page(self.url)

    # //command + click o ctrl + click
    # //caso de prueba rechazo o cuando el usuario no existe/credenciales incorrecta
    # [test case]fallido
    def make_a_login_fail(self, input_user, input_password):
        self.driver.find_element(*self.locator.SEARCH_INPUT_USER).send_keys(input_user) #COLOCAR EL USUARIO  INCORRECTO
        self.driver.find_element(*self.locator.SEARCH_INPUT_PASSWORD).send_keys(input_password) #COLOCAR EL PASSOWRD INCORRECTO
        self.driver.find_element(*self.locator.CHECKBOX_REMEMBERME).click() #CLICK AL CHECKBOX REMEMBER ME
        self.driver.find_element(*self.locator.SEARCH_BUTTON).click() #CLICK AL  BUTON DE LOGIN
        self.wait.until(EC.presence_of_element_located(self.locator.BUTTON_RESULT))
        self.driver.save_screenshot("results/fail_login.png")

    # //caso de prueba existo o con un usuario real o existente 
    def make_a_login_pass(self, input_user, input_password):
        self.driver.save_screenshot("results/intro_page.png")
        self.driver.find_element(*self.locator.SEARCH_INPUT_USER).send_keys(input_user)
        self.driver.save_screenshot("results/insert_user.png")
        self.driver.find_element(*self.locator.SEARCH_INPUT_PASSWORD).send_keys(input_password)
        self.driver.save_screenshot("results/password.png")
        self.driver.find_element(*self.locator.CHECKBOX_REMEMBERME).click() #CLICK AL CHECKBOX REMEMBER ME
        self.driver.save_screenshot("results/checkbok_click.png")
        self.driver.find_element(*self.locator.SEARCH_BUTTON).click()
        self.driver.save_screenshot("results/login.png")
        self.driver.find_element(*self.locator.RESULTS).click()
        self.driver.save_screenshot("results/droplist.png")
        self.wait.until(EC.presence_of_element_located(self.locator.BUTTON_LOGOUT))
        self.driver.find_element(*self.locator.BUTTON_LOGOUT).click()
        self.driver.save_screenshot("results/logout.png")


