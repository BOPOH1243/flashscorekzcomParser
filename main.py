from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

chrome_options = Options()
chrome_options.add_argument("--no-sandbox") 
chrome_options.add_argument("--disable-dev-shm-usage")
#chrome_options.add_argument("--headless") # пока что без headless режима
chrome_options.add_argument("--disable-gpu") 
chrome_options.add_argument("--window-size=1920,1080")  

service = Service(ChromeDriverManager().install())  # Автоматически управляет версией ChromeDriver

driver = webdriver.Chrome(service=service, options=chrome_options)


def get_league_matches(url: str):
    wait = WebDriverWait(driver, 10)

    driver.get(url)

    # ждём появления блока с результатами
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".event.event--results")))

    # Кликаем на "Показать больше матчей" пока кнопка есть
    while True:
        try:
            show_more = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[span[text()='Показать больше матчей']]"))
            )
            driver.execute_script("arguments[0].click();", show_more)
            time.sleep(1.5)  # пауза для подгрузки
        except Exception:
            break

    # Собираем все матчи
    matches = driver.find_elements(By.CSS_SELECTOR, ".event__match")

    results = []
    for match in matches:
        try:
            link_el = match.find_element(By.CSS_SELECTOR, "a.eventRowLink")
            link = link_el.get_attribute("href")
        except Exception:
            link = None

        try:
            participants = [p.text for p in match.find_elements(By.CSS_SELECTOR, ".wcl-participant_bctDY")]
        except Exception:
            participants = []

        results.append({
            "url": link,
            "participants": participants
        })

    return results


try:
    league_url = "https://www.flashscorekz.com/football/england/premier-league-2024-2025/results/"
    matches_data = get_league_matches(league_url)

    print("\n--- Матчи ---")
    for m in matches_data:
        print(m)

except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    driver.quit()
