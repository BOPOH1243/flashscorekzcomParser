# main.py
from collections import defaultdict
from statistics import mean

from webdriver import get_webdriver
from data_processor import get_league_matches, get_match_statistics
from csv_exporter import export_to_csv


LEAGUE_URLS = [
    "https://www.flashscorekz.com/football/england/premier-league-2024-2025/results/",
    "https://www.flashscorekz.com/football/spain/laliga-2024-2025/results/",
]


def build_team_match_index(matches, limit=10):
    """
    Формирует словарь {команда: [10 матчей]}
    """
    teams = set()
    for m in matches:
        teams.update(m["participants"])

    team_matches = defaultdict(list)
    for team in teams:
        count = 0
        for match in matches:
            if team in match["participants"]:
                team_matches[team].append(match)
                count += 1
                if count >= limit:
                    break
    return team_matches


def extract_corners(stats, team_name):
    """
    Извлекает угловые для команды и соперника из структуры статистики матча
    """
    corners = stats.get("sections", {}).get("АТАКА", {}).get("Угловые")
    if not corners:
        return None, None

    home_team = stats.get("home_team")
    away_team = stats.get("away_team")

    home_val = corners["home"]
    away_val = corners["away"]

    if not isinstance(home_val, (int, float)) or not isinstance(away_val, (int, float)):
        try:
            home_val = int(home_val)
            away_val = int(away_val)
        except Exception:
            return None, None

    if team_name == home_team:
        return home_val, away_val
    elif team_name == away_team:
        return away_val, home_val
    return None, None


def main():
    driver = get_webdriver()
    all_team_matches = defaultdict(list)

    try:
        # 1. Сбор матчей для каждой лиги
        for url in LEAGUE_URLS:
            matches = get_league_matches(driver, url)
            team_matches = build_team_match_index(matches, limit=10)
            for team, mlist in team_matches.items():
                all_team_matches[team].extend(mlist)

        # 2. Сбор статистики по угловым
        team_corners = defaultdict(list)

        for team, matches in all_team_matches.items():
            for match in matches:
                stats = get_match_statistics(driver, match["url"])
                team_val, opp_val = extract_corners(stats, team)
                if team_val is not None and opp_val is not None:
                    total = team_val + opp_val
                    team_corners[team].append((total, team_val, opp_val))

        # 3. Подсчёт средних значений
        results = []
        for team, values in team_corners.items():
            if not values:
                continue
            avg_total = mean(v[0] for v in values)
            avg_team = mean(v[1] for v in values)
            avg_opp = mean(v[2] for v in values)

            results.append({
                "team": team,
                "avg_total_corners": avg_total,
                "avg_team_corners": avg_team,
                "avg_opponent_corners": avg_opp,
            })

        # 4. Сортировка по среднему тоталу
        results.sort(key=lambda x: x["avg_total_corners"], reverse=True)

        # 5. Экспорт в CSV
        export_to_csv(results, filename="corners_stats.csv")

        print("✅ Готово! Результаты сохранены в corners_stats.csv")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
