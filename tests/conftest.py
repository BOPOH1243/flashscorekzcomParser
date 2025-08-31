# tests/conftest.py
import pytest
from src.webdriver import get_webdriver


@pytest.fixture(scope="session")
def driver():
    """
    Фикстура pytest для инициализации и закрытия Selenium WebDriver.
    Запускается один раз на сессию.
    """
    driver = get_webdriver()
    yield driver
    driver.quit()
