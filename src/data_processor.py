# data_processor.py
import time
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _safe_int(s):
    """
    Пробует преобразовать s в int, иначе возвращает None.
    s может быть '6' или ' 6 ' — учитываем пробелы.
    """
    if s is None:
        return None
    try:
        return int(str(s).strip())
    except Exception:
        return None


def get_league_matches(driver, url: str) -> List[Dict[str, Any]]:
    """
    Собирает список матчей со страницы результатов лиги.
    Возвращает список словарей {'url': ..., 'participants': [team1, team2]}.
    driver: экземпляр webdriver (передаём извне).
    """
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".event.event--results")))

    # Нажимаем "Показать больше матчей" пока элемент существует
    while True:
        try:
            show_more = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[span[text()='Показать больше матчей']]"))
            )
            driver.execute_script("arguments[0].click();", show_more)
            time.sleep(1.2)
        except Exception:
            break

    matches = driver.find_elements(By.CSS_SELECTOR, ".event__match")
    results = []
    for match in matches:
        try:
            link_el = match.find_element(By.CSS_SELECTOR, "a.eventRowLink")
            link = link_el.get_attribute("href")
        except Exception:
            link = None

        try:
            participants = [p.text.strip() for p in match.find_elements(By.CSS_SELECTOR, ".wcl-participant_bctDY")]
        except Exception:
            participants = []

        if link and participants:
            results.append({"url": link, "participants": participants})
    return results


def get_match_statistics(driver, url: str) -> Dict[str, Any]:
    """
    Открывает страницу матча (нормализуя фрагмент после # к '#/match-summary/match-statistics/0'),
    ждёт загрузки статистики и возвращает словарь:
    {
      "home_team": str or None,
      "away_team": str or None,
      "score": {"home": int|None, "away": int|None},
      "sections": { section_name: { category_name: {"home": val, "away": val}, ... }, ... }
    }

    Простая (жёсткая) реализация: минимальные fallback'ы, без сложного парсинга строк.
    """
    wait = WebDriverWait(driver, 15)

    base = url.split('#')[0]
    target = base + "#/match-summary/match-statistics/0"
    driver.get(target)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-analytics-context="tab-match-statistics"]')))
    time.sleep(0.6)  # дать JS подгрузиться

    result: Dict[str, Any] = {
        "home_team": None,
        "away_team": None,
        "score": {"home": None, "away": None},
        "sections": {}
    }

    # home / away имена команд
    try:
        home_el = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__home")
        result["home_team"] = home_el.text.strip()
    except Exception:
        pass
    try:
        away_el = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__away")
        result["away_team"] = away_el.text.strip()
    except Exception:
        pass

    # счёт голов
    try:
        spans = driver.find_elements(By.CSS_SELECTOR, ".detailScore__wrapper>span")
        if len(spans) >= 2:
            result["score"]["home"] = _safe_int(spans[0].text)
            result["score"]["away"] = _safe_int(spans[2].text)
    except Exception:
        pass

    # секции: мы перебираем .section, но берём только те, у которых есть .sectionHeader
    sections = driver.find_elements(By.CSS_SELECTOR, ".section")
    for sec in sections:
        try:
            header = sec.find_elements(By.CSS_SELECTOR, ".sectionHeader")
            if not header:
                continue
            section_name = header[0].text.strip()
            if not section_name:
                continue

            stats = sec.find_elements(By.CSS_SELECTOR, '[data-testid="wcl-statistics"]')
            if not stats:
                continue

            section_data = {}
            for s in stats:
                try:
                    cat_el = s.find_element(By.CSS_SELECTOR, '[data-testid="wcl-statistics-category"]')
                    cat_name = cat_el.text.strip()
                except Exception:
                    continue

                # Берём домашнее и гостевое значения по жёстким селекторам (как было указано)
                home_val = None
                away_val = None
                try:
                    home_val = s.find_element(By.CSS_SELECTOR, ".wcl-value_XJG99.wcl-homeValue_3Q-7P").text.strip()
                except Exception:
                    # если не найдено — пробуем общий класс
                    try:
                        home_val = s.find_element(By.CSS_SELECTOR, ".wcl-homeValue").text.strip()
                    except Exception:
                        home_val = None
                try:
                    away_val = s.find_element(By.CSS_SELECTOR, ".wcl-value_XJG99.wcl-awayValue_Y-QR1").text.strip()
                except Exception:
                    try:
                        away_val = s.find_element(By.CSS_SELECTOR, ".wcl-awayValue").text.strip()
                    except Exception:
                        away_val = None

                section_data[cat_name] = {"home": home_val, "away": away_val}

            if section_data:
                result["sections"][section_name] = section_data
        except Exception:
            continue

    return result
