import pytest # type: ignore

class BaseTest:
    """Base class to expose fixtures as attributes for class-based tests."""

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, driver, wait, settings, credentials):
        self.driver = driver
        self.wait = wait
        self.settings = settings
        self.credentials = credentials
