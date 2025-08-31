# src/data_processor.py
import time
from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ------------------ Утилиты ------------------

def _safe_int(s: Optional[str]) -> Optional[int]:
    """Пробует привести строку к int, возвращает None при неудаче."""
    if not s:
        return None
    try:
        return int(str(s).strip())
    except ValueError:
        return None


# ------------------ League Matches ------------------

def _expand_all_matches(driver: WebDriver, wait: WebDriverWait) -> None:
    """Кликает по 'Показать больше матчей' пока возможно."""
    while True:
        try:
            show_more = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[span[text()='Показать больше матчей']]"))
            )
            driver.execute_script("arguments[0].click();", show_more)
            time.sleep(1.2)
        except Exception:
            break


def _parse_match_element(match_el) -> Optional[Dict[str, Any]]:
    """Парсит один элемент матча в словарь {url, participants}."""
    try:
        link_el = match_el.find_element(By.CSS_SELECTOR, "a.eventRowLink")
        link = link_el.get_attribute("href")
    except Exception:
        return None

    participants = [
        p.text.strip()
        for p in match_el.find_elements(By.CSS_SELECTOR, ".wcl-participant_bctDY")
        if p.text.strip()
    ]

    if not (link and participants):
        return None

    return {"url": link, "participants": participants}


def get_league_matches(driver: WebDriver, url: str) -> List[Dict[str, Any]]:
    """
    Собирает список матчей со страницы результатов лиги.
    Возвращает [{'url': ..., 'participants': [team1, team2]}, ...]
    """
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".event.event--results")))

    _expand_all_matches(driver, wait)

    matches = driver.find_elements(By.CSS_SELECTOR, ".event__match")
    return [m for m in (_parse_match_element(el) for el in matches) if m]


# ------------------ Match Statistics ------------------

def _normalize_match_url(url: str) -> str:
    """Заменяет хвост ссылки на '#/match-summary/match-statistics/0'."""
    return url.split('#')[0] + "#/match-summary/match-statistics/0"


def _get_team_names(driver: WebDriver) -> Dict[str, Optional[str]]:
    """Возвращает имена команд home/away."""
    home = away = None
    try:
        home = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__home").text.strip()
    except Exception:
        pass
    try:
        away = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__away").text.strip()
    except Exception:
        pass
    return {"home_team": home, "away_team": away}


def _get_score(driver: WebDriver) -> Dict[str, Optional[int]]:
    """Возвращает счёт матча (home/away)."""
    score = {"home": None, "away": None}
    try:
        spans = driver.find_elements(By.CSS_SELECTOR, ".detailScore__wrapper>span")
        if len(spans) >= 2:
            score["home"] = _safe_int(spans[0].text)
            score["away"] = _safe_int(spans[2].text) if len(spans) > 2 else _safe_int(spans[1].text)
    except Exception:
        pass
    return score


def _parse_section(section_el) -> Optional[Dict[str, Any]]:
    """Парсит одну секцию статистики (например 'АТАКА')."""
    try:
        header = section_el.find_elements(By.CSS_SELECTOR, ".sectionHeader")
        if not header:
            return None
        section_name = header[0].text.strip()
        if not section_name:
            return None

        stats = section_el.find_elements(By.CSS_SELECTOR, '[data-testid="wcl-statistics"]')
        if not stats:
            return None

        section_data = {}
        for s in stats:
            try:
                cat_el = s.find_element(By.CSS_SELECTOR, '[data-testid="wcl-statistics-category"]')
                cat_name = cat_el.text.strip()
            except Exception:
                continue

            home_val, away_val = None, None
            try:
                home_val = s.find_element(By.CSS_SELECTOR, ".wcl-value_XJG99.wcl-homeValue_3Q-7P").text.strip()
            except Exception:
                try:
                    home_val = s.find_element(By.CSS_SELECTOR, ".wcl-homeValue").text.strip()
                except Exception:
                    pass
            try:
                away_val = s.find_element(By.CSS_SELECTOR, ".wcl-value_XJG99.wcl-awayValue_Y-QR1").text.strip()
            except Exception:
                try:
                    away_val = s.find_element(By.CSS_SELECTOR, ".wcl-awayValue").text.strip()
                except Exception:
                    pass

            section_data[cat_name] = {"home": home_val, "away": away_val}

        return {section_name: section_data} if section_data else None
    except Exception:
        return None


def _get_sections(driver: WebDriver) -> Dict[str, Any]:
    """Возвращает все секции статистики матча."""
    result = {}
    sections = driver.find_elements(By.CSS_SELECTOR, ".section")
    for sec in sections:
        parsed = _parse_section(sec)
        if parsed:
            result.update(parsed)
    return result


def get_match_statistics(driver: WebDriver, url: str) -> Dict[str, Any]:
    """
    Открывает страницу матча, ждёт загрузки статистики и возвращает:
    {
      "home_team": str|None,
      "away_team": str|None,
      "score": {"home": int|None, "away": int|None},
      "sections": { section_name: { category_name: {"home": val, "away": val}, ... } }
    }
    """
    wait = WebDriverWait(driver, 15)

    driver.get(_normalize_match_url(url))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-analytics-context="tab-match-statistics"]')))
    time.sleep(0.6)  # дать JS догрузиться

    teams = _get_team_names(driver)
    score = _get_score(driver)
    sections = _get_sections(driver)

    return {
        "home_team": teams["home_team"],
        "away_team": teams["away_team"],
        "score": score,
        "sections": sections,
    }
