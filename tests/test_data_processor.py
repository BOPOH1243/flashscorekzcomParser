# tests/test_data_processor.py
from src.data_processor import get_league_matches, get_match_statistics


def test_get_league_matches(driver):
    """
    Проверяет, что в Английской Премьер-Лиге найдено ровно 384 сыгранных матча.
    """
    url = "https://www.flashscorekz.com/football/england/premier-league-2024-2025/results/"
    matches = get_league_matches(driver, url)

    # количество матчей фиксировано для сезона -> 380
    assert len(matches) == 380, f"Ожидалось 380 матча, найдено {len(matches)}"


def test_get_match_statistics(driver):
    """
    Проверяет корректность статистики матча Борнмут - Лестер.
    URL: https://www.flashscorekz.com/match/football/44RKa9ke/#/match-summary/match-statistics/0
    """
    url = "https://www.flashscorekz.com/match/football/44RKa9ke/#/match-summary/match-statistics/0"
    stats = get_match_statistics(driver, url)

    # команды
    assert stats["home_team"] == "Борнмут"
    assert stats["away_team"] == "Лестер"

    # счёт
    assert str(stats["score"]["home"]) == "2"
    assert str(stats["score"]["away"]) == "0"

    # угловые в разделе "АТАКА"
    corners = stats["sections"]["АТАКА"]["Угловые"]
    assert str(corners["home"]) == "6"
    assert str(corners["away"]) == "1"
