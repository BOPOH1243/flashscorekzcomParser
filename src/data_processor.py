# data_processor.py
import time
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _safe_int(s: str):
    if not s:
        return None
    s = s.strip()
    try:
        return int(s)
    except Exception:
        return s


def get_league_matches(driver, url: str) -> List[Dict[str, Any]]:
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".event.event--results")))

    # жмём "Показать больше матчей", пока кнопка есть
    while True:
        try:
            show_more = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[span[text()='Показать больше матчей']]"))
            )
            driver.execute_script("arguments[0].click();", show_more)
            time.sleep(1.5)
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
            participants = [p.text for p in match.find_elements(By.CSS_SELECTOR, ".wcl-participant_bctDY")]
        except Exception:
            participants = []

        if link and participants:
            results.append({"url": link, "participants": participants})

    return results


def get_match_statistics(driver, url: str) -> Dict[str, Any]:
    wait = WebDriverWait(driver, 15)

    base = url.split('#')[0]
    target_url = base + "#/match-summary/match-statistics/0"
    driver.get(target_url)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-analytics-context="tab-match-statistics"]')))
    time.sleep(0.8)

    result: Dict[str, Any] = {
        "home_team": None,
        "away_team": None,
        "score": {"home": None, "away": None},
        "sections": {}
    }

    # имена команд
    try:
        home_team_el = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__home")
        result["home_team"] = home_team_el.text.strip()
    except Exception:
        pass
    try:
        away_team_el = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__away")
        result["away_team"] = away_team_el.text.strip()
    except Exception:
        pass

    # счёт
    try:
        spans = driver.find_elements(By.CSS_SELECTOR, ".detailScore__wrapper>span")
        if len(spans) >= 2:
            result["score"]["home"] = _safe_int(spans[0].text)
            result["score"]["away"] = _safe_int(spans[1].text)
    except Exception:
        pass

    # секции
    sections = driver.find_elements(By.CSS_SELECTOR, ".section")
    for sec in sections:
        try:
            header_els = sec.find_elements(By.CSS_SELECTOR, ".sectionHeader")
            if not header_els:
                continue
            section_name = header_els[0].text.strip()
            if not section_name:
                continue

            stats_elems = sec.find_elements(By.CSS_SELECTOR, '[data-testid="wcl-statistics"]')
            if not stats_elems:
                continue

            section_data: Dict[str, Dict[str, Any]] = {}
            for stat in stats_elems:
                try:
                    cat_el = stat.find_element(By.CSS_SELECTOR, '[data-testid="wcl-statistics-category"]')
                    category_name = cat_el.text.strip()
                except Exception:
                    continue

                home_val = None
                away_val = None
                try:
                    home_val = stat.find_element(By.CSS_SELECTOR, ".wcl-value_XJG99.wcl-homeValue_3Q-7P").text.strip()
                except Exception:
                    pass
                try:
                    away_val = stat.find_element(By.CSS_SELECTOR, ".wcl-value_XJG99.wcl-awayValue_Y-QR1").text.strip()
                except Exception:
                    pass

                section_data[category_name] = {
                    "home": _safe_int(home_val),
                    "away": _safe_int(away_val)
                }

            if section_data:
                result["sections"][section_name] = section_data
        except Exception:
            continue

    return result
