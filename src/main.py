# main.py
from collections import defaultdict
from webdriver import get_webdriver
from data_processor import get_league_matches, get_match_statistics


def build_team_match_index(matches, limit=10):
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


def main():
    driver = get_webdriver()
    try:
        league_url = "https://www.flashscorekz.com/football/england/premier-league-2024-2025/results/"
        matches = get_league_matches(driver, league_url)
        print(f"Всего матчей собрано: {len(matches)}")

        team_matches = build_team_match_index(matches, limit=10)
        print(f"Команд собрано: {len(team_matches)}")

        # пример обработки матча
        if matches:
            first_match = matches[0]
            stats = get_match_statistics(driver, first_match["url"])
            print("\n--- Пример статистики ---")
            print(stats)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
