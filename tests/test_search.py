from typing import Dict, List
import pytest  # type: ignore

from pages.search_page import SearchPage


def _require_credentials(credentials: Dict, required_keys: List[str]):
    missing = [key for key in required_keys if not credentials.get(key)]
    if missing:
        pytest.skip(f"Faltan variables de entorno para las pruebas: {', '.join(missing)}")


@pytest.fixture
def login_page(driver, wait, settings):
    page = SearchPage(driver, wait, settings["base_url"])
    page.open()
    return page


def test_login_with_invalid_password_shows_error(login_page, credentials):
    """Login muestra error cuando la contraseña es incorrecta."""
    _require_credentials(credentials, ["username", "invalid_password"])

    login_page.login(credentials["username"], credentials["invalid_password"], remember_me=True)
    assert login_page.is_login_error_displayed(), "Debería mostrarse un mensaje de error al fallar el login."


def test_login_without_password_shows_validation(login_page, credentials):
    """Validación al intentar iniciar sesión sin contraseña."""
    _require_credentials(credentials, ["username"])

    login_page.login(credentials["username"], "")
    validation = login_page.get_validation_message(login_page.locator.PASSWORD_INPUT)
    assert validation or login_page.is_login_error_displayed(), "Se espera validación o mensaje de error sin contraseña."
    assert login_page.is_login_form_visible(), "El formulario de login debe seguir visible."


def test_login_without_username_shows_validation(login_page, credentials):
    """Validación al intentar iniciar sesión sin usuario."""
    _require_credentials(credentials, ["password"])

    login_page.login("", credentials["password"])
    validation = login_page.get_validation_message(login_page.locator.USERNAME_INPUT)
    assert validation or login_page.is_login_error_displayed(), "Se espera validación o mensaje de error sin usuario."
    assert login_page.is_login_form_visible(), "El formulario de login debe seguir visible."


@pytest.mark.smoke
def test_user_can_login_and_logout(login_page, credentials):
    """Flujo completo: login exitoso y logout."""
    _require_credentials(credentials, ["username", "password"])

    login_page.login(credentials["username"], credentials["password"])
    assert login_page.is_logged_in(), "El menú de usuario debe ser visible después del login."

    login_page.logout()
    assert login_page.is_login_form_visible(), "Tras cerrar sesión debe volver el formulario de login."


def test_remember_me_can_be_toggled(login_page):
    """El checkbox de 'Recordar usuario' permite activarse y desactivarse."""
    checkbox = login_page.set_remember_me(True)
    assert checkbox.is_selected(), "El checkbox debe quedar activado."

    checkbox = login_page.set_remember_me(False)
    assert not checkbox.is_selected(), "El checkbox debe quedar desactivado."
