# coding=utf-8
import os
import pytest
from pages.search_page import SearchPage
from tests.base_test import BaseTest
from dotenv import load_dotenv

load_dotenv()

class TestSearch(BaseTest):

    @pytest.fixture
    def load_pages(self):
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        failpassword = os.getenv("FAIL_PASSWORD")

        self.page = SearchPage(self.driver, self.wait)
        self.page.go_to_search_page()
        return username, password, failpassword

    def test_login_fail(self, load_pages):
        username, password,failpassword = load_pages
        self.page.make_a_login_fail(username, failpassword)

    def test_login_pass(self, load_pages):
        username, password, failpassword = load_pages
        self.page.make_a_login_pass(username, password)

