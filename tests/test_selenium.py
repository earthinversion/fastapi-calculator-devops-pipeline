"""
Selenium UI tests — spins up the FastAPI app via uvicorn, opens a browser,
and tests the UI end-to-end.
Run these AFTER the unit tests (they're slower).

Requirements:
  - Chrome + chromedriver installed
  - All packages in requirements.txt installed

To run just these tests:
  pytest tests/test_selenium.py
"""

import sys
import os
import time
import threading
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

# --- Skip gracefully if selenium is not installed ---
selenium = pytest.importorskip("selenium", reason="selenium not installed — skipping UI tests")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import uvicorn
import app as fastapi_app


@pytest.fixture(scope="module")
def server():
    """Start the FastAPI app via uvicorn in a background thread."""
    config = uvicorn.Config(fastapi_app.app, host="127.0.0.1", port=5001, log_level="error")
    srv = uvicorn.Server(config)
    thread = threading.Thread(target=srv.run)
    thread.daemon = True
    thread.start()
    time.sleep(1)  # give the server a moment to start
    yield
    # thread is daemon — dies when tests finish


@pytest.fixture(scope="module")
def driver():
    """Headless Chrome driver."""
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    d = webdriver.Chrome(options=opts)
    yield d
    d.quit()


BASE_URL = "http://localhost:5001"


class TestCalculatorUI:
    def test_page_loads(self, server, driver):
        driver.get(BASE_URL)
        assert "Calculator" in driver.title

    def test_addition(self, server, driver):
        driver.get(BASE_URL)
        driver.find_element(By.NAME, "a").send_keys("10")
        driver.find_element(By.NAME, "b").send_keys("5")
        Select(driver.find_element(By.NAME, "operation")).select_by_value("add")
        driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        result = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "result"))
        ).text
        assert "15" in result

    def test_division_by_zero(self, server, driver):
        driver.get(BASE_URL)
        driver.find_element(By.NAME, "a").send_keys("10")
        driver.find_element(By.NAME, "b").send_keys("0")
        Select(driver.find_element(By.NAME, "operation")).select_by_value("divide")
        driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        error = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "error"))
        ).text
        assert "zero" in error.lower()
